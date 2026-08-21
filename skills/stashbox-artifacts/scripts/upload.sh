#!/bin/sh

set -eu

usage() {
  printf 'usage: %s <artifact.html|artifact.md> [viewer-url]\n' "${0##*/}" >&2
  exit 2
}

[ "$#" -ge 1 ] && [ "$#" -le 2 ] || usage

artifact=$1
viewer_url=${2-}
base_url='https://stashbox.local.bysliek.com'

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

if [ -z "$viewer_url" ]; then
  viewer_url=$(sed -n \
    's@.*<!--[[:space:]]*Stashbox:[[:space:]]*\(https://stashbox\.local\.bysliek\.com/[^[:space:]>]*\)[[:space:]]*-->.*@\1@p' \
    "$artifact" | sed -n '1p')
fi

if [ -n "$viewer_url" ]; then
  stash_id=$(printf '%s' "$viewer_url" | jq -Rer \
    'capture("^https://stashbox\\.local\\.bysliek\\.com/(?<id>[A-Za-z0-9_-]+)$").id') || {
    printf 'stashbox: expected a stable Stashbox viewer URL: %s\n' "$viewer_url" >&2
    exit 2
  }
  api_url="$base_url/api/stashes/$stash_id"
  headers=$(curl --fail-with-body --silent --show-error \
    --dump-header - --output /dev/null "$api_url")
  etag=$(printf '%s' "$headers" | awk '
    BEGIN { IGNORECASE = 1 }
    /^etag:/ { sub(/\r$/, "", $2); value = $2 }
    END { print value }
  ')
  if [ -z "$etag" ]; then
    printf 'stashbox: metadata did not contain an ETag; refusing an unsafe update\n' >&2
    exit 1
  fi
  response=$(curl --fail-with-body --silent --show-error \
    --request PUT \
    --data-binary "@$artifact" \
    -H "Content-Type: $content_type" \
    -H "X-Stash-Filename: $filename" \
    -H "If-Match: $etag" \
    "$api_url")
else
  response=$(curl --fail-with-body --silent --show-error \
    --data-binary "@$artifact" \
    -H "Content-Type: $content_type" \
    -H "X-Stash-Filename: $filename" \
    "$base_url/api/stashes")
fi

url=$(printf '%s' "$response" | jq -er '
  .url
  | strings
  | select(test("^https://stashbox\\.local\\.bysliek\\.com/[A-Za-z0-9_-]+$"))
') || {
  printf 'stashbox: response did not contain a valid viewer URL\n' >&2
  exit 1
}

revision=$(printf '%s' "$response" | jq -er '.revision | numbers') || {
  printf 'stashbox: response did not contain a revision number\n' >&2
  exit 1
}

if [ -z "$viewer_url" ]; then
  printf 'Created revision %s\n' "$revision" >&2
elif [ "$(printf '%s' "$response" | jq -r '.changed // false')" = 'true' ]; then
  printf 'Published revision %s\n' "$revision" >&2
else
  printf 'Already current at revision %s\n' "$revision" >&2
fi

printf '%s\n' "$url"
