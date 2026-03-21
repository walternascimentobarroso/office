.PHONY: up down test install clean help

# Default target
all: help

# Start the FastAPI application with auto-reload
up:
	@echo "🚀 Starting Excel API server..."
	uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Stop the application (if running in background)
down:
	@echo "🛑 Stopping server..."
	@pkill -f uvicorn || echo "No uvicorn process found"

# Run tests
test:
	@echo "🧪 Running tests..."
	uv run pytest

# Install/update dependencies
install:
	@echo "📦 Installing dependencies..."
	uv sync

# Clean cache files
clean:
	@echo "🧹 Cleaning cache files..."
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

# Show available commands
help:
	@echo "📋 Available commands:"
	@echo "  up      - Start the FastAPI server with auto-reload"
	@echo "  down    - Stop the server"
	@echo "  test    - Run the test suite"
	@echo "  install - Install/update dependencies"
	@echo "  clean   - Clean cache files"
	@echo "  help    - Show this help message"