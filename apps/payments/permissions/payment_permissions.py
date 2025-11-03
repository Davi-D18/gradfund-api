from rest_framework.permissions import BasePermission


class CanCreatePayment(BasePermission):
    """Apenas usuários do tipo publico_externo podem criar pagamentos"""
    
    def has_permission(self, request, view):
        if request.method == 'POST':
            return (
                request.user.is_authenticated and 
                hasattr(request.user, 'usuario_user') and
                request.user.usuario_user.tipo_usuario == 'publico_externo'
            )
        return request.user.is_authenticated


class IsPaymentParticipant(BasePermission):
    """Apenas contratante ou prestador podem ver detalhes do pagamento"""
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        if not hasattr(request.user, 'usuario_user'):
            return False
        
        user_profile = request.user.usuario_user
        return (
            obj.contratante == user_profile or 
            obj.prestador == user_profile
        )