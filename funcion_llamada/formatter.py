import os
import requests
from dotenv import load_dotenv

load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


def construir_bloques_slack(plan: dict, nombre_producto: str) -> list:
    """
    Convierte el dict que devuelve generar_recomendacion() en bloques de
    Slack Block Kit, para que se vea como un mini-documento (encabezado,
    secciones, campos en negrita).

    Args:
        plan: dict con diagnostico, recomendacion, explicacion,
              plan_de_accion, comparacion, fuentes_externas.
        nombre_producto: nombre del producto analizado.

    Returns:
        list de bloques listos para el payload de Slack.
    """
    comparacion = plan.get("comparacion", {})
    recomendacion = plan.get("recomendacion", {})
    plan_accion = plan.get("plan_de_accion", {})
    fuentes = plan.get("fuentes_externas", [])

    bloques = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"Recomendacion de inventario: {nombre_producto}",
                "emoji": True,
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f":bar_chart: *Ahorro estimado del agente:* "
                    f"${comparacion.get('ahorro_estimado_pesos', 0):,.2f} MXN "
                    f"({comparacion.get('diferencia_unidades', 0)} unidades "
                    f"menos de desperdicio vs. la formula ingenua)"
                ),
            },
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Diagnostico:*\n{plan.get('diagnostico', 'N/A')}",
            },
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Escenario bajo:*\n{recomendacion.get('escenario_bajo', 'N/A')}",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Escenario esperado:*\n{recomendacion.get('escenario_esperado', 'N/A')}",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Escenario alto:*\n{recomendacion.get('escenario_alto', 'N/A')}",
                },
            ],
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Explicacion:*\n{plan.get('explicacion', 'N/A')}",
            },
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"*Plan de accion*\n"
                    f"• *Que hacer:* {plan_accion.get('que_hacer', 'N/A')}\n"
                    f"• *Cuando:* {plan_accion.get('cuando', 'N/A')}\n"
                    f"• *Riesgo si no se sigue:* {plan_accion.get('riesgo_si_no_se_sigue', 'N/A')}"
                ),
            },
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Formula ingenua:*\n{comparacion.get('formula_ingenua_unidades', 'N/A')} unidades",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Recomendacion del agente:*\n{comparacion.get('agente_unidades', 'N/A')} unidades",
                },
            ],
        },
    ]

    if fuentes:
        texto_fuentes = "\n".join(f"• {url}" for url in fuentes[:5])
        bloques.append({"type": "divider"})
        bloques.append(
            {
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": f"*Fuentes consultadas:*\n{texto_fuentes}"}
                ],
            }
        )

    return bloques


def enviar_a_slack(plan: dict, nombre_producto: str) -> dict:
    """
    Arma el mensaje en Block Kit y lo envia al webhook de Slack (o a la
    URL de pruebas configurada en SLACK_WEBHOOK_URL).

    Returns:
        dict con "ok": bool y "status_code" o "error".
    """
    if not SLACK_WEBHOOK_URL:
        raise RuntimeError("Falta SLACK_WEBHOOK_URL en el archivo .env")

    bloques = construir_bloques_slack(plan, nombre_producto)
    payload = {"blocks": bloques}

    try:
        respuesta = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
        respuesta.raise_for_status()
        return {"ok": True, "status_code": respuesta.status_code}
    except requests.exceptions.RequestException as e:
        return {"ok": False, "error": str(e)}


if __name__ == "__main__":
    plan_prueba = {
        "diagnostico": "Se detecto un patron de demanda con caidas los lunes y picos el fin de semana.",
        "recomendacion": {
            "escenario_bajo": 200,
            "escenario_esperado": 230,
            "escenario_alto": 260,
        },
        "explicacion": "La recomendacion considera la estacionalidad detectada y el proximo Dia de la Dona.",
        "plan_de_accion": {
            "que_hacer": "Aumentar produccion 10% para el fin de semana",
            "cuando": "A partir del proximo viernes",
            "riesgo_si_no_se_sigue": "Perdida estimada de $500 MXN y desperdicio de insumos (harina, azucar, aceite)",
        },
        "comparacion": {
            "formula_ingenua_unidades": 255,
            "agente_unidades": 230,
            "diferencia_unidades": 25,
            "ahorro_estimado_pesos": 162.5,
        },
        "fuentes_externas": ["https://ejemplo.com/nota1"],
    }

    resultado = enviar_a_slack(plan_prueba, "Glaseada Clasica")
    print(resultado)
