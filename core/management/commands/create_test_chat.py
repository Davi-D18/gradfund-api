from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.chat.models import ChatRoom
from apps.services.models import Service


class Command(BaseCommand):
    help = 'Cria dados de teste para o chat'

    def handle(self, *args, **options):
        try:
            # Buscar ou criar usuários de teste
            user1, created = User.objects.get_or_create(
                username='estudante_test',
                defaults={'email': 'estudante@test.com'}
            )
            
            user2, created = User.objects.get_or_create(
                username='contratante_test', 
                defaults={'email': 'contratante@test.com'}
            )
            
            # Buscar primeiro serviço disponível
            service = Service.objects.first()
            if not service:
                self.stdout.write(
                    self.style.ERROR('Nenhum serviço encontrado. Crie um serviço primeiro.')
                )
                return
            
            # Criar sala de chat de teste
            chat_room, created = ChatRoom.objects.get_or_create(
                servico=service,
                defaults={'ativo': True}
            )
            
            # Adicionar participantes
            chat_room.participantes.add(user1, user2)
            
            self.stdout.write(
                self.style.SUCCESS(f'Sala de chat criada: ID {chat_room.id}')
            )
            self.stdout.write(f'Participantes: {user1.username}, {user2.username}')
            self.stdout.write(f'Serviço: {service.titulo}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao criar dados de teste: {str(e)}')
            )