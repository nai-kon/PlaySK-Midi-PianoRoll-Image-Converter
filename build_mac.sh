#! /bin/zsh
set -euo pipefail

# build exe
uv run pyinstaller build_mac.spec -y

# remove temp folder
rm -rf 'dist/PlaySK Midi to Piano Roll Image Converter/'

# check 3rd party license (Pillow is displayed somehow "UNKNOWN")
uv run pip-licenses --partial-match --allow-only="MIT;BSD;MPL;Apache;HPND;GPLv2;CC0 1.0;UNKNOWN" 1> /dev/null

# generate 3rd party license txt
uv run pip-licenses --format=plain-vertical --with-license-file --no-license-path --output-file="3rd-party-license.txt"

# copy files
cp -p "3rd-party-license.txt" dist/
cp -pr "src/assets/" "dist/assets/"