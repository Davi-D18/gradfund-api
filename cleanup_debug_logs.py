#!/usr/bin/env python3
"""
Script para remover logs de debug dos arquivos após testes
"""
import os
import re

def cleanup_debug_logs():
    """Remove logs de debug dos arquivos"""
    print("🧹 LIMPANDO LOGS DE DEBUG\n")
    
    files_to_clean = [
        'apps/chat/consumers/chat_consumer.py',
        'apps/chat/consumers/user_consumer.py',
        'apps/chat/middleware/jwt_auth_middleware.py',
        'apps/chat/controllers/test_notification_controller.py'
    ]
    
    base_path = 'c:/Users/tec_info_noite/Documents/TCC/gradfund-api'
    
    for file_path in files_to_clean:
        full_path = os.path.join(base_path, file_path)
        
        if not os.path.exists(full_path):
            print(f"⚠️ Arquivo não encontrado: {file_path}")
            continue
        
        print(f"🔧 Limpando: {file_path}")
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remover logs específicos de debug
        debug_patterns = [
            r'print\(f?"🔍.*?\)\n?',
            r'print\(f?"✅.*?\)\n?',
            r'print\(f?"❌.*?\)\n?',
            r'print\(f?"📤.*?\)\n?',
            r'print\(f?"📨.*?\)\n?',
            r'print\(f?"🔔.*?\)\n?',
            r'logger\.info\(f?"🔍.*?\)\n?',
            r'logger\.info\(f?"✅.*?\)\n?',
            r'logger\.info\(f?"📤.*?\)\n?',
            r'logger\.info\(f?"📨.*?\)\n?',
            r'logger\.info\(f?"🔔.*?\)\n?',
        ]
        
        original_lines = len(content.split('\n'))
        
        for pattern in debug_patterns:
            content = re.sub(pattern, '', content, flags=re.MULTILINE)
        
        # Remover linhas vazias excessivas
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        new_lines = len(content.split('\n'))
        removed_lines = original_lines - new_lines
        
        if removed_lines > 0:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Removidas {removed_lines} linhas de debug")
        else:
            print(f"  ℹ️ Nenhum log de debug encontrado")
    
    print("\n🎉 LIMPEZA CONCLUÍDA!")
    print("\n📋 ARQUIVOS LIMPOS:")
    for file_path in files_to_clean:
        print(f"  - {file_path}")

if __name__ == "__main__":
    cleanup_debug_logs()