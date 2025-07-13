.PHONY: install test run-mcp run-http run-multi run-standalone clean help

# Default target
help:
	@echo "Talebook MCP Server - Available Commands:"
	@echo "  install        - Install dependencies"
	@echo "  test           - Run tests"
	@echo "  run-mcp        - Run MCP server (stdio transport)"
	@echo "  run-http       - Run HTTP server (FastAPI)"
	@echo "  run-multi      - Run multi-transport server"
	@echo "  run-standalone - Run standalone HTTP server"
	@echo "  test-endpoints - Test all HTTP endpoints"
	@echo "  test-mcp       - Test MCP initialization"
	@echo "  clean          - Clean up temporary files"
	@echo "  help           - Show this help message"

install:
	pip install -r requirements.txt

test:
	python test/test_server.py

run-mcp:
	python src/server.py

run-http:
	python src/server.py --fastapi

run-multi:
	python src/multi_transport_server.py

run-standalone:
	python src/standalone_server.py

test-endpoints:
	python test/test_endpoints.py

test-mcp:
	python test/test_mcp_init.py

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
