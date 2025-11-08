import logging
import uuid
from decimal import Decimal

import requests
from django.conf import settings
from django.utils import timezone
from apps.payments.models import Payment

logger = logging.getLogger(__name__)


class PayoutError(Exception):
    pass


class PayoutService:
    """Gerencia transferências de valores para os prestadores."""

    def __init__(self):
        mercadopago_settings = settings.MERCADOPAGO
        self.fake_mode = mercadopago_settings.get('FAKE_PAYOUTS', True)
        self.access_token = mercadopago_settings.get('ACCESS_TOKEN')
        self.collector_id = mercadopago_settings.get('COLLECTOR_ID')
        self.base_url = mercadopago_settings.get('PAYOUT_BASE_URL', 'https://api.mercadopago.com')

    def processar_pagamento(self, payment: Payment):
        """
        Processa o repasse do pagamento.
        Retorna tuple (success: bool, message: str | None)
        """
        if payment.payout_status != 'ready':
            return False, 'Pagamento ainda não está pronto para transferência.'

        prestador = payment.prestador
        possui_pix = (
            prestador.preferred_payout_method == 'pix'
            and bool(prestador.pix_key)
            and bool(prestador.pix_key_type)
        )
        possui_conta = (
            prestador.preferred_payout_method == 'bank_transfer'
            and all([
                prestador.payout_bank_code,
                prestador.payout_bank_branch,
                prestador.payout_bank_account,
                prestador.payout_bank_account_type,
                prestador.payout_account_holder_name,
                prestador.payout_account_holder_document,
            ])
        )

        if not (possui_pix or possui_conta):
            payment.payout_status = 'awaiting_info'
            payment.payout_last_error = 'Dados de recebimento ausentes ou incompletos.'
            payment.payout_amount = None
            payment.save(update_fields=['payout_status', 'payout_last_error', 'payout_amount', 'data_atualizacao'])
            return False, payment.payout_last_error

        payment.payout_attempts += 1
        payment.payout_status = 'in_progress'
        payment.save(update_fields=['payout_attempts', 'payout_status', 'data_atualizacao'])

        if self.fake_mode:
            transaction_id = f'FAKE-PAYOUT-{uuid.uuid4()}'
            payment.payout_status = 'completed'
            payment.payout_transaction_id = transaction_id
            payment.payout_completed_at = timezone.now()
            payment.payout_last_error = ''
            payment.save(update_fields=[
                'payout_status',
                'payout_transaction_id',
                'payout_completed_at',
                'payout_last_error',
                'data_atualizacao',
            ])
            return True, None

        try:
            if possui_pix:
                transaction_id = self._transferir_pix(payment)
            else:
                transaction_id = self._transferir_bancario(payment)
        except PayoutError as exc:
            logger.exception('Falha ao processar payout %s', payment.id)
            payment.payout_status = 'failed'
            payment.payout_last_error = str(exc)
            payment.save(update_fields=['payout_status', 'payout_last_error', 'data_atualizacao'])
            return False, str(exc)

        payment.payout_status = 'completed'
        payment.payout_transaction_id = transaction_id
        payment.payout_completed_at = timezone.now()
        payment.payout_last_error = ''
        payment.save(update_fields=[
            'payout_status',
            'payout_transaction_id',
            'payout_completed_at',
            'payout_last_error',
            'data_atualizacao',
        ])
        return True, None

    # ------------------------------------------------------------------
    # Métodos privados
    # ------------------------------------------------------------------
    def _headers(self):
        if not self.access_token:
            raise PayoutError('ACCESS_TOKEN do Mercado Pago não configurado.')
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
        }

    def _transferir_pix(self, payment: Payment) -> str:
        prestador = payment.prestador
        payload = {
            "amount": float(Decimal(payment.valor_prestador)),
            "currency_id": "BRL",
            "description": f"Repasse GradFund - Serviço {payment.servico.titulo}",
            "external_reference": str(payment.id),
            "metadata": {
                "payment_id": str(payment.id),
                "service_id": str(payment.servico.id),
            },
            "payment_method": {
                "type": "pix",
                "pix": {
                    "key": prestador.pix_key,
                    "key_type": prestador.pix_key_type,
                },
            },
        }
        if self.collector_id:
            payload["source"] = {"id": self.collector_id}

        url = f"{self.base_url.rstrip('/')}/v1/transfers"
        response = requests.post(url, json=payload, headers=self._headers(), timeout=30)
        if response.status_code not in (200, 201):
            raise PayoutError(
                f"Erro na transferência PIX (status {response.status_code}): {response.text}"
            )
        data = response.json()
        transaction_id = str(data.get('id') or data.get('transfer_id') or uuid.uuid4())
        return transaction_id

    def _transferir_bancario(self, payment: Payment) -> str:
        prestador = payment.prestador
        identificacao_tipo = 'CPF' if len(prestador.payout_account_holder_document or '') <= 11 else 'CNPJ'
        payload = {
            "amount": float(Decimal(payment.valor_prestador)),
            "currency_id": "BRL",
            "description": f"Repasse GradFund - Serviço {payment.servico.titulo}",
            "external_reference": str(payment.id),
            "metadata": {
                "payment_id": str(payment.id),
                "service_id": str(payment.servico.id),
            },
            "payment_method": {
                "type": "bank_transfer",
                "bank_transfer": {
                    "bank_code": prestador.payout_bank_code,
                    "branch_number": prestador.payout_bank_branch,
                    "account_number": prestador.payout_bank_account,
                    "account_type": prestador.payout_bank_account_type,
                    "holder_name": prestador.payout_account_holder_name,
                    "holder_document": {
                        "type": identificacao_tipo,
                        "number": prestador.payout_account_holder_document,
                    },
                },
            },
        }
        if self.collector_id:
            payload["source"] = {"id": self.collector_id}

        url = f"{self.base_url.rstrip('/')}/v1/transfers"
        response = requests.post(url, json=payload, headers=self._headers(), timeout=30)
        if response.status_code not in (200, 201):
            raise PayoutError(
                f"Erro na transferência bancária (status {response.status_code}): {response.text}"
            )
        data = response.json()
        transaction_id = str(data.get('id') or data.get('transfer_id') or uuid.uuid4())
        return transaction_id
