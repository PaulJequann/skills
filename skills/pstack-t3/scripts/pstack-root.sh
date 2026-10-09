#!/usr/bin/env bash
# Prints the newest installed pstack plugin root. Harnesses install pstack at different versions.
set -euo pipefail
best= bestv=
for d in "$HOME"/.claude/plugins/marketplaces/pstack-claude/plugins/pstack \
         "$HOME"/.claude/plugins/cache/pstack-claude/pstack/* \
         "${CODEX_HOME:-$HOME/.codex}"/plugins/cache/pstack-claude/pstack/*; do
  [[ -f $d/skills/poteto-mode/SKILL.md ]] || continue
  v=$(sed -n 's/.*"version": *"\([^"]*\)".*/\1/p' "$d/.claude-plugin/plugin.json" 2>/dev/null | head -1)
  if [[ -z $best ]] || [[ $(printf '%s\n%s\n' "$bestv" "${v:-0}" | sort -V | tail -1) == "${v:-0}" && ${v:-0} != "$bestv" ]]; then
    best=$d bestv=${v:-0}
  fi
done
[[ -n $best ]] || { echo "pstack not installed under ~/.claude or ~/.codex" >&2; exit 1; }
echo "$best"
