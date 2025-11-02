from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import Mock, patch
from decimal import Decimal
from apps.payments.services.mercadopago_service import MercadoPagoService
from apps.payments.services.payment_service import PaymentService
from apps.payments.models import Payment, PaymentWebhook
from apps.authentication.models import CustomerUser
from apps.services.models import Service, TypeService
from apps.academic.models import Universidade, Curso


class MercadoPagoServiceTest(TestCase):
    def setUp(self):
        self.mp_service = MercadoPagoService()
    
    def test_calcular_split_pagamento(self):
        """Testa cálculo de split do pagamento"""
        valor_total = Decimal('100.00')
        result = self.mp_service.calcular_split_pagamento(valor_total)
        
        self.assertEqual(result['valor_total'], Decimal('100.00'))
        self.assertEqual(result['comissao_plataforma'], Decimal('7.00'))
        self.assertEqual(result['valor_universitario'], Decimal('93.00'))
    
    @patch.object(MercadoPagoService, '__init__', lambda x: None)
    @patch('mercadopago.SDK')
    def test_criar_preferencia(self, mock_sdk):
        """Testa criação de preferência no Mercado Pago"""
        # Mock da resposta do SDK
        mock_preference = Mock()
        mock_preference.create.return_value = {
            'status': 201,
            'response': {
                'id': 'pref_123',
                'init_point': 'https://mercadopago.com/checkout',
                'sandbox_init_point': 'https://sandbox.mercadopago.com/checkout'
            }
        }
        mock_sdk_instance = Mock()
        mock_sdk_instance.preference.return_value = mock_preference
        mock_sdk.return_value = mock_sdk_instance
        
        # Criar instância manualmente
        mp_service = MercadoPagoService.__new__(MercadoPagoService)
        mp_service.sdk = mock_sdk_instance
        
        payment_data = {
            'payment_id': 'payment_123',
            'titulo': 'Aula de Python',
            'valor_total': Decimal('50.00'),
            'contratante_nome': 'João Silva',
            'contratante_email': 'joao@test.com'
        }
        
        result = mp_service.criar_preferencia(payment_data)
        
        self.assertEqual(result['status'], 201)
        self.assertIn('response', result)
        mock_preference.create.assert_called_once()
    
    @patch.object(MercadoPagoService, '__init__', lambda x: None)
    @patch('mercadopago.SDK')
    def test_consultar_pagamento(self, mock_sdk):
        """Testa consulta de pagamento no Mercado Pago"""
        mock_payment = Mock()
        mock_payment.get.return_value = {
            'status': 200,
            'response': {
                'id': '123',
                'status': 'approved',
                'external_reference': 'payment_123'
            }
        }
        mock_sdk_instance = Mock()
        mock_sdk_instance.payment.return_value = mock_payment
        mock_sdk.return_value = mock_sdk_instance
        
        # Criar instância manualmente
        mp_service = MercadoPagoService.__new__(MercadoPagoService)
        mp_service.sdk = mock_sdk_instance
        
        result = mp_service.consultar_pagamento('123')
        
        self.assertEqual(result['status'], 200)
        mock_payment.get.assert_called_once_with('123')


class PaymentServiceTest(TestCase):
    def setUp(self):
        # Setup completo
        self.universidade = Universidade.objects.create(nome="UFSC")
        self.curso = Curso.objects.create(nome="Ciência da Computação")
        
        self.user_universitario = User.objects.create_user(
            username="estudante", email="estudante@test.com"
        )
        self.user_publico = User.objects.create_user(
            username="publico", email="publico@test.com"
        )
        
        self.universitario = CustomerUser.objects.create(
            usuario=self.user_universitario,
            tipo_usuario="universitario",
            universidade=self.universidade,
            curso=self.curso
        )
        self.publico_externo = CustomerUser.objects.create(
            usuario=self.user_publico,
            tipo_usuario="publico_externo"
        )
        
        self.tipo_servico = TypeService.objects.create(nome="Aulas")
        self.servico = Service.objects.create(
            estudante=self.universitario,
            titulo="Aula de Python",
            descricao="Aula particular",
            tipo_servico=self.tipo_servico,
            preco=5000,
            ativo=True
        )
        
        self.payment_service = PaymentService()
    
    def test_criar_pagamento_sucesso(self):
        """Testa criação de pagamento com sucesso"""
        with patch.object(self.payment_service.mp_service, 'criar_preferencia') as mock_criar_pref:
            mock_criar_pref.return_value = {
                'status': 201,
                'response': {
                    'id': 'pref_123',
                    'init_point': 'https://mercadopago.com/checkout',
                    'sandbox_init_point': 'https://sandbox.mercadopago.com/checkout'
                }
            }
            
            result = self.payment_service.criar_pagamento(
                contratante=self.publico_externo,
                servico_id=self.servico.id
            )
            
            self.assertIn('payment_id', result)
            self.assertIn('checkout_url', result)
            self.assertEqual(result['valor_total'], Decimal('50.00'))
            
            # Verificar se pagamento foi criado no banco
            payment = Payment.objects.get(id=result['payment_id'])
            self.assertEqual(payment.contratante, self.publico_externo)
            self.assertEqual(payment.prestador, self.universitario)
            self.assertEqual(payment.servico, self.servico)
    
    def test_criar_pagamento_servico_inexistente(self):
        """Testa erro ao tentar pagar serviço inexistente"""
        import uuid
        fake_id = uuid.uuid4()
        
        with self.assertRaises(ValueError) as context:
            self.payment_service.criar_pagamento(
                contratante=self.publico_externo,
                servico_id=fake_id
            )
        
        self.assertIn("Serviço não encontrado", str(context.exception))
    
    def test_criar_pagamento_tipo_usuario_invalido(self):
        """Testa erro quando universitário tenta contratar"""
        with self.assertRaises(ValueError) as context:
            self.payment_service.criar_pagamento(
                contratante=self.universitario,
                servico_id=self.servico.id
            )
        
        self.assertIn("público externo", str(context.exception))
    
    def test_criar_pagamento_proprio_servico(self):
        """Testa erro ao tentar contratar próprio serviço"""
        with self.assertRaises(ValueError) as context:
            self.payment_service.criar_pagamento(
                contratante=self.universitario,  # Mesmo usuário que criou o serviço
                servico_id=self.servico.id
            )
        
        # Pode dar erro de tipo de usuário ou próprio serviço
        error_msg = str(context.exception)
        self.assertTrue(
            "próprio serviço" in error_msg or "público externo" in error_msg
        )
    
    def test_cancelar_pagamentos_pendentes_anteriores(self):
        """Testa cancelamento de pagamentos pendentes anteriores"""
        # Criar pagamento pendente anterior
        payment_anterior = Payment.objects.create(
            contratante=self.publico_externo,
            prestador=self.universitario,
            servico=self.servico,
            valor_total=Decimal('50.00'),
            status='pending'
        )
        
        with patch.object(self.payment_service.mp_service, 'criar_preferencia') as mock_criar_pref:
            mock_criar_pref.return_value = {
                'status': 201,
                'response': {
                    'id': 'pref_123',
                    'init_point': 'https://mercadopago.com/checkout',
                    'sandbox_init_point': 'https://sandbox.mercadopago.com/checkout'
                }
            }
            
            self.payment_service.criar_pagamento(
                contratante=self.publico_externo,
                servico_id=self.servico.id
            )
        
        # Verificar se pagamento anterior foi cancelado
        payment_anterior.refresh_from_db()
        self.assertEqual(payment_anterior.status, 'cancelled')
    
    def test_processar_webhook_payment(self):
        """Testa processamento de webhook de pagamento"""
        # Criar pagamento
        payment = Payment.objects.create(
            contratante=self.publico_externo,
            prestador=self.universitario,
            servico=self.servico,
            valor_total=Decimal('50.00')
        )
        
        webhook_data = {
            'type': 'payment',
            'data': {'id': '123'}
        }
        
        with patch.object(self.payment_service.mp_service, 'consultar_pagamento') as mock_consulta:
            mock_consulta.return_value = {
                'status': 200,
                'response': {
                    'id': '123',
                    'status': 'approved',
                    'external_reference': str(payment.id),
                    'payment_method_id': 'pix'
                }
            }
            
            webhook = self.payment_service.processar_webhook(webhook_data)
            
            self.assertTrue(webhook.processado)
            self.assertEqual(webhook.evento_tipo, 'payment')
            
            # Verificar se pagamento foi atualizado
            payment.refresh_from_db()
            self.assertEqual(payment.status, 'approved')
            self.assertEqual(payment.mercadopago_payment_id, '123')
            self.assertEqual(payment.metodo_pagamento, 'pix')
    
    def test_processar_webhook_tipo_desconhecido(self):
        """Testa processamento de webhook de tipo desconhecido"""
        webhook_data = {
            'type': 'unknown',
            'data': {'id': '123'}
        }
        
        webhook = self.payment_service.processar_webhook(webhook_data)
        
        self.assertFalse(webhook.processado)
        self.assertEqual(webhook.evento_tipo, 'unknown')