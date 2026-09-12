import pandas as pd
import requests
import os

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


def construir_blocks(resultado: dict) -> list:
    recomendacion = resultado["recomendacion"]
    plan = resultado["plan_de_accion"]
    comparacion = resultado["comparacion"]

    fuentes = resultado.get("fuentes_externas", [])

    # Convertir las URLs en enlaces de Slack
    fuentes_texto = "\n".join(
        f"• <{url}|Fuente {i + 1}>"
        for i, url in enumerate(fuentes)
    )

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Análisis de demanda"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    "*Diagnóstico*\n"
                    f"{resultado['diagnostico']}"
                )
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    "*Recomendación de producción*\n"
                    f"• Escenario bajo: *{recomendacion['escenario_bajo']} unidades*\n"
                    f"• Escenario esperado: *{recomendacion['escenario_esperado']} unidades*\n"
                    f"• Escenario alto: *{recomendacion['escenario_alto']} unidades*"
                )
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    "*Explicación*\n"
                    f"{resultado['explicacion']}"
                )
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    "*Plan de acción*\n"
                    f"*Qué hacer:* {plan['que_hacer']}\n"
                    f"*Cuándo:* {plan['cuando']}\n"
                    f"*Riesgo si no se sigue:* {plan['riesgo_si_no_se_sigue']}"
                )
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    "*Comparación*\n"
                    f"Fórmula ingenua: *{comparacion['formula_ingenua_unidades']} unidades*\n"
                    f"Agente: *{comparacion['agente_unidades']} unidades*\n"
                    f"Diferencia: *{comparacion['diferencia_unidades']} unidades*\n"
                    f"Ahorro estimado: *${comparacion['ahorro_estimado_pesos']:,.2f} MXN*"
                )
            }
        }
    ]

    if fuentes_texto:
        blocks.extend([
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🔗 Fuentes externas*\n{fuentes_texto}"
                }
            }
        ])

    return blocks

def enviar_a_slack(blocks: list) -> None:
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")

    response = requests.post(
        webhook_url,
        json={"blocks": blocks},
        timeout=10
    )

    response.raise_for_status()