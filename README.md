# Dashboard de finanzas personales — Bolivia

> Aplicación Streamlit para registrar ingresos y gastos en BOB y USD, ver el flujo mensual y proyectar el ahorro con Monte Carlo. Para uso personal y como ejemplo de análisis de datos financieros.

**Estado (2026-11-17):** PARCIAL — código completo (`app.py`, generador de datos demo, plantilla CSV); no ejecutado en este corte; falta `requirements.txt`, `.gitignore` y licencia; las rutas del README anterior no coincidían con el repo (corregidas aquí).
**Repo:** kapitalya/dashboard-finanzas-personales-bo · **Rama por defecto:** main · **Alias/nombres anteriores:** ninguno

> Aviso: análisis educativo, no es consejo financiero. La simulación Monte Carlo usa supuestos normales simplificados; no predice tu ahorro real.

## Qué hace

- `app.py`: dashboard Streamlit. Lee `datos/transacciones.csv` con las columnas `fecha`, `tipo`, `categoria`, `monto_bob`, `moneda` y `nota`. Si el archivo no existe, usa datos demo generados en código (semilla 42). Muestra KPIs de ingresos, gastos y ahorro, flujo mensual, distribución de gastos y filtros por año, tipo y categoría. El tipo de cambio paralelo (BOB/USD) se ingresa en la barra lateral.
- Proyección Monte Carlo: simula 12 meses de ingreso y gasto con distribución normal alrededor de un valor base y reporta P10, P50 y P90 del ahorro acumulado. Número de simulaciones seleccionable (1000, 5000 o 10000).
- `generar_datos_demo.py`: genera transacciones sintéticas de un año con `--anio`, `--ingreso` y `--semilla`.
- `template_transacciones.csv`: plantilla con la cabecera que usa `app.py` y 7 filas de ejemplo.

## Stack

Python. Librerías importadas: `streamlit`, `pandas`, `numpy`, `matplotlib`, y `json`/`os`/`datetime` de la biblioteca estándar.

## Estructura

```
dashboard-finanzas-personales-bo/
├── app.py                        # Dashboard Streamlit
├── generar_datos_demo.py         # Generador de datos sintéticos (en la raíz, no en src/)
├── template_transacciones.csv    # Plantilla de transacciones (en la raíz, no en datos/)
└── README.md
```

`datos/` no existe en el repo: lo crea `generar_datos_demo.py` al ejecutarse, o el usuario al copiar sus transacciones.

## Instalación y uso

```bash
git clone https://github.com/kapitalya/dashboard-finanzas-personales-bo
cd dashboard-finanzas-personales-bo

python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install streamlit pandas numpy matplotlib     # sin requirements.txt: versiones sin fijar

# Opción A: ver el dashboard con datos de demostración
streamlit run app.py

# Opción B: generar datos de ejemplo primero
python generar_datos_demo.py --anio 2024 --ingreso 9500 --semilla 42
mkdir -p datos
cp datos/transacciones_2024.csv datos/transacciones.csv
streamlit run app.py
```

Argumentos de `generar_datos_demo.py`: `--anio` (2024), `--ingreso` (ingreso base mensual en BOB, 9500), `--semilla` (42). El archivo generado es `datos/transacciones_<anio>.csv`.

El dashboard abre en `http://localhost:8501`.

## Cómo usar tus datos reales

1. Copia `template_transacciones.csv` a `datos/transacciones.csv` (crea `datos/` antes).
2. Completa las filas con tus transacciones (puedes exportarlas desde tu banco).
3. Ejecuta `streamlit run app.py`.

Formato del CSV (cabecera de la plantilla, igual a la que lee `app.py`):

| Campo | Tipo | Ejemplo |
|---|---|---|
| `fecha` | YYYY-MM-DD | 2024-03-15 |
| `tipo` | Ingreso / Gasto | Gasto |
| `categoria` | Texto libre | Alimentación |
| `monto_bob` | Número | 1850.50 |
| `moneda` | BOB / USD | BOB |
| `nota` | Texto libre | Supermercado |

## Variables de entorno (solo nombres)

Ninguna. No hay `.env.example`.

## Pruebas y CI

- Sin pruebas automatizadas ni workflows de CI en el repo.

### Resultados

- No hay cifras de resultados en el README. La proyección Monte Carlo depende de los datos cargados y de la semilla; no hay salidas guardadas en el repo. Resultados no verificables en el repo.

## Despliegue

No aplica: aplicación local. No hay configuración de despliegue en el repo.

## Estado y relaciones

- Repositorio independiente. El README anterior enlazaba repos de una cuenta personal fuera de la organización (`Serius69/*`); no auditados en este corte.

## Precios y planes

No aplica (herramienta personal, sin venta). Precios y planes: fuente única `Vault/EMPRESA/portafolio/PRECIOS-APROBADOS-20261108.md`.

## Seguridad, privacidad y derechos

- Los datos de transacciones son personales: `datos/` no debe subirse a un repo público. Este repo no incluye `.gitignore` que lo excluya; agregarlo antes de usar datos reales.
- Los datos de demostración son sintéticos (generados por `generar_datos_demo.py` o por `app.py`).
- Licencia: el repo no tiene archivo LICENSE; no hay derechos de reutilización declarados.

## Convenciones de trabajo

Cambios por rama `codex/*` y PR contra `main` (no hay rama `develop`). CI: no hay workflows configurados.
