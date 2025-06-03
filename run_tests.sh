#!/bin/bash

echo "Running Adaptive Chatbot Test Suite"
echo "==================================="

echo "Installing test dependencies..."
pip install pytest pytest-mock pytest-cov

echo -e "\nRunning unit tests..."
pytest tests/unit -v

echo -e "\nRunning integration tests..."
pytest tests/integration -v

echo -e "\nRunning all tests with coverage..."
pytest tests/ --cov=src/chatbot --cov-report=term-missing

echo -e "\nGenerating coverage report..."
pytest tests/ --cov=src/chatbot --cov-report=html

echo -e "\nTest run complete!"
echo "Coverage report available in htmlcov/index.html"