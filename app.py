"""
app.py
─────────────────────────────────────────────────────────────────────────────
Dashboard de Finanzas Personales — Contexto Bolivia
Construido con Streamlit + pandas + matplotlib

Funcionalidades:
  - Registro y análisis de ingresos/gastos en BOB y USD
  - Conversión automática al tipo de cambio paralelo actual
  - KPIs financieros personales
  - Proyección de ahorro con simulación Monte Carlo
  - Análisis de categorías de gasto

Uso:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from datetime import datetime, date
import json
import os

# ─── CONFIGURACIÓN DE PÁGINA ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Finanzas Personales BO",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── ESTILOS CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1B4F72, #2E86C1);
        padding: 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin: 5px;
    }
    .metric-value { font-size: 28px; font-weight: bold; margin: 8px 0; }
    .metric-label { font-size: 13px; opacity: 0.85; }
    .metric-delta-pos { color: #2ECC71; font-size: 13px; }
    .metric-delta-neg { color: #E74C3C; font-size: 13px; }
    .alert-box {
        padding: 12px 16px;
        border-radius: 8px;
        margin: 8px 0;
    }
    .alert-warning { background: #FEF9E7; border-left: 4px solid #F39C12; }
    .alert-success { background: #EAFAF1; border-left: 4px solid #27AE60; }
    .alert-danger  { background: #FDEDEC; border-left: 4px solid #E74C3C; }
    .section-header {
        font-size: 18px; font-weight: bold;
        color: #1B4F72; margin: 20px 0 10px 0;
        border-bottom: 2px solid #2E86C1;
        padding-bottom: 6px;
    }
</style>
""", unsafe_allow_html=True)


# ─── DATOS DE EJEMPLO ─────────────────────────────────────────────────────────
@st.cache_data
def cargar_datos_demo():
    """Genera datos de ejemplo representativos de finanzas personales bolivianas."""
    np.random.seed(42)
    meses = pd.date_range('2024-01-01', '2024-12-01', freq='MS')

    categorias_gasto = {
        'Alimentación':   (1800, 200),
        'Alquiler':       (2500, 0),
        'Transporte':     (600,  80),
        'Servicios':      (450,  50),
        'Salud':          (300,  150),
        'Educación':      (800,  100),
        'Entretenimiento':(400,  120),
        'Ropa':           (350,  200),
        'Ahorro USD':     (500,  50),
        'Otros':          (300,  100),
    }

    registros = []
    for mes in meses:
        # Ingreso con variación estacional
        ingreso_base = 9500
        if mes.month in [6, 7]:   # Aguinaldo semestral
            ingreso_base += 4000
        if mes.month == 12:       # Aguinaldo anual
            ingreso_base += 9500
        ingreso = ingreso_base + np.random.normal(0, 300)

        registros.append({
            'fecha':     mes,
            'tipo':      'Ingreso',
            'categoria': 'Salario',
            'monto_bob': round(ingreso, 2),
            'moneda':    'BOB',
            'nota':      'Salario mensual'
        })

        for cat, (media, std) in categorias_gasto.items():
            monto = max(0, np.random.normal(media, std))
            registros.append({
                'fecha':     mes,
                'tipo':      'Gasto',
                'categoria': cat,
                'monto_bob': round(monto, 2),
                'moneda':    'BOB',
                'nota':      ''
            })

    return pd.DataFrame(registros)


def cargar_datos_usuario():
    """Carga datos desde archivo local si existe, si no usa demo."""
    ruta = 'datos/transacciones.csv'
    if os.path.exists(ruta):
        df = pd.read_csv(ruta, parse_dates=['fecha'])
        return df, False
    return cargar_datos_demo(), True


# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://via.placeholder.com/200x60/1B4F72/FFFFFF?text=FinanzasBO", width=200)
    st.markdown("---")

    st.markdown("### ⚙️ Configuración")

    # Tipo de cambio
    tc_oficial  = 6.96
    tc_paralelo = st.number_input(
        "Tipo de cambio paralelo (BOB/USD)",
        min_value=6.96, max_value=20.0,
        value=10.50, step=0.05,
        help="Ingresa el tipo de cambio paralelo actual"
    )

    st.caption(f"Oficial: {tc_oficial} | Paralelo: {tc_paralelo} | "
               f"Prima: {((tc_paralelo/tc_oficial)-1)*100:.1f}%")

    st.markdown("---")
    st.markdown("### 📅 Filtros")
    anio_sel = st.selectbox("Año", [2024, 2023], index=0)

    meses_nombres = ['Ene','Feb','Mar','Abr','May','Jun',
                     'Jul','Ago','Sep','Oct','Nov','Dic']
    mes_inicio, mes_fin = st.select_slider(
        "Rango de meses",
        options=list(range(1, 13)),
        value=(1, 12),
        format_func=lambda x: meses_nombres[x-1]
    )

    st.markdown("---")
    st.markdown("### 🎯 Metas")
    meta_ahorro_pct = st.slider(
        "Meta de ahorro (%)",
        min_value=5, max_value=50, value=20,
        help="% del ingreso que quieres ahorrar"
    )
    meta_fondo_emergencia = st.number_input(
        "Fondo de emergencia (USD)",
        min_value=500, max_value=20000, value=3000, step=500
    )

    st.markdown("---")
    st.markdown("### 📂 Datos")
    usar_demo = st.checkbox("Usar datos de demostración", value=True)
    if not usar_demo:
        archivo = st.file_uploader(
            "Subir CSV de transacciones",
            type=['csv'],
            help="Formato: fecha, tipo, categoria, monto_bob, moneda, nota"
        )


# ─── CARGA DE DATOS ───────────────────────────────────────────────────────────
df_raw, es_demo = cargar_datos_usuario()

if es_demo:
    st.info("📋 Mostrando **datos de demostración**. Para usar tus propios datos, "
            "activa 'Usar datos' en la barra lateral y sube tu CSV.")

# Filtrar por período seleccionado
df = df_raw[
    (df_raw['fecha'].dt.year == anio_sel) &
    (df_raw['fecha'].dt.month >= mes_inicio) &
    (df_raw['fecha'].dt.month <= mes_fin)
].copy()

# Agregar columna USD al tipo de cambio paralelo
df['monto_usd'] = (df['monto_bob'] / tc_paralelo).round(2)

# Separar ingresos y gastos
ingresos = df[df['tipo'] == 'Ingreso']
gastos   = df[df['tipo'] == 'Gasto']


# ─── ENCABEZADO ───────────────────────────────────────────────────────────────
st.title("💰 Dashboard de Finanzas Personales")
st.caption(f"Bolivia · {meses_nombres[mes_inicio-1]} – {meses_nombres[mes_fin-1]} {anio_sel} "
           f"· TC paralelo: {tc_paralelo} BOB/USD")
st.markdown("---")


# ─── KPIs PRINCIPALES ─────────────────────────────────────────────────────────
total_ingresos = ingresos['monto_bob'].sum()
total_gastos   = gastos['monto_bob'].sum()
ahorro_bob     = total_ingresos - total_gastos
ahorro_usd     = ahorro_bob / tc_paralelo
tasa_ahorro    = (ahorro_bob / total_ingresos * 100) if total_ingresos > 0 else 0
n_meses        = df['fecha'].dt.month.nunique()

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    delta_color = "normal"
    st.metric(
        label="💵 Ingresos Totales",
        value=f"Bs {total_ingresos:,.0f}",
        delta=f"${total_ingresos/tc_paralelo:,.0f} USD"
    )
with col2:
    st.metric(
        label="💸 Gastos Totales",
        value=f"Bs {total_gastos:,.0f}",
        delta=f"${total_gastos/tc_paralelo:,.0f} USD",
        delta_color="inverse"
    )
with col3:
    color = "normal" if ahorro_bob >= 0 else "inverse"
    st.metric(
        label="💰 Ahorro Neto",
        value=f"Bs {ahorro_bob:,.0f}",
        delta=f"${ahorro_usd:,.0f} USD",
        delta_color=color
    )
with col4:
    delta_ahorro = tasa_ahorro - meta_ahorro_pct
    st.metric(
        label="📊 Tasa de Ahorro",
        value=f"{tasa_ahorro:.1f}%",
        delta=f"{delta_ahorro:+.1f}% vs meta {meta_ahorro_pct}%",
        delta_color="normal" if delta_ahorro >= 0 else "inverse"
    )
with col5:
    meses_fondo = (meta_fondo_emergencia * tc_paralelo) / (total_gastos / n_meses) if n_meses > 0 else 0
    ahorro_mensual_prom = ahorro_bob / n_meses if n_meses > 0 else 0
    meses_para_fondo = (meta_fondo_emergencia * tc_paralelo - ahorro_bob) / ahorro_mensual_prom \
                        if ahorro_mensual_prom > 0 else float('inf')
    st.metric(
        label="🛡️ Meses p/ Fondo Emergencia",
        value=f"{max(0, meses_para_fondo):.0f} meses",
        delta=f"Meta: ${meta_fondo_emergencia:,} USD"
    )

st.markdown("---")


# ─── ALERTAS FINANCIERAS ──────────────────────────────────────────────────────
st.markdown('<div class="section-header">🚨 Alertas Financieras</div>', unsafe_allow_html=True)

alertas = []
if tasa_ahorro < meta_ahorro_pct:
    alertas.append(('danger', f'Tasa de ahorro ({tasa_ahorro:.1f}%) por debajo de tu meta ({meta_ahorro_pct}%). '
                               f'Necesitas ahorrar Bs {(meta_ahorro_pct/100 * total_ingresos - ahorro_bob):,.0f} más.'))

cat_mayor = gastos.groupby('categoria')['monto_bob'].sum().idxmax()
pct_mayor = gastos.groupby('categoria')['monto_bob'].sum().max() / total_gastos * 100
if pct_mayor > 35:
    alertas.append(('warning', f'"{cat_mayor}" representa el {pct_mayor:.1f}% de tus gastos. '
                                f'Considera si hay margen de optimización.'))

if ahorro_usd >= meta_fondo_emergencia:
    alertas.append(('success', f'✅ ¡Fondo de emergencia alcanzado! '
                                f'Tienes ${ahorro_usd:,.0f} USD ≥ meta de ${meta_fondo_emergencia:,} USD.'))

if tc_paralelo > tc_oficial * 1.3:
    alertas.append(('warning', f'Prima cambiaria elevada ({((tc_paralelo/tc_oficial)-1)*100:.1f}%). '
                                f'Considera ahorrar en USD o activos dolarizados.'))

if not alertas:
    alertas.append(('success', '✅ Todo en orden. Tus finanzas están dentro de los parámetros.'))

cols_alert = st.columns(min(len(alertas), 3))
for i, (tipo, msg) in enumerate(alertas):
    with cols_alert[i % 3]:
        icon = '⚠️' if tipo == 'warning' else ('🔴' if tipo == 'danger' else '✅')
        st.markdown(
            f'<div class="alert-box alert-{tipo}">{icon} {msg}</div>',
            unsafe_allow_html=True
        )

st.markdown("---")


# ─── GRÁFICAS PRINCIPALES ────────────────────────────────────────────────────
col_izq, col_der = st.columns([3, 2])

with col_izq:
    st.markdown('<div class="section-header">📈 Flujo Mensual</div>', unsafe_allow_html=True)

    mensual_ing = ingresos.groupby(ingresos['fecha'].dt.month)['monto_bob'].sum()
    mensual_gas = gastos.groupby(gastos['fecha'].dt.month)['monto_bob'].sum()
    mensual_aho = (mensual_ing - mensual_gas).fillna(0)

    meses_x = sorted(set(mensual_ing.index) | set(mensual_gas.index))
    meses_labels = [meses_nombres[m-1] for m in meses_x]

    fig, ax = plt.subplots(figsize=(10, 4))
    x = np.arange(len(meses_x))
    w = 0.30

    bars1 = ax.bar(x - w, [mensual_ing.get(m, 0) for m in meses_x],
                    w, label='Ingresos', color='#2E86C1', alpha=0.85)
    bars2 = ax.bar(x,     [mensual_gas.get(m, 0) for m in meses_x],
                    w, label='Gastos',   color='#E74C3C', alpha=0.85)
    bars3 = ax.bar(x + w, [mensual_aho.get(m, 0) for m in meses_x],
                    w, label='Ahorro',
                    color=[('#27AE60' if v >= 0 else '#E74C3C')
                           for v in [mensual_aho.get(m, 0) for m in meses_x]],
                    alpha=0.85)

    ax.set_xticks(x); ax.set_xticklabels(meses_labels)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'Bs {v/1000:.0f}k'))
    ax.set_title('Ingresos, Gastos y Ahorro por Mes', fontweight='bold')
    ax.legend(fontsize=9)
    ax.axhline(0, color='black', lw=0.8)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col_der:
    st.markdown('<div class="section-header">🗂️ Gastos por Categoría</div>', unsafe_allow_html=True)

    por_cat = gastos.groupby('categoria')['monto_bob'].sum().sort_values(ascending=False)
    colores_pie = plt.cm.Set3(np.linspace(0, 1, len(por_cat)))

    fig2, ax2 = plt.subplots(figsize=(6, 5))
    wedges, texts, autotexts = ax2.pie(
        por_cat.values,
        labels=por_cat.index,
        autopct='%1.1f%%',
        colors=colores_pie,
        startangle=90,
        pctdistance=0.82
    )
    for text in texts:     text.set_fontsize(9)
    for atext in autotexts: atext.set_fontsize(8)

    ax2.set_title('Distribución de Gastos', fontweight='bold')
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()

st.markdown("---")


# ─── PROYECCIÓN MONTE CARLO ───────────────────────────────────────────────────
st.markdown('<div class="section-header">🎲 Proyección de Ahorro — Simulación Monte Carlo</div>',
            unsafe_allow_html=True)
st.caption("Proyecta tu ahorro acumulado a 12 meses asumiendo variabilidad en ingresos y gastos")

col_mc1, col_mc2, col_mc3 = st.columns(3)
with col_mc1:
    ingreso_base_mc = st.number_input(
        "Ingreso mensual base (BOB)",
        value=int(total_ingresos / n_meses) if n_meses > 0 else 9500,
        step=500
    )
with col_mc2:
    variabilidad = st.slider("Variabilidad (%)", 5, 30, 10,
                              help="Desviación estándar como % del ingreso/gasto")
with col_mc3:
    n_sims = st.selectbox("Simulaciones", [1000, 5000, 10000], index=1)

if st.button("▶️ Ejecutar simulación", type="primary"):
    gasto_base_mc = total_gastos / n_meses if n_meses > 0 else ingreso_base_mc * 0.8
    sigma_ing = ingreso_base_mc * variabilidad / 100
    sigma_gas = gasto_base_mc   * variabilidad / 100
    HORIZONTE = 12

    np.random.seed(42)
    ahorros_sim = np.zeros((n_sims, HORIZONTE))

    for s in range(n_sims):
        acumulado = 0
        for m in range(HORIZONTE):
            ing = max(0, np.random.normal(ingreso_base_mc, sigma_ing))
            gas = max(0, np.random.normal(gasto_base_mc,   sigma_gas))
            acumulado += max(0, ing - gas)
            ahorros_sim[s, m] = acumulado

    p10 = np.percentile(ahorros_sim, 10, axis=0)
    p50 = np.percentile(ahorros_sim, 50, axis=0)
    p90 = np.percentile(ahorros_sim, 90, axis=0)

    meses_fc = list(range(1, HORIZONTE + 1))

    fig3, ax3 = plt.subplots(figsize=(11, 5))

    # Sombrear IC
    ax3.fill_between(meses_fc, p10, p90, alpha=0.15, color='#2E86C1', label='Rango P10-P90')
    ax3.fill_between(meses_fc, p10, p50, alpha=0.20, color='#E74C3C')

    ax3.plot(meses_fc, p50, color='#2E86C1', lw=2.5, marker='o', ms=5, label='Escenario base (P50)')
    ax3.plot(meses_fc, p10, color='#E74C3C', lw=1.5, linestyle='--', label='Escenario pesimista (P10)')
    ax3.plot(meses_fc, p90, color='#27AE60', lw=1.5, linestyle='--', label='Escenario optimista (P90)')

    # Línea meta fondo emergencia
    meta_bob = meta_fondo_emergencia * tc_paralelo
    ax3.axhline(meta_bob, color='#F39C12', lw=2, linestyle=':', label=f'Meta fondo emergencia (Bs {meta_bob:,.0f})')

    ax3.set_xlabel('Mes')
    ax3.set_ylabel('Ahorro acumulado (BOB)')
    ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'Bs {v/1000:.0f}k'))
    ax3.set_title(f'Proyección de Ahorro a 12 Meses — {n_sims:,} simulaciones Monte Carlo',
                   fontweight='bold')
    ax3.legend(fontsize=9)
    ax3.set_xticks(meses_fc)
    ax3.set_xticklabels([meses_nombres[i % 12] for i in range(HORIZONTE)], fontsize=9)
    plt.tight_layout()
    st.pyplot(fig3)
    plt.close()

    # Resumen
    col_r1, col_r2, col_r3 = st.columns(3)
    col_r1.metric("Ahorro estimado a 12m (P50)",
                   f"Bs {p50[-1]:,.0f}", f"${p50[-1]/tc_paralelo:,.0f} USD")
    col_r2.metric("Escenario pesimista (P10)",
                   f"Bs {p10[-1]:,.0f}", f"${p10[-1]/tc_paralelo:,.0f} USD",
                   delta_color="inverse")
    col_r3.metric("Escenario optimista (P90)",
                   f"Bs {p90[-1]:,.0f}", f"${p90[-1]/tc_paralelo:,.0f} USD")

    mes_meta = next((i+1 for i, v in enumerate(p50) if v >= meta_bob), None)
    if mes_meta:
        st.success(f"🎯 En el escenario base, alcanzas tu fondo de emergencia en el **mes {mes_meta}**")
    else:
        faltante = meta_bob - p50[-1]
        st.warning(f"⚠️ En el escenario base, al mes 12 te faltarán Bs {faltante:,.0f} para el fondo de emergencia.")

st.markdown("---")


# ─── TABLA DE TRANSACCIONES ───────────────────────────────────────────────────
st.markdown('<div class="section-header">📋 Detalle de Transacciones</div>', unsafe_allow_html=True)

col_f1, col_f2 = st.columns(2)
with col_f1:
    filtro_tipo = st.multiselect("Tipo", ['Ingreso', 'Gasto'], default=['Ingreso', 'Gasto'])
with col_f2:
    cats_disponibles = df['categoria'].unique().tolist()
    filtro_cat = st.multiselect("Categoría", cats_disponibles, default=cats_disponibles[:5])

df_tabla = df[df['tipo'].isin(filtro_tipo) & df['categoria'].isin(filtro_cat)].copy()
df_tabla['monto_bob'] = df_tabla['monto_bob'].map(lambda x: f"Bs {x:,.2f}")
df_tabla['monto_usd'] = df_tabla['monto_usd'].map(lambda x: f"${x:,.2f}")
df_tabla['fecha']     = df_tabla['fecha'].dt.strftime('%Y-%m-%d')

st.dataframe(
    df_tabla[['fecha', 'tipo', 'categoria', 'monto_bob', 'monto_usd', 'nota']],
    use_container_width=True,
    hide_index=True
)

st.markdown("---")
st.caption("💡 **Cómo usar con tus datos reales:** Crea un CSV con columnas "
           "`fecha, tipo, categoria, monto_bob, moneda, nota` y súbelo en la barra lateral.")
