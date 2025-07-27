#!/usr/bin/env bash
set -e

# 1. Migrações (aplica apenas pendentes)
echo "🔄 Aplicando migrations..."
python manage.py migrate --noinput

# 2. Variável para o diretório de estáticos
STATIC_DIR="staticfiles"
# 2a. Arquivo de exemplo para testar existência de estáticos do Admin
CHECK_FILE="$STATIC_DIR/admin/css/base.css"

# 3. Se o diretório não existir, ou estiver vazio, ou faltar o arquivo CHECK_FILE, roda collectstatic
if [ ! -d "$STATIC_DIR" ] \
   || [ -z "$(ls -A -- "$STATIC_DIR")" ] \
   || [ ! -f "$CHECK_FILE" ]; then

  echo "📦 Coletando arquivos estáticos..."
  python manage.py collectstatic --noinput

else
  echo "✅ Arquivos estáticos já coletados, pulando collectstatic."
fi

# 4. Criar superusuário a partir das variáveis de ambiente
echo "👤 Verificando superusuário..."
python manage.py shell -c "
import os
from django.contrib.auth import get_user_model
User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
if username and email and password:
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f'✅ Superusuário {username} criado com sucesso!')
    else:
        print(f'ℹ️ Superusuário {username} já existe.')
else:
    print('⚠️ Variáveis de ambiente para superusuário não definidas.')
"

# 5. Inicia o Gunicorn na porta definida pelo Render
echo "🚀 Iniciando Gunicorn..."
exec gunicorn core.wsgi:application --bind 0.0.0.0:$PORT