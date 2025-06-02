#!/bin/bash

echo "Running comprehensive API tests..."

pip install pytest requests

pytest tests/test_all_endpoints.py -v --tb=short --cov=src/chatbot --cov-report=html

echo "Tests complete."