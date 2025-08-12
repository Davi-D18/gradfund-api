#!/usr/bin/env python3
"""
Script para executar todos os testes do sistema de chat
"""
import subprocess
import sys
import os

def run_test_script(script_name, description):
    """Executa um script de teste"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, cwd=os.getcwd())
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSOU")
            return True
        else:
            print(f"❌ {description} - FALHOU")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao executar {script_name}: {str(e)}")
        return False

def main():
    """Executa todos os testes"""
    print("🚀 EXECUTANDO TODOS OS TESTES DO SISTEMA DE CHAT")
    print("=" * 60)
    
    tests = [
        ("test_redis_connection.py", "Teste de Conexão Redis"),
        ("test_chat_notifications.py", "Teste de Notificações do Chat"),
    ]
    
    results = []
    
    for script, description in tests:
        if os.path.exists(script):
            success = run_test_script(script, description)
            results.append((description, success))
        else:
            print(f"⚠️ Script não encontrado: {script}")
            results.append((description, False))
    
    # Resumo final
    print(f"\n{'='*60}")
    print("📊 RESUMO DOS TESTES")
    print(f"{'='*60}")
    
    passed = 0
    total = len(results)
    
    for description, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{description}: {status}")
        if success:
            passed += 1
    
    print(f"\n📈 RESULTADO FINAL: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Iniciar servidor Django: python manage.py runserver")
        print("2. Iniciar frontend: pnpm dev")
        print("3. Testar com dois usuários em navegadores diferentes")
        print("4. Verificar logs no console e terminal")
        print("5. Usar componente de debug no canto inferior direito")
        
        print("\n🧹 LIMPEZA (OPCIONAL):")
        print("- Executar: python cleanup_debug_logs.py")
        print("- Remover componente ChatListDebug da produção")
        
    else:
        print(f"\n⚠️ {total - passed} TESTE(S) FALHARAM")
        print("Verifique os logs acima para identificar problemas")
        print("\n💡 SOLUÇÕES COMUNS:")
        print("- Instalar e iniciar Redis")
        print("- Verificar dependências Python")
        print("- Verificar configurações no settings.py")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)