from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Permite acesso apenas se o objeto pertence ao usuário logado.
    """
    def has_object_permission(self, request, view, obj):
        # obj.estudante.usuario é o FK para CustomerUser.usuario
        return obj.estudante.usuario == request.user