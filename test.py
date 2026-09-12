from services.funciones import construir_contexto
from funcion_llamada.main import generar_recomendacion

contexto = construir_contexto("Glaseada Clásica")

resultado = generar_recomendacion(contexto)

print(resultado)