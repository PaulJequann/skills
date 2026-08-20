# GitHub Copilot CLI over ACP, via acpx.
#
# Prefer the plain `copilot` adapter. This one exists for hosts that want every
# agent on one transport, and it is deliberately launched through acpx's
# --agent escape hatch.
#
# Why the escape hatch: acpx normally spawns a bare `copilot --acp --stdio`,
# which leaves Copilot's full toolset — including shell — visible to the model.
# Copilot then sometimes picks shell to locate a file (observed: a filesystem
# -wide `find / -maxdepth 6 -iname "session.js"`). acpx's autoDeny policy
# correctly refuses it, but Copilot does not fall back to `view`/`grep`; it
# aborts the turn with no message chunks and acpx exits 5. Passing Copilot's
# native --available-tools removes shell from the model's view, so the denial
# never has to happen.

ADAPTER_DECODER='acp'
ADAPTER_SUMMARY='GitHub Copilot CLI (acpx/ACP)'

adapter_available() {
  command -v acpx >/dev/null 2>&1 && command -v copilot >/dev/null 2>&1
}

adapter_missing_reason() {
  command -v acpx >/dev/null 2>&1 || { printf 'acpx is not installed'; return; }
  printf 'copilot is not installed'
}

adapter_run() {
  local prompt_path="$1" out_path="$2" err_path="$3"

  # Model and effort go to Copilot itself rather than to acpx --model: this
  # adapter already owns the launch command, and Copilot's own flags are the
  # ones whose accepted values we can state exactly. Defaults match copilot.sh
  # so the two transports review with the same brain.
  local agent_command='copilot --acp --stdio'
  agent_command+=' --available-tools=view,grep,glob'
  agent_command+=' --disable-builtin-mcps --no-ask-user'
  agent_command+=" --model=${REVIEW_MODEL:-gpt-5.6-luna}"
  agent_command+=" --effort=${REVIEW_EFFORT:-max}"

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
    --agent "$agent_command" \
    exec -f "$prompt_path" \
    >"$out_path" 2>"$err_path"
}
