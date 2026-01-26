#!/bin/bash
set -e

# Get IDs of all running containers and stop them
docker ps -q | xargs docker rm -f
