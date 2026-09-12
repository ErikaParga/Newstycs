import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODELO = "openrouter/free"


PROMPT_SISTEMA = """Eres un analista de inventario experto en el problema del \
vendedor de periódicos (cantidad óptima de pedido bajo demanda incierta), \
especializado en productos de panadería con alta rotación diaria.

Vas a recibir:
1. Métricas ya calculadas y agregadas del histórico de ventas de un producto \
(totales y tasas).
2. Un resumen adicional de patrones (por ejemplo, comportamiento por día de la \
semana o por eventos especiales), si está disponible.
3. Contexto externo actual (tendencias de temporada, eventos próximos) \
obtenido de una búsqueda web.

Tu tarea es generar un plan de acción razonado, y devolver ÚNICAMENTE un JSON \
válido (sin texto antes ni después, sin markdown) con exactamente esta estructura:

{
  "diagnostico": "string: qué patrones detectaste (tendencia, estacionalidad, efecto de promociones/eventos)",
  "recomendacion": {
    "escenario_bajo": number,
    "escenario_esperado": number,
    "escenario_alto": number
  },
  "explicacion": "string: por qué llegaste a esa recomendación, citando factores del diagnóstico y del contexto externo",
  "plan_de_accion": {
    "que_hacer": "string",
    "cuando": "string",
    "riesgo_si_no_se_sigue": "string, incluye costo económico y de recursos si aplica"
  },
  "comparacion": {
    "formula_ingenua_unidades": number,
    "agente_unidades": number,
    "diferencia_unidades": number,
    "ahorro_estimado_pesos": number
  }
}

Reglas:
- Los números en "comparacion" deben basarse en las métricas entregadas, no \
inventados. "formula_ingenua_unidades" sale de la producción total histórica \
de la fórmula ingenua; "agente_unidades" es tu recomendación (escenario \
esperado) escalada al mismo periodo si aplica.
- Si el contexto externo no aporta nada útil (viene vacío), basa tu análisis \
solo en las métricas y el resumen de patrones, y dilo en el diagnóstico.
- Nunca agregues texto fuera del JSON.
"""


def generar_plan(
    metricas: dict,
    resumen_patrones: dict,
    contexto_exa: dict,
    nombre_producto: str,
) -> dict:
    """
    Arma el prompt combinando las métricas ya calculadas + el resumen de
    patrones del histórico + contexto externo, llama a OpenRouter y
    devuelve el plan ya parseado como dict.

    Args:
        metricas: dict con métricas agregadas (producción, ventas,
                  desperdicio, tasas, ingresos, etc.) tal como las manda
                  la compañera encargada del filtrado.
        resumen_patrones: dict opcional con patrones adicionales detectados
                           en el histórico (ej. por día de semana).
        contexto_exa: dict con "respuesta" y "citas" de buscar_contexto_externo.
        nombre_producto: nombre/SKU del producto.
    """
    if not OPENROUTER_API_KEY:
        raise RuntimeError("Falta OPENROUTER_API_KEY en el archivo .env")

    prompt_usuario = f"""Producto: {nombre_producto}

Métricas agregadas del histórico:
{json.dumps(metricas, ensure_ascii=False, indent=2)}

Resumen de patrones adicionales (si viene vacío, ignóralo):
{json.dumps(resumen_patrones, ensure_ascii=False, indent=2)}

Contexto externo (búsqueda web reciente):
{contexto_exa.get("respuesta", "(sin contexto externo disponible)")}
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODELO,
        "messages": [
            {"role": "system", "content": PROMPT_SISTEMA},
            {"role": "user", "content": prompt_usuario},
        ],
        "response_format": {"type": "json_object"},
    }

    respuesta = requests.post(
        OPENROUTER_URL, headers=headers, json=payload, timeout=30
    )
    respuesta.raise_for_status()
    data = respuesta.json()

    contenido = data["choices"][0]["message"]["content"]

    try:
        plan = json.loads(contenido)
    except json.JSONDecodeError:
        inicio = contenido.find("{")
        fin = contenido.rfind("}") + 1
        plan = json.loads(contenido[inicio:fin])

    return plan


if __name__ == "__main__":
    metricas_prueba = {
        "produccion_total": 93360,
        "ventas_totales": 81252,
        "desperdicio_total": 12108,
        "ventas_perdidas_total": 12209,
        "tasa_desperdicio": 0.13,
        "tasa_faltante": 0.13,
        "ingreso_total": 1462536,
        "costo_desperdicio_total": 78702.0,
    }
    contexto_prueba = {"respuesta": "Próxima quincena y Día Nacional de la Dona."}
    resultado = generar_plan(metricas_prueba, {}, contexto_prueba, "Glaseada Clásica")
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
