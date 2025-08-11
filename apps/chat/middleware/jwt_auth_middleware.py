from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from jwt import decode as jwt_decode
from django.conf import settings
from urllib.parse import parse_qs
from apps.authentication.models import CustomerUser

User = get_user_model()

@database_sync_to_async
def get_customer_user(user_id):
    try:
        django_user = User.objects.get(id=user_id)
        customer_user = CustomerUser.objects.get(usuario=django_user)
        return customer_user
    except (User.DoesNotExist, CustomerUser.DoesNotExist):
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    """Middleware de autenticação JWT para WebSocket"""
    
    async def __call__(self, scope, receive, send):
        print(f"🔍 MIDDLEWARE - Scope type: {scope.get('type')}")
        
        # Extrair token da query string ou headers
        token = None
        
        # Tentar query string primeiro
        query_string = scope.get('query_string', b'').decode()
        print(f"🔍 MIDDLEWARE - Query string: {query_string}")
        
        if query_string:
            query_params = parse_qs(query_string)
            if 'token' in query_params:
                token = query_params['token'][0]
                print(f"🔍 MIDDLEWARE - Token encontrado: {token[:50]}...")
        
        # Se não encontrou na query, tentar headers
        if not token:
            headers = dict(scope.get('headers', []))
            auth_header = headers.get(b'authorization', b'').decode()
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                print(f"🔍 MIDDLEWARE - Token do header: {token[:50]}...")
        
        # Validar token
        if token:
            try:
                UntypedToken(token)
                decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user_id = decoded_data.get('user_id')
                
                print(f"🔍 MIDDLEWARE - Token válido, user_id: {user_id}")
                
                if user_id:
                    if isinstance(user_id, str):
                        user_id = int(user_id)
                    customer_user = await get_customer_user(user_id)
                    scope['user'] = customer_user
                    if isinstance(customer_user, CustomerUser):
                        print(f"✅ MIDDLEWARE - CustomerUser autenticado (ID: {customer_user.id})")
                    else:
                        print("❌ MIDDLEWARE - CustomerUser não encontrado")
                else:
                    scope['user'] = AnonymousUser()
                    print("❌ MIDDLEWARE - user_id não encontrado no token")
            except (InvalidToken, TokenError, ValueError) as e:
                scope['user'] = AnonymousUser()
                print(f"❌ MIDDLEWARE - Token inválido: {str(e)}")
        else:
            scope['user'] = AnonymousUser()
            print("❌ MIDDLEWARE - Token não encontrado")
        
        return await super().__call__(scope, receive, send)