@echo off

@REM rem build exe
uv run pyinstaller build_win.spec -y

@REM rem check 3rd party license (Pillow is displayed somehow "UNKNOWN")
uv run pip-licenses --partial-match --allow-only="MIT;BSD;MPL;Apache;HPND;GPLv2;CC0 1.0;UNKNOWN" > nul || exit /b 1

@REM rem generate 3rd party license txt
uv run pip-licenses --format=plain-vertical --with-license-file --no-license-path --output-file="3rd-party-license.txt"

@REM rem copy files
xcopy /i /y "3rd-party-license.txt" ".\dist\PlaySK Midi to Piano Roll Image Converter\"
xcopy /s /i /y ".\src\assets\" ".\dist\PlaySK Midi to Piano Roll Image Converter\assets\"