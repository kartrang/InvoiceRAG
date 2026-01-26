#!/bin/bash
set -euo pipefail
set -x

# Stop and remove the running container (if any)
container_name="my_container" # Replace with your container name

# Get the container ID
container_id=$(docker ps -q -f name="$container_name")

if [ -n "$container_id" ]; then
    docker stop "$container_id"
    docker rm "$container_id"
    echo "Stopped and removed container: $container_name (ID: $container_id)"
else
    echo "No running container to stop or remove for: $container_name"
fi
