#!/bin/bash

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}First-Time Setup for Adaptive Chatbot${NC}"
echo "========================================"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed!"
    echo "Please install Docker Desktop from https://docker.com"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed!"
    exit 1
fi

if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo -e "${GREEN}.env file created${NC}"
    echo "Please edit .env and add your OPENROUTER_API_KEY"
    echo ""
fi

echo "Making scripts executable..."
chmod +x *.sh

echo "Pulling Docker images..."
docker-compose pull

echo ""
echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Add your OPENROUTER_API_KEY to the .env file"
echo "2. Run: ./start.sh"