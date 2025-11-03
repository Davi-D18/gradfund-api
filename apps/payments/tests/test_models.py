from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from decimal import Decimal
from apps.payments.models import Payment, PaymentWebhook
from apps.authentication.models import CustomerUser
from apps.services.models import Service, TypeService
from apps.academic.models import Universidade, Curso


class PaymentModelTest(TestCase):
    def setUp(self):
        # Criar universidade e curso
        self.universidade = Universidade.objects.create(
            nome="UFSC", sigla="UFSC", cidade="Florianópolis", estado="SC"
        )
        self.curso = Curso.objects.create(nome="Ciência da Computação")
        
        # Criar usuários
        self.user_universitario = User.objects.create_user(
            username="estudante", email="estudante@test.com", password="test123"
        )
        self.user_publico = User.objects.create_user(
            username="publico", email="publico@test.com", password="test123"
        )
        
        # Criar perfis
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
        
        # Criar tipo de serviço
        self.tipo_servico = TypeService.objects.create(nome="Aulas Particulares")
        
        # Criar serviço
        self.servico = Service.objects.create(
            estudante=self.universitario,
            titulo="Aula de Python",
            descricao="Aula particular de Python",
            tipo_servico=self.tipo_servico,
            preco=5000  # R$ 50,00 em centavos
        )
    
    def test_payment_creation(self):
        """Testa criação de pagamento"""
        payment = Payment.objects.create(
            contratante=self.publico_externo,
            prestador=self.universitario,
            servico=self.servico,
            valor_total=Decimal('50.00')
        )
        
        self.assertEqual(payment.contratante, self.publico_externo)
        self.assertEqual(payment.prestador, self.universitario)
        self.assertEqual(payment.servico, self.servico)
        self.assertEqual(payment.valor_total, Decimal('50.00'))
        self.assertEqual(payment.status, 'pending')
    
    def test_payment_str_method(self):
        """Testa método __str__ do Payment"""
        payment = Payment.objects.create(
            contratante=self.publico_externo,
            prestador=self.universitario,
            servico=self.servico,
            valor_total=Decimal('50.00')
        )
        
        expected = f"Pagamento {payment.id} - {self.servico.titulo}"
        self.assertEqual(str(payment), expected)
    
    def test_payment_valor_total_validation(self):
        """Testa validação de valor mínimo"""
        payment = Payment(
            contratante=self.publico_externo,
            prestador=self.universitario,
            servico=self.servico,
            valor_total=Decimal('0.00')
        )
        
        with self.assertRaises(ValidationError):
            payment.full_clean()


class PaymentWebhookModelTest(TestCase):
    def setUp(self):
        # Setup básico igual ao PaymentModelTest
        self.universidade = Universidade.objects.create(nome="UFSC")
        self.curso = Curso.objects.create(nome="Ciência da Computação")
        
        self.user_universitario = User.objects.create_user(
            username="estudante", email="estudante@test.com"
        )
        self.user_publico = User.objects.create_user(
            username="publico", email="publico@test.com"
        )
        
        self.universitario = CustomerUser.objects.create(
            usuario=self.user_universitario, tipo_usuario="universitario"
        )
        self.publico_externo = CustomerUser.objects.create(
            usuario=self.user_publico, tipo_usuario="publico_externo"
        )
        
        self.tipo_servico = TypeService.objects.create(nome="Aulas")
        self.servico = Service.objects.create(
            estudante=self.universitario,
            titulo="Aula",
            descricao="Descrição",
            tipo_servico=self.tipo_servico,
            preco=5000
        )
        
        self.payment = Payment.objects.create(
            contratante=self.publico_externo,
            prestador=self.universitario,
            servico=self.servico,
            valor_total=Decimal('50.00')
        )
    
    def test_webhook_creation(self):
        """Testa criação de webhook"""
        webhook_data = {"type": "payment", "data": {"id": "123"}}
        
        webhook = PaymentWebhook.objects.create(
            payment=self.payment,
            webhook_data=webhook_data,
            evento_tipo="payment.created"
        )
        
        self.assertEqual(webhook.payment, self.payment)
        self.assertEqual(webhook.webhook_data, webhook_data)
        self.assertEqual(webhook.evento_tipo, "payment.created")
        self.assertFalse(webhook.processado)
    
    def test_webhook_str_method(self):
        """Testa método __str__ do PaymentWebhook"""
        webhook = PaymentWebhook.objects.create(
            webhook_data={"test": "data"},
            evento_tipo="payment.updated"
        )
        
        expected = f"Webhook payment.updated - {webhook.data_recebimento}"
        self.assertEqual(str(webhook), expected)