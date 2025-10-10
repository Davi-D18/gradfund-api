"""
Configurações de desenvolvimento.
"""

import os
from .base import *  # noqa: F403
from datetime import timedelta

DEBUG = True

# Configuração do banco de dados
# Se DB_HOST estiver definido (rodando no Docker), usa PostgreSQL
# Senão, mantém SQLite para desenvolvimento local sem Docker
if os.getenv('DB_HOST'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'gradfund'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
            'HOST': os.getenv('DB_HOST', 'db'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }

# Allowed hosts para desenvolvimento
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '*']

# Email - Override to use console backend in development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# Swagger settings
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    }
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}

CORS_ALLOW_ALL_ORIGINS = True