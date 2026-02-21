# 📥 GUÍA DE INSTALACIÓN

## Requisitos del Sistema

- **Python**: 3.8 o superior
- **OS**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Espacio en disco**: ~100 MB
- **RAM**: Mínimo 512 MB (recomendado 2 GB)

---

## 🪟 INSTALACIÓN EN WINDOWS

### Paso 1: Descargar Python
1. Visita [python.org](https://www.python.org/downloads/)
2. Descarga **Python 3.10** o superior
3. **IMPORTANTE**: Marca la opción "Add Python to PATH" durante instalación

### Paso 2: Verificar Python
Abre CMD (Símbolo del sistema) y escribe:
```cmd
python --version
```

Debes ver: `Python 3.10.x` o superior

### Paso 3: Descargar el Proyecto
```cmd
git clone <url-del-repositorio>
cd finanzas_app
```

O descarga como ZIP desde GitHub.

### Paso 4: Crear Entorno Virtual
```cmd
python -m venv venv
venv\Scripts\activate
```

Verás: `(venv)` al inicio de la línea de comandos

### Paso 5: Instalar Dependencias
```cmd
pip install -r requirements.txt
```

### Paso 6: Ejecutar la Aplicación
```cmd
python app.py
```

---

## 🍎 INSTALACIÓN EN macOS

### Paso 1: Instalar Python (si no tienes)
Con Homebrew:
```bash
brew install python@3.10
```

O descarga desde [python.org](https://www.python.org/downloads/)

### Paso 2: Verificar Python
```bash
python3 --version
```

### Paso 3: Clonar el Repositorio
```bash
git clone <url-del-repositorio>
cd finanzas_app
```

### Paso 4: Crear Entorno Virtual
```bash
python3 -m venv venv
source venv/bin/activate
```

### Paso 5: Instalar Dependencias
```bash
pip install -r requirements.txt
```

### Paso 6: Ejecutar
```bash
python app.py
```

---

## 🐧 INSTALACIÓN EN LINUX (Ubuntu/Debian)

### Paso 1: Instalar Python y pip
```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip git
```

### Paso 2: Clonar el Repositorio
```bash
git clone <url-del-repositorio>
cd finanzas_app
```

### Paso 3: Crear Entorno Virtual
```bash
python3 -m venv venv
source venv/bin/activate
```

### Paso 4: Instalar Dependencias
```bash
pip install -r requirements.txt
```

### Paso 5: Ejecutar
```bash
python app.py
```

---

## 🐧 INSTALACIÓN EN LINUX (Fedora/RHEL)

### Paso 1: Instalar Dependencias
```bash
sudo dnf install python3 python3-venv python3-pip git
```

### Paso 2 al 5: Mismo que Ubuntu
(Sigue los pasos 2-5 de la sección Ubuntu)

---

## ⚠️ SOLUCIÓN DE PROBLEMAS

### Problema: "python: comando no encontrado"
**Solución:**
- Windows: Reinstala Python y marca "Add to PATH"
- Mac/Linux: Usa `python3` en lugar de `python`

### Problema: "No module named 'matplotlib'"
**Solución:**
```bash
pip install --upgrade matplotlib
```

### Problema: "No module named 'tkinter'"
Este módulo debería venir con Python, pero si no:

**Windows:**
- Reinstala Python y marca "tcl/tk and IDLE"

**Mac:**
```bash
brew install python-tk
```

**Linux:**
```bash
sudo apt install python3-tk
```

### Problema: "Error: 'venv' is not activated"
**Solución:** Debes activar el entorno virtual primero:
```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### Problema: Puerto 5000 ocupado (si fuera servidor)
**Solución:** Cambia el puerto en `config.py` o usa otro número

### Problema: Permisos denegados en Linux
**Solución:**
```bash
chmod +x app.py
sudo python app.py  # Si es necesario
```

---

## ✅ VERIFICAR INSTALACIÓN

Para confirmar que todo está correcto:

```bash
# Activar entorno virtual
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# Verificar módulos
python -c "import tkinter; print('✓ tkinter OK')"
python -c "import matplotlib; print('✓ matplotlib OK')"
python -c "import sqlite3; print('✓ sqlite3 OK')"

# Ejecutar app
python app.py
```

Deberías ver una ventana GUI abierta.

---

## 🔄 ACTUALIZAR DEPENDENCIAS

Cuando salga una nueva versión:

```bash
# Activar entorno virtual
source venv/bin/activate  # Mac/Linux
# o
venv\Scripts\activate  # Windows

# Actualizar
pip install --upgrade -r requirements.txt

# Ejecutar nuevamente
python app.py
```

---

## 🗑️ DESINSTALAR / LIMPIAR

### Eliminar el Entorno Virtual
```bash
# Windows
rmdir /s venv

# Mac/Linux
rm -rf venv
```

### Eliminar la Base de Datos (para reset)
```bash
rm data/finanzas.db
# o
del data\finanzas.db  # Windows
```

---

## 📞 SOPORTE

Si encuentras problemas:

1. **Lee el README.md** - Hay más información
2. **Verifica los requisitos** - Python 3.8+
3. **Reporta el error** - Con el mensaje completo en GitHub Issues

---

**¡Instalación completada! 🎉 Ahora ejecuta `python app.py`**
