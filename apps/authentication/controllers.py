from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from apps.authentication.schemas import UserSerializer, TokenObtainPairSerializer, CustomerUserProfileSerializer, CustomerUserUpdateSerializer
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404


class RegisterView(generics.CreateAPIView, generics.DestroyAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer


class UserProfileView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        from apps.authentication.models import CustomerUser
        return CustomerUser.objects.select_related(
            'usuario', 'universidade', 'curso'
        ).get(usuario=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CustomerUserProfileSerializer
        return CustomerUserUpdateSerializer
    
    def destroy(self, request, *args, **kwargs):
        # Deletar o User (CustomerUser será deletado em cascade)
        request.user.delete()
        return Response({'message': 'Conta deletada com sucesso'}, status=status.HTTP_204_NO_CONTENT)


class DeleteView(generics.DestroyAPIView):
    queryset = get_user_model().objects.all()
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'user_id'
    
    def delete(self, request, user_id):
        user = get_object_or_404(get_user_model(), id=user_id)
        user.delete()
        return Response({'message': 'Usuário deletado com sucesso'}, status=status.HTTP_204_NO_CONTENT)
