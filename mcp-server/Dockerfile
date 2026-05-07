FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV MCP_HTTP_PORT=3000

WORKDIR /app

COPY pyproject.toml .
COPY src ./src

RUN python -m pip install --upgrade pip setuptools wheel
RUN python -m pip install --no-cache-dir .

EXPOSE 3000
CMD ["python", "-m", "mcp_server.http_server"]
