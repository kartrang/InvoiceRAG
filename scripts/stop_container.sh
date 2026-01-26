#!/bin/bash
set -e

# Stop and remove all running containers
containerids=$(docker ps -q)

if [ -n "$containerids" ]; then
  docker rm -f $containerids
else
  echo "No running containers to stop."
fi
