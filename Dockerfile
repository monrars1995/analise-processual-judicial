FROM python:3.12-slim

LABEL maintainer="monrars1995"
LABEL description="Análise Processual Judicial - Skill para extração de timeline e identificação de irregularidades processuais"

WORKDIR /app

# Install system dependencies for pdfplumber
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY scripts/ /app/scripts/
COPY references/ /app/references/
COPY SKILL.md /app/
COPY README.md /app/
COPY install.sh /app/

RUN pip install --no-cache-dir pdfplumber reportlab

# Create volume for input/output
VOLUME ["/data"]
WORKDIR /data

# Default command shows help
CMD ["python", "-c", "print('Analise Processual Judicial Docker'); print('Comandos:'); print('  docker run -v $(pwd):/data analise-processual-judicial python /app/scripts/extrair_dados.py /data/processo.pdf /data/processo.json'); print('  docker run -v $(pwd):/data analise-processual-judicial python /app/scripts/identificar_irregularidades.py /data/processo.json /data/irregularidades.json'); print('  docker run -v $(pwd):/data analise-processual-judicial python /app/scripts/gerar_relatorio.py /data/processo.json /data/irregularidades.json /data/relatorio.pdf')"]
