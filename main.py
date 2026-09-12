from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def prueba_funcionamiento():
    return {"mensaje": "API de Newstycs funcionando"}

