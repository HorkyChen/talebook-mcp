.PHONY: install test run-mcp run-http clean help

# Default target
help:
	@echo "Talebook MCP Server - Available Commands:"
	@echo "  install     - Install dependencies"
	@echo "  test        - Run tests"
	@echo "  run-mcp     - Run MCP server (stdio transport)"
	@echo "  run-http    - Run HTTP server (FastAPI)"
	@echo "  clean       - Clean up temporary files"
	@echo "  help        - Show this help message"

install:
	pip install -r requirements.txt

test:
	python test/test_server.py

run-mcp:
	python src/server.py

run-http:
	python src/server.py --fastapi

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
