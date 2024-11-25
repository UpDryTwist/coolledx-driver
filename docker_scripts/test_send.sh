#!/usr/bin/env bash

SCRIPT_DIR="$(dirname "$(realpath "$0")")"

"${SCRIPT_DIR}/tweak_via_docker.sh" \
	-t "<#ff0000>Now<#00f0f0> is the time for all <#0000ff>good men" \
	-f calibri -C black -H 13 -m 2 -w as-is -g crop-pad -z left -y top
