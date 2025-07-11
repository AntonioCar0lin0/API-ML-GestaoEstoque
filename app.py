from pydantic import BaseModel
from fastapi import FastAPI

app = FastAPI()

class Input(BaseModel):
    instances: list[list[float]]

@app.post("/predict")
def predict(data: Input):
    return {"predictions": [sum(x) for x in data.instances]}
