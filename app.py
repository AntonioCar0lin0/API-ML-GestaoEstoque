
# Arquivo principal para configurar o cors, iniciar a aplicação e rotas
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.analytics_route import router as analytics_router
import logging

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analytics_router, prefix="/analytics")
logging.basicConfig(level=logging.DEBUG)
