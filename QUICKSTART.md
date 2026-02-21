# 🚀 QUICKSTART - Prueba Flujo v2.0

## Guía Rápida para Probar Transacciones y UI Mejorada

---

## 1️⃣ INICIAR LA APP

```bash
cd d:\Programación\Finanzas\Finanzas2026_App\finanzas_app
python app.py
```

---

## 2️⃣ CREAR CUENTA DE PRUEBA

```
Email: test@flujo.local
Contraseña: Flujo123!
```

O usa credenciales existentes si ya tienes cuenta.

---

## 3️⃣ PROBAR TRANSACCIONES (lo NUEVO ✨)

### Paso A: Navega a Weekly
Haz click en **"📅 Seguimiento Semanal"** en el sidebar

### Paso B: Ver KPIs Actualizados
Al llegar a Weekly, verás 4 tarjetas grandes mostrando datos de la semana actual:
- **💵 INGRESOS**: Total de ingresos esta semana
- **📤 GASTOS**: Total de gastos esta semana
- **💳 PAGOS**: Total de pagos a deudas
- **⚖️ BALANCE**: Ingresos - Gastos - Pagos

**Nota**: Si es la primera vez, mostrarán $0. Vamos a cambiar eso...

### Paso C: Agregar Primera Transacción
1. Busca hoy (el día con ⭐)
2. Haz click en **"+ Agregar"**
3. Se abre un diálogo mejorado:

```
📅 Nuevo registro - 20/03/2024
Registra un nuevo ingreso, gasto o pago

Tipo de registro:
  💰 Ingreso  |  📤 Gasto  |  💳 Pago de Deuda
  
Cantidad ($): [5000]        ← Ingresa cantidad
Descripción: [Sueldo]       ← Opcional
Categoría: [Alimentación]   ← Elige una

[💾 Guardar Entrada] [Cancelar]
```

4. Llena los campos:
   - **Tipo**: 💰 Ingreso
   - **Cantidad**: 5000
   - **Descripción**: Sueldo del mes
   - **Categoría**: Otro
   
5. Click **"💾 Guardar Entrada"**

6. ✅ Verás mensaje de éxito
7. 💰 El KPI de INGRESOS ahora mostrará $5000

### Paso D: Agregar Más Transacciones

**Agrega un GASTO**:
1. Mismo día, click "+ Agregar"
2. Tipo: 📤 Gasto
3. Cantidad: 800
4. Descripción: Almuerzo con equipo
5. Categoría: Alimentación
6. Guardar

✅ GASTOS KPI → $800

**Agrega un PAGO a deuda**:
1. Click "+ Agregar"
2. Tipo: 💳 Pago de Deuda
3. Cantidad: 1000
4. Categoría: Otro
5. Guardar

✅ PAGOS KPI → $1000

### Paso E: Ver Summary Actualizado

Ahora los KPIs deben mostrar:
- **INGRESOS**: $5,000.00
- **GASTOS**: $800.00
- **PAGOS**: $1,000.00
- **BALANCE**: $3,200.00 ✅ (5000 - 800 - 1000)

---

## 4️⃣ PROBAR UI MEJORADA

### KPI Cards Rediseñados
- Iconos más grandes y visibles
- Valores destacados en color
- Barra superior coloreada
- Mejor espaciado

### Buttons con Hover
- Pasa mouse sobre botones
- Verás relieve visual "sunken"
- Better visual feedback

### Entry Fields Mejorados
- Haz focus en un campo
- El borde se vuelve amarillo/dorado
- Indica campo activo claramente
- Al salir, vuelve a gris

### Diálogos Mejorados
- Nuevo: Diálogos centrados en pantalla
- Separadores visuales claros
- Mejor organización de contenido
- No resizable (interfaz más limpia)

### Day Cards Mejorados
- Ahora muestran 4 columnas: ingresos, gastos, pagos, balance
- Lista las transacciones registradas
- Cada transacción muestra emoji, nombre y monto

---

## 5️⃣ PROBAR REPORTES

### Ver Datos en Reports
1. Navega a **"📊 Reportes & Análisis"**
2. Verás 4 tabs: Income/Expense, Debt, Expenses, Monthly
3. **Income vs Expenses** tab debe mostrar datos:
   - Gráfico de barras comparando ingresos vs gastos
   - Debe haber una barra para Mes 1 con tus datos

---

## 6️⃣ PRUEBAS ADICIONALES

### Probar Deshacer (Cercando app)
1. Agrega una transacción
2. Cierra la app (`Ctrl+Q` o botón X)
3. Abre nuevamente
4. Navega a Weekly
5. ✅ La transacción sigue ahí (BD persistió)

### Probar Múltiples Días
1. Clickea día anterior ("← Anterior" botón)
2. Agrega transacción al día anterior
3. Vuelve a hoy ("Hoy" botón)
4. Cada day card muestra sus propias transacciones
5. KPI semanal sigue acumulando todo

### Probar Categorías Nuevas
1. + Agregar
2. Categoría dropdown muestra 8 opciones
3. Prueba: Salud, Educación, Diversión
4. Se guardan correctamente
5. Reports → "Gastos por Categoría" las muestra

---

## 🐛 TROUBLESHOOTING

### "KeyError: 'income'" en Reports
- **Causa**: ReportService retorna estructura vieja
- **Solución**: Reinicia la app, verifica que reports.py y report_service.py estén actualizados

### "Transacción no se guarda"
- **Causa**: FinanceService.create_transaction() no se llama
- **Solución**: Verifica que weekly.py `save_entry()` llama `FinanceService.create_transaction()`
- **Debug**: Abre console y busca logs de error

### "KPIs siguen en $0"
- **Causa**: get_transactions_by_date_range retorna lista vacía
- **Solución**: Verifica que transaction_date pasado sea ISO format (YYYY-MM-DD)

### "Diálogo aparece roto" (off-screen)
- **Causa**: Pantalla con resolución baja
- **Solución**: DialogWindow ahora auto-centra, ajusta geometry si es necesario

---

## 📝 CHECKLIST DE VALIDACIÓN

**Transacciones**
- [ ] Puedo agregar ingreso
- [ ] Puedo agregar gasto
- [ ] Puedo agregar pago
- [ ] Se guardan en BD
- [ ] KPIs se actualizan
- [ ] Day cards muestran transacciones
- [ ] Puedo ver transacciones después de reiniciar

**UI/UX**
- [ ] KPI cards se ven más grandes
- [ ] Buttons tienen efecto hover
- [ ] Entry fields muestran focus state
- [ ] Diálogos están centrados
- [ ] Categorías expandidas a 8
- [ ] Colores Flujo aplicados

**Reportes**
- [ ] Income vs Expenses muestra datos
- [ ] Gastos por categoría se actualiza
- [ ] Debt projection calcula correctamente
- [ ] Monthly summary tiene datos reales

---

## 💡 TIPS

### Para Pruebas Rápidas
```python
# En python REPL, conexión a BD
from src.database.db import db
transactions = db.execute_query(
    "SELECT * FROM transactions WHERE user_id = 1 ORDER BY date DESC LIMIT 5"
)
for t in transactions:
    print(f"{t[5]} - ${t[2]} ({t[4]})")  # category, amount, type
```

### Ver Logs
```bash
# La app escribe logs en console
# Busca líneas como:
# "Transacción creada: income 5000 COP"
# "Error creando transacción: ..."
```

### BD Location
```
d:\Programación\Finanzas\Finanzas2026_App\finanzas_app\data\finances.db
```

Puedes inspeccionar con SQLite Explorer (VS Code extension) si quieres.

---

## 🎯 OBJETIVO ALCANZADO

Con esta guía, habrás probado:
- ✅ Sistema completo de transacciones
- ✅ Persistencia en BD
- ✅ Actualización de KPIs en tiempo real
- ✅ UI/UX mejorada

**Si todo funciona → Flujo v2.0 está LISTO PARA PRODUCCIÓN** 🚀

---

## ❓ PREGUNTAS?

Verifica:
1. `MEJORAS_TRANSACCIONES_UI.md` - Guía técnica detallada
2. `CHANGELOG.md` - Cambios por versión
3. `README.md` - Guía general de la app
4. Logs de console - Errores detallados

¡Espero que disfrutes usando Flujo! 💚📊✨
