#!/usr/bin/env bash

# Routes one review prompt (stdin) to one review agent and prints one validated
# review package (stdout). Any non-zero exit means the review is INCOMPLETE and
# must never be reported as clean.
#
# Adding an agent means adding one file to agents/ that defines
# ADAPTER_DECODER, ADAPTER_SUMMARY, adapter_available, adapter_missing_reason,
# and adapter_run. Nothing else in this skill changes.

set -uo pipefail

export LC_ALL=C

agent="${REVIEW_AGENT:-auto}"
max_turns="${REVIEW_MAX_TURNS:-10}"
timeout_seconds="${REVIEW_TIMEOUT_SECONDS:-600}"
max_output_bytes="${REVIEW_MAX_OUTPUT_BYTES:-24576}"
# Headroom for an adapter's own cooperative timeout to fire first, so acpx can
# exit cleanly and report a real diagnosis before the watchdog kills the tree.
timeout_grace_seconds="${REVIEW_TIMEOUT_GRACE_SECONDS:-60}"
debug_root="${REVIEW_DEBUG_DIR:-}"
list_only=false

# Order used by --agent auto. First reachable agent wins. Direct Copilot sits
# above its ACP twin because it is faster and needs one less dependency, and
# both sit above gemini, whose read-only path is still unverified.
default_preference='grok-build copilot copilot-acp gemini'
read -r -a preferred_agents <<<"${REVIEW_AGENT_PREFERENCE:-$default_preference}"

script_dir="$(
  CDPATH='' cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P
)"
agents_dir="$script_dir/agents"
parser_path="$script_dir/parse-review.mjs"

fail() {
  printf 'code-review: %s\n' "$1" >&2
  exit 1
}

is_positive_integer() {
  [[ "$1" =~ ^[1-9][0-9]*$ ]]
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent)
      [[ $# -ge 2 ]] || fail '--agent requires a value'
      agent="$2"
      shift 2
      ;;
    --list)
      list_only=true
      shift
      ;;
    -h | --help)
      printf 'usage: run-review.sh [--agent <id>|auto] [--list] < prompt\n'
      exit 0
      ;;
    *)
      fail "unknown argument: $1"
      ;;
  esac
done

is_positive_integer "$max_turns" ||
  fail 'REVIEW_MAX_TURNS must be a positive integer'
is_positive_integer "$timeout_seconds" ||
  fail 'REVIEW_TIMEOUT_SECONDS must be a positive integer'
is_positive_integer "$max_output_bytes" ||
  fail 'REVIEW_MAX_OUTPUT_BYTES must be a positive integer'
is_positive_integer "$timeout_grace_seconds" ||
  fail 'REVIEW_TIMEOUT_GRACE_SECONDS must be a positive integer'

[[ -d "$agents_dir" ]] || fail "agent directory is missing: $agents_dir"

load_adapter() {
  local adapter_path="$agents_dir/$1.sh"
  [[ -f "$adapter_path" ]] || return 1

  unset -f adapter_available adapter_run adapter_missing_reason 2>/dev/null
  unset ADAPTER_DECODER ADAPTER_SUMMARY 2>/dev/null
  # shellcheck disable=SC1090
  source "$adapter_path" || return 1

  [[ -n "${ADAPTER_DECODER:-}" ]] || fail "adapter $1 does not set ADAPTER_DECODER"
}

if [[ "$list_only" == true ]]; then
  for adapter_path in "$agents_dir"/*.sh; do
    [[ -e "$adapter_path" ]] || fail 'no agent adapters are installed'
    adapter_id="$(basename -- "$adapter_path" .sh)"
    load_adapter "$adapter_id" || continue

    if adapter_available; then
      printf '%-14s available    %s\n' "$adapter_id" "${ADAPTER_SUMMARY:-}"
    else
      printf '%-14s unavailable  (%s)\n' "$adapter_id" "$(adapter_missing_reason)"
    fi
  done
  exit 0
fi

if [[ "$agent" == auto ]]; then
  selected=''
  for candidate in "${preferred_agents[@]}"; do
    load_adapter "$candidate" || continue
    if adapter_available; then
      selected="$candidate"
      break
    fi
  done
  [[ -n "$selected" ]] ||
    fail 'no review agent is available on this machine (see --list)'
  agent="$selected"
fi

load_adapter "$agent" || fail "unknown agent: $agent (see --list)"
adapter_available || fail "agent $agent is unavailable: $(adapter_missing_reason)"

command -v node >/dev/null 2>&1 || fail 'node is not installed'
[[ -f "$parser_path" ]] || fail "review parser is missing: $parser_path"

review_tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/code-review.XXXXXX")" ||
  fail 'could not create a temporary directory'

cleanup() {
  rm -rf -- "$review_tmp_dir"
}
trap cleanup EXIT

prompt_path="$review_tmp_dir/prompt.txt"
raw_output_path="$review_tmp_dir/events.jsonl"
error_path="$review_tmp_dir/agent.stderr"
assistant_path="$review_tmp_dir/assistant.txt"
review_path="$review_tmp_dir/review.txt"
parser_error_path="$review_tmp_dir/parser.stderr"
metadata_path="$review_tmp_dir/metadata.txt"
debug_capture_dir=''

copy_if_present() {
  [[ ! -e "$1" ]] || cp -- "$1" "$2/$(basename -- "$1")"
}

capture_artifacts() {
  local capture_root="$1" include_raw="$2"

  mkdir -p -- "$capture_root" ||
    fail "could not create diagnostic directory: $capture_root"
  debug_capture_dir="$(mktemp -d "$capture_root/run.XXXXXX")" ||
    fail "could not create diagnostics under: $capture_root"
  chmod 700 "$debug_capture_dir"

  copy_if_present "$assistant_path" "$debug_capture_dir"
  copy_if_present "$error_path" "$debug_capture_dir"
  copy_if_present "$parser_error_path" "$debug_capture_dir"
  copy_if_present "$review_path" "$debug_capture_dir"
  copy_if_present "$metadata_path" "$debug_capture_dir"

  if [[ "$include_raw" == 'true' ]]; then
    copy_if_present "$prompt_path" "$debug_capture_dir"
    copy_if_present "$raw_output_path" "$debug_capture_dir"
  fi
}

cat >"$prompt_path"
[[ -s "$prompt_path" ]] || fail 'review prompt is empty'

export REVIEW_MAX_TURNS="$max_turns"
export REVIEW_TIMEOUT_SECONDS="$timeout_seconds"

printf 'code-review: agent=%s decoder=%s\n' "$agent" "$ADAPTER_DECODER" >&2

# A stuck agent must not hang the caller forever. ACP adapters pass their own
# cooperative --timeout to acpx, but a direct-CLI adapter has no such lever, so
# enforcement lives here and covers every adapter uniformly. timeout(1) is not
# present on a stock macOS host, hence the hand-rolled watchdog.
timeout_sentinel="$review_tmp_dir/timed_out"
hard_timeout_seconds=$((timeout_seconds + timeout_grace_seconds))

# Job control gives each background job its own process group, so a kill can
# reach the agent's whole child tree rather than just the adapter function.
set -m
adapter_run "$prompt_path" "$raw_output_path" "$error_path" &
agent_pid=$!

(
  sleep "$hard_timeout_seconds"
  : >"$timeout_sentinel"
  kill -TERM "-$agent_pid" 2>/dev/null || kill -TERM "$agent_pid" 2>/dev/null
  sleep 10
  kill -KILL "-$agent_pid" 2>/dev/null || kill -KILL "$agent_pid" 2>/dev/null
) &
watchdog_pid=$!
set +m

# Job control makes the shell announce the kill ("Terminated: 15 adapter_run…").
# That notice reads like a crash on a path the watchdog handled deliberately.
wait "$agent_pid" 2>/dev/null
agent_exit=$?

kill -TERM "-$watchdog_pid" 2>/dev/null || kill -TERM "$watchdog_pid" 2>/dev/null
wait "$watchdog_pid" 2>/dev/null

agent_timed_out=false
[[ ! -e "$timeout_sentinel" ]] || agent_timed_out=true

printf 'agent=%s\nagent_exit=%s\nagent_timed_out=%s\n' \
  "$agent" "$agent_exit" "$agent_timed_out" >"$metadata_path"

node "$parser_path" \
  "$ADAPTER_DECODER" \
  "$raw_output_path" \
  "$assistant_path" \
  "$review_path" \
  "$max_output_bytes" \
  "$metadata_path" \
  2>"$parser_error_path"
parser_exit=$?
printf 'parser_exit=%s\n' "$parser_exit" >>"$metadata_path"

usage_summary="$(sed -n 's/^usage=//p' "$metadata_path" | tail -n 1)"
if [[ -n "$usage_summary" ]]; then
  printf 'code-review: usage %s\n' "$usage_summary" >&2
fi

if [[ -n "$debug_root" ]]; then
  capture_artifacts "$debug_root" true
fi

if ((parser_exit != 0)); then
  if [[ -z "$debug_capture_dir" ]]; then
    capture_artifacts "${TMPDIR:-/tmp}/code-review-failures" false
  fi

  if [[ "$agent_timed_out" == true ]]; then
    printf 'code-review: %s exceeded the %ss watchdog and was terminated\n' \
      "$agent" "$hard_timeout_seconds" >&2
  fi

  printf 'code-review: incomplete review from %s (agent exit %s): ' \
    "$agent" "$agent_exit" >&2
  tail -n 1 "$parser_error_path" >&2

  # A CLI that fails before emitting any events (bad model, bad flag, auth)
  # explains itself on stderr, not in the event stream. Under --json-strict
  # acpx keeps stderr clean, so this is quiet for healthy ACP runs.
  if [[ -s "$error_path" ]]; then
    printf 'code-review: %s said:\n' "$agent" >&2
    grep -v '^[[:space:]]*$' "$error_path" | tail -n 3 |
      sed 's/^/  /' >&2
  fi

  printf 'code-review: diagnostics: %s\n' "$debug_capture_dir" >&2
  exit 1
fi

cat "$review_path"
