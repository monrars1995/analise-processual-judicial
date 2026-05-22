# Build stage
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml requirements.txt ./
COPY analise_processual_judicial/ ./analise_processual_judicial/

RUN pip install --user --no-cache-dir -r requirements.txt
RUN pip install --user --no-cache-dir -e .

# Runtime stage
FROM python:3.12-slim

LABEL maintainer="monrars1995"
LABEL description="Análise Processual Judicial - Skill para extração de timeline e identificação de irregularidades processuais"

WORKDIR /data

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY --from=builder /app /app
WORKDIR /app

# Default command shows help
CMD ["analise-processual", "--help"]
