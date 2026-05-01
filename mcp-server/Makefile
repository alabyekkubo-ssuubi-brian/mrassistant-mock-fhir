.PHONY: help install dev-up dev-down fhir-up fhir-down fhir-logs load-data run http-server server-http ngrok-up test test-tools test-mcp test-http test-curl inspect clean

# Prefer Compose V2 (`docker compose`); fall back to standalone `docker-compose`
DOCKER_COMPOSE := $(shell if docker compose version >/dev/null 2>&1; then echo "docker compose"; elif command -v docker-compose >/dev/null 2>&1; then echo docker-compose; else echo ""; fi)

# Default target
help:
	@echo "Hospital FHIR MCP Server"
	@echo ""
	@echo "Development:"
	@echo "  make dev-up      Start HAPI FHIR, load mock data"
	@echo "  make dev-down    Stop all services"
	@echo "  make run         Run MCP server (stdio mode)"
	@echo ""
	@echo "HTTP Mode (for public deployment):"
	@echo "  make http-server   Run MCP server with HTTP transport"
	@echo "  make server-http   Same as http-server (matches repo root)"
	@echo "  make ngrok-up    Start ngrok tunnel (auto-detects domain)"
	@echo ""
	@echo "Testing:"
	@echo "  make test-tools  Test MCP tools directly (no protocol)"
	@echo "  make test-mcp    Test via MCP client (stdio)"
	@echo "  make test-http   Test via MCP HTTP client"
	@echo "  make test-curl   Test FHIR endpoints with curl"
	@echo "  make inspect     Launch MCP Inspector (browser UI)"
	@echo ""
	@echo "Individual commands:"
	@echo "  make install     Install Python dependencies"
	@echo "  make fhir-up     Start HAPI FHIR server"
	@echo "  make fhir-down   Stop HAPI FHIR server"
	@echo "  make fhir-logs   Tail HAPI FHIR logs"
	@echo "  make load-data   Load mock FHIR data"
	@echo "  make test        Run all tests"
	@echo "  make clean       Remove virtual env and docker volumes"
	@echo ""
	@echo "Docker Compose (for fhir-up): install plugin or docker-compose binary."
	@echo "  Debian/Ubuntu: sudo apt install docker-compose-plugin"

# Install dependencies
install:
	uv sync

# Start everything for development
dev-up: fhir-up
	@echo "Waiting for HAPI FHIR to start..."
	@uv run python -c "import time; time.sleep(10)"
	@$(MAKE) wait-for-fhir
	@$(MAKE) load-data
	@echo ""
	@echo "✓ Development environment ready!"
	@echo ""
	@echo "Run MCP server with: make run"
	@echo "Or in one command:   uv run mcp-server"

# Stop everything
dev-down: fhir-down
	@echo "✓ Development environment stopped"

# HAPI FHIR commands
fhir-up:
	@if [ -z "$(DOCKER_COMPOSE)" ]; then \
		echo >&2 "Docker Compose not found (need 'docker compose' or 'docker-compose')."; \
		echo >&2 "  Debian/Ubuntu: sudo apt install docker-compose-plugin"; \
		echo >&2 "  Or: https://docs.docker.com/compose/install/linux/"; \
		exit 1; \
	fi
	@$(DOCKER_COMPOSE) up -d
	@echo "HAPI FHIR starting at http://localhost:8080/fhir"

fhir-down:
	@if [ -n "$(DOCKER_COMPOSE)" ]; then $(DOCKER_COMPOSE) down; fi

fhir-logs:
	@if [ -z "$(DOCKER_COMPOSE)" ]; then echo >&2 "Docker Compose not found"; exit 1; fi
	@$(DOCKER_COMPOSE) logs -f

# Wait for FHIR server to be ready (Python: works on Windows without curl/sleep in PATH)
wait-for-fhir:
	@echo "Checking FHIR server health..."
	@uv run python scripts/wait_for_fhir.py

# Load mock data
load-data:
	uv run python scripts/load_mock_data.py

# Run MCP server (stdio mode - for local testing)
run:
	uv run mcp-server

# Run MCP server with HTTP transport (for public deployment)
http-server:
	uv run python -m mcp_server.http_server

# Alias for root Makefile / docs that say `make server-http`
server-http: http-server

# Start ngrok tunnel (reads token from .env.ngrok, auto-detects domain)
ngrok-up:
	@if [ ! -f .env.ngrok ]; then \
		echo "✗ .env.ngrok not found!"; \
		echo ""; \
		echo "Create it from the example:"; \
		echo "  cp .env.ngrok.example .env.ngrok"; \
		echo ""; \
		echo "Then edit .env.ngrok and add your auth token from:"; \
		echo "  https://dashboard.ngrok.com/get-started/your-authtoken"; \
		exit 1; \
	fi
	@. ./.env.ngrok && \
	if [ -z "$$NGROK_AUTHTOKEN" ] || [ "$$NGROK_AUTHTOKEN" = "your_auth_token_here" ]; then \
		echo "✗ NGROK_AUTHTOKEN not set in .env.ngrok"; \
		exit 1; \
	fi && \
	export NGROK_AUTHTOKEN="$$NGROK_AUTHTOKEN" && \
	echo "Checking for existing ngrok domains..." && \
	DOMAIN=$$(ngrok api reserved-domains list 2>/dev/null | grep -o '"domain":"[^"]*"' | head -1 | cut -d'"' -f4) && \
	if [ -n "$$DOMAIN" ]; then \
		echo "Found domain: $$DOMAIN"; \
		echo "Starting ngrok tunnel on port 3000..."; \
		ngrok http --domain="$$DOMAIN" 3000; \
	else \
		echo "No static domain found. Using random URL."; \
		echo "To get a free static domain, visit: https://dashboard.ngrok.com/cloud-edge/domains"; \
		ngrok http 3000; \
	fi

# Run all tests
test: test-tools

# Test MCP tools directly (bypasses MCP protocol)
test-tools:
	uv run python scripts/test_tools.py

# Test via MCP client (full JSON-RPC protocol)
test-mcp:
	uv run python scripts/test_mcp_client.py

# Test via MCP HTTP client
test-http:
	uv run python scripts/sample_mcp_http_client.py

# Test FHIR endpoints with curl
test-curl:
	chmod +x scripts/test_fhir_curl.sh
	./scripts/test_fhir_curl.sh

# Launch MCP Inspector (browser UI)
inspect:
	npx @modelcontextprotocol/inspector uv run mcp-server

# Clean up
clean:
	@if [ -n "$(DOCKER_COMPOSE)" ]; then $(DOCKER_COMPOSE) down -v; fi
	rm -rf .venv
	rm -rf __pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Cleaned up"
