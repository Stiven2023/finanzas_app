"""
Crear acceso directo de Flujo en el escritorio
Ejecuta: python create_shortcut.py
"""
import os
import sys
from pathlib import Path

def create_desktop_shortcut():
    """Crea un acceso directo en el escritorio"""
    try:
        # Obtener ruta del escritorio
        desktop = Path.home() / "Desktop"
        
        # Ruta de la aplicación
        app_dir = Path(__file__).parent
        bat_file = app_dir / "Flujo.bat"
        
        # Crear shortcut usando VBScript
        vbs_script = f'''
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{desktop}\\Flujo.lnk"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{bat_file}"
oLink.WorkingDirectory = "{app_dir}"
oLink.Description = "Flujo - Gestor Financiero Profesional"
oLink.IconLocation = "{app_dir}\\assets\\logos\\flujo.ico"
oLink.Save
'''
        
        # Crear archivo temporal .vbs
        vbs_file = app_dir / "create_shortcut.vbs"
        with open(vbs_file, 'w', encoding='utf-8') as f:
            f.write(vbs_script)
        
        # Ejecutar VBScript
        os.system(f'cscript "{vbs_file}"')
        
        # Eliminar archivo temporal
        vbs_file.unlink()
        
        print(f"✅ Acceso directo creado en: {desktop}\\Flujo.lnk")
        print(f"📍 Apunta a: {bat_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error creando shortcut: {e}")
        return False

if __name__ == "__main__":
    print("🌊 Creando acceso directo de Flujo...")
    if create_desktop_shortcut():
        print("✨ ¡Listo! Puedes ejecutar Flujo desde el escritorio")
    else:
        print("⚠️ Intenta ejecutar como administrador")
