from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch, Mock
from decimal import Decimal
from apps.payments.models import Payment, PaymentWebhook
from apps.authentication.models import CustomerUser
from apps.services.models import Service, TypeService
from apps.academic.models import Universidade, Curso


class PaymentViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Setup completo
        self.universidade = Universidade.objects.create(nome="UFSC")
        self.curso = Curso.objects.create(nome="Ciência da Computação")
        
        # Usuários
        self.user_universitario = User.objects.create_user(
            username="estudante", email="estudante@test.com", password="test123"
        )
        self.user_publico = User.objects.create_user(
            username="publico", email="publico@test.com", password="test123"
        )
        
        # Perfis
        self.universitario = CustomerUser.objects.create(
            usuario=self.user_universitario,
            tipo_usuario="universitario",
            universidade=self.universidade,
            curso=self.curso,
            mp_access_token="TEST-123456789"
        )
        self.publico_externo = CustomerUser.objects.create(
            usuario=self.user_publico,
            tipo_usuario="publico_externo"
        )
        
        # Serviço
        self.tipo_servico = TypeService.objects.create(nome="Aulas")
        self.servico = Service.objects.create(
            estudante=self.universitario,
            titulo="Aula de Python",
            descricao="Aula particular",
            tipo_servico=self.tipo_servico,
            preco=5000,
            ativo=True
        )
        
        # Pagamento
        self.payment = Payment.objects.create(
            contratante=self.publico_externo,
            prestador=self.universitario,
            servico=self.servico,
            valor_total=Decimal('50.00')
        )
    
    def get_jwt_token(self, user):
        """Helper para obter token JWT"""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    
    def authenticate_user(self, user):
        """Helper para autenticar usuário"""
        token = self.get_jwt_token(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    
    @patch('apps.payments.services.payment_service.PaymentService.criar_pagamento')
    def test_create_payment_success(self, mock_criar_pagamento):
        """Testa criação de pagamento com sucesso"""
        self.authenticate_user(self.user_publico)
        
        mock_criar_pagamento.return_value = {
            'payment_id': 'test-id',
            'checkout_url': 'https://mercadopago.com/checkout',
            'valor_total': Decimal('50.00')
        }
        
        data = {'servico_id': str(self.servico.id)}
        response = self.client.post('/api/v1/payments/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('payment_id', response.data)
        self.assertIn('checkout_url', response.data)
    
    def test_create_payment_unauthorized(self):
        """Testa criação de pagamento sem autenticação"""
        data = {'servico_id': str(self.servico.id)}
        response = self.client.post('/api/v1/payments/', data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_payment_wrong_user_type(self):
        """Testa criação de pagamento com tipo de usuário errado"""
        self.authenticate_user(self.user_universitario)
        
        data = {'servico_id': str(self.servico.id)}
        response = self.client.post('/api/v1/payments/', data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_payment_invalid_service(self):
        """Testa criação de pagamento com serviço inválido"""
        self.authenticate_user(self.user_publico)
        
        data = {'servico_id': 'invalid-uuid'}
        response = self.client.post('/api/v1/payments/', data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('apps.payments.services.payment_service.PaymentService.criar_pagamento')
    def test_create_payment_service_error(self, mock_criar_pagamento):
        """Testa erro no serviço de pagamento"""
        self.authenticate_user(self.user_publico)
        
        mock_criar_pagamento.side_effect = ValueError("Serviço não encontrado")
        
        data = {'servico_id': str(self.servico.id)}
        response = self.client.post('/api/v1/payments/', data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_list_payments_as_contratante(self):
        """Testa listagem de pagamentos como contratante"""
        self.authenticate_user(self.user_publico)
        
        response = self.client.get('/api/v1/payments/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], str(self.payment.id))
    
    def test_list_payments_as_prestador(self):
        """Testa listagem de pagamentos como prestador"""
        self.authenticate_user(self.user_universitario)
        
        response = self.client.get('/api/v1/payments/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_retrieve_payment_as_participant(self):
        """Testa detalhes de pagamento como participante"""
        self.authenticate_user(self.user_publico)
        
        response = self.client.get(f'/api/v1/payments/{self.payment.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.payment.id))
    
    def test_retrieve_payment_as_non_participant(self):
        """Testa acesso negado para não participante"""
        # Criar outro usuário
        other_user = User.objects.create_user(username="other", email="other@test.com")
        CustomerUser.objects.create(usuario=other_user, tipo_usuario="publico_externo")
        
        self.authenticate_user(other_user)
        
        response = self.client.get(f'/api/v1/payments/{self.payment.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_meus_pagamentos_action(self):
        """Testa action meus_pagamentos"""
        self.authenticate_user(self.user_publico)
        
        response = self.client.get('/api/v1/payments/meus_pagamentos/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_meus_recebimentos_action(self):
        """Testa action meus_recebimentos"""
        self.authenticate_user(self.user_universitario)
        
        response = self.client.get('/api/v1/payments/meus_recebimentos/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class WebhookControllerTest(TestCase):
    def setUp(self):
        self.client = APIClient()
    
    @patch('apps.payments.services.payment_service.PaymentService.processar_webhook')
    def test_webhook_success(self, mock_processar_webhook):
        """Testa processamento de webhook com sucesso"""
        mock_webhook = Mock()
        mock_webhook.id = 'webhook-123'
        mock_processar_webhook.return_value = mock_webhook
        
        webhook_data = {
            'type': 'payment',
            'data': {'id': '123'}
        }
        
        response = self.client.post('/api/v1/payments/webhook/', webhook_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertEqual(response.data['status'], 'processed')
        mock_processar_webhook.assert_called_once_with(webhook_data)
    
    @patch('apps.payments.services.payment_service.PaymentService.processar_webhook')
    def test_webhook_error(self, mock_processar_webhook):
        """Testa erro no processamento de webhook"""
        mock_processar_webhook.side_effect = Exception("Erro interno")
        
        webhook_data = {
            'type': 'payment',
            'data': {'id': '123'}
        }
        
        response = self.client.post('/api/v1/payments/webhook/', webhook_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)
    
    def test_webhook_no_auth_required(self):
        """Testa que webhook não requer autenticação"""
        webhook_data = {'type': 'test'}
        
        # Não autenticar o cliente
        response = self.client.post('/api/v1/payments/webhook/', webhook_data)
        
        # Deve processar mesmo sem autenticação (pode dar erro interno, mas não 401)
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)