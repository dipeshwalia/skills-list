#!/bin/sh
# Sync original parent repositories configured in upstreams.json.
set -eu
script_dir=$(CDPATH= cd -P "$(dirname "$0")" && pwd)
exec python3 "$script_dir/upstream.py" sync "$@"
