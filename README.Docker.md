# 🐳 Guia de Instalação Docker - GradFund Backend

Este guia mostra como rodar o backend do GradFund usando Docker, sem precisar instalar Python, PostgreSQL ou Redis na sua máquina.

## 📋 Pré-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop) instalado
- [Docker Compose](https://docs.docker.com/compose/install/) (já vem com Docker Desktop)

## 🚀 Como Rodar

### 1. Criar arquivo de variáveis de ambiente

Copie o arquivo de exemplo:

```bash
cp env.example .env
```

Ou crie manualmente um arquivo `.env` com o seguinte conteúdo:

```env
# Django
DJANGO_SECRET_KEY=your-secret-key-here-change-in-production
DJANGO_SETTINGS_MODULE=core.settings.development

# Database PostgreSQL
DB_NAME=gradfund
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379
```

### 2. Iniciar os containers

```bash
docker-compose up -d
```

Isso irá:
- ✅ Baixar as imagens necessárias (PostgreSQL, Redis, Python)
- ✅ Construir a imagem do backend
- ✅ Criar e iniciar todos os containers
- ✅ Executar migrações do banco de dados
- ✅ Coletar arquivos estáticos

### 3. Ver os logs

```bash
docker-compose logs -f
```

Para ver logs de um serviço específico:

```bash
docker-compose logs -f backend
```

### 4. Executar comandos Django

#### Criar superusuário (admin)

```bash
docker-compose exec backend python manage.py createsuperuser
```

#### Executar migrações

```bash
docker-compose exec backend python manage.py migrate
```

#### Executar seeders (popular banco de dados)

```bash
# Universidades
docker-compose exec backend python manage.py seed_universidades

# Cursos
docker-compose exec backend python manage.py seed_cursos

# Tipos de serviço
docker-compose exec backend python manage.py seed_typeservices
```

#### Acessar shell do Django

```bash
docker-compose exec backend python manage.py shell
```

### 5. Acessar a aplicação

- **API**: http://localhost:8000
- **Admin Django**: http://localhost:8000/admin
- **Swagger (Documentação API)**: http://localhost:8000/swagger
- **WebSocket**: ws://localhost:8000/ws/

### 6. Parar os containers

```bash
docker-compose down
```

Para parar E remover volumes (⚠️ isso apaga o banco de dados):

```bash
docker-compose down -v
```

## 🔧 Comandos Úteis

### Ver containers rodando

```bash
docker-compose ps
```

### Rebuild da imagem (após mudanças no código)

```bash
docker-compose up -d --build
```

### Acessar terminal do container

```bash
docker-compose exec backend bash
```

### Ver logs de erro

```bash
docker-compose logs --tail=100 backend
```

### Reiniciar um serviço específico

```bash
docker-compose restart backend
```

## 📁 Estrutura de Volumes

Os dados são persistidos em volumes Docker:

- `postgres_data`: Dados do PostgreSQL
- `redis_data`: Dados do Redis
- `static_volume`: Arquivos estáticos do Django
- `media_volume`: Arquivos de mídia (uploads)

## 🐛 Troubleshooting

### Porta 8000 já está em uso

Mude a porta no `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "8001:8000"  # Muda de 8000 para 8001
```

### Erro de conexão com banco de dados

Aguarde alguns segundos para o PostgreSQL inicializar completamente, depois reinicie:

```bash
docker-compose restart backend
```

### Limpar tudo e começar do zero

```bash
docker-compose down -v
docker-compose up -d --build
```

### Ver consumo de recursos

```bash
docker stats
```

## 🔄 Desenvolvimento

Durante o desenvolvimento, o código está sincronizado com o container através de volumes:

- Mudanças no código Python são refletidas automaticamente (Django em modo DEBUG)
- Para mudanças em `requirements.txt`, precisa rebuild: `docker-compose up -d --build`
- Para mudanças em variáveis de ambiente, reinicie: `docker-compose restart backend`

## 📚 Próximos Passos

Após o backend rodando, inicie o frontend:

```bash
cd ../gradfund
pnpm install
pnpm dev
```

O frontend rodará em http://localhost:3000 e se conectará ao backend em http://localhost:8000

