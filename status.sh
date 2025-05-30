#!/bin/bash

echo "Docker Containers Status:"
echo "============================"
docker-compose ps

echo ""
echo "Resource Usage:"
docker stats --no-stream