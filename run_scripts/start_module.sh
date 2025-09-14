#!/usr/bin/env bash
#
# Copyright (c) 2025. All rights reserved.
#

set -e

echo "Starting up . . ."

user="$(id -u)"
grp="$(id -g)"

if [ -n "${MAP_UID}" ]; then
	echo "Mapping UID to ${MAP_UID}"
	usermod -u "${MAP_UID}" dockeruser
	find / \
		-path "/proc" -prune -o \
		-path "/sys" -prune -o \
		-uid "${user}" -exec chown dockeruser {} \; || true
fi

if [ -n "${MAP_GID}" ]; then
	echo "Mapping GID to ${MAP_GID}"
	groupmod -g "${MAP_GID}" dockergroup
	find / \
		-path "/proc" -prune -o \
		-path "/sys" -prune -o \
		-gid "${grp}" -exec chgrp dockergroup {} \; || true
fi

if [ -n "${UMASK}" ]; then
	echo "Mapping umask to ${UMASK}"
	umask "${UMASK}"
fi

source /app/.venv/bin/activate
cd /app

if [[ $# -eq 0 ]]; then
	set -- "python" "-m" ""
fi

if [ "${user}" = '0' ]; then
	echo "Running chown on /app"
	# Don't know if we need this or not - removing to speed up
	# [ -d "/app" ] && (chown -R dockeruser:dockergroup /app || true)
	echo "Running as gosu dockeruser"
	exec gosu dockeruser "$0" "$@"
else
	echo "Running"
	exec "$@"
fi
