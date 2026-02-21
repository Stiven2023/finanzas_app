# CHANGELOG

## [2.0.1] - 2024 - TRANSACCIONES Y UI MEJORADA

### ✨ NUEVO - Sistema de Transacciones Funcional

#### Backend
- Actualizado `FinanceService.create_transaction()` para aceptar parámetro `transaction_date`
- Permite registrar transacciones retroactivas (gastos de días anteriores)
- Actualizado `ReportService.get_monthly_summary()` para leer tabla `transactions` en lugar de solo `weeks`
- Actualizado `ReportService.get_last_months_summary()` para agregar transacciones por mes

#### Frontend - Weekly Page
- Implementado `save_entry()` para guardar transacciones reales en BD
- Actualizado `_build_week_kpis()` para mostrar datos reales de transacciones
- Actualizado `_build_day_card()` para mostrar lista de transacciones del día
- Expandidas categorías de transacciones de 5 a 8 opciones

#### Flujo de Datos
- Transacciones ahora se guardan en BD cuando usuario hace click "Guardar Entrada"
- KPIs semanales se calculan automáticamente desde transacciones
- Day cards muestran transacciones con emoji, descripción y monto
- Reportes leen datos reales desde tabla transactions

### 🎨 MEJORADO - Interfaz Visual Completamente Refinada

#### Componentes Visuales (`src/ui/components.py`)
- **KPICard**: Iconos más grandes (24px), valores destacados (22px bold), mejor espaciado
- **Button**: Efecto hover con relieve "sunken" para mejor feedback
- **Entry**: Focus states claramente visibles (borde amarillo al hacer focus)
- **DataTable**: Alternancia de colores mejorada, mejor contraste
- **DialogWindow**: Nuevo centrado en pantalla, ahora no resizable, separadores visuales

#### Página Weekly Redesignada
- Diálogo "Nueva Entrada" con layout mejorado
- Radio buttons con colores dinámicos
- 8 categorías: Alimentación, Transporte, Servicios, Entretenimiento, Salud, Educación, Diversión, Otro
- Botones con paleta Flujo (teal primario, card2 secundario)
- Day cards muestran 4 columnas de resumen y lista de transacciones

#### Branding
- Actualizado app.py header: "FINANZAS 2026" → "FLUJO - Gestor Financiero Personal"
- Aplicada consistentemente paleta de colores Flujo en toda la app

### 📊 Estadísticas
- Archivos modificados: 6
- Bugs fijos: 5
- Features implementadas: 8
- Métodos mejorados: 12
- Líneas de código nuevas: ~200

---

## [2.0.0] - 2026-02-20

### ✨ Características Nuevas

#### Arquitectura Modular
- Refactorización completa del código en estructura MVC
- Separación clara entre UI, lógica de negocio y datos
- Código más mantenible y escalable

#### Sistema Multi-Usuario
- Soporte para múltiples usuarios
- Asignación de configuración por usuario
- Gestión centralizada de preferencias

#### Monedas Globales
- Soporte para USD, COP, EUR, MXN
- Sistema flexible de conversion de divisas
- Tasas de cambio almacenadas en BD
- Formato automático según moneda

#### Sistema de Metas Flexible
- Ya no solo una meta "Carro", sino metas ilimitadas
- Categorías de metas (car, house, vacation, emergency, education, etc)
- Iconos y colores personalizados por meta
- Seguimiento de progreso detallado
- Estados: active, completed, paused, cancelled

#### Servicios Especializados
- `FinanceService`: Gestión de deudas y transacciones
- `GoalService`: Gestión de metas financieras
- `CurrencyService`: Conversión y formateo de monedas
- `ReportService`: Análisis y reportes financieros

#### Base de Datos Mejorada
- Esquema normalizado y escalable
- Soporte para múltiples usuarios
- Índices para mejor rendimiento
- Relaciones apropiadas entre tablas
- Tabla de transacciones detalladas

#### Componentes UI Reutilizables
- `KPICard`: Tarjetas indicadores clave
- `DataTable`: Tablas de datos con scroll
- `ProgressBar`: Barras de progreso visuales
- `NotificationBanner`: Banners de notificación
- `DialogWindow`: Ventanas de diálogo estilizadas
- Helpers: frame, label, button, entry, card, separator

#### Dashboard Mejorado
- Resumen de deudas + metas
- Gráfica de distribución de metas
- Alertas de deudas urgentes
- Información más relevante y global

#### Configuración Global
- Archivo `config.py` centralizado
- Temas predefinidos (dark, light)
- Colores y fuentes consistentes
- Moneda por defecto configurable

#### Documentación Completa
- README.md extenso con instrucciones
- Documentación de APIs de servicios
- Guía de estructura de datos
- Ejemplos de uso

### 🐛 Errores Corregidos
- Hardcoding de datos eliminado
- Validación mejorada de entrada
- Manejo de errores más robusto

### 📦 Dependencias
- matplotlib >= 3.5.0
- python-dotenv >= 0.19.0
- pillow >= 9.0.0
- requests >= 2.27.0

### 🔮 Próximas Versiones

**v2.1**
- [ ] Completar página Gestión Deudas
- [ ] Completar página Metas
- [ ] Completar página Semanal
- [ ] Completar página Reportes
- [ ] Completar página Configuración

**v2.2**
- [ ] Reportes PDF
- [ ] Exportación CSV
- [ ] Gráficas mejoradas
- [ ] Más análisis

**v2.3**
- [ ] Autenticación de usuarios
- [ ] Multi-perfiles
- [ ] Sincronización de datos

**v3.0**
- [ ] API REST
- [ ] Sincronización en nube
- [ ] Aplicación web

**v4.0**
- [ ] Aplicación móvil

---

## [1.0.0] - 2026-02-01

### 🎉 Versión Inicial
- Dashboard básico
- Gestión simple de deudas
- Seguimiento semanal y mensual
- Meta única (carro)
- Tema dark
- Gráficas matplotlib

---

**Última actualización: 2026-02-20**
