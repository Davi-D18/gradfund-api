from django.test import TestCase
from django.contrib.auth.models import User, AnonymousUser
from rest_framework.test import APIRequestFactory
from unittest.mock import Mock
from decimal import Decimal
from apps.payments.permissions.payment_permissions import (
    CanCreatePayment,
    IsPaymentParticipant
)
from apps.payments.models import Payment
from apps.authentication.models import CustomerUser
from apps.services.models import Service, TypeService
from apps.academic.models import Universidade, Curso


class CanCreatePaymentTest(TestCase):
    def setUp(self):
        self.permission = CanCreatePayment()
        self.factory = APIRequestFactory()
        
        # Criar usuários
        self.user_publico = User.objects.create_user(
            username="publico", email="publico@test.com"
        )
        self.user_universitario = User.objects.create_user(
            username="estudante", email="estudante@test.com"
        )
        
        # Criar perfis
        self.publico_externo = CustomerUser.objects.create(
            usuario=self.user_publico,
            tipo_usuario="publico_externo"
        )
        self.universitario = CustomerUser.objects.create(
            usuario=self.user_universitario,
            tipo_usuario="universitario",
            mp_access_token="TEST-123456789"
        )
    
    def test_post_permission_publico_externo(self):
        """Testa permissão POST para público externo"""
        request = self.factory.post('/api/v1/payments/')
        request.user = self.user_publico
        
        view = Mock()
        
        self.assertTrue(
            self.permission.has_permission(request, view)
        )
    
    def test_post_permission_universitario(self):
        """Testa negação de permissão POST para universitário"""
        request = self.factory.post('/api/v1/payments/')
        request.user = self.user_universitario
        
        view = Mock()
        
        self.assertFalse(
            self.permission.has_permission(request, view)
        )
    
    def test_post_permission_anonymous(self):
        """Testa negação de permissão POST para usuário anônimo"""
        request = self.factory.post('/api/v1/payments/')
        request.user = AnonymousUser()
        
        view = Mock()
        
        self.assertFalse(
            self.permission.has_permission(request, view)
        )
    
    def test_post_permission_user_without_profile(self):
        """Testa negação de permissão para usuário sem perfil"""
        user_without_profile = User.objects.create_user(
            username="noprofile", email="noprofile@test.com"
        )
        
        request = self.factory.post('/api/v1/payments/')
        request.user = user_without_profile
        
        view = Mock()
        
        self.assertFalse(
            self.permission.has_permission(request, view)
        )
    
    def test_get_permission_authenticated(self):
        """Testa permissão GET para usuário autenticado"""
        request = self.factory.get('/api/v1/payments/')
        request.user = self.user_publico
        
        view = Mock()
        
        self.assertTrue(
            self.permission.has_permission(request, view)
        )
    
    def test_get_permission_anonymous(self):
        """Testa negação de permissão GET para usuário anônimo"""
        request = self.factory.get('/api/v1/payments/')
        request.user = AnonymousUser()
        
        view = Mock()
        
        self.assertFalse(
            self.permission.has_permission(request, view)
        )


class IsPaymentParticipantTest(TestCase):
    def setUp(self):
        self.permission = IsPaymentParticipant()
        self.factory = APIRequestFactory()
        
        # Setup completo
        self.universidade = Universidade.objects.create(nome="UFSC")
        
        # Usuários
        self.user_publico = User.objects.create_user(
            username="publico", email="publico@test.com"
        )
        self.user_universitario = User.objects.create_user(
            username="estudante", email="estudante@test.com"
        )
        self.user_outro = User.objects.create_user(
            username="outro", email="outro@test.com"
        )
        
        # Perfis
        self.publico_externo = CustomerUser.objects.create(
            usuario=self.user_publico,
            tipo_usuario="publico_externo"
        )
        self.universitario = CustomerUser.objects.create(
            usuario=self.user_universitario,
            tipo_usuario="universitario",
            mp_access_token="TEST-123456789"
        )
        self.outro_usuario = CustomerUser.objects.create(
            usuario=self.user_outro,
            tipo_usuario="publico_externo"
        )
        
        # Serviço e pagamento
        self.tipo_servico = TypeService.objects.create(nome="Aulas")
        self.servico = Service.objects.create(
            estudante=self.universitario,
            titulo="Aula de Python",
            descricao="Aula particular",
            tipo_servico=self.tipo_servico,
            preco=5000
        )
        
        self.payment = Payment.objects.create(
            contratante=self.publico_externo,
            prestador=self.universitario,
            servico=self.servico,
            valor_total=Decimal('50.00')
        )
    
    def test_permission_contratante(self):
        """Testa permissão para contratante"""
        request = self.factory.get('/api/v1/payments/1/')
        request.user = self.user_publico
        
        view = Mock()
        
        self.assertTrue(
            self.permission.has_object_permission(request, view, self.payment)
        )
    
    def test_permission_prestador(self):
        """Testa permissão para prestador"""
        request = self.factory.get('/api/v1/payments/1/')
        request.user = self.user_universitario
        
        view = Mock()
        
        self.assertTrue(
            self.permission.has_object_permission(request, view, self.payment)
        )
    
    def test_permission_denied_other_user(self):
        """Testa negação de permissão para outro usuário"""
        request = self.factory.get('/api/v1/payments/1/')
        request.user = self.user_outro
        
        view = Mock()
        
        self.assertFalse(
            self.permission.has_object_permission(request, view, self.payment)
        )
    
    def test_permission_denied_anonymous(self):
        """Testa negação de permissão para usuário anônimo"""
        request = self.factory.get('/api/v1/payments/1/')
        request.user = AnonymousUser()
        
        view = Mock()
        
        self.assertFalse(
            self.permission.has_object_permission(request, view, self.payment)
        )
    
    def test_permission_denied_user_without_profile(self):
        """Testa negação de permissão para usuário sem perfil"""
        user_without_profile = User.objects.create_user(
            username="noprofile", email="noprofile@test.com"
        )
        
        request = self.factory.get('/api/v1/payments/1/')
        request.user = user_without_profile
        
        view = Mock()
        
        self.assertFalse(
            self.permission.has_object_permission(request, view, self.payment)
        )