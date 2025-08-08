from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from apps.chat.models.chat import ChatRoom, Message
from apps.chat.services.chat_service import ChatService
from apps.services.models import Service, TypeService
from apps.authentication.models import CustomerUser
from apps.academic.models import Universidade, Curso


class ChatServiceTestCase(TestCase):
    """Testes para ChatService"""
    
    def setUp(self):
        # Criar usuários
        self.user1 = User.objects.create_user(username='estudante', email='estudante@test.com')
        self.user2 = User.objects.create_user(username='contratante', email='contratante@test.com')
        
        # Criar dados acadêmicos
        self.universidade = Universidade.objects.create(nome='UFSC', sigla='UFSC')
        self.curso = Curso.objects.create(nome='Engenharia')
        
        # Criar customer users
        self.customer1 = CustomerUser.objects.create(
            usuario=self.user1,
            tipo_usuario='universitario',
            universidade=self.universidade,
            curso=self.curso
        )
        self.customer2 = CustomerUser.objects.create(
            usuario=self.user2,
            tipo_usuario='publico_externo'
        )
        
        # Criar tipo de serviço e serviço
        self.tipo_servico = TypeService.objects.create(nome='Aulas')
        self.servico = Service.objects.create(
            estudante=self.customer1,
            titulo='Aula de Python',
            descricao='Aulas particulares',
            tipo_servico=self.tipo_servico,
            preco=50
        )
    
    def test_criar_sala_por_servico(self):
        """Testa criação de sala por serviço"""
        sala = ChatService.criar_ou_obter_sala_por_servico(self.servico.id, self.user2)
        
        self.assertIsInstance(sala, ChatRoom)
        self.assertEqual(sala.servico, self.servico)
        self.assertTrue(sala.participantes.filter(id=self.user1.id).exists())
        self.assertTrue(sala.participantes.filter(id=self.user2.id).exists())
    
    def test_obter_sala_existente(self):
        """Testa obtenção de sala já existente"""
        # Criar primeira sala
        sala1 = ChatService.criar_ou_obter_sala_por_servico(self.servico.id, self.user2)
        
        # Tentar criar novamente - deve retornar a mesma
        sala2 = ChatService.criar_ou_obter_sala_por_servico(self.servico.id, self.user2)
        
        self.assertEqual(sala1.id, sala2.id)
    
    def test_verificar_permissao_sala(self):
        """Testa verificação de permissões"""
        sala = ChatService.criar_ou_obter_sala_por_servico(self.servico.id, self.user2)
        
        # Participantes devem ter permissão
        self.assertTrue(ChatService.verificar_permissao_sala(sala, self.user1))
        self.assertTrue(ChatService.verificar_permissao_sala(sala, self.user2))
        
        # Usuário externo não deve ter permissão
        user3 = User.objects.create_user(username='externo', email='externo@test.com')
        self.assertFalse(ChatService.verificar_permissao_sala(sala, user3))
    
    def test_validar_criacao_sala_invalida(self):
        """Testa validação de criação com dados inválidos"""
        # Tentar criar sala consigo mesmo
        validacao = ChatService.validar_criacao_sala(self.servico.id, self.user1)
        self.assertFalse(validacao['valido'])
        
        # Serviço inexistente
        validacao = ChatService.validar_criacao_sala(999, self.user2)
        self.assertFalse(validacao['valido'])


class ChatAPITestCase(APITestCase):
    """Testes para API do chat"""
    
    def setUp(self):
        # Criar usuários
        self.user1 = User.objects.create_user(username='estudante', email='estudante@test.com')
        self.user2 = User.objects.create_user(username='contratante', email='contratante@test.com')
        
        # Criar dados acadêmicos
        self.universidade = Universidade.objects.create(nome='UFSC', sigla='UFSC')
        self.curso = Curso.objects.create(nome='Engenharia')
        
        # Criar customer users
        self.customer1 = CustomerUser.objects.create(
            usuario=self.user1,
            tipo_usuario='universitario',
            universidade=self.universidade,
            curso=self.curso
        )
        self.customer2 = CustomerUser.objects.create(
            usuario=self.user2,
            tipo_usuario='publico_externo'
        )
        
        # Criar serviço
        self.tipo_servico = TypeService.objects.create(nome='Aulas')
        self.servico = Service.objects.create(
            estudante=self.customer1,
            titulo='Aula de Python',
            descricao='Aulas particulares',
            tipo_servico=self.tipo_servico,
            preco=50
        )
    
    def test_listar_salas_sem_autenticacao(self):
        """Testa listagem sem autenticação"""
        response = self.client.get('/api/v1/chat/rooms/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_criar_sala_por_servico(self):
        """Testa criação de sala via API"""
        self.client.force_authenticate(user=self.user2)
        
        response = self.client.post('/api/v1/chat/rooms/criar_por_servico/', {
            'servico_id': self.servico.id
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['servico'], self.servico.id)
    
    def test_listar_salas_usuario(self):
        """Testa listagem de salas do usuário"""
        # Criar sala
        sala = ChatService.criar_ou_obter_sala_por_servico(self.servico.id, self.user2)
        
        self.client.force_authenticate(user=self.user2)
        response = self.client.get('/api/v1/chat/rooms/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], sala.id)
    
    def test_marcar_mensagens_como_lidas(self):
        """Testa marcação de mensagens como lidas"""
        # Criar sala e mensagem
        sala = ChatService.criar_ou_obter_sala_por_servico(self.servico.id, self.user2)
        Message.objects.create(
            sala_chat=sala,
            remetente=self.user1,
            conteudo='Olá!'
        )
        
        self.client.force_authenticate(user=self.user2)
        response = self.client.patch(f'/api/v1/chat/rooms/{sala.id}/messages/marcar_todas_lidas/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('mensagens marcadas como lidas', response.data['message'])


class ChatModelTestCase(TestCase):
    """Testes para models do chat"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', email='user1@test.com')
        self.user2 = User.objects.create_user(username='user2', email='user2@test.com')
        
        # Criar dados mínimos para o serviço
        self.universidade = Universidade.objects.create(nome='UFSC')
        self.curso = Curso.objects.create(nome='Engenharia')
        self.customer1 = CustomerUser.objects.create(
            usuario=self.user1,
            tipo_usuario='universitario',
            universidade=self.universidade,
            curso=self.curso
        )
        self.tipo_servico = TypeService.objects.create(nome='Aulas')
        self.servico = Service.objects.create(
            estudante=self.customer1,
            titulo='Teste',
            descricao='Teste',
            tipo_servico=self.tipo_servico,
            preco=50
        )
        
        self.sala = ChatRoom.objects.create(servico=self.servico)
        self.sala.participantes.add(self.user1, self.user2)
    
    def test_criacao_sala(self):
        """Testa criação de sala de chat"""
        self.assertTrue(self.sala.ativo)
        self.assertEqual(self.sala.participantes.count(), 2)
    
    def test_criacao_mensagem(self):
        """Testa criação de mensagem"""
        mensagem = Message.objects.create(
            sala_chat=self.sala,
            remetente=self.user1,
            conteudo='Teste de mensagem'
        )
        
        self.assertEqual(mensagem.conteudo, 'Teste de mensagem')
        self.assertEqual(mensagem.remetente, self.user1)
        self.assertFalse(mensagem.lida)
    
    def test_string_representation(self):
        """Testa representação string dos models"""
        mensagem = Message.objects.create(
            sala_chat=self.sala,
            remetente=self.user1,
            conteudo='Teste'
        )
        
        self.assertIn('user1', str(mensagem))
        self.assertIn('Teste', str(mensagem))