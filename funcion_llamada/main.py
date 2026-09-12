import pandas as pd

from resumen import resumir_dataframe
from exa_client import buscar_contexto_externo
from openrouter_client import generar_plan


def generar_recomendacion(datos_producto: dict) -> dict:
    """
    Función única que Aldeb importa y llama desde el endpoint de FastAPI.

    Args:
        datos_producto: dict con el formato que entrega la compañera
                        encargada del filtrado/cálculo:
                        {
                            "producto": str,
                            "metricas": {...ya calculadas...},
                            "historico": [...lista de registros diarios...]
                        }

    Returns:
        dict con: diagnostico, recomendacion, explicacion, plan_de_accion,
                  comparacion, fuentes_externas. Listo para pasar a
                  formatter.py y mandar por webhook a Slack.
    """
    nombre_producto = datos_producto["producto"]
    metricas = datos_producto["metricas"]
    historico = datos_producto.get("historico", [])

    # El histórico es opcional para el resumen de patrones (día de semana,
    # eventos, etc.) — si no viene, se sigue solo con las métricas ya dadas.
    resumen_patrones = {}
    if historico:
        df_historico = pd.DataFrame(historico)
        resumen_patrones = resumir_dataframe(df_historico)

    contexto_exa = buscar_contexto_externo(nombre_producto)
    plan = generar_plan(metricas, resumen_patrones, contexto_exa, nombre_producto)

    plan["fuentes_externas"] = contexto_exa.get("citas", [])

    return plan


if __name__ == "__main__":
    # Ejemplo simulando el formato que manda la compañera
    datos_prueba = {
        "producto": "Glaseada Clásica",
        "metricas": {
            "produccion_total": 93360,
            "ventas_totales": 81252,
            "desperdicio_total": 12108,
            "ventas_perdidas_total": 12209,
            "tasa_desperdicio": 0.13,
            "tasa_faltante": 0.13,
            "ingreso_total": 1462536,
            "costo_desperdicio_total": 78702.0,
        },
        "historico": [],  # aquí llegaría la lista real de registros diarios
    }

    resultado = generar_recomendacion(datos_prueba)

    import json
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
