from django.utils import timezone
from django.db import transaction
from django.conf import settings
from django.core.mail import send_mail
from apps.payments.models import Payment, PaymentWebhook
from apps.payments.services.mercadopago_service import MercadoPagoService
from apps.services.models import Service
from apps.authentication.models import CustomerUser
import logging

logger = logging.getLogger(__name__)


class PaymentService:
    def __init__(self):
        self.mp_service = MercadoPagoService()
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@gradfund.local')
    
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

        # Calcular split do pagamento (7% plataforma, 93% prestador)
        split = self.mp_service.calcular_split_pagamento(payment.valor_total)
        payment.valor_plataforma = split['comissao_plataforma']
        payment.valor_prestador = split['valor_universitario']
        payment.payout_amount = split['valor_universitario']
        payment.payout_status = 'ready'  # Pronto para split automático via application_fee
        payment.save(update_fields=['valor_plataforma', 'valor_prestador', 'payout_amount', 'payout_status'])
        
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        
        # Verificar se universitário tem conta MP conectada
        if not servico.estudante.mp_access_token:
            raise ValueError("Universitário precisa conectar conta do Mercado Pago primeiro.")
        
        # Verificar se token ainda é válido (pode ter expirado)
        try:
            # Testar token fazendo uma consulta simples
            mp_service_test = MercadoPagoService(servico.estudante.mp_access_token)
            test_response = mp_service_test.sdk.payment_methods().list_all()
            if test_response.get('status') != 200:
                raise ValueError("Token do Mercado Pago expirado. Universitário precisa reconectar conta")
        except Exception as e:
            logger.warning(f"Token MP inválido para usuário {servico.estudante.id}: {str(e)}")
            raise ValueError("Token do Mercado Pago inválido. Universitário precisa reconectar conta")
        
        # IMPORTANTE: Criar preferência usando token do PRESTADOR (universitário)
        # O application_fee será deduzido automaticamente e enviado para a conta da plataforma
        # O restante (93%) vai automaticamente para a conta do prestador
        payment_data = {
            'payment_id': payment.id,
            'titulo': servico.titulo,
            'valor_total': payment.valor_total,
            'contratante_nome': contratante.usuario.get_full_name() or contratante.usuario.username,
            'contratante_email': contratante.usuario.email,
            'webhook_url': f'{settings.BASE_URL}/api/v1/payments/webhook/',
            'success_url': f'{frontend_url}/pagamentos/sucesso',
            'failure_url': f'{frontend_url}/pagamentos/erro',
            'pending_url': f'{frontend_url}/pagamentos/pendente',
            'comissao_plataforma': split['comissao_plataforma'],  # 7% para plataforma (application_fee)
        }
        
        try:
            # Usar access token do universitário para criar preferência
            mp_service_universitario = MercadoPagoService(servico.estudante.mp_access_token)
            mp_response = mp_service_universitario.criar_preferencia(payment_data)
            
            if mp_response.get('status') == 201:
                preference = mp_response['response']
                payment.mercadopago_preference_id = preference['id']
                payment.save(update_fields=['mercadopago_preference_id'])
                
                logger.info(f"Preferência criada com sucesso: {preference['id']} para payment: {payment.id}")
                
                return {
                    'payment_id': payment.id,
                    'preference_id': preference['id'],
                    'checkout_url': preference['init_point'],
                    'sandbox_checkout_url': preference['sandbox_init_point'],
                    'valor_total': payment.valor_total,
                    'valor_plataforma': payment.valor_plataforma,
                    'valor_prestador': payment.valor_prestador,
                    'payout_status': payment.payout_status,
                    'qr_code': preference.get('qr_code', ''),
                }
            else:
                payment.status = 'rejected'
                payment.save(update_fields=['status'])
                error_msg = f"Erro ao criar preferência no Mercado Pago. Status: {mp_response.get('status')}"
                logger.error(f"{error_msg}, Response: {mp_response}")
                raise Exception(error_msg)
                
        except Exception as e:
            payment.status = 'rejected'
            payment.save(update_fields=['status'])
            logger.error(f"Erro ao criar pagamento {payment.id}: {str(e)}")
            raise
    
    @transaction.atomic
    def processar_webhook(self, webhook_data):
        """Processa webhook do Mercado Pago"""
        # Salvar webhook
        webhook = PaymentWebhook.objects.create(
            webhook_data=webhook_data,
            evento_tipo=webhook_data.get('type', 'unknown')
        )
        
        event_type = webhook_data.get('type')
        logger.info(f"Processando webhook tipo: {event_type}")
        
        # Processar eventos de pagamento
        if event_type == 'payment':
            payment_id = webhook_data.get('data', {}).get('id')
            
            if payment_id:
                logger.info(f"Consultando pagamento MP: {payment_id}")
                
                # Usar token da plataforma para consultar webhook
                mp_service = MercadoPagoService()
                mp_response = mp_service.consultar_pagamento(payment_id)
                
                if mp_response['status'] == 200:
                    payment_info = mp_response['response']
                    external_reference = payment_info.get('external_reference')
                    
                    logger.info(f"Pagamento MP consultado - Status: {payment_info.get('status')}, External Ref: {external_reference}")
                    
                    if external_reference:
                        try:
                            payment = Payment.objects.get(id=external_reference)
                            webhook.payment = payment
                            
                            # Atualizar status do pagamento
                            old_status = payment.status
                            new_status = payment_info.get('status', 'pending')
                            
                            payment.mercadopago_payment_id = payment_id
                            payment.status = new_status
                            payment.metodo_pagamento = payment_info.get('payment_method_id', '')
                            
                            logger.info(f"Atualizando payment {payment.id}: {old_status} -> {new_status}")
                            
                            # Processar diferentes status
                            if new_status == 'approved' and old_status != 'approved':
                                payment.data_aprovacao = timezone.now()
                                logger.info(f"Pagamento {payment.id} aprovado - iniciando split")
                                self._processar_pagamento_aprovado(payment)
                                
                            elif new_status == 'rejected':
                                logger.info(f"Pagamento {payment.id} rejeitado")
                                self._processar_pagamento_rejeitado(payment)
                                
                            elif new_status == 'cancelled':
                                logger.info(f"Pagamento {payment.id} cancelado")
                                self._processar_pagamento_cancelado(payment)
                                
                            elif new_status in ['pending', 'in_process']:
                                logger.info(f"Pagamento {payment.id} pendente")
                                self._processar_pagamento_pendente(payment)
                            
                            payment.save()
                            webhook.processado = True
                            
                            logger.info(f"Payment {payment.id} atualizado com sucesso")
                            
                        except Payment.DoesNotExist:
                            logger.warning(f"Payment não encontrado para external_reference: {external_reference}")
                else:
                    logger.error(f"Erro ao consultar pagamento MP {payment_id}: {mp_response}")
        
        elif event_type in ['merchant_order', 'plan', 'subscription']:
            logger.info(f"Evento {event_type} recebido mas não processado")
        
        else:
            logger.warning(f"Tipo de evento desconhecido: {event_type}")
        
        webhook.save()
        return webhook

    def _processar_pagamento_aprovado(self, payment: Payment):
        """Processa pagamento aprovado - split automático via marketplace_fee"""
        logger.info(f"Pagamento {payment.id} aprovado - split automático via marketplace_fee")
        
        # O split foi processado automaticamente pelo Mercado Pago usando marketplace_fee:
        # - marketplace_fee (7%) foi para a conta da plataforma automaticamente
        # - valor_total - marketplace_fee (93%) ficou na conta do universitário automaticamente
        
        # Validar e registrar os valores para controle interno
        from apps.payments.services.split_service import SplitService
        split_service = SplitService()
        split = split_service.calcular_split(payment.valor_total)
        
        payment.valor_plataforma = split['valor_plataforma']
        payment.valor_prestador = split['valor_universitario']
        payment.payout_status = 'completed'  # Split automático já foi feito pelo MP
        payment.payout_amount = split['valor_universitario']
        
        logger.info(f"Split automático confirmado: Plataforma R${payment.valor_plataforma} (7%), Universitário R${payment.valor_prestador} (93%)")
        logger.info("Dinheiro já foi dividido automaticamente pelo Mercado Pago via marketplace_fee")
    
    def _processar_pagamento_rejeitado(self, payment: Payment):
        """Processa pagamento rejeitado"""
        logger.info(f"Pagamento rejeitado: {payment.id}")
        # Notificar contratante sobre rejeição se necessário
        
    def _processar_pagamento_cancelado(self, payment: Payment):
        """Processa pagamento cancelado"""
        logger.info(f"Pagamento cancelado: {payment.id}")
        # Notificar partes sobre cancelamento se necessário
        
    def _processar_pagamento_pendente(self, payment: Payment):
        """Processa pagamento pendente"""
        logger.info(f"Pagamento pendente: {payment.id}")
        # Notificar sobre status pendente se necessário