#!/bin/bash

# LexiAI Deployment Script
# This script helps with deploying the LexiAI application

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored messages
print_message() {
  echo -e "${GREEN}[LexiAI]${NC} $1"
}

print_warning() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
  print_error "Docker is not installed. Please install Docker and try again."
  exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
  print_error "Docker Compose is not installed. Please install Docker Compose and try again."
  exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
  print_warning "No .env file found. Creating from .env.example..."
  if [ -f .env.example ]; then
    cp .env.example .env
    print_message ".env file created. Please edit it with your configuration before continuing."
    exit 0
  else
    print_error ".env.example file not found. Please create a .env file manually."
    exit 1
  fi
fi

# Parse command line arguments
COMMAND=${1:-help}

case $COMMAND in
  build)
    print_message "Building Docker images..."
    docker-compose build
    print_message "Build completed successfully."
    ;;
    
  up)
    print_message "Starting LexiAI services..."
    docker-compose up -d
    print_message "Services started successfully."
    print_message "You can access the application at http://localhost:${PORT:-80}"
    ;;
    
  down)
    print_message "Stopping LexiAI services..."
    docker-compose down
    print_message "Services stopped successfully."
    ;;
    
  restart)
    print_message "Restarting LexiAI services..."
    docker-compose restart
    print_message "Services restarted successfully."
    ;;
    
  logs)
    print_message "Showing logs..."
    docker-compose logs -f
    ;;
    
  db-migrate)
    print_message "Running database migrations..."
    docker-compose exec backend flask db upgrade
    print_message "Migrations completed successfully."
    ;;
    
  db-init)
    print_message "Initializing database..."
    docker-compose exec backend flask db init
    docker-compose exec backend flask db migrate -m "Initial migration"
    docker-compose exec backend flask db upgrade
    print_message "Database initialized successfully."
    ;;
    
  test)
    print_message "Running tests..."
    docker-compose exec backend python run_tests.py
    ;;
    
  shell)
    print_message "Opening shell in backend container..."
    docker-compose exec backend /bin/bash
    ;;
    
  help|*)
    echo "LexiAI Deployment Script"
    echo ""
    echo "Usage: ./deploy.sh [command]"
    echo ""
    echo "Commands:"
    echo "  build       Build Docker images"
    echo "  up          Start all services"
    echo "  down        Stop all services"
    echo "  restart     Restart all services"
    echo "  logs        Show logs from all services"
    echo "  db-migrate  Run database migrations"
    echo "  db-init     Initialize database and run first migration"
    echo "  test        Run tests"
    echo "  shell       Open shell in backend container"
    echo "  help        Show this help message"
    ;;
esac

