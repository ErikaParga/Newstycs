import pandas as pd


def resumir_dataframe(df: pd.DataFrame, max_categorias: int = 5) -> dict:
    """
    Genera un resumen genérico de un DataFrame de ventas, sin asumir nombres
    de columna fijos. Funciona con cualquier estructura que el equipo entregue.

    Args:
        df: DataFrame ya filtrado (idealmente para un solo producto).
        max_categorias: límite de valores únicos a reportar en columnas
                        categóricas (para no explotar en columnas tipo fecha).

    Returns:
        dict con metadatos + estadísticas por tipo de columna.
    """
    resumen = {
        "columnas_disponibles": list(df.columns),
        "num_registros": len(df),
    }

    columnas_numericas = df.select_dtypes(include="number").columns
    for col in columnas_numericas:
        resumen[col] = {
            "total": float(df[col].sum()),
            "promedio": round(float(df[col].mean()), 2),
            "min": float(df[col].min()),
            "max": float(df[col].max()),
        }

    columnas_booleanas = df.select_dtypes(include="bool").columns
    for col in columnas_booleanas:
        resumen[col] = {"dias_activos": int(df[col].sum())}

    # object/string, excluyendo columnas tipo fecha (muchos valores únicos, poco útil agregado)
    columnas_categoricas = df.select_dtypes(include=["object", "string"]).columns
    for col in columnas_categoricas:
        if df[col].nunique() > 50:  # heurística simple para saltar columnas tipo fecha/id
            continue
        conteo = df[col].value_counts(dropna=True).head(max_categorias).to_dict()
        resumen[col] = conteo

    return resumen


if __name__ == "__main__":
    df = pd.read_csv("/mnt/user-data/uploads/ventas_donas.csv")

    # Simulamos lo que haría Aldeb: filtrar por un solo producto antes de pasártelo
    producto_objetivo = "Glaseada Clásica"
    df_filtrado = df[df["producto"] == producto_objetivo].copy()

    resumen = resumir_dataframe(df_filtrado)

    import json
    print(json.dumps(resumen, indent=2, ensure_ascii=False, default=str))
