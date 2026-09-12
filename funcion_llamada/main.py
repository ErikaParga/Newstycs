import pandas as pd

from resumen import resumir_dataframe
from exa_client import buscar_contexto_externo
from openrouter_client import generar_plan
from formatter import enviar_a_slack


def generar_recomendacion(datos_producto: dict, enviar_slack: bool = True) -> dict:
    """
    Funcion unica que Aldeb importa y llama desde el endpoint de FastAPI.

    Args:
        datos_producto: dict con el formato que entrega la companera
                        encargada del filtrado/calculo:
                        {
                            "producto": str,
                            "metricas": {...ya calculadas...},
                            "historico": [...lista de registros diarios...]
                        }
        enviar_slack: si True, ademas de devolver el plan lo manda al
                      webhook de Slack configurado en SLACK_WEBHOOK_URL.

    Returns:
        dict con: diagnostico, recomendacion, explicacion, plan_de_accion,
                  comparacion, fuentes_externas, y (si enviar_slack=True)
                  el resultado del envio en "slack_status".
    """
    nombre_producto = datos_producto["producto"]
    metricas = datos_producto["metricas"]
    historico = datos_producto.get("historico", [])

    resumen_patrones = {}
    if historico:
        df_historico = pd.DataFrame(historico)
        resumen_patrones = resumir_dataframe(df_historico)

    print("Llamando a Exa...")
    contexto_exa = buscar_contexto_externo(nombre_producto)

    print("Llamando a OpenRouter...")
    plan = generar_plan(metricas, resumen_patrones, contexto_exa, nombre_producto)
    plan["fuentes_externas"] = contexto_exa.get("citas", [])

    if enviar_slack:
        print("Enviando a Slack...")
        resultado_envio = enviar_a_slack(plan, nombre_producto)
        plan["slack_status"] = resultado_envio
        print("Resultado del envio:", resultado_envio)

    return plan


if __name__ == "__main__":
    datos_prueba = {
        "producto": "Glaseada Clasica",
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
        "historico": [],
    }

    resultado = generar_recomendacion(datos_prueba)

    import json
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
