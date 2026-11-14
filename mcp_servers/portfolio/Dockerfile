# Multi-stage lightweight Docker image for GigBid Portfolio MCP Server
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir mcp pydantic

# Copy portfolio server code and data
COPY mcp_servers/ /app/mcp_servers/
COPY data/ /app/data/

ENV PYTHONPATH=/app
ENV GIGBID_DATA_DIR=/app/data

# Run over standard input/output (stdio) for MCP clients (Claude Desktop, Cursor, GigBid)
ENTRYPOINT ["python3", "-m", "mcp_servers.portfolio.server"]
