import pandas as pd

_df = pd.read_csv("datos/ventas_donas.csv")

def obtener_datos_producto(producto: str) -> pd.DataFrame:
    datos = _df[_df["producto"] == producto]
    if datos.empty:
        raise ValueError(f"No hay datos para el producto '{producto}'")
    return datos

def calcular_metricas(datos: pd.DataFrame) -> dict:
    producidas = datos["unidades_producidas_formula_ingenua"].sum()
    vendidas = datos["unidades_vendidas"].sum()
    desperdiciadas = datos["unidades_desperdiciadas"].sum()
    faltantes = datos["ventas_perdidas_por_faltante"].sum()

    return {
        "dias_analizados": len(datos),
        "produccion_total": int(producidas),
        "ventas_totales": int(vendidas),
        "desperdicio_total": int(desperdiciadas),
        "ventas_perdidas_total": int(faltantes),

        "tasa_desperdicio": (
            float(desperdiciadas / producidas)
            if producidas else 0.0
        ),

        "tasa_faltante": (
            float(faltantes / (vendidas + faltantes))
            if (vendidas + faltantes) else 0.0
        ),

        "ingreso_total": float(datos["ingreso"].sum()),
        "costo_desperdicio_total": float(
            datos["costo_desperdicio_pesos"].sum()
        ),

        "precio_unitario_promedio": float(
            datos["precio_unitario"].mean()
        ),

        "costo_produccion_unitario": float(
            datos["costo_produccion_unitario"].mean()
        ),
    }

def construir_contexto(producto: str) -> dict:
    datos = obtener_datos_producto(producto)
    metricas = calcular_metricas(datos)

    historico = datos.to_dict(orient="records")

    return {
        "producto": producto,
        "metricas": metricas,
        "historico": historico
    }

