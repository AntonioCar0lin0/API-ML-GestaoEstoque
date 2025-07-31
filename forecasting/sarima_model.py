# Treinamento com SARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_squared_error
import numpy as np

def treinar_sarima(serie):
    modelo = SARIMAX(serie, order=(1,1,1), seasonal_order=(1,1,1,7))
    return modelo

def avaliar_sarima(modelo, serie, horizon=15):
    treino = serie[:-horizon]
    teste = serie[-horizon:]

    try:
        fitted = modelo.fit(disp=False)
        preds = fitted.forecast(steps=horizon)
        rmse = np.sqrt(mean_squared_error(teste, preds))
        return rmse
    except Exception:
        return np.inf
