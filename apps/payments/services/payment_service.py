from django.utils import timezone
from django.db import transaction
from apps.payments.models import Payment, PaymentWebhook
from apps.payments.services.mercadopago_service import MercadoPagoService
from apps.services.models import Service
from apps.authentication.models import CustomerUser


class PaymentService:
    def __init__(self):
        self.mp_service = MercadoPagoService()
    
    @transaction.atomic
    def criar_pagamento(self, contratante, servico_id):
        """Cria um novo pagamento"""
        # Validações
        try:
            servico = Service.objects.get(id=servico_id, ativo=True)
        except Service.DoesNotExist:
            raise ValueError("Serviço não encontrado ou inativo")
        
        if contratante.tipo_usuario != 'publico_externo':
            raise ValueError("Apenas usuários do tipo público externo podem contratar serviços")
        
        if servico.estudante.tipo_usuario != 'universitario':
            raise ValueError("Apenas universitários podem oferecer serviços")
        
        if contratante == servico.estudante:
            raise ValueError("Não é possível contratar o próprio serviço")
        
        # Cancelar pagamentos pendentes anteriores do mesmo usuário para o mesmo serviço
        Payment.objects.filter(
            contratante=contratante,
            servico=servico,
            status='pending'
        ).update(status='cancelled')
        
        # Criar pagamento
        payment = Payment.objects.create(
            contratante=contratante,
            prestador=servico.estudante,
            servico=servico,
            valor_total=servico.preco / 100  # Converter centavos para reais
        )
        
        # Verificar se universitário tem token MP
        if not servico.estudante.mp_access_token:
            raise ValueError("Universitário precisa conectar conta do Mercado Pago primeiro")
        
        # Usar token do universitário para criar preferência
        mp_service = MercadoPagoService(servico.estudante.mp_access_token)
        
        # Criar preferência no Mercado Pago
        payment_data = {
            'payment_id': payment.id,
            'titulo': servico.titulo,
            'valor_total': payment.valor_total,
            'contratante_nome': contratante.usuario.get_full_name() or contratante.usuario.username,
            'contratante_email': contratante.usuario.email,
            'webhook_url': f'/api/v1/payments/webhook/',
        }
        
        mp_response = mp_service.criar_preferencia(payment_data)
        
        if mp_response['status'] == 201:
            preference = mp_response['response']
            payment.mercadopago_preference_id = preference['id']
            payment.save()
            
            return {
                'payment_id': payment.id,
                'checkout_url': preference['init_point'],
                'sandbox_checkout_url': preference['sandbox_init_point'],
                'valor_total': payment.valor_total,
                'qr_code': preference.get('qr_code', ''),
            }
        else:
            payment.status = 'rejected'
            payment.save()
            raise Exception("Erro ao criar preferência no Mercado Pago")
    
    @transaction.atomic
    def processar_webhook(self, webhook_data):
        """Processa webhook do Mercado Pago"""
        # Salvar webhook
        webhook = PaymentWebhook.objects.create(
            webhook_data=webhook_data,
            evento_tipo=webhook_data.get('type', 'unknown')
        )
        
        # Processar apenas eventos de pagamento
        if webhook_data.get('type') == 'payment':
            payment_id = webhook_data.get('data', {}).get('id')
            
            if payment_id:
                # Consultar pagamento no Mercado Pago
                mp_response = self.mp_service.consultar_pagamento(payment_id)
                
                if mp_response['status'] == 200:
                    payment_info = mp_response['response']
                    external_reference = payment_info.get('external_reference')
                    
                    if external_reference:
                        try:
                            payment = Payment.objects.get(id=external_reference)
                            webhook.payment = payment
                            
                            # Atualizar status do pagamento
                            old_status = payment.status
                            payment.mercadopago_payment_id = payment_id
                            payment.status = payment_info.get('status', 'pending')
                            payment.metodo_pagamento = payment_info.get('payment_method_id', '')
                            
                            if payment.status == 'approved' and old_status != 'approved':
                                payment.data_aprovacao = timezone.now()
                            
                            payment.save()
                            webhook.processado = True
                            
                        except Payment.DoesNotExist:
                            pass
        
        webhook.save()
        return webhook