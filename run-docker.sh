#!/bin/bash

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "Please edit .env file and add your API keys before running again."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker and try again."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

# Build and start the containers
echo "Starting SQL Chatbot with Docker Compose..."
docker-compose up -d --build

# Check if containers are running
if [ $? -eq 0 ]; then
    echo ""
    echo "SQL Chatbot is now running!"
    echo "Access the application at:"
    echo "  - Streamlit frontend: http://localhost:5000"
    echo "  - FastAPI backend: http://localhost:8000"
    echo ""
    echo "To view logs:"
    echo "  docker-compose logs -f"
    echo ""
    echo "To stop the application:"
    echo "  docker-compose down"
else
    echo "Failed to start the application. Please check the error messages above."
    exit 1
fi