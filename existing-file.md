#!/bin/bash
set -euo pipefail
set -x

# Stop the running container (if any)
container_name="my_container" # Replace with your container name

# Check if the container is running and get the container ID
container_id=$(docker ps | awk -v name="$container_name" '$NF == name {print $1}')

if [ -n "$container_id" ]; then
    # Stop and remove the container
docker stop "$container_id"
docker rm "$container_id"
echo "Stopped and removed container: $container_name"
else
    echo "No running container to stop for: $container_name"
fi
