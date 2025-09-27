from rest_framework import permissions
from django.core.exceptions import ObjectDoesNotExist

from apps.authentication.models import CustomerUser


class IsServiceOwner(permissions.BasePermission):
    """
    Permite ações de escrita (update/partial_update/destroy) somente ao dono do service.
    """

    def has_object_permission(self, request, view, obj):
        # Se ação for de modificação, exige autenticação e que o usuário seja o dono.
        if view.action in ("update", "partial_update", "destroy"):
            if not request.user or not request.user.is_authenticated:
                return False
            estudante_user = getattr(getattr(obj, "estudante", None), "usuario", None)
            return estudante_user == request.user

        # Para outras ações, não impõe restrição aqui (outras permissões podem complementar).
        return True


class CanViewInactiveService(permissions.BasePermission):
    """
    Impede que usuários do tipo 'publico_externo' visualizem serviços onde ativo=False.
    """

    message = "Você não tem permissão para ver esse serviço"

    def has_object_permission(self, request, view, obj):
        if view.action == "retrieve" and not getattr(obj, "ativo", True):
            if not request.user or not request.user.is_authenticated:
                return False

            try:
                user_cust = CustomerUser.objects.get(usuario=request.user)
            except ObjectDoesNotExist:
                return False

            return user_cust.tipo_usuario != "publico_externo"

        return True
