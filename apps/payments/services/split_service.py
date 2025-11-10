from decimal import Decimal
import logging
from django.conf import settings
from apps.payments.models import Payment

logger = logging.getLogger(__name__)

class SplitService:
    """Serviço para processar split de pagamentos sem marketplace_fee"""
    
    def __init__(self):
        self.commission_rate = getattr(settings, 'GRADFUND_COMMISSION_RATE', 0.07)  # 7%
    
    def calcular_split(self, valor_total):
        """Calcula divisão do pagamento"""
        valor_total = Decimal(str(valor_total))
        valor_plataforma = valor_total * Decimal(str(self.commission_rate))
        valor_universitario = valor_total - valor_plataforma
        
        return {
            'valor_total': valor_total,
            'valor_plataforma': valor_plataforma.quantize(Decimal('0.01')),
            'valor_universitario': valor_universitario.quantize(Decimal('0.01')),
            'percentual_plataforma': self.commission_rate * 100,
            'percentual_universitario': (1 - self.commission_rate) * 100
        }
    
    def processar_split_aprovado(self, payment: Payment):
        """Processa split após pagamento aprovado"""
        logger.info(f"Processando split para pagamento {payment.id}")
        
        split = self.calcular_split(payment.valor_total)
        
        # Atualizar valores no pagamento
        payment.valor_plataforma = split['valor_plataforma']
        payment.valor_prestador = split['valor_universitario']
        payment.payout_amount = split['valor_universitario']
        
        # Adicionar observação sobre o split
        observacao = (
            f"Split processado: "
            f"Plataforma R${split['valor_plataforma']} ({split['percentual_plataforma']:.1f}%), "
            f"Universitário R${split['valor_universitario']} ({split['percentual_universitario']:.1f}%)"
        )
        
        if payment.observacoes:
            payment.observacoes += f"\n{observacao}"
        else:
            payment.observacoes = observacao
        
        payment.save(update_fields=[
            'valor_plataforma', 
            'valor_prestador', 
            'payout_amount', 
            'observacoes',
            'data_atualizacao'
        ])
        
        logger.info(f"Split processado com sucesso para pagamento {payment.id}")
        
        return split
    
    def get_resumo_financeiro(self, payment: Payment):
        """Retorna resumo financeiro do split"""
        return {
            'payment_id': payment.id,
            'valor_total': float(payment.valor_total),
            'valor_plataforma': float(payment.valor_plataforma or 0),
            'valor_universitario': float(payment.valor_prestador or 0),
            'percentual_plataforma': f"{self.commission_rate * 100:.1f}%",
            'percentual_universitario': f"{(1 - self.commission_rate) * 100:.1f}%",
            'status_payout': payment.payout_status,
            'metodo_pagamento': payment.metodo_pagamento,
            'data_aprovacao': payment.data_aprovacao.isoformat() if payment.data_aprovacao else None
        }