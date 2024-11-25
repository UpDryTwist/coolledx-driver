#!/usr/bin/env bash
# Pass any parameters into this script that you want to pass to tweak_sign.py ...

# Use the docker image to send codes to the sign

docker run --privileged -v /var/run/dbus:/var/run/dbus \
	registry.supercroy.com/updrytwist/coolledx:latest \
	python3 /app/utils/tweak_sign.py "$@"
