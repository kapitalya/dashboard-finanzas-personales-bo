# 💰 Dashboard de Finanzas Personales — Bolivia

![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-2.1-150458?style=flat&logo=pandas&logoColor=white)
![Status](https://img.shields.io/badge/Estado-Activo-brightgreen)

Dashboard interactivo de finanzas personales diseñado para el contexto boliviano. Incluye conversión automática al tipo de cambio paralelo, proyección de ahorro con simulación Monte Carlo y alertas financieras personalizadas.

---

## 🎯 Por Qué Este Dashboard Es Diferente

Los dashboards financieros genéricos no contemplan la realidad boliviana:
- **Doble moneda:** Los bolivianos manejan BOB y USD simultáneamente
- **Tipo de cambio paralelo:** Divergente del oficial desde 2022
- **Aguinaldo:** Ingresos extraordinarios en junio y diciembre
- **Prima cambiaria:** Impacto real en el poder adquisitivo

Este dashboard incorpora esas particularidades nativamente.

---

## 🖥️ Funcionalidades

| Módulo | Descripción |
|---|---|
| **KPIs en tiempo real** | Ingresos, gastos, ahorro neto, tasa de ahorro vs meta |
| **Conversión automática** | BOB ↔ USD al tipo de cambio paralelo configurable |
| **Alertas financieras** | Detecta si estás por debajo de tu meta de ahorro |
| **Flujo mensual** | Gráfica de barras ingresos/gastos/ahorro por mes |
| **Distribución de gastos** | Pie chart por categoría |
| **Monte Carlo** | Proyección de ahorro a 12 meses con P10/P50/P90 |
| **Filtros interactivos** | Por período, tipo y categoría |

---

## 📐 La Simulación Monte Carlo

El módulo de proyección genera N simulaciones de tus próximos 12 meses asumiendo que tus ingresos y gastos siguen distribuciones normales alrededor de tu promedio histórico.

```python
for simulacion in range(N):
    for mes in range(12):
        ingreso = Normal(ingreso_base, sigma_ingreso)
        gasto   = Normal(gasto_base,   sigma_gasto)
        ahorro_acumulado[mes] += max(0, ingreso - gasto)

# Resultado: distribución de ahorros posibles
P10 = escenario_pesimista   # 10% de simulaciones están por debajo
P50 = escenario_base        # mediana
P90 = escenario_optimista   # 10% de simulaciones están por encima
```

Esto da rangos honestos en lugar de una proyección lineal que asume que todo saldrá perfecto.

---

## 📁 Estructura

```
dashboard-finanzas-personales-bo/
├── app.py                          # Dashboard Streamlit principal
├── src/
│   └── generar_datos_demo.py       # Generador de datos de ejemplo
├── datos/
│   └── template_transacciones.csv  # Plantilla para tus propios datos
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚙️ Instalación y Uso

```bash
git clone https://github.com/Serius69/dashboard-finanzas-personales-bo
cd dashboard-finanzas-personales-bo

python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Opción A: ver con datos de demostración
streamlit run app.py

# Opción B: generar datos de ejemplo primero
python src/generar_datos_demo.py --anio 2024 --ingreso 9500
cp datos/transacciones_2024.csv datos/transacciones.csv
streamlit run app.py
```

El dashboard abre en `http://localhost:8501`

---

## 📊 Cómo Usar con Tus Datos Reales

1. Copia `datos/template_transacciones.csv`
2. Completa con tus transacciones reales (puedes exportar desde tu banco)
3. Guarda como `datos/transacciones.csv`
4. Lanza `streamlit run app.py`

**Formato del CSV:**

| Campo | Tipo | Ejemplo |
|---|---|---|
| `fecha` | YYYY-MM-DD | 2024-03-15 |
| `tipo` | Ingreso / Gasto | Gasto |
| `categoria` | Texto libre | Alimentación |
| `monto_bob` | Número | 1850.50 |
| `moneda` | BOB / USD | BOB |
| `nota` | Texto libre | Supermercado |

---

## 🔗 Proyectos Relacionados

- [💱 Dólar Paralelo Bolivia — ARIMA](https://github.com/Serius69/dolar-paralelo-bolivia-arima) — Predicción del TC paralelo
- [🇧🇴 Inflación Bolivia — SARIMA](https://github.com/Serius69/inflacion-bolivia-series-tiempo) — Contexto macroeconómico
- [📈 Portafolio de Activos](https://github.com/Serius69/portafolio-acciones-bolivia) — Qué hacer con tus ahorros

---

## 👤 Autor

**Sergio** — Data Scientist en Finanzas | [github.com/Serius69](https://github.com/Serius69)
