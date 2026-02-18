# run.py - EJECUTA ESTE ARCHIVO
import subprocess
import socket
import sys
import os

def get_local_ip():
    """Obtener la IP local automáticamente"""
    try:
        # Crear socket temporal para obtener IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def create_windows_firewall_rule():
    """Crear regla de firewall automáticamente (Windows)"""
    try:
        # Verificar si ya existe la regla
        result = subprocess.run(
            ['netsh', 'advfirewall', 'firewall', 'show', 'rule', 'name="Flask UrbanFood"'],
            capture_output=True,
            text=True
        )
        
        if "No rules match" in result.stdout:
            print("🔧 Creando regla en el firewall de Windows...")
            subprocess.run([
                'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                'name="Flask UrbanFood"',
                'dir=in',
                'action=allow',
                'protocol=TCP',
                'localport=5000',
                'remoteip=localsubnet',
                'description="Permitir Urban Food en red local"'
            ], check=True)
            print("✅ Regla de firewall creada")
        else:
            print("✅ Regla de firewall ya existe")
    except Exception as e:
        print(f"⚠️  No se pudo crear regla de firewall: {e}")
        print("⚠️  Puede que necesites permisos de administrador")

if __name__ == '__main__':
    # Obtener IP local
    local_ip = get_local_ip()
    
    print("=" * 60)
    print("🚀 SERVIDOR URBAN FOOD - ACCESO MULTIDISPOSITIVO")
    print("=" * 60)
    print("📡 Tu IP local es:", local_ip)
    print("")
    print("🌐 URLS de acceso:")
    print(f"   📍 En ESTA computadora:  http://localhost:5000")
    print(f"   📱 En CELULAR/Tablet:    http://{local_ip}:5000")
    print(f"   💻 En OTRA PC:           http://{local_ip}:5000")
    print("")
    print("🔑 Credenciales de prueba:")
    print("   👑 Administrador:  admin / admin123")
    print("   👤 Vendedor 1:     vendedor1 / vende123")
    print("   👤 Vendedor 2:     vendedor2 / vende456")
    print("")
    print("⚠️  IMPORTANTE:")
    print("   1. Todos deben estar en la MISMA RED WiFi")
    print("   2. Puede solicitar permiso de firewall")
    print("   3. Para detener: Presiona CTRL+C")
    print("=" * 60)
    
    # Intentar crear regla de firewall (solo Windows)
    if sys.platform == 'win32':
        create_windows_firewall_rule()
    
    print("\n▶️  Iniciando servidor...\n")
    
    # Ejecutar Flask
    subprocess.run([sys.executable, "app.py"])