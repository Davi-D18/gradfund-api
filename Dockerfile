# Imagem base do Python
FROM python:3.11-slim

# Variáveis de ambiente para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema necessárias para psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar o código do projeto
COPY . .

# Criar diretório para arquivos estáticos e media
RUN mkdir -p staticfiles media

# Dar permissão de execução ao entrypoint
RUN chmod +x entrypoint.sh

# Expor porta 8000
EXPOSE 8000

# Executar entrypoint
ENTRYPOINT ["./entrypoint.sh"]

