#!/usr/bin/bash

podman build -t maruchan .

podman unshare chown $UID:$UID -R $(pwd)/data

podman run -ti --rm \
    -v $(pwd)/data:/data:ro,Z \
    localhost/maruchan:latest

podman unshare chown 0:0 -R $(pwd)/data
