# Integração Mercado Pago + Django/DRF  
> **Objetivo**: Permitir que usuários criem Serviços via API, e que outros usuários comprem esses Serviços por meio da integração com Mercado Pago.  
> A conta em Mercado Pago já será criada separadamente. A IA deverá entender o contexto técnico e implementar os endpoints, lógica de pagamento e pós-pagamento.

---

Para fazer toda a funcionalidade de pagamento, separe em um app a parte chamado `payments`

## 1. Visão geral do sistema  
- Usuário do tipo “universitario” cria um ou vários serviços pela API do Django/DRF.  
- Usuário do tipo "publico_externo" acessa um endpoint para iniciar a compra de um desses Serviços.  
- O backend cria uma ordem (`Order`) em status “pending” (aguardando pagamento).  
- O backend solicita a criação de um pagamento ou preferência no Mercado Pago usando o SDK Python.  
- O comprador efetua o pagamento via Mercado Pago (cartão, PIX, boleto ou outro método suportado).  
- O backend recebe notificação via **Webhook** ou consulta status do pagamento, e atualiza a ordem para “paid” ou “failed”.  
- Após pagamento aprovado: lógica de pós­pagamento, notiicar o front-end que foi pago e atualizar a ordem no banco.  
- O sistema deve estar preparado para ambiente de **sandbox/teste** e ambiente de produção, com chaves correspondentes.

---

## 2. Modelagem de dados sugerida  
```python
# models.py

class Order(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders_made")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="orders_received")
    status = models.CharField(
        max_length=20,
        choices=[("pending","Pendente"), ("paid","Pago"), ("failed","Falhou")],
        default="pending"
    )
    payment_id = models.CharField(max_length=255, blank=True, null=True)  # id retornado pelo MercadoPago
    external_reference = models.CharField(max_length=255, blank=True, null=True)  # se necessário
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
````

## 4. Integração backend com Mercado Pago

### 4.1 Instalação e configuração

* Instale o SDK oficial para Python:

  ````bash
  pip install mercadopago 
  ````
* Configure as credenciais no `base.py`, por exemplo:

  ```python
  MERCADO_PAGO_ACCESS_TOKEN = "<sua-access_token>"
  MERCADO_PAGO_PUBLIC_KEY = "<sua-public_key>"
  MERCADO_PAGO_MODE = "sandbox"  # ou "production"
  ```
* Inicialize o SDK no código:

  ````apps/payments/apps.py
  from django.apps import AppConfig
  import mercadopago

  class ServicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.services'

    def ready(self):
      sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN) 

  ````

### 4.2 Criar pagamento ou preferência

* Você pode optar por **pagamento direto** (`api/v1/payments`) ou usar uma **preferência** para checkout modal/redirecionado.
* Exemplo simples de pagamento direto usando SDK:

  ```python
  payment_data = {
      "transaction_amount": float(product.price),
      "token": token_do_cartão,  # se for cartão
      "description": product.title,
      "installments": 1,
      "payment_method_id": payment_method_id,
      "payer": {
          "email": buyer.email,
          "identification": {
              "type": "CPF",
              "number": buyer.cpf
          }
      }
  }
  result = sdk.payment().create(payment_data)
  payment = result["response"]
  ```

  Esse fluxo está descrito na documentação de pagamentos da API. ([Mercado Pago][1])
* Exemplo de integração via PIX ou método alternativo:

  ```python
  payment_data = {
      "transaction_amount": float(product.price),
      "description": product.title,
      "payment_method_id": "pix",
      "payer": {
          "email": buyer.email
      }
  }
  request_options = mercadopago.config.RequestOptions()
  request_options.custom_headers = {"X-Idempotency-Key": uuid4().hex}
  result = sdk.payment().create(payment_data, request_options)
  ```

  Conforme documentação de PIX da Mercado Pago. ([mercadopago.com.br][2])

### 4.3 Webhook e atualização de status

* Configure no painel da Mercado Pago o endereço de **notificação (Webhook URL)** apontando para o endpoint do seu sistema, ex: `/api/webhook/mercadopago/`.
* Quando a notificação for recebida, valide os dados, busque o `payment_id`, recupere o status via SDK ou use o payload da notificação, e atualize o `Order.status` para `paid` ou `failed`.
* Use o cabeçalho `X-Idempotency-Key` para evitar processar duplicatas. ([Mercado Pago][1])

---

## 5. Fluxo completo (exemplo)

1. Usuário vendedor cria produto via `POST /api/products/`.
2. Usuário comprador visualiza produto, escolhe comprar.
3. Front-end envia `POST /api/orders/` com `product_id`.
4. Backend cria `Order(status="pending")`, gera pagamento/preference na Mercado Pago, recebe `payment_id` ou `preference_id`, retorna ao front-end link ou dados para checkout.
5. Comprador efetua pagamento via checkout da Mercado Pago.
6. Mercado Pago envia notificação para o webhook ou front-end retorna com callback.
7. Backend valida pagamento, atualiza `Order.status = "paid"` ou `"failed"`.
8. Após pagamento aprovado: lógica de pós-pagamento — por exemplo:

   * Marca produto como vendido ou `is_active=False`.
   * Notifica usuário vendedor e comprador (e-mail, push, etc).
   * Se for marketplace: calcula comissão, repassa valor ou registra repasse.
9. Front-end mostra status ao comprador e vendedor.

---

## 6. Considerações de segurança e boas práticas

* Nunca exponha `ACCESS_TOKEN` no front-end — use apenas no backend.
* Use ambiente **sandbox/teste** antes de migrar para produção. ([mercadopago.com.br][3])
* Configure `X-Idempotency-Key` nos headers para evitar duplicação de chamadas. ([mercadopago.com.br][2])
* Valide todos os campos recebidos nas requisições (produto existe, preço correto, usuário autenticado, autorização válida).
* Trate erros de pagamento (cartão recusado, boleto vencido, PIX não confirmado, falhas de conexão).
* Registre logs de pagamento, notificação webhook, estado da ordem para auditoria.
* Proteja o endpoint de webhook: verifique assinatura ou token, bloqueie requisições não autorizadas.
* Considere implementar timeout para “pending” orders — se o pagamento não for finalizado em X horas, marque como “failed” ou expirada.

---

## 7. Exemplos de código (DRF ViewSet simplificado)

```python
# serializers.py
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id","title","description","price","currency","is_active"]

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id","product","status","payment_id","external_reference","created_at","updated_at"]

# views.py
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        product_id = request.data.get("product_id")
        product = get_object_or_404(Product, id=product_id, is_active=True)
        order = Order.objects.create(buyer=request.user, product=product)
        # Criar pagamento via MercadoPago
        import mercadopago
        sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
        payment_data = {
            "transaction_amount": float(product.price),
            "description": product.title,
            "payer": {"email": request.user.email}
        }
        result = sdk.payment().create(payment_data)
        payment = result["response"]
        order.payment_id = payment["id"]
        order.save()
        return Response({"order_id": order.id, "payment_status": payment["status"]})
```

---

## 8. Checklist final para a IA

* [ ] Criar ou usar modelos `Product` e `Order` conforme modelagem.
* [ ] Endpoints REST para criação/listagem de Serviços.
* [ ] Endpoint para iniciar compra (`Order` creation + chamada Mercado Pago).
* [ ] Integração com SDK da Mercado Pago (instalação, configuração, uso).
* [ ] Webhook endpoint para receber notificações de pagamento.
* [ ] Lógica de pós-pagamento (atualização status, marcações, notificações).
* [ ] Tratamento de erros, duplicações, segurança.
* [ ] Ambiente de sandbox/teste vs produção configurável.
* [ ] Documentar no código/README instruções de uso, variáveis de ambiente, testes.

[1]: https://www.mercadopago.com.ar/developers/en/reference/payments/_payments/post?utm_source=chatgpt.com "Create payment - Payments - Mercado Pago Developers"
[2]: https://www.mercadopago.com.br/developers/en/docs/checkout-bricks/payment-brick/payment-submission/pix?utm_source=chatgpt.com "Pix - Payments submission - Mercado Pago Developers"
[3]: https://www.mercadopago.com.br/developers/en/docs/checkout-pro/configure-development-enviroment?utm_source=chatgpt.com "Configure development environment - Stages of integration"
