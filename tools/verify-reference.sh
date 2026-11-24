#!/bin/sh
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
archive=${METAFOR_SOURCE_ARCHIVE:?set METAFOR_SOURCE_ARCHIVE to the metafor 5.2-1 source archive}
expected=25c421cf52279294b11ab3166adfeb327dd22034a03a46487f081a19a163339b
actual=$(shasum -a 256 "$archive" | awk '{print $1}')
[ "$actual" = "$expected" ] || { echo "unexpected metafor archive SHA-256: $actual" >&2; exit 1; }

temporary_dir=$(mktemp -d)
trap 'rm -rf "$temporary_dir"' EXIT HUP INT TERM
cp "$repo_root/reference/v1/generate.R" "$temporary_dir/generate.R"
(cd "$temporary_dir" && Rscript generate.R)
cmp "$repo_root/reference/v1/bcg.csv" "$temporary_dir/bcg.csv"
cmp "$repo_root/reference/v1/bcg-reference.json" "$temporary_dir/bcg-reference.json"
printf '%s\n' BCG_REFERENCE_REGENERATED_IDENTICALLY
