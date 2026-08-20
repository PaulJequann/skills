# GitHub Copilot CLI, invoked directly.
#
# Copilot also speaks ACP (`copilot --acp`), but the direct CLI is preferred:
# it is faster, needs no acpx, and exposes a tool-AVAILABILITY filter that ACP
# permission policy cannot replicate. See copilot-acp.sh for why that matters.

ADAPTER_DECODER='copilot-jsonl'
ADAPTER_SUMMARY='GitHub Copilot CLI (direct)'

adapter_available() {
  command -v copilot >/dev/null 2>&1
}

adapter_missing_reason() {
  printf 'copilot is not installed'
}

# $1 prompt file, $2 stdout events file, $3 stderr file
adapter_run() {
  local prompt_path="$1" out_path="$2" err_path="$3"

  # Three independent layers, because denial alone is not a sandbox:
  #   --available-tools  the model never sees anything but read/search
  #   --deny-tool        denial outranks --allow-all-tools if a tool slips in
  #   --disable-*/--no-* nothing can block waiting for a human or an MCP server
  local args=(
    --available-tools='view,grep,glob'
    --deny-tool='shell'
    --deny-tool='write'
    --deny-tool='url'
    --disable-builtin-mcps
    --no-ask-user
    --allow-all-tools
    --no-color
    --output-format json
  )

  # Model and reasoning effort are independent knobs in Copilot: "gpt-5.6-luna"
  # is the model, "max" is an effort level.
  #
  # Review is a deliberate, low-volume, high-stakes task, so this adapter pins a
  # strong model at maximum reasoning rather than inheriting whatever the
  # interactive session happens to be set to. REVIEW_MODEL/REVIEW_EFFORT still
  # win when the caller asks for something specific.
  args+=(--model "${REVIEW_MODEL:-gpt-5.6-luna}")
  args+=(--effort "${REVIEW_EFFORT:-max}")

  # Copilot reads the prompt from stdin only when -p is absent; `-p -` is
  # treated as literal prompt text, not a stdin marker.
  copilot "${args[@]}" <"$prompt_path" >"$out_path" 2>"$err_path"
}
