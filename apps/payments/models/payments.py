from django.db import models
from django.core.validators import MinValueValidator
from apps.authentication.models import CustomerUser
from apps.services.models import Service
from core.models import UUIDModel


PAYMENT_STATUS_CHOICES = [
    ('pending', 'Pendente'),
    ('approved', 'Aprovado'),
    ('rejected', 'Rejeitado'),
    ('cancelled', 'Cancelado'),
    ('refunded', 'Estornado'),
]


class Payment(UUIDModel):
    contratante = models.ForeignKey(
        CustomerUser, 
        on_delete=models.CASCADE, 
        related_name='payments_as_contratante'
    )
    prestador = models.ForeignKey(
        CustomerUser, 
        on_delete=models.CASCADE, 
        related_name='payments_as_prestador'
    )
    servico = models.ForeignKey(
        Service, 
        on_delete=models.CASCADE, 
        related_name='payments'
    )
    valor_total = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    mercadopago_payment_id = models.CharField(max_length=100, null=True, blank=True)
    mercadopago_preference_id = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    metodo_pagamento = models.CharField(max_length=50, null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    data_aprovacao = models.DateTimeField(null=True, blank=True)
    observacoes = models.TextField(blank=True)

    class Meta:
        ordering = ['-data_criacao']
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'

    def __str__(self):
        return f"Pagamento {self.id} - {self.servico.titulo}"


class PaymentWebhook(UUIDModel):
    payment = models.ForeignKey(
        Payment, 
        on_delete=models.CASCADE, 
        related_name='webhooks',
        null=True, 
        blank=True
    )
    webhook_data = models.JSONField()
    evento_tipo = models.CharField(max_length=50)
    processado = models.BooleanField(default=False)
    data_recebimento = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_recebimento']
        verbose_name = 'Webhook de Pagamento'
        verbose_name_plural = 'Webhooks de Pagamento'

    def __str__(self):
        return f"Webhook {self.evento_tipo} - {self.data_recebimento}"