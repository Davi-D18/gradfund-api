import json
import uuid
from django.core.management.base import BaseCommand
from django.urls import get_resolver
from django.conf import settings
from rest_framework import serializers
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView


class Command(BaseCommand):
    help = 'Exporta todas as rotas da API para uma collection do Postman'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='postman_collection.json',
            help='Nome do arquivo de saída (padrão: postman_collection.json)'
        )

    def handle(self, *args, **options):
        output_file = options['output']
        
        # Estrutura base da collection do Postman
        collection = {
            "info": {
                "name": "GradFund API",
                "description": "Collection gerada automaticamente das rotas da API",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": [],
            "variable": [
                {
                    "key": "base_url",
                    "value": "http://localhost:8000",
                    "type": "string"
                }
            ]
        }

        # Obter todas as rotas
        resolver = get_resolver()
        routes = self.get_routes(resolver.url_patterns)
        
        # Remover duplicatas baseado no padrão da URL
        unique_routes = {}
        for route in routes:
            key = route['pattern']
            if key not in unique_routes:
                unique_routes[key] = route
            else:
                # Mesclar métodos se a rota já existir
                existing_methods = set(unique_routes[key]['methods'])
                new_methods = set(route['methods'])
                unique_routes[key]['methods'] = list(existing_methods.union(new_methods))
        
        # Agrupar rotas por app
        grouped_routes = {}
        for route in unique_routes.values():
            app_name = self.get_app_name(route['pattern'])
            if app_name not in grouped_routes:
                grouped_routes[app_name] = []
            grouped_routes[app_name].append(route)

        # Criar items da collection
        for app_name, app_routes in grouped_routes.items():
            folder = {
                "name": app_name.title(),
                "item": []
            }
            
            for route in app_routes:
                for method in route['methods']:
                    item = self.create_postman_item(route, method)
                    folder["item"].append(item)
            
            collection["item"].append(folder)

        # Salvar arquivo
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(collection, f, indent=2, ensure_ascii=False)

        self.stdout.write(
            self.style.SUCCESS(f'Collection exportada com sucesso para: {output_file}')
        )

    def get_routes(self, urlpatterns, prefix=''):
        routes = []
        
        for pattern in urlpatterns:
            if hasattr(pattern, 'url_patterns'):
                # Include pattern
                cleaned_pattern = self.clean_pattern(str(pattern.pattern))
                new_prefix = prefix + cleaned_pattern
                # Garantir separação com /
                if new_prefix and not new_prefix.endswith('/') and cleaned_pattern:
                    new_prefix += '/'
                routes.extend(self.get_routes(pattern.url_patterns, new_prefix))
            else:
                # URL pattern
                cleaned_pattern = self.clean_pattern(str(pattern.pattern))
                route_pattern = prefix + cleaned_pattern
                
                # Filtrar apenas rotas da API e admin
                if self.should_include_route(route_pattern):
                    methods = self.get_http_methods(pattern)
                    
                    if methods:
                        routes.append({
                            'pattern': route_pattern,
                            'name': getattr(pattern, 'name', ''),
                            'methods': methods,
                            'callback': pattern.callback
                        })
        
        return routes

    def get_http_methods(self, pattern):
        methods = []
        
        if hasattr(pattern.callback, 'cls'):
            view_class = pattern.callback.cls
            
            # Verificar se é ModelViewSet
            if issubclass(view_class, ModelViewSet):
                methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
            else:
                # Para outras views, verificar métodos definidos
                if hasattr(view_class, 'post') and not hasattr(view_class, 'get'):
                    methods = ['POST']  # Apenas POST (como register)
                elif hasattr(view_class, 'get') and not hasattr(view_class, 'post'):
                    methods = ['GET']   # Apenas GET
                elif hasattr(view_class, 'post') and hasattr(view_class, 'get'):
                    methods = ['GET', 'POST']
                else:
                    # Fallback: verificar http_method_names
                    if hasattr(view_class, 'http_method_names'):
                        allowed_methods = view_class.http_method_names
                        methods = [m.upper() for m in allowed_methods if m not in ['options', 'head']]
                    else:
                        methods = ['GET']
        else:
            # Function-based view - assumir GET por padrão
            methods = ['GET']
            
        return methods

    def clean_pattern(self, pattern):
        """Remove regex e limpa o padrão da URL"""
        import re
        # Remove caracteres de regex
        pattern = pattern.replace('^', '').replace('$', '')
        # Remove parâmetros regex complexos, mantém apenas o path
        pattern = re.sub(r'\(\?P<[^>]+>[^)]+\)', '', pattern)
        pattern = re.sub(r'\([^)]*\)', '', pattern)
        # Remove caracteres de escape
        pattern = pattern.replace(r'\.', '')
        pattern = pattern.replace(r'\/', '/')
        # Limpa barras duplas e múltiplas
        pattern = re.sub(r'/+', '/', pattern)
        # Remove barra inicial se existir (será adicionada depois)
        if pattern.startswith('/'):
            pattern = pattern[1:]
        # Remove barra final
        if pattern.endswith('/'):
            pattern = pattern[:-1]
        return pattern
    
    def should_include_route(self, pattern):
        """Verifica se a rota deve ser incluída"""
        # Normalizar pattern
        pattern = pattern.strip('/')
        # Incluir apenas rotas da API e admin
        return (
            pattern.startswith('api/v1') or 
            pattern.startswith('admin') or
            pattern == 'admin'
        )
    
    def get_app_name(self, pattern):
        pattern_str = str(pattern)
        if pattern_str.startswith('admin'):
            return 'admin'
        elif 'auth' in pattern_str:
            return 'authentication'
        elif 'service' in pattern_str:
            return 'services'
        elif 'academic' in pattern_str:
            return 'academic'
        else:
            return 'api'

    def create_postman_item(self, route, method):
        url_path = route['pattern']
        
        # Normalizar URL path
        url_path = url_path.strip('/')
        if url_path:
            url_path = '/' + url_path + '/'
        else:
            url_path = '/'
        
        # Nome mais limpo
        endpoint_name = url_path.replace('/api/v1/', '').replace('/', ' ').strip()
        if not endpoint_name:
            endpoint_name = url_path.strip('/')
            
        item = {
            "name": f"{method} {endpoint_name}",
            "request": {
                "method": method,
                "header": [],
                "url": {
                    "raw": "{{base_url}}" + url_path,
                    "host": ["{{base_url}}"],
                    "path": [p for p in url_path.strip('/').split('/') if p]
                }
            }
        }

        # Adicionar headers baseado no método
        if method in ['POST', 'PUT', 'PATCH']:
            item["request"]["header"].append({
                "key": "Content-Type",
                "value": "application/json"
            })
            
            # Adicionar body de exemplo
            item["request"]["body"] = {
                "mode": "raw",
                "raw": self.get_example_body(route, method)
            }

        # Adicionar header de autenticação (exceto para login/register)
        if not any(x in url_path for x in ['token', 'register', 'admin']):
            item["request"]["header"].append({
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
            })

        return item

    def get_example_body(self, route, method):
        pattern = str(route['pattern'])
        
        # Exemplos específicos por rota
        if 'register' in pattern:
            return json.dumps({
                "username": "usuario_exemplo",
                "email": "usuario@exemplo.com",
                "password": "senha123",
                "tipo_usuario": "universitario",
                "universidade": 1,
                "curso": 1,
                "ano_formatura": 2025
            }, indent=2)
        elif 'token' in pattern and 'refresh' not in pattern:
            return json.dumps({
                "credential": "usuario@exemplo.com",
                "password": "senha123"
            }, indent=2)
        elif 'refresh' in pattern:
            return json.dumps({
                "refresh": "{{refresh_token}}"
            }, indent=2)
        elif 'service' in pattern:
            if method == 'POST':
                return json.dumps({
                    "titulo": "Exemplo de Serviço",
                    "descricao": "Descrição do serviço",
                    "preco": 100,
                    "tipo_servico": 1
                }, indent=2)
            elif method in ['PUT', 'PATCH']:
                return json.dumps({
                    "titulo": "Serviço Atualizado",
                    "descricao": "Nova descrição",
                    "preco": 150
                }, indent=2)
        
        return json.dumps({"exemplo": "dados"}, indent=2)