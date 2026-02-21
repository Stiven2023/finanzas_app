# Flujo (Finanzas 2026 App)

Aplicación de escritorio en Python para gestión financiera personal con enfoque en:
- Deudas
- Metas
- Registro de transacciones
- Seguimiento diario y semanal
- Reportes básicos

## Estado actual

- UI de escritorio con `tkinter`
- Nueva base UI con `PySide6` (migración progresiva)
- Persistencia en SQLite (local) o PostgreSQL (Docker)
- Arquitectura modular por capas (`models`, `services`, `ui`, `database`)
- Ejecutable para Windows generado con PyInstaller
- API HTTP con FastAPI para ejecución en Docker

## Estructura principal

```text
finanzas_app/
├─ app.py
├─ config.py
├─ requirements.txt
├─ build_windows.bat
├─ src/
│  ├─ database/
│  ├─ models/
│  ├─ services/
│  └─ ui/
│     ├─ components.py
│     ├─ main_window.py
│     └─ pages/
└─ data/
```

## Requisitos

- Python 3.10+ (recomendado 3.12)
- Windows (flujo actual de build)

## Ejecución en desarrollo

1. Crear entorno virtual:

```bash
python -m venv .venv
```

2. Activar entorno virtual:

```bash
.venv\Scripts\activate
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. Ejecutar app:

```bash
python app.py
```

## Ejecutar nueva UI (PySide6)

```bash
python app_qt.py
```

### Selección automática de base de datos (desktop)

`app.py` y `app_qt.py` ahora hacen autodetección:
- si PostgreSQL está disponible (ej. Docker en `localhost:5432`), usan `postgres`.
- si no está disponible, hacen fallback automático a `sqlite`.

También puedes forzar el motor con variables de entorno (`DB_ENGINE=postgres|sqlite`).

## Ejecutar API FastAPI local

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Documentación interactiva:
- http://localhost:8000/docs

## Build ejecutable Windows

### Opción rápida

Ejecutar:

```bash
build_windows.bat
```

### Opción manual

```bash
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --clean --windowed --name Flujo app.py
```

Salida:
- `dist/Flujo/Flujo.exe`
- `dist/Flujo-win64.zip` (si se comprime manualmente)

## Docker (API + base de datos SQLite persistente)

## Docker (API + PostgreSQL)

### Levantar

```bash
docker compose up --build
```

### Detener

```bash
docker compose down
```

Persistencia de datos:
- se guarda en el volumen `postgres_data` de Docker.

Variables de entorno para DB en Docker:
- `DB_ENGINE=postgres`
- `DB_HOST=postgres`
- `DB_PORT=5432`
- `DB_NAME=flujo`
- `DB_USER=flujo`
- `DB_PASSWORD=flujo123`

## Módulos clave

- `src/services/auth_service.py`: autenticación y seguridad
- `src/services/finance_service.py`: deudas y transacciones
- `src/services/goal_service.py`: metas
- `src/services/report_service.py`: agregados/reportes
- `src/ui/pages/weekly.py`: vista diaria y semanal tipo tabla
- `src/ui_qt/`: nueva UI en PySide6
- `src/api/main.py`: backend FastAPI

## Notas de datos

- La base SQLite se genera localmente para desarrollo.
- No se recomienda versionar bases de datos reales con datos personales.

## Próximos pasos recomendados

- Normalizar internacionalización de textos
- Mejorar exportación de reportes
- Cobertura de tests en capa `services`
- Migración opcional a API (FastAPI) + frontend web
