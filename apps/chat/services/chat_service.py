from django.contrib.auth.models import User
from django.db.models import Q
from apps.chat.models.chat import ChatRoom, Message
from apps.services.models.service import Service


class ChatService:
    """Service para lógica de negócio do chat"""
    
    @staticmethod
    def criar_ou_obter_sala_por_servico(servico_id: int, contratante: User) -> ChatRoom:
        """
        Cria ou obtém sala de chat entre estudante (dono do serviço) e contratante
        """
        try:
            servico = Service.objects.get(id=servico_id)
            estudante = servico.estudante.usuario
            
            # Verificar se já existe sala entre os usuários para este serviço
            sala_existente = ChatRoom.objects.filter(
                servico=servico,
                participantes=estudante
            ).filter(
                participantes=contratante
            ).filter(ativo=True).first()
            
            if sala_existente:
                return sala_existente
            
            # Criar nova sala
            sala = ChatRoom.objects.create(servico=servico)
            sala.participantes.add(estudante, contratante)
            
            return sala
            
        except Service.DoesNotExist:
            raise ValueError("Serviço não encontrado")
    
    @staticmethod
    def verificar_permissao_sala(sala: ChatRoom, usuario: User) -> bool:
        """
        Verifica se usuário tem permissão para acessar a sala
        """
        return sala.participantes.filter(id=usuario.id).exists() and sala.ativo
    
    @staticmethod
    def obter_salas_usuario(usuario: User):
        """
        Obtém todas as salas ativas do usuário ordenadas por última mensagem
        """
        return ChatRoom.objects.filter(
            participantes=usuario,
            ativo=True
        ).prefetch_related('participantes', 'servico').order_by('-ultima_mensagem_em')
    
    @staticmethod
    def contar_mensagens_nao_lidas(sala: ChatRoom, usuario: User) -> int:
        """
        Conta mensagens não lidas pelo usuário na sala
        """
        return Message.objects.filter(
            sala_chat=sala,
            lida=False
        ).exclude(remetente=usuario).count()
    
    @staticmethod
    def marcar_mensagens_como_lidas(sala: ChatRoom, usuario: User) -> int:
        """
        Marca todas as mensagens da sala como lidas (exceto as do próprio usuário)
        """
        return Message.objects.filter(
            sala_chat=sala,
            lida=False
        ).exclude(remetente=usuario).update(lida=True)
    
    @staticmethod
    def obter_participante_oposto(sala: ChatRoom, usuario_atual: User) -> User:
        """
        Obtém o outro participante da conversa (não o usuário atual)
        """
        return sala.participantes.exclude(id=usuario_atual.id).first()
    
    @staticmethod
    def validar_criacao_sala(servico_id: int, contratante: User) -> dict:
        """
        Valida se é possível criar sala para o serviço
        """
        try:
            servico = Service.objects.get(id=servico_id)
            estudante = servico.estudante.usuario
            
            # Não pode criar sala consigo mesmo
            if estudante.id == contratante.id:
                return {
                    'valido': False,
                    'erro': 'Não é possível criar conversa com você mesmo'
                }
            
            # Verificar se serviço está ativo
            if not servico.ativo:
                return {
                    'valido': False,
                    'erro': 'Serviço não está mais disponível'
                }
            
            return {
                'valido': True,
                'servico': servico,
                'estudante': estudante
            }
            
        except Service.DoesNotExist:
            return {
                'valido': False,
                'erro': 'Serviço não encontrado'
            }