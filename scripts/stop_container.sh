#!/bin/bash
set -e  # Exit on any failure

# Get the IDs of all running containers and stop them
docker ps -q | xargs docker rm -f