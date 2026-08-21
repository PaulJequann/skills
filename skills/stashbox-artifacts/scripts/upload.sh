#!/bin/sh

set -eu

usage() {
  printf 'usage: %s <artifact.html|artifact.md>\n' "${0##*/}" >&2
  exit 2
}

[ "$#" -eq 1 ] || usage

artifact=$1

if [ ! -f "$artifact" ] || [ ! -r "$artifact" ]; then
  printf 'stashbox: file is not readable: %s\n' "$artifact" >&2
  exit 2
fi

extension=${artifact##*.}
extension=$(printf '%s' "$extension" | tr '[:upper:]' '[:lower:]')

case "$extension" in
  html|htm) content_type='text/html' ;;
  md|markdown) content_type='text/markdown' ;;
  *)
    printf 'stashbox: unsupported file type: %s\n' "$artifact" >&2
    exit 2
    ;;
esac

size=$(wc -c < "$artifact" | tr -d '[:space:]')
if [ "$size" -gt 10485760 ]; then
  printf 'stashbox: file exceeds the 10 MiB upload limit: %s bytes\n' "$size" >&2
  exit 2
fi

filename=${artifact##*/}
line_count=$(printf '%s' "$filename" | wc -l | tr -d '[:space:]')
filename_without_cr=$(printf '%s' "$filename" | tr -d '\r')
if [ "$line_count" -ne 0 ] || [ "$filename" != "$filename_without_cr" ]; then
  printf 'stashbox: filename contains a newline: %s\n' "$filename" >&2
  exit 2
fi

for command_name in curl jq; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    printf 'stashbox: required command is unavailable: %s\n' "$command_name" >&2
    exit 127
  fi
done

response=$(curl --fail-with-body --silent --show-error \
  --data-binary "@$artifact" \
  -H "Content-Type: $content_type" \
  -H "X-Stash-Filename: $filename" \
  'https://stashbox.local.bysliek.com/api/stashes')

url=$(printf '%s' "$response" | jq -er '
  .url
  | strings
  | select(test("^https://stashbox\\.local\\.bysliek\\.com/"))
') || {
  printf 'stashbox: response did not contain a valid viewer URL\n' >&2
  exit 1
}

printf '%s\n' "$url"
