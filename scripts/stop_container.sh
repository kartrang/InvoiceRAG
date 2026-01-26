#!/bin/bash
set -e  # Stop the script on any command failure

# Function to handle errors gracefully
function error_exit {
  echo "Error: $1"
  exit 1
}

# Get the IDs of all running containers
containerids=$(docker ps -q)

# If any containers are found, stop them
if [ -n "$containerids" ]; then
  echo "Stopping and removing containers..."
  docker rm -f $containerids || error_exit "Failed to remove containers."
else
  echo "No running containers found."
fi
