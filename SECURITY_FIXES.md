# Correções de Segurança e Performance - GradFund API

## 🚨 Correções Críticas (Prioridade Máxima)

### 1. Code Injection - CWE-94
**Arquivo:** `core/management/commands/seeder.py` (linha 113-114)
- **Problema:** Uso de `exec()` com entrada não sanitizada
- **Impacto:** Vulnerabilidade crítica de execução remota de código

**Subtarefas:**
- [ ] 1.1 Analisar código atual do seeder que usa `exec()`
- [ ] 1.2 Implementar função de importação dinâmica segura usando `importlib`
- [ ] 1.3 Substituir `exec(seeder_class + '().run()')` por importação segura
- [ ] 1.4 Adicionar validação de nome de classe antes da importação
- [ ] 1.5 Testar execução de seeders após mudança
- [ ] 1.6 Documentar nova implementação

### 2. Path Traversal - CWE-22
**Arquivos afetados:** 4 arquivos com múltiplas ocorrências
- **Problema:** Construção de caminhos com entrada não validada
- **Impacto:** Acesso não autorizado ao sistema de arquivos

**Subtarefas:**
- [ ] 2.1 **authentication/schemas.py (linhas 202-203, 207-208)**
  - [ ] 2.1.1 Identificar uso de caminhos de arquivo não validados
  - [ ] 2.1.2 Implementar validação com `os.path.abspath()` e `startswith()`
  - [ ] 2.1.3 Usar `django.utils._os.safe_join()` para construção segura
- [ ] 2.2 **createapp.py (múltiplas linhas)**
  - [ ] 2.2.1 Mapear todas as ocorrências de path traversal
  - [ ] 2.2.2 Validar nomes de apps antes de criar diretórios
  - [ ] 2.2.3 Usar `pathlib.Path` para manipulação segura
- [ ] 2.3 **typeservice_seeder.py (linha 27-28)**
  - [ ] 2.3.1 Validar caminho do arquivo JSON
  - [ ] 2.3.2 Restringir acesso apenas ao diretório de dados
- [ ] 2.4 **chat_consumer.py (linha 254-255)**
  - [ ] 2.4.1 Identificar uso de caminhos dinâmicos
  - [ ] 2.4.2 Implementar whitelist de caminhos permitidos
- [ ] 2.5 Criar função utilitária para validação de caminhos
- [ ] 2.6 Testar tentativas de path traversal após correções

### 3. Falta de Verificação de Permissões
**Arquivo:** `apps/chat/controllers/message_controller.py` (linha 41-67)
- **Problema:** Usuários podem marcar mensagens como lidas sem permissão
- **Impacto:** Bypass de controle de acesso

**Subtarefas:**
- [ ] 3.1 Analisar método `marcar_lida` atual
- [ ] 3.2 Identificar como `marcar_todas_lidas` implementa verificação
- [ ] 3.3 Adicionar `ChatService.verificar_permissao_sala()` no início do método
- [ ] 3.4 Implementar retorno 403 Forbidden para usuários sem permissão
- [ ] 3.5 Testar cenários de acesso negado
- [ ] 3.6 Documentar regras de permissão

## ⚠️ Correções de Alta Prioridade

### 4. Validações Faltando
**Impacto:** Possíveis erros de integridade e experiência ruim do usuário

**Subtarefas:**
- [ ] 4.1 **CustomerUserUpdateSerializer (authentication/schemas.py)**
  - [ ] 4.1.1 Analisar validações existentes em `UserSerializer`
  - [ ] 4.1.2 Implementar `validate_username()` com exclusão do usuário atual
  - [ ] 4.1.3 Implementar `validate_email()` com exclusão do usuário atual
  - [ ] 4.1.4 Testar updates com dados duplicados
  - [ ] 4.1.5 Testar updates com dados únicos
- [ ] 4.2 **UniversidadeSerializer (academic/schemas/academic_schema.py)**
  - [ ] 4.2.1 Adicionar verificação `if not value or len(value) < 3`
  - [ ] 4.2.2 Implementar mensagem de erro apropriada para valores nulos
  - [ ] 4.2.3 Testar validação com valores None, vazios e válidos
- [ ] 4.3 **CursoSerializer (academic/schemas/academic_schema.py)**
  - [ ] 4.3.1 Aplicar mesma correção de validação nula
  - [ ] 4.3.2 Padronizar mensagens de erro

### 5. Tratamento de Erros Inadequado
**Impacto:** Dificuldade de debug e mascaramento de problemas

**Subtarefas:**
- [ ] 5.1 **Seeders (múltiplos arquivos)**
  - [ ] 5.1.1 `typeservice_seeder.py`: Substituir `except Exception` por `FileNotFoundError`, `json.JSONDecodeError`, `IntegrityError`
  - [ ] 5.1.2 `universidade_seeder.py`: Adicionar tratamento específico para erros de arquivo
  - [ ] 5.1.3 `curso_seeder.py`: Implementar exceções específicas
- [ ] 5.2 **Chat Consumer (chat/consumers/chat_consumer.py)**
  - [ ] 5.2.1 Adicionar try-catch para `json.dumps()` e `self.send()`
  - [ ] 5.2.2 Implementar logging estruturado para erros
- [ ] 5.3 **Models (múltiplos)**
  - [ ] 5.3.1 `chat/models/chat.py`: Adicionar verificação nula em `__str__`
  - [ ] 5.3.2 `academic/models/academics.py`: Implementar fallback em `__str__`
- [ ] 5.4 Criar classes de exceção customizadas para o projeto
- [ ] 5.5 Implementar logging consistente para todas as exceções

### 6. Problemas de Performance - Queries N+1
**Impacto:** Lentidão na aplicação e sobrecarga do banco

**Subtarefas:**
- [ ] 6.1 **Chat Schema Optimization**
  - [ ] 6.1.1 Identificar ViewSet que usa `ChatRoomSerializer`
  - [ ] 6.1.2 Adicionar `prefetch_related('mensagens')` no queryset
  - [ ] 6.1.3 Otimizar método `get_mensagens_nao_lidas`
  - [ ] 6.1.4 Implementar cache para contagem de mensagens
  - [ ] 6.1.5 Testar performance antes/depois
- [ ] 6.2 **Admin Dashboard Optimization**
  - [ ] 6.2.1 Mapear todas as queries executadas
  - [ ] 6.2.2 Combinar queries relacionadas com `select_related`
  - [ ] 6.2.3 Usar `aggregate()` para contagens
  - [ ] 6.2.4 Implementar cache para estatísticas
  - [ ] 6.2.5 Medir tempo de resposta antes/depois
- [ ] 6.3 **Academic Controllers**
  - [ ] 6.3.1 Adicionar paginação em `UniversidadeViewSet`
  - [ ] 6.3.2 Adicionar paginação em `CursoViewSet`
  - [ ] 6.3.3 Implementar filtros básicos
- [ ] 6.4 **JWT Middleware Optimization**
  - [ ] 6.4.1 Remover validação JWT duplicada
  - [ ] 6.4.2 Otimizar query de CustomerUser com `select_related`
  - [ ] 6.4.3 Implementar cache de usuário por sessão

## 🔧 Correções de Média Prioridade

### 7. CORS Inseguro
**Arquivo:** `core/settings/development.py` (linha 31-32)
**Impacto:** Vulnerabilidade de segurança em desenvolvimento

**Subtarefas:**
- [ ] 7.1 Identificar domínios do frontend em desenvolvimento
- [ ] 7.2 Criar lista `CORS_ALLOWED_ORIGINS` com domínios específicos
- [ ] 7.3 Remover `CORS_ALLOW_ALL_ORIGINS = True`
- [ ] 7.4 Configurar `CORS_ALLOWED_ORIGINS` para produção
- [ ] 7.5 Testar requisições CORS do frontend
- [ ] 7.6 Documentar configuração CORS no README

### 8. Configuração de Produção
**Arquivo:** `manage.py` (linha 8-9)
**Impacto:** Risco de usar configurações de desenvolvimento em produção

**Subtarefas:**
- [ ] 8.1 Criar variável de ambiente `DJANGO_SETTINGS_MODULE`
- [ ] 8.2 Modificar `manage.py` para usar variável de ambiente
- [ ] 8.3 Definir fallback seguro para `core.settings.base`
- [ ] 8.4 Atualizar scripts de deploy
- [ ] 8.5 Atualizar documentação de instalação
- [ ] 8.6 Testar em diferentes ambientes

### 9. Otimizações Gerais de Performance
**Impacto:** Melhoria da experiência do usuário

**Subtarefas:**
- [ ] 9.1 **Academic Controllers**
  - [ ] 9.1.1 Implementar `PageNumberPagination` customizada
  - [ ] 9.1.2 Adicionar `filterset_fields = ['nome']` em ambos ViewSets
  - [ ] 9.1.3 Implementar `search_fields` para busca
  - [ ] 9.1.4 Adicionar `ordering_fields`
- [ ] 9.2 **JWT Middleware (já coberto em 6.4)**
- [ ] 9.3 **Database Indexes**
  - [ ] 9.3.1 Analisar campos frequentemente consultados
  - [ ] 9.3.2 Adicionar índices em campos de busca
  - [ ] 9.3.3 Otimizar índices compostos se necessário
- [ ] 9.4 **Caching Strategy**
  - [ ] 9.4.1 Implementar cache para dados estáticos (universidades, cursos)
  - [ ] 9.4.2 Cache de sessão para dados de usuário
  - [ ] 9.4.3 Cache de queries frequentes

## 📝 Melhorias de Qualidade de Código

### 10. Nomenclatura e Consistência
**Impacto:** Manutenibilidade e padronização do código

**Subtarefas:**
- [ ] 10.1 **Chat Models**
  - [ ] 10.1.1 Alterar `('text', 'Texto')` para `('texto', 'Texto')`
  - [ ] 10.1.2 Verificar impacto em dados existentes
  - [ ] 10.1.3 Criar migração de dados se necessário
  - [ ] 10.1.4 Atualizar frontend para usar novos valores
- [ ] 10.2 **Padronização Geral**
  - [ ] 10.2.1 Auditar uso de inglês/português em choices
  - [ ] 10.2.2 Padronizar mensagens de erro para português
  - [ ] 10.2.3 Revisar nomenclatura de variáveis
- [ ] 10.3 **Code Style**
  - [ ] 10.3.1 Configurar pre-commit hooks
  - [ ] 10.3.2 Executar black/flake8 em todo o código
  - [ ] 10.3.3 Padronizar imports

### 11. Documentação
**Impacto:** Facilita manutenção e onboarding

**Subtarefas:**
- [ ] 11.1 **Scripts**
  - [ ] 11.1.1 Corrigir comentário Gunicorn→Daphne em `start.sh`
  - [ ] 11.1.2 Adicionar comentários explicativos em scripts
- [ ] 11.2 **Code Documentation**
  - [ ] 11.2.1 Adicionar docstrings em métodos complexos
  - [ ] 11.2.2 Documentar regras de negócio no código
  - [ ] 11.2.3 Criar exemplos de uso para comandos customizados
- [ ] 11.3 **API Documentation**
  - [ ] 11.3.1 Melhorar documentação Swagger
  - [ ] 11.3.2 Adicionar exemplos de request/response
  - [ ] 11.3.3 Documentar códigos de erro

### 12. Otimização de Database
**Impacto:** Performance de queries e storage

**Subtarefas:**
- [ ] 12.1 **UUID Analysis**
  - [ ] 12.1.1 Avaliar necessidade real de UUID vs AutoField
  - [ ] 12.1.2 Medir impacto de performance atual
  - [ ] 12.1.3 Considerar migração para AutoField se apropriado
- [ ] 12.2 **Index Optimization**
  - [ ] 12.2.1 Analisar queries mais frequentes
  - [ ] 12.2.2 Adicionar índices compostos onde necessário
  - [ ] 12.2.3 Remover índices não utilizados
- [ ] 12.3 **Query Optimization**
  - [ ] 12.3.1 Implementar `select_related` em ForeignKeys
  - [ ] 12.3.2 Usar `prefetch_related` em ManyToMany
  - [ ] 12.3.3 Otimizar queries do admin interface

## 🔄 Plano de Implementação Detalhado

### Fase 1 - Críticas (Imediato - 1 dia)
**Objetivo:** Eliminar vulnerabilidades críticas de segurança
- [ ] **Dia 1 - Manhã:** Subtarefas 1.1 a 1.6 (Code Injection)
- [ ] **Dia 1 - Tarde:** Subtarefas 2.1 a 2.4 (Path Traversal)
- [ ] **Dia 1 - Noite:** Subtarefas 3.1 a 3.6 (Permissões Chat)

**Critério de Conclusão:** Todas as vulnerabilidades críticas corrigidas e testadas

### Fase 2 - Altas (2-3 dias)
**Objetivo:** Melhorar robustez e performance crítica
- [ ] **Dia 2:** Subtarefas 4.1 a 4.3 (Validações)
- [ ] **Dia 3:** Subtarefas 5.1 a 5.5 (Tratamento de Erros)
- [ ] **Dia 4:** Subtarefas 6.1 a 6.4 (Performance N+1)

**Critério de Conclusão:** Validações robustas, erros específicos, queries otimizadas

### Fase 3 - Médias (2-3 dias)
**Objetivo:** Configurações seguras e otimizações gerais
- [ ] **Dia 5:** Subtarefas 7.1 a 7.6 (CORS) + 8.1 a 8.6 (Configuração)
- [ ] **Dia 6-7:** Subtarefas 9.1 a 9.4 (Otimizações Gerais)

**Critério de Conclusão:** Configurações de produção seguras, performance melhorada

### Fase 4 - Melhorias (3-4 dias)
**Objetivo:** Qualidade de código e documentação
- [ ] **Dia 8:** Subtarefas 10.1 a 10.3 (Nomenclatura)
- [ ] **Dia 9:** Subtarefas 11.1 a 11.3 (Documentação)
- [ ] **Dia 10-11:** Subtarefas 12.1 a 12.3 (Database Optimization)

**Critério de Conclusão:** Código padronizado, bem documentado e otimizado

### Cronograma de Testes
- [ ] **Testes Diários:** Após cada fase, executar suite de testes
- [ ] **Testes de Integração:** Dias 4, 7, 11
- [ ] **Testes de Performance:** Dias 4, 7, 11
- [ ] **Testes de Segurança:** Dias 1, 4, 11

## 🧪 Testes Necessários

### Testes de Segurança
- [ ] Teste de path traversal
- [ ] Teste de injection
- [ ] Teste de permissões de chat

### Testes de Performance
- [ ] Benchmark de queries otimizadas
- [ ] Teste de carga com paginação
- [ ] Monitoramento de N+1 queries

### Testes de Integração
- [ ] Fluxo completo de chat
- [ ] Autenticação JWT
- [ ] CORS em diferentes ambientes

## 📊 Métricas de Sucesso

- **Segurança:** 0 vulnerabilidades críticas/altas
- **Performance:** Redução de 50%+ no tempo de resposta
- **Qualidade:** Cobertura de testes > 80%
- **Manutenibilidade:** Redução de code smells

---

**Nota:** Implementar correções em ordem de prioridade. Testar cada correção antes de prosseguir para a próxima.