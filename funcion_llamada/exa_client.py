import os
import requests
from dotenv import load_dotenv

load_dotenv()

EXA_API_KEY = os.getenv("EXA_API_KEY")
EXA_ANSWER_URL = "https://api.exa.ai/answer"


def buscar_contexto_externo(nombre_producto: str) -> dict:
    """
    Consulta Exa para traer tendencias de temporada y eventos comerciales
    próximos relevantes al producto.

    Returns:
        dict con:
          - "respuesta": texto de la respuesta de Exa (con contexto ya sintetizado)
          - "citas": lista de fuentes que Exa usó para responder
    """
    if not EXA_API_KEY:
        raise RuntimeError("Falta EXA_API_KEY en el archivo .env")

    query = (
        f"Tendencias de temporada actuales y eventos comerciales o fechas "
        f"especiales próximas relevantes para la venta de {nombre_producto} "
        f"en panaderías/donerías en México."
    )

    headers = {
        "Authorization": f"Bearer {EXA_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "query": query,
        "text": True,
    }

    try:
        respuesta = requests.post(
            EXA_ANSWER_URL, headers=headers, json=payload, timeout=15
        )
        respuesta.raise_for_status()
        data = respuesta.json()
    except requests.exceptions.RequestException as e:
        # Si Exa falla, no debe tumbar todo el flujo — regresamos vacío
        # y el prompt de OpenRouter simplemente razona solo con el histórico.
        return {
            "respuesta": "",
            "citas": [],
            "error": str(e),
        }

    return {
        "respuesta": data.get("answer", ""),
        "citas": [c.get("url", "") for c in data.get("citations", [])],
    }


if __name__ == "__main__":
    resultado = buscar_contexto_externo("dona glaseada clásica")
    import json
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
