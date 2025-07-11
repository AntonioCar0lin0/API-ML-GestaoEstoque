from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()

class PredictionRequest(BaseModel):
    instances: list[list[float]]  # ou conforme seu modelo

@router.post("/predict")
def predict(request: PredictionRequest):
    # Simulação de modelo
    resultados = [sum(instancia) for instancia in request.instances]
    return {"predictions": resultados}
