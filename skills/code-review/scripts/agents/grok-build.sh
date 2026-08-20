# xAI Grok Build, via acpx. Grok Build speaks ACP only, so acpx is required.
#
# This is the invocation the retired grok-review wrapper used, unchanged.

ADAPTER_DECODER='acp'
ADAPTER_SUMMARY='xAI Grok Build (acpx)'

adapter_available() {
  command -v acpx >/dev/null 2>&1 && command -v grok >/dev/null 2>&1
}

adapter_missing_reason() {
  command -v acpx >/dev/null 2>&1 || { printf 'acpx is not installed'; return; }
  printf 'grok is not installed'
}

adapter_run() {
  local prompt_path="$1" out_path="$2" err_path="$3"

  acpx \
    --cwd "$PWD" \
    --format json \
    --json-strict \
    --suppress-reads \
    --approve-reads \
    --allowed-tools 'read_file,grep,list_dir' \
    --no-terminal \
    --policy '{"autoDeny":["execute","edit","delete","move"]}' \
    --max-turns "$REVIEW_MAX_TURNS" \
    --timeout "$REVIEW_TIMEOUT_SECONDS" \
    ${REVIEW_MODEL:+--model "$REVIEW_MODEL"} \
    grok-build exec -f "$prompt_path" \
    >"$out_path" 2>"$err_path"
}
