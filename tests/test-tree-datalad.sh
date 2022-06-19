#!/usr/bin/env bash

set -euo pipefail

opts=("$@")
# import functions from tree-datalad by sourcing the script
source tree-datalad

marker_regex='  <--\[DS\]$'
exit_code=0

is_dataset() {
    datalad siblings -d "$1" &>/dev/null
}

has_ds_marker() {
    echo "$1" | grep -qE "$marker_regex"
}

pass() {
    local msg="$1"
    echo "[opts='${opts[*]}'] [OK]  $msg"
}

fail() {
    local msg="$1"
    >&2 echo "[opts='${opts[*]}'] [FAIL]  $msg"
    exit_code=1
}

# Test that output differs from output of 'tree' only by the marker
if [[ "$(tree "${opts[@]}")" = "$(tree-datalad "${opts[@]}" | sed -E "s/$marker_regex//g")" ]]; then
    pass "stripped output of tree-datalad is identical to output of tree"
else
    fail "stripped output of tree-datalad differs from output of tree"
fi

# Test that dataset detection does not change if using short or full paths
if [[ "$(tree-datalad "${opts[@]}" | grep -noE "$marker_regex")" = "$(tree-datalad -f "${opts[@]}" | grep -noE "$marker_regex")" ]]; then
    pass "dataset markers are identical with short or full paths (-f)"
else
    fail "dataset markers differ when using short or full paths (-f)"
fi

# Test dataset detection by comparing with datalad command
# To skip the full path extraction, we force the '-f' option to show full paths
tree-datalad -f "${opts[@]}" |
while IFS=$'\n' read -r line; do
    path="$(extract_path "$line" | sed -E "s/$marker_regex//g")"

    if [[ -z $path ]]; then
        continue
    fi

    if is_dataset "$path" && has_ds_marker "$line"; then
        pass "'$path' is a dataset and has a DS marker"
    elif ! is_dataset "$path" && ! has_ds_marker "$line"; then
        pass "'$path' is not a dataset and has no DS marker"
    elif is_dataset "$path" && ! has_ds_marker "$line"; then
        fail "'$path' is dataset but has no DS marker"
    elif ! is_dataset "$path" && has_ds_marker "$line"; then
        fail "'$path' is not a dataset but has a DS marker"
    fi
done

exit $exit_code
