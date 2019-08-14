#!/usr/bin/env bash

set -exo pipefail

UDID=`idevice_id -l | grep -o "[^ ]\+\( \+[^ ]\+\)*"`
PORT=33333
RESOLUTION="400x600"

./build/ios_minicap \
    --udid $UDID \
    --port $PORT \
    --resolution $RESOLUTION
