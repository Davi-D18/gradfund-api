from django.utils import timezone
from django.db import transaction
from django.conf import settings
from django.core.mail import send_mail
from apps.payments.models import Payment, PaymentWebhook
from apps.payments.services.mercadopago_service import MercadoPagoService
from apps.payments.services.payout_service import PayoutService
from apps.services.models import Service
from apps.authentication.models import CustomerUser


class PaymentService:
    def __init__(self):
        self.mp_service = MercadoPagoService()
        self.payout_service = PayoutService()
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

        split = self.mp_service.calcular_split_pagamento(payment.valor_total)
        payment.valor_plataforma = split['comissao_plataforma']
        payment.valor_prestador = split['valor_universitario']
        payment.payout_amount = split['valor_universitario']
        payment.payout_status = 'awaiting_info'
        payment.save(update_fields=['valor_plataforma', 'valor_prestador', 'payout_amount', 'payout_status'])
        
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        # Criar preferência no Mercado Pago
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
            'comissao_plataforma': split['comissao_plataforma'],
        }
        
        mp_response = self.mp_service.criar_preferencia(payment_data)
        
        if mp_response.get('status') == 201:
            preference = mp_response['response']
            payment.mercadopago_preference_id = preference['id']
            payment.save(update_fields=['mercadopago_preference_id'])
            
            return {
                'payment_id': payment.id,
                'preference_id': preference['id'],  # Para checkout embutido
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
            raise Exception(f"Erro ao criar preferência no Mercado Pago. Status: {mp_response.get('status')}, Response: {mp_response}")
    
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
                # Usar token da plataforma para consultar webhook
                mp_service = MercadoPagoService()  # Token da plataforma
                mp_response = mp_service.consultar_pagamento(payment_id)
                
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
                            
                            should_process_payout = False

                            if payment.status == 'approved' and old_status != 'approved':
                                payment.data_aprovacao = timezone.now()
                                self._atualizar_status_payout(payment)
                                should_process_payout = payment.payout_status == 'ready'
                            
                            payment.save()

                            if should_process_payout:
                                self._processar_payout(payment)

                            webhook.processado = True
                            
                        except Payment.DoesNotExist:
                            pass
        
        webhook.save()
        return webhook

    def _processar_payout(self, payment: Payment):
        success, message = self.payout_service.processar_pagamento(payment)
        payment.refresh_from_db()
        if success:
            if payment.payout_failed_notified:
                payment.payout_failed_notified = False
                payment.save(update_fields=['payout_failed_notified', 'data_atualizacao'])
        else:
            if payment.payout_status == 'failed' and not payment.payout_failed_notified:
                self._notificar_prestador_falha_payout(payment, message)
                payment.payout_failed_notified = True
                payment.save(update_fields=['payout_failed_notified', 'data_atualizacao'])
            if not message:
                message = 'Falha ao processar repasse. Verifique os logs.'
            payment.observacoes = (payment.observacoes or '') + f"\n[PAYOUT] {message}"
            payment.save(update_fields=['observacoes', 'data_atualizacao'])

    def _atualizar_status_payout(self, payment: Payment):
        """Define o status de payout com base nos dados do prestador."""
        prestador: CustomerUser = payment.prestador
        if payment.payout_status == 'completed':
            return  # nada a fazer
        
        possui_pix = prestador.preferred_payout_method == 'pix' and bool(prestador.pix_key)
        possui_conta = (
            prestador.preferred_payout_method == 'bank_transfer' and
            all([
                prestador.payout_bank_code,
                prestador.payout_bank_branch,
                prestador.payout_bank_account,
                prestador.payout_account_holder_name,
                prestador.payout_account_holder_document,
            ])
        )
        
        if possui_pix or possui_conta:
            status_changed = payment.payout_status != 'ready'
            if status_changed:
                payment.payout_requested_at = timezone.now()
                payment.payout_missing_info_notified = False
            payment.payout_status = 'ready'
            payment.payout_amount = payment.valor_prestador
            payment.payout_last_error = ''
        else:
            status_changed = payment.payout_status != 'awaiting_info'
            payment.payout_status = 'awaiting_info'
            payment.payout_amount = None
            payment.payout_last_error = (
                'Prestador ainda não cadastrou os dados de recebimento. '
                'Solicite a atualização do perfil.'
            )
            if status_changed or not payment.payout_missing_info_notified:
                self._notificar_prestador_dados_faltando(payment)
                payment.payout_missing_info_notified = True

        payment.save(update_fields=[
            'payout_status',
            'payout_amount',
            'payout_last_error',
            'payout_requested_at',
            'payout_missing_info_notified',
            'data_atualizacao',
        ])

    def _notificar_prestador_dados_faltando(self, payment: Payment):
        prestador = payment.prestador
        email = prestador.usuario.email
        if not email:
            return
        assunto = 'GradFund - Complete seus dados para receber pagamentos'
        url_config = f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/configuracoes/pagamentos"
        mensagem = (
            f"Olá {prestador.usuario.username},\n\n"
            "Você recebeu uma venda, mas ainda não cadastrou os dados de recebimento (PIX ou conta bancária).\n"
            f"Acesse: {url_config} para completar as informações e receber seus repasses.\n\n"
            "Equipe GradFund"
        )
        send_mail(assunto, mensagem, self.from_email, [email], fail_silently=True)

    def _notificar_prestador_falha_payout(self, payment: Payment, detalhe: str | None):
        prestador = payment.prestador
        email = prestador.usuario.email
        if not email:
            return
        assunto = 'GradFund - Falha ao transferir seu pagamento'
        detalhe = detalhe or 'O repasse automático não pôde ser concluído.'
        mensagem = (
            f"Olá {prestador.usuario.username},\n\n"
            "Tentamos transferir um pagamento para a sua conta, mas houve uma falha.\n"
            f"Detalhes: {detalhe}\n\n"
            "Atualize ou verifique seus dados em Configurações > Pagamentos para tentar novamente.\n\n"
            "Equipe GradFund"
        )
        send_mail(assunto, mensagem, self.from_email, [email], fail_silently=True)