#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Starting Adaptive Chatbot...${NC}"

if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo -e "${RED}Please add your OPENROUTER_API_KEY to .env file${NC}"
    exit 1
fi

if ! grep -q "OPENROUTER_API_KEY=.*[^[:space:]]" .env; then
    echo -e "${RED}Error: OPENROUTER_API_KEY is not set in .env${NC}"
    exit 1
fi

echo "Building containers..."
docker-compose build

echo "Starting database..."
docker-compose up -d postgres

echo "Waiting for database to be ready..."
sleep 5

echo "Initializing database..."
docker-compose run --rm backend python -m chatbot.init_db

echo "Creating default configurations..."
docker-compose run --rm backend python -m chatbot.config_cli init

echo "Starting all services..."
docker-compose up -d

echo -e "${GREEN}Application started successfully!${NC}"
echo ""
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "To view logs: ./logs.sh"
echo "To stop: ./stop.sh"