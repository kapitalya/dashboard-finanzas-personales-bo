"""
src/generar_datos_demo.py
─────────────────────────────────────────────────────────────────────────────
Genera un CSV de transacciones de ejemplo para probar el dashboard.
Simula finanzas personales de un profesional boliviano típico.

Uso:
    python src/generar_datos_demo.py
    python src/generar_datos_demo.py --anio 2024 --ingreso 9500
"""

import argparse
import numpy as np
import pandas as pd
import os


def generar_transacciones(anio: int = 2024, ingreso_base: float = 9500,
                           semilla: int = 42) -> pd.DataFrame:
    """
    Genera transacciones mensuales realistas para Bolivia.

    Incluye:
    - Salario mensual con variación
    - Aguinaldo semestral (junio) y anual (diciembre)
    - Gastos por categoría con distribuciones realistas
    - Gastos extraordinarios ocasionales
    """
    np.random.seed(semilla)
    meses = pd.date_range(f'{anio}-01-01', f'{anio}-12-01', freq='MS')

    # Categorías: (media_bob, std_bob, frecuencia_mensual)
    categorias = {
        'Alimentación':    (1800, 200,  1.0),
        'Alquiler':        (2500,   0,  1.0),
        'Transporte':      (600,   80,  1.0),
        'Servicios':       (450,   50,  1.0),  # Luz, agua, internet, celular
        'Salud':           (300,  150,  0.7),  # No siempre hay gastos
        'Educación':       (800,  100,  1.0),
        'Entretenimiento': (400,  120,  0.9),
        'Ropa':            (350,  200,  0.5),  # Cada 2 meses aprox
        'Ahorro USD':      (500,   50,  1.0),  # Compra dólares
        'Otros':           (300,  100,  1.0),
    }

    registros = []

    for mes in meses:
        # ── INGRESOS ──────────────────────────────────────────────────────────
        ingreso = ingreso_base + np.random.normal(0, 300)

        # Aguinaldo semestral (junio)
        if mes.month == 6:
            ingreso += ingreso_base * 0.5

        # Aguinaldo anual (diciembre)
        if mes.month == 12:
            ingreso += ingreso_base

        registros.append({
            'fecha':     mes,
            'tipo':      'Ingreso',
            'categoria': 'Salario',
            'monto_bob': round(max(ingreso, 0), 2),
            'moneda':    'BOB',
            'nota':      'Salario mensual' + (' + Aguinaldo' if mes.month in [6, 12] else '')
        })

        # Ingreso extra ocasional (freelance, etc.)
        if np.random.random() < 0.2:  # 20% de probabilidad cada mes
            extra = np.random.uniform(500, 2000)
            registros.append({
                'fecha':     mes,
                'tipo':      'Ingreso',
                'categoria': 'Ingreso Extra',
                'monto_bob': round(extra, 2),
                'moneda':    'BOB',
                'nota':      'Trabajo freelance / extra'
            })

        # ── GASTOS ────────────────────────────────────────────────────────────
        for cat, (media, std, freq) in categorias.items():
            if np.random.random() > freq:
                continue

            monto = max(0, np.random.normal(media, std))

            # Aumentos estacionales
            if cat == 'Entretenimiento' and mes.month in [12, 1]:
                monto *= 1.5   # Fiestas de fin de año
            if cat == 'Ropa' and mes.month in [4, 10]:
                monto *= 2.0   # Cambio de temporada

            registros.append({
                'fecha':     mes,
                'tipo':      'Gasto',
                'categoria': cat,
                'monto_bob': round(monto, 2),
                'moneda':    'BOB',
                'nota':      ''
            })

        # Gasto extraordinario ocasional (médico, reparación, viaje)
        if np.random.random() < 0.15:
            gastos_ext = {
                'Salud': np.random.uniform(500, 2000),
                'Viaje': np.random.uniform(800, 3000),
                'Reparación/Hogar': np.random.uniform(300, 1500),
            }
            cat_ext = np.random.choice(list(gastos_ext.keys()))
            registros.append({
                'fecha':     mes,
                'tipo':      'Gasto',
                'categoria': cat_ext,
                'monto_bob': round(gastos_ext[cat_ext], 2),
                'moneda':    'BOB',
                'nota':      'Gasto extraordinario'
            })

    df = pd.DataFrame(registros).sort_values(['fecha', 'tipo']).reset_index(drop=True)
    return df


def resumen(df: pd.DataFrame) -> None:
    """Imprime resumen del dataset generado."""
    ingresos = df[df['tipo'] == 'Ingreso']['monto_bob'].sum()
    gastos   = df[df['tipo'] == 'Gasto']['monto_bob'].sum()
    ahorro   = ingresos - gastos

    print('\n' + '='*50)
    print('RESUMEN DATOS GENERADOS')
    print('='*50)
    print(f'Total registros: {len(df):,}')
    print(f'Período: {df["fecha"].min().date()} → {df["fecha"].max().date()}')
    print(f'\nIngresos totales: Bs {ingresos:,.2f}')
    print(f'Gastos totales:   Bs {gastos:,.2f}')
    print(f'Ahorro neto:      Bs {ahorro:,.2f}  ({ahorro/ingresos*100:.1f}%)')
    print(f'\nTop 3 categorías de gasto:')
    top3 = df[df['tipo']=='Gasto'].groupby('categoria')['monto_bob'].sum()\
             .sort_values(ascending=False).head(3)
    for cat, monto in top3.items():
        print(f'  {cat:<20} Bs {monto:,.0f}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Genera datos demo para el dashboard')
    parser.add_argument('--anio',    type=int,   default=2024,   help='Año a simular')
    parser.add_argument('--ingreso', type=float, default=9500.0, help='Ingreso base mensual (BOB)')
    parser.add_argument('--semilla', type=int,   default=42,     help='Semilla aleatoria')
    args = parser.parse_args()

    os.makedirs('datos', exist_ok=True)
    df = generar_transacciones(args.anio, args.ingreso, args.semilla)

    ruta = f'datos/transacciones_{args.anio}.csv'
    df.to_csv(ruta, index=False)
    print(f'✅ Archivo guardado: {ruta}')
    resumen(df)

    print(f'\n💡 Para ver el dashboard:')
    print(f'   1. Copia {ruta} → datos/transacciones.csv')
    print(f'   2. streamlit run app.py')
