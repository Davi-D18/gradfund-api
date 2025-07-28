from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from apps.authentication.schemas import UserSerializer, TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404


class RegisterView(generics.CreateAPIView, generics.DestroyAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer


class DeleteView(generics.DestroyAPIView):
    queryset = get_user_model().objects.all()
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'user_id'
    
    def delete(self, request, user_id):
        user = get_object_or_404(get_user_model(), id=user_id)
        user.delete()
        return Response({'message': 'Usuário deletado com sucesso'}, status=status.HTTP_204_NO_CONTENT)
