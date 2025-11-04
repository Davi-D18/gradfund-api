from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError
from decimal import Decimal
from apps.payments.schemas.payment_schema import (
    PaymentCreateSerializer,
    PaymentDetailSerializer,
    PaymentListSerializer
)
from apps.payments.models import Payment
from apps.authentication.models import CustomerUser
from apps.services.models import Service, TypeService
from apps.academic.models import Universidade, Curso


class PaymentCreateSerializerTest(TestCase):
    def setUp(self):
        # Setup básico
        self.universidade = Universidade.objects.create(nome="UFSC")
        self.curso = Curso.objects.create(nome="Ciência da Computação")
        
        self.user_universitario = User.objects.create_user(
            username="estudante", email="estudante@test.com"
        )
        self.universitario = CustomerUser.objects.create(
            usuario=self.user_universitario,
            tipo_usuario="universitario",
            mp_access_token="TEST-123456789"
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
    
    def test_valid_servico_id(self):
        """Testa validação com serviço válido"""
        data = {'servico_id': str(self.servico.id)}
        serializer = PaymentCreateSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['servico_id'], self.servico.id)
    
    def test_invalid_servico_id_format(self):
        """Testa validação com formato de UUID inválido"""
        data = {'servico_id': 'invalid-uuid'}
        serializer = PaymentCreateSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('servico_id', serializer.errors)
    
    def test_nonexistent_servico_id(self):
        """Testa validação com serviço inexistente"""
        import uuid
        fake_id = uuid.uuid4()
        
        data = {'servico_id': str(fake_id)}
        serializer = PaymentCreateSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('servico_id', serializer.errors)
        self.assertIn('não encontrado', str(serializer.errors['servico_id'][0]))
    
    def test_inactive_servico(self):
        """Testa validação com serviço inativo"""
        self.servico.ativo = False
        self.servico.save()
        
        data = {'servico_id': str(self.servico.id)}
        serializer = PaymentCreateSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('servico_id', serializer.errors)
    
    def test_missing_servico_id(self):
        """Testa validação sem servico_id"""
        data = {}
        serializer = PaymentCreateSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('servico_id', serializer.errors)


class PaymentDetailSerializerTest(TestCase):
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
            mp_access_token="TEST-123456789"
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
            preco=5000
        )
        
        self.payment = Payment.objects.create(
            contratante=self.publico_externo,
            prestador=self.universitario,
            servico=self.servico,
            valor_total=Decimal('50.00'),
            status='approved',
            metodo_pagamento='pix'
        )
    
    def test_serialization(self):
        """Testa serialização do pagamento"""
        serializer = PaymentDetailSerializer(self.payment)
        data = serializer.data
        
        self.assertEqual(data['id'], str(self.payment.id))
        self.assertEqual(data['contratante_nome'], 'publico')
        self.assertEqual(data['prestador_nome'], 'estudante')
        self.assertEqual(data['servico_titulo'], 'Aula de Python')
        self.assertEqual(data['valor_total'], '50.00')
        self.assertEqual(data['status'], 'approved')
        self.assertEqual(data['metodo_pagamento'], 'pix')
    
    def test_read_only_fields(self):
        """Testa que campos são read-only"""
        serializer = PaymentDetailSerializer()
        
        read_only_fields = serializer.Meta.read_only_fields
        self.assertIn('id', read_only_fields)
        self.assertIn('data_criacao', read_only_fields)
        self.assertIn('data_atualizacao', read_only_fields)


class PaymentListSerializerTest(TestCase):
    def setUp(self):
        # Setup igual ao PaymentDetailSerializerTest
        self.universidade = Universidade.objects.create(nome="UFSC")
        
        self.user_universitario = User.objects.create_user(
            username="estudante", email="estudante@test.com"
        )
        self.user_publico = User.objects.create_user(
            username="publico", email="publico@test.com"
        )
        
        self.universitario = CustomerUser.objects.create(
            usuario=self.user_universitario,
            tipo_usuario="universitario",
            mp_access_token="TEST-123456789"
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
            preco=5000
        )
        
        self.payment = Payment.objects.create(
            contratante=self.publico_externo,
            prestador=self.universitario,
            servico=self.servico,
            valor_total=Decimal('50.00')
        )
    
    def test_list_serialization(self):
        """Testa serialização para listagem"""
        serializer = PaymentListSerializer(self.payment)
        data = serializer.data
        
        expected_fields = [
            'id', 'servico_titulo', 'contratante_nome', 
            'prestador_nome', 'valor_total', 'status', 'data_criacao'
        ]
        
        for field in expected_fields:
            self.assertIn(field, data)
        
        self.assertEqual(data['servico_titulo'], 'Aula de Python')
        self.assertEqual(data['contratante_nome'], 'publico')
        self.assertEqual(data['prestador_nome'], 'estudante')
    
    def test_multiple_payments_serialization(self):
        """Testa serialização de múltiplos pagamentos"""
        # Criar segundo pagamento
        payment2 = Payment.objects.create(
            contratante=self.publico_externo,
            prestador=self.universitario,
            servico=self.servico,
            valor_total=Decimal('75.00')
        )
        
        payments = Payment.objects.all()
        serializer = PaymentListSerializer(payments, many=True)
        
        self.assertEqual(len(serializer.data), 2)
        self.assertNotEqual(serializer.data[0]['id'], serializer.data[1]['id'])