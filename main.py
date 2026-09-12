from fastapi import FastAPI
from services.funciones import construir_contexto, construir_blocks,enviar_a_slack
from funcion_llamada.main import generar_recomendacion



app = FastAPI()

@app.get("/")
def prueba_funcionamiento():
    return {"mensaje": "API de Newstycs funcionando"}

@app.post("/")
def enviar_analisis():
    datos = construir_contexto("Glaseada Clásica")
    resultado = generar_recomendacion(datos)

    blocks = construir_blocks(resultado)

    enviar_a_slack(blocks)  

    return {
        "ok": True,
        "mensaje": "Análisis enviado a Slack"
    }