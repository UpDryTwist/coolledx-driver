#!/usr/bin/env bash
# Pass any parameters into this script that you want to pass to scan.py ...

MY_REGISTRY=registry.supercroy.com/updrytwist

# Use the docker image to scan for bluetooth devices
docker pull ${MY_REGISTRY}/coolledx:latest

docker run --privileged -v /var/run/dbus:/var/run/dbus \
	${MY_REGISTRY}/coolledx:latest \
	python3 /app/utils/scan.py "$@"
