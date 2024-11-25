#!/usr/bin/env bash
#
# Copyright (c) 2024. All rights reserved.
#

set -e

echo "Starting up . . ."

user="$(id -u)"

if [ -n "${MAP_UID}" ]; then
	echo "Mapping UID to ${MAP_UID}"
	usermod -u "${MAP_UID}" dockeruser
	find / -user "${user}" -exec chown -h dockeruser {} \; || true
fi

if [ -n "${MAP_GID}" ]; then
	echo "Mapping GID to ${MAP_GID}"
	groupmod -g "${MAP_GID}" dockergroup
	find / -group "${user}" -exec chgrp -h dockergroup {} \; || true
fi

source /app/.venv/bin/activate
cd /app

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
