#!/bin/bash
set -e

# Stop the running container (if any)
container_name="my_container" # Replace with your container name
if docker ps | grep -q "$container_name"; then
    docker stop "$container_name"
    echo "Stopped container: $container_name"
else
    echo "No running container to stop"
fi
