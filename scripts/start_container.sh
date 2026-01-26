#!/bin/bash
set -e

# Pull the Docker image from Docker Hub
docker pull kartrang/devopsfullcycle-app:latest .

# Run the Docker image as a container
docker run -d -p 8501:8501 kartrang/devopsfullcycle-app 
