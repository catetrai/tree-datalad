#!/usr/bin/env bash
#
# Installation script for 'tree' program on Linux.
#

set -euo pipefail

tree_pkg_name="$1"  # e.g. tree_1.8.0-1_amd64.deb

# Installation via download of deb package: https://askubuntu.com/a/1147861
wget https://mirrors.edge.kernel.org/ubuntu/pool/universe/t/tree/"$tree_pkg_name"
sudo dpkg -i "$tree_pkg_name"
sudo apt install -f  # install remaining dependencies
tree --version  # will fail if not installed