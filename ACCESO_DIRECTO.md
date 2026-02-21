# 🌊 Flujo - Crear Acceso Directo

Hay varias formas de crear un acceso directo a **Flujo**:

---

## **Opción 1: Automático (Recomendado)**

```bash
python create_shortcut.py
```

Esto creará un acceso directo en tu **Escritorio** automáticamente.

---

## **Opción 2: Manual (Windows)**

### Método A: Arrastra y suelta
1. Haz clic derecho en `Flujo.bat`
2. Selecciona "Crear acceso directo"
3. Mueve el acceso directo al Escritorio

### Método B: Crear manualmente
1. Haz clic derecho en el Escritorio
2. Selecciona "Nuevo" → "Acceso directo"
3. Pegua esta ruta:
   ```
   C:\ruta\a\finanzas_app\Flujo.bat
   ```
4. Nombre: `Flujo`
5. Haz clic en "Finalizar"

---

## **Opción 3: Ejecutable compilado (PyInstaller)**

Si quieres un `.exe` profesional sin necesidad de Python:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=assets/logos/flujo.ico app.py
```

Esto crea `dist/app.exe` que puedes ejecutar sin consola.

---

## **Opción 4: Ejecutar desde terminal**

```bash
python app.py           # Con consola
pythonw app.py          # Sin consola
.\Flujo.bat             # Desde PowerShell
Flujo.bat               # Desde CMD
```

---

## **Archivos disponibles:**

- **Flujo.bat** → Ejecuta la app con consola (útil para ver errores)
- **Flujo_silent.bat** → Ejecuta sin ventana de consola visible
- **create_shortcut.py** → Script para crear acceso directo automáticamente

---

## **Recomendación final:**

Para mejor experiencia de usuario:
1. Ejecuta: `python create_shortcut.py` (o Opción 2B)
2. Usa `Flujo_silent.bat` como destino (sin consola)
3. Personaliza el ícono si tienes uno

¡Listo! Ahora puedes ejecutar Flujo desde el escritorio como una app de escritorio profesional. 🚀
