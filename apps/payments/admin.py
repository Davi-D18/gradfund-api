from django.contrib import admin
from apps.payments.models import Payment, PaymentWebhook


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'contratante', 'prestador', 'servico', 
        'valor_total', 'status', 'data_criacao'
    ]
    list_filter = ['status', 'data_criacao', 'metodo_pagamento']
    search_fields = [
        'contratante__usuario__username', 
        'prestador__usuario__username',
        'servico__titulo'
    ]
    readonly_fields = [
        'id', 'mercadopago_payment_id', 'mercadopago_preference_id',
        'data_criacao', 'data_atualizacao', 'data_aprovacao'
    ]
    ordering = ['-data_criacao']


@admin.register(PaymentWebhook)
class PaymentWebhookAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'payment', 'evento_tipo', 
        'processado', 'data_recebimento'
    ]
    list_filter = ['evento_tipo', 'processado', 'data_recebimento']
    readonly_fields = [
        'id', 'webhook_data', 'data_recebimento'
    ]
    ordering = ['-data_recebimento']