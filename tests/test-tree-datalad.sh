#!/usr/bin/env bash

set -euo pipefail

marker_regex='  <--\[DS\]$'

is_dataset() {
    datalad siblings -d "$1" &>/dev/null
}

has_ds_marker() {
    echo "$1" | grep -qE "$marker_regex"
}

# Test that output differs from output of 'tree' only by the marker
if [[ "$(tree "$@")" = "$(tree-datalad "$@" | sed -E "s/$marker_regex//g")" ]]; then
    echo "[opts='$*'] [OK]   stripped output of tree-datalad is identical to output of tree"
else
    >&2 echo "[opts='$*'] [FAIL] stripped output of tree-datalad differs from output of tree"
fi

# Test dataset detection: compare with datalad command
tree-datalad "$@" |
# Test that dataset detection does not change if using short or full paths
if [[ "$(tree-datalad "$@" | grep -noE "$marker_regex")" = "$(tree-datalad -f "$@" | grep -noE "$marker_regex")" ]]; then
    echo "[opts='$*'] [OK]   dataset markers are identical with short or full paths (-f)"
else
    >&2 echo "[opts='$*'] [FAIL] dataset markers differ when using short or full paths (-f)"
fi

while IFS=$'\n' read -r line; do
    path="$(echo "$line" |
        sed 's/\x1B\[[0-9;]\{1,\}[A-Za-z]//g' |  # strip color codes
        sed -E 's/\/$//g' |  # strip directory suffix '/' (if tree -F)
        sed -E 's/[0-9]+ directories, [0-9]+ files//g' |  # strip report line
        sed -E "s/$marker_regex//g" |  # strip marker
        sed -E 's/^.* ([^ ]+)[/=*>|]?$/\1/g')"

    if [[ -z $path ]]; then
        continue
    fi

    if is_dataset "$path" && has_ds_marker "$line"; then
        echo "[opts='$*'] [OK]   '$path' is a dataset and has a DS marker"
    elif ! is_dataset "$path" && ! has_ds_marker "$line"; then
        echo "[opts='$*'] [OK]   '$path' is not a dataset and has no DS marker"
    elif is_dataset "$path" && ! has_ds_marker "$line"; then
        >&2 echo "[opts='$*'] [FAIL] '$path' is dataset but has no DS marker"
    elif ! is_dataset "$path" && has_ds_marker "$line"; then
        >&2 echo "[opts='$*'] [FAIL] '$path' is not a dataset but has a DS marker"
    fi
done
