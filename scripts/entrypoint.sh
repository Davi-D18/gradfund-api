#!/bin/bash

# Exit on error
set -e

echo "🔄 Aguardando banco de dados..."
sleep 2

echo "🔄 Executando migrações..."
python manage.py migrate --noinput

echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear

echo "✅ Inicialização completa!"
echo "🚀 Iniciando servidor..."

# Executar o comando passado ao container
exec "$@"

