# Multi-stage build for docs2db-mcp-server
FROM python:3.12-slim AS build

WORKDIR /app

# Install build dependencies
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml ./
COPY README.md ./
COPY LICENSE ./

# Install dependencies
RUN uv pip install --system --no-cache .

# Copy source
COPY src/ ./src/

# Final stage
FROM python:3.12-slim AS final

WORKDIR /app

# Copy installed packages from build stage
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=build /usr/local/bin /usr/local/bin
COPY --from=build /app/src /app/src

# Create non-root user
RUN useradd --uid 1001 --create-home --shell /bin/bash mcp && \
    chown -R mcp:mcp /app

USER mcp

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8002/sse').read()" || exit 1

EXPOSE 8002

# Run server
CMD ["python", "-m", "docs2db_mcp"]
