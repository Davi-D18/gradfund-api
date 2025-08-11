from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_auth_endpoint(request):
    """Endpoint simples para testar autenticação"""
    return Response({
        'authenticated': True,
        'user_id': request.user.id,
        'username': request.user.username,
        'message': 'Token JWT funcionando corretamente!'
    })


@api_view(['GET'])
def test_public_endpoint(request):
    """Endpoint público para teste"""
    return Response({
        'public': True,
        'message': 'Endpoint público funcionando!'
    })