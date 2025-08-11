#!/usr/bin/env python3
"""
Script para monitorar conexões WebSocket em tempo real
"""
import time
import requests
import json
from datetime import datetime

def monitor_websockets():
    """Monitora conexões WebSocket ativas"""
    print("🔍 Monitorando conexões WebSocket...")
    print("Pressione Ctrl+C para parar\n")
    
    try:
        while True:
            try:
                # Fazer requisição para o endpoint de status
                response = requests.get(
                    'http://localhost:8000/api/v1/chat/websocket/status/',
                    headers={'Authorization': 'Bearer YOUR_ADMIN_TOKEN'}  # Substituir por token real
                )
                
                if response.status_code == 200:
                    data = response.json()
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    print(f"[{timestamp}] Conexões ativas: {data['active_connections']}")
                    
                    if data['connections']:
                        print("  Conexões:")
                        for conn in data['connections']:
                            print(f"    - {conn}")
                    
                    print("-" * 50)
                else:
                    print(f"Erro na requisição: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                print("❌ Servidor não está rodando")
            except Exception as e:
                print(f"Erro: {e}")
            
            time.sleep(5)  # Verificar a cada 5 segundos
            
    except KeyboardInterrupt:
        print("\n👋 Monitoramento interrompido")

if __name__ == "__main__":
    monitor_websockets()