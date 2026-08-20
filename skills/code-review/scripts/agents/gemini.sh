# Google Gemini CLI, via acpx.
#
# Launched through acpx's --agent escape hatch so Gemini's own
# `--approval-mode plan` (documented read-only mode) applies to the session.
# Relying on acpx's autoDeny policy alone leaves write and shell tools visible
# to the model, which invites a denied tool call and an aborted turn.
#
# ACP mode needs non-interactive auth: without GEMINI_API_KEY or GOOGLE_API_KEY
# the CLI blocks on interactive OAuth and acpx times out during initialize.
# Availability below reports only that the binary exists, so a run can still
# fail on auth; the runner reports that as incomplete, never as clean.
# UNVERIFIED: the read-only behaviour of this adapter has not been observed
# end-to-end, because no machine used so far had non-interactive Gemini auth.

ADAPTER_DECODER='acp'
ADAPTER_SUMMARY='Google Gemini CLI (acpx, plan mode)'

adapter_available() {
  command -v acpx >/dev/null 2>&1 && command -v gemini >/dev/null 2>&1
}

adapter_missing_reason() {
  command -v acpx >/dev/null 2>&1 || { printf 'acpx is not installed'; return; }
  printf 'gemini is not installed'
}

adapter_run() {
  local prompt_path="$1" out_path="$2" err_path="$3"

  acpx \
    --cwd "$PWD" \
    --format json \
    --json-strict \
    --suppress-reads \
    --approve-reads \
    --non-interactive-permissions deny \
    --no-terminal \
    --policy '{"autoDeny":["execute","edit","delete","move"]}' \
    --max-turns "$REVIEW_MAX_TURNS" \
    --timeout "$REVIEW_TIMEOUT_SECONDS" \
    ${REVIEW_MODEL:+--model "$REVIEW_MODEL"} \
    --agent 'gemini --acp --approval-mode plan' \
    exec -f "$prompt_path" \
    >"$out_path" 2>"$err_path"
}
