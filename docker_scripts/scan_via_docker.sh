#!/usr/bin/env bash
# Pass any parameters into this script that you want to pass to scan.py ...

# Use the docker image to scan for bluetooth devices

docker run --privileged -v /var/run/dbus:/var/run/dbus \
	registry.supercroy.com/updrytwist/coolledx:latest \
	python3 /app/utils/scan.py "$@"
