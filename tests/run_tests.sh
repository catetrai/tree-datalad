#!/usr/bin/env bash


set -euo pipefail

debug=false
if [[ "$#" = 1 ]] && [[ "$1" = "--debug" ]]; then
    debug=true
fi

create_dirs() {
    local outdir="$1"
    # Create 4-level directory/dataset hierarchy
    echo "Creating directory/dataset hierarchy ..."
    datalad create -c text2git "$outdir"/superds
    (
        cd "$outdir"/superds
        datalad create  -d . -c text2git subds1
        mkdir -p subdir1/subsubdir1 emptydir
        echo -n $'\x01' > subds1/annexed.dat
        echo "regular file in subds" > subds1/regular.txt
        echo "regular file in subdir" > subdir1/subsubdir1/regular.txt
    )
    datalad save -r -d "$outdir"/superds
}

cleanup() {
    # Delete test datasets
    if ! $debug; then
        chmod -R +w "$tmpdir"
        rm -rf "$tmpdir"
        echo "Removed tempdir '$tmpdir'"
    fi
}

tmpdir="$(mktemp --dry-run -d -t 'tree-datalad-tests-XXXXXXXXXXX')"
trap cleanup EXIT
create_dirs "$tmpdir"
# import tree options
source ./tree_opts.sh

# For actual tests, allow error exit code (means test failure)
set +e
exit_code=0
for opt in $tree_opts; do
    for level in 1 4; do
        ./test_tree_datalad.sh -I .git -L "$level" "$opt" "$tmpdir"
        exit_code=$((exit_code+$?))
    done
done 2>&1 | tee tree-datalad-tests_"$(date +"%Y-%m-%d_%H%M")".log

if [[ "$exit_code" -gt 0 ]]; then
    exit 1
fi
