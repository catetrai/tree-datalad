#!/usr/bin/env bash
#
# Update the list of 'tree' versions on which tree-datalad will be tested.
# Pulls list of available package versions from a Debian package repository.
# Only relevant for Linux installation.
#

set -euo pipefail

# Regex for identifying line of the GitHub workflow YAML config file
# to be modified with updated tree package versions
config_regex='tree-version: \[.*\]'

list_pkg_versions() {
    # Comma-separated list of package names retrieved from ubuntu repository
    rsync --list-only rsync://mirrors.kernel.org/mirrors/ubuntu/pool/universe/t/tree/ |
        grep -E 'tree_.*_amd64.deb$' |
        sed -E 's/^.*(tree_.*_amd64.deb)$/\1/g' |
        paste -sd "," -
}

find_github_workflow_config_file() {
    # Find matching YAML file(s) in this git repo
    grep -l "$config_regex" \
        "$(git rev-parse --show-toplevel)"/.github/workflows/*.yml
}

update_workflow_config() {
    # Modify the .github/workflow/*.yml file(s) in-place
    # with updated package names
    sed -i -E "/${config_regex}/ s|\[.*\]|\[$(list_pkg_versions)\]|g" \
        "$(find_github_workflow_config_file)"
}

update_workflow_config
