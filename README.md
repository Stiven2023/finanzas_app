# Flujo (Finanzas 2026 App)

Aplicación de escritorio en Python para gestión financiera personal con enfoque en:
- Deudas
- Metas
- Registro de transacciones
- Seguimiento diario y semanal
- Reportes básicos

## Estado actual

- UI de escritorio con `tkinter`
- Persistencia en SQLite
- Arquitectura modular por capas (`models`, `services`, `ui`, `database`)
- Ejecutable para Windows generado con PyInstaller

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

## Módulos clave

- `src/services/auth_service.py`: autenticación y seguridad
- `src/services/finance_service.py`: deudas y transacciones
- `src/services/goal_service.py`: metas
- `src/services/report_service.py`: agregados/reportes
- `src/ui/pages/weekly.py`: vista diaria y semanal tipo tabla

## Notas de datos

- La base SQLite se genera localmente para desarrollo.
- No se recomienda versionar bases de datos reales con datos personales.

## Próximos pasos recomendados

- Normalizar internacionalización de textos
- Mejorar exportación de reportes
- Cobertura de tests en capa `services`
- Migración opcional a API (FastAPI) + frontend web
