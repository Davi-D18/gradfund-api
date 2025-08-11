#!/usr/bin/env python3
"""
Teste simples de autenticação
"""
import requests

def test_auth():
    print("🔍 TESTE DE AUTENTICAÇÃO\n")
    
    # Teste 1: Endpoint sem autenticação
    print("1. Testando endpoint público...")
    try:
        response = requests.get('http://localhost:8000/api/v1/chat/debug/all-users/')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Usuários encontrados: {data.get('total_users', 0)}")
    except Exception as e:
        print(f"   Erro: {e}")
    
    # Teste 2: Endpoint com autenticação (deve falhar sem token)
    print("\n2. Testando endpoint protegido sem token...")
    try:
        response = requests.get('http://localhost:8000/api/v1/chat/debug/api-user/')
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:100]}...")
    except Exception as e:
        print(f"   Erro: {e}")
    
    print("\n3. Para testar com token:")
    print("   - Faça login no frontend")
    print("   - Copie o token do localStorage")
    print("   - Execute: curl -H 'Authorization: Bearer SEU_TOKEN' http://localhost:8000/api/v1/chat/debug/api-user/")

if __name__ == "__main__":
    test_auth()