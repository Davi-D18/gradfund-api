# GradFund API

## 📋 Sobre o Projeto

O **GradFund** é uma plataforma online que para facilitar a arrecadação de fundos para formaturas de estudantes de universidades públicas através do oferecimento de serviços diversos.

### 🎯 Problemática

Estudantes de universidades públicas enfrentam dificuldades para arrecadar fundos para suas formaturas devido a:

- **Falta de tempo** pelos estudos intensivos
- **Limitação de recursos financeiros** pessoais
- **Carência de ferramentas eficientes** para organizar campanhas de arrecadação

### 💡 Solução

A plataforma conecta estudantes universitários com a comunidade externa (pessoas físicas) através de um marketplace de serviços, onde:

- **Estudantes** cadastram e oferecem serviços diversos baseados em suas habilidades
- **Comunidade externa** visualiza e contrata os serviços
- **Contato direto** entre estudante e contratante para negociação
- **Valores acordados** são direcionados para o fundo de formatura do estudante

> **MVP**: Esta versão inicial foca na conexão entre estudantes e contratantes. Integração com plataformas de pagamento será implementada em versões futuras.

### 🎓 Público-Alvo

- Estudantes matriculados em universidades públicas
- Foco em discentes que dependem de iniciativas próprias para custear eventos de formatura

## 🛠️ Arquitetura da API

### Apps Principais

**🔐 Authentication**
- Gerenciamento de usuários
- Sistema de autenticação JWT
- Tipos de usuário (estudante, público externo)

**🎓 Academic**
- Cadastro de universidades
- Catálogo de cursos universitários
- Vinculação de estudantes às instituições

**💼 Services**
- Cadastro e gerenciamento de serviços oferecidos
- Categorização por tipos de serviço
- Sistema de precificação
- Vinculação estudante-serviço

### 🏗️ Estrutura Técnica

```
gradfund-api/
├── apps/                    # Apps funcionais do Django
│   ├── authentication/     # Gestão de usuários
│   ├── academic/           # Universidades e cursos
│   └── services/           # Marketplace de serviços
├── core/                   # Funcionalidades centrais
├── utils/                  # Utilitários compartilhados
├── seeders/                # População inicial do banco
```

## 🎯 Funcionalidades Principais

### Para Estudantes
- **Cadastro personalizado** com informações acadêmicas
- **Criação de serviços** com descrição, preço e categoria
- **Gestão de ofertas** (criar, editar, desativar)
- **Perfil acadêmico** vinculado à universidade e curso

### Para Contratantes
- **Navegação por serviços** disponíveis
- **Filtros por categoria** e tipo de serviço
- **Visualização de perfis** dos estudantes
- **Sistema de contato** direto com o estudante
- **Negociação direta** de valores e condições

## 🔧 Tecnologias Utilizadas

- **Django 5.2.4** - Framework web principal
- **Django REST Framework** - API REST
- **JWT Authentication** - Sistema de autenticação
- **PostgreSQL** - Banco de dados (produção)
- **SQLite** - Banco de dados (desenvolvimento)

## 🌟 Diferenciais

### Flexibilidade Total
- Estudantes podem oferecer **qualquer tipo de serviço**, não apenas relacionado ao curso
- Categorias amplas que abrangem habilidades pessoais e profissionais

### Foco Social
- **Exclusivo para universidades públicas**
- Apoio direto ao **financiamento de formaturas**
- Valorização das **habilidades estudantis**

### MVP Focado
- **Conexão direta** entre estudantes e contratantes
- **Simplicidade** na navegação e contratação

## 🎯 Impacto Esperado

- **Facilitar** o acesso a recursos para formaturas
- **Valorizar** as habilidades dos estudantes universitários
- **Fomentar** o empreendedorismo estudantil

---

> **Nota**: Esta é a API backend da plataforma. O frontend web será desenvolvido separadamente e consumirá esta API através dos endpoints REST documentados.

## 🔗 Frontend

Frontend web application repository: [gradfund-web](https://github.com/Davi-D18/gradfund)