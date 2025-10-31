# Boas práticas: Python + Django + Django REST Framework (PEP8)

Resumo curto com práticas recomendadas para escrever código limpo, testável e consistente em projetos Python/Django/DRF, seguindo convenções PEP8.

## 1. Estilo e formatação (PEP8)
- Use nomes descritivos e snake_case para funções/variáveis; PascalCase para classes.
- Linhas com no máximo 79 caracteres (ou 88 se usar Black com configuração padrão).
- Indentação com 4 espaços; evite tabs.
- Espaçamento: uma linha em branco entre funções e duas entre classes de nível superior.
- Imports: padrão — stdlib, terceiros, locais; separados por linha em branco. Use isort.
- Docstrings em funções/classes: curta descrição + parâmetros/retorno quando relevante.
- Ferramentas: Black (formatação), Flake8 (lint), isort (ordenar imports), mypy/pyright (tipagem opcional).

Exemplo:
```python
# bom: nome/descritivo, 4 espaços
def calcular_total_itens(itens: list) -> int:
  """Retorna a soma das quantidades na lista de itens."""
  return sum(item.qtd for item in itens)
```

## 2. Estrutura do projeto
- Seguir layout padrão Django:
  - projeto_root/
  - manage.py
  - project_name/
  - apps/
    - app_name/
    - models.py
    - views.py
    - serializers.py
    - urls.py
    - tests/
- Apps pequenas e coesas: uma responsabilidade por app.
- `settings/` dividido por ambiente (base.py, dev.py, prod.py) ou usar django-environ para variáveis sensíveis.
- Mantenha arquivos longos separados (ex.: forms.py, serializers.py, services.py).

## 3. Models
- Use nomes no singular e verbose_name quando necessário.
- Adicione índices e constraints no Meta quando fizer sentido.
- Evite lógica complexa no model — preferir services ou managers para regras de negócio.
- Use QuerySet/Manager customizados para consultas reutilizáveis.

Exemplo:
```python
class OrderQuerySet(models.QuerySet):
  def finalized(self):
    return self.filter(status='finalized')

class Order(models.Model):
  status = models.CharField(max_length=20)
  objects = OrderQuerySet.as_manager()
```

## 4. Serializers (DRF)
- Mantenha serializers focados: validação e (de)serialização.
- Prefira serializers.ModelSerializer quando apropriado; use Serializer para casos custom.
- Validations: usar `validate_<field>` e `validate()` para validação de objeto.
- Evite lógica de negócio complexa nos serializers — delegue a services.

Exemplo:
```python
class ProductSerializer(serializers.ModelSerializer):
  class Meta:
    model = Product
    fields = ['id', 'name', 'price']

  def validate_price(self, value):
    if value < 0:
      raise serializers.ValidationError("Preço inválido.")
    return value
```

## 5. Views / ViewSets (DRF)
- Prefira ViewSets + Routers para CRUD simples.
- Para endpoints customizados, escreva Actions (`@action`) ou views funcionais quando simples.
- Separe responsabilidades: view apenas orquestra, a lógica vai em services/managers.

Exemplo:
```python
class ProductViewSet(viewsets.ModelViewSet):
  queryset = Product.objects.all()
  serializer_class = ProductSerializer
```

## 6. URLs
- Use names para rotas (`name=`) e `reverse()`/`reverse_lazy`.
- Registrar ViewSets nos routers em vez de manualmente montar todas as rotas.

## 7. Settings e segredos
- Nunca comitar segredos. Use variáveis de ambiente e ferramentas como django-environ.
- Desabilite DEBUG em produção; configure ALLOWED_HOSTS.
- Configure loggers de forma explícita.

## 8. Segurança
- Usar CSRF, XSS e proteção contra SQL injection via ORM.
- Revogar permissões excessivas e revisar CORS/Rate limiting.
- Use HTTPS e HSTS em produção.
- Hash de senha com configurações default do Django (bcrypt/Argon2 se configurado).

## 9. Testes
- TDD quando possível. Cobertura para models, serializers, views, permissions e integrações.
- Testes pequenos e rápidos; evitar dependência de serviços externos (usar mocks).
- Fixtures simples: factories (factory_boy) em vez de fixtures globais complexas.

Exemplo:
```python
def test_product_serializer_invalid_price():
  data = {'name': 'p', 'price': -1}
  serializer = ProductSerializer(data=data)
  assert not serializer.is_valid()
  assert 'price' in serializer.errors
```

## 10. Migrations
- Gerar migrations claras e revisá-las antes de commitar.
- Evitar grandes migrations que alterem muitos registros em produção sem estratégia (usar migrations em etapas).

## 11. Performance
- Use `select_related` / `prefetch_related` para evitar N+1.
- Paginação nos endpoints list para limitar payload.
- Cache quando fizer sentido (cache fragment, per-view ou Redis).

## 12. APIs e contratos
- Versionamento de API (/api/v1/).
- Use respostas consistentes: código HTTP apropriado, corpo com mensagem/erro padronizado.
- Documentação automática: use drf-yasg, drf-spectacular ou CoreAPI.

## 13. CI/CD e qualidade
- Pipeline com: linting, formatação, testes, segurança (bandit), análise de dependências.
- Revisões de código obrigatórias e checks automáticos.

## 14. Boas práticas operacionais
- Rollbacks e migrations testadas em staging.
- Logs estruturados e métricas de performance.
- Backups e políticas de retenção.

## Referências rápidas
- PEP8 / Python style guide.
- Documentação Django e DRF.
- Black, Flake8, isort, factory_boy, pytest, Sentry/Prometheus.

Observação final: prefira código simples e legível; extraia complexidade para funções/serviços testáveis; automatize formatação e lint para manter consistência do time.