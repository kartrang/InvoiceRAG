#!/bin/bash
set -e

# Stop and remove all running containers (if any)
containerids=$(docker ps -q)

if [ -n "$containerids" ]; then
  echo "Stopping and removing running containers: $containerids"
  docker rm -f $containerids
else
  echo "No running containers to stop."
fi
