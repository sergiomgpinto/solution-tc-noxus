#!/bin/bash

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Starting in DEVELOPMENT mode...${NC}"

if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠Created .env file - please add your OPENROUTER_API_KEY"
fi

echo "Building development containers..."
docker-compose -f docker-compose.dev.yml build

echo "Starting services with hot-reload..."
docker-compose -f docker-compose.dev.yml up
