from fastapi import FastAPI
from routes.analytics_route import router as analytics_router

app = FastAPI()

# Conecta suas rotas
app.include_router(analytics_router)

@app.get("/")
def root():
    return {"message": "API de ML conectada com sucesso!"}
