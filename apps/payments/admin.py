from django.contrib import admin
from apps.payments.models import Payment, PaymentWebhook


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'contratante', 'prestador', 'servico',
        'valor_total', 'valor_prestador', 'valor_plataforma',
        'status', 'payout_status', 'data_criacao'
    ]
    list_filter = ['status', 'payout_status', 'data_criacao', 'metodo_pagamento']
    search_fields = [
        'contratante__usuario__username',
        'prestador__usuario__username',
        'servico__titulo'
    ]
    readonly_fields = [
        'id', 'mercadopago_payment_id', 'mercadopago_preference_id',
        'valor_plataforma', 'valor_prestador', 'payout_status',
        'payout_amount', 'payout_attempts', 'payout_last_error',
        'payout_transaction_id', 'payout_requested_at', 'payout_completed_at',
        'payout_missing_info_notified', 'payout_failed_notified',
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