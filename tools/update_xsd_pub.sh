#!/usr/bin/env bash

set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <full-upstream-commit-sha>" >&2
    exit 2
fi

revision=$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')
if [[ ! $revision =~ ^[0-9a-f]{40}$ ]]; then
    echo "Revision must be a full 40-character commit SHA." >&2
    exit 2
fi

script_directory=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
repository_root=$(cd -- "$script_directory/.." && pwd)
schema_directory="$repository_root/lvlspy/extensions/io/xml/xsd_pub"
revision_file="$repository_root/XSD_REVISION"
provenance_file="$schema_directory/README.md"
upstream_url="https://bitbucket.org/mbradle/liblvls_xsd.git"
python_command=${PYTHON:-python}

expected_files=(
    catalog
    level_types.xsd
    levels.xsd
    liblvls_input.xsd
    spcoll.xsd
    zone_types.xsd
    zones.xsd
)

temporary_directory=$(mktemp -d)
trap 'rm -rf "$temporary_directory"' EXIT
checkout="$temporary_directory/liblvls_xsd"
distribution_directory="$temporary_directory/dist"

git clone --quiet --no-checkout "$upstream_url" "$checkout"
git -C "$checkout" checkout --quiet --detach "$revision"

resolved_revision=$(git -C "$checkout" rev-parse HEAD)
if [[ $resolved_revision != "$revision" ]]; then
    echo "Resolved revision $resolved_revision does not match $revision." >&2
    exit 1
fi

for filename in "${expected_files[@]}"; do
    if [[ ! -f "$checkout/$filename" ]]; then
        echo "Expected upstream file is missing: $filename" >&2
        exit 1
    fi
done

for source_file in "$checkout"/*.xsd; do
    filename=$(basename -- "$source_file")
    allowed=false
    for expected_file in "${expected_files[@]}"; do
        if [[ $filename == "$expected_file" ]]; then
            allowed=true
            break
        fi
    done
    if [[ $allowed == false ]]; then
        echo "Unexpected upstream schema requires review: $filename" >&2
        exit 1
    fi
done

mkdir -p "$schema_directory"
for filename in "${expected_files[@]}"; do
    cp "$checkout/$filename" "$schema_directory/$filename"
done

for existing_file in "$schema_directory"/*.xsd; do
    filename=$(basename -- "$existing_file")
    keep=false
    for expected_file in "${expected_files[@]}"; do
        if [[ $filename == "$expected_file" ]]; then
            keep=true
            break
        fi
    done
    if [[ $keep == false ]]; then
        rm -- "$existing_file"
    fi
done

printf '%s\n' "$revision" > "$revision_file"
"$python_command" - "$provenance_file" "$revision" <<'PY'
from pathlib import Path
import re
import sys

provenance_file = Path(sys.argv[1])
revision = sys.argv[2]
content = provenance_file.read_text(encoding="utf-8")
updated, replacements = re.subn(
    r"Upstream commit: `[0-9a-f]{40}`",
    f"Upstream commit: `{revision}`",
    content,
)
if replacements != 1:
    raise SystemExit("Could not update the upstream commit in README.md.")
provenance_file.write_text(updated, encoding="utf-8")
PY

cd "$repository_root"
"$python_command" -m pytest -v tests
"$python_command" -m build --outdir "$distribution_directory"
"$python_command" - "$distribution_directory" <<'PY'
from pathlib import Path
import sys
from zipfile import ZipFile

distribution_directory = Path(sys.argv[1])
wheel = next(distribution_directory.glob("*.whl"))
expected = {
    "lvlspy/extensions/io/xml/xsd_pub/catalog",
    "lvlspy/extensions/io/xml/xsd_pub/level_types.xsd",
    "lvlspy/extensions/io/xml/xsd_pub/levels.xsd",
    "lvlspy/extensions/io/xml/xsd_pub/liblvls_input.xsd",
    "lvlspy/extensions/io/xml/xsd_pub/spcoll.xsd",
    "lvlspy/extensions/io/xml/xsd_pub/zone_types.xsd",
    "lvlspy/extensions/io/xml/xsd_pub/zones.xsd",
    "lvlspy/extensions/io/xml/xsd_pub/README.md",
}

with ZipFile(wheel) as archive:
    missing = expected.difference(archive.namelist())
if missing:
    raise SystemExit(f"Wheel is missing vendored files: {sorted(missing)}")

print(f"Verified vendored schemas in {wheel.name}.")
PY

git status --short -- XSD_REVISION lvlspy/extensions/io/xml/xsd_pub
echo "Schema snapshot updated to $revision; review and commit the changes above."
