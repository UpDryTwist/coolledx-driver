#!/usr/bin/env bash
# Pass any parameters into this script that you want to pass to tweak_sign.py ...

# Use the docker image to send codes to the sign

MY_REGISTRY=registry.supercroy.com/updrytwist

# If you want to use the fonts on the host machine, set this to 1.  Otherwise,
# the container will use the fonts that are included in the container.
USE_HOST_FONTS=0

if [[ ${USE_HOST_FONTS} == "1" ]]; then
	HOST_FONTS="-v /usr/share/fonts:/usr/share/fonts -v /usr/local/share/fonts:/usr/local/share/fonts"
else
	HOST_FONTS=""
fi

docker pull ${MY_REGISTRY}/coolledx:latest

# shellcheck disable=SC2086
docker run --privileged \
	-v /var/run/dbus:/var/run/dbus \
	${HOST_FONTS} \
	${MY_REGISTRY}/coolledx:latest \
	python3 /app/utils/tweak_sign.py "$@"
