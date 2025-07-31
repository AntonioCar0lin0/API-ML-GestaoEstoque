import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_squared_error

# Gerar série temporal fictícia
np.random.seed(42)
datas = pd.date_range(start="2023-01-01", periods=100)
valores = np.cumsum(np.random.randn(100) * 5 + 50)
serie = pd.Series(valores, index=datas)

# Dividir em treino e teste
horizon = 15
treino = serie[:-horizon]
teste = serie[-horizon:]

# Treinar modelos
arima_model = ARIMA(treino, order=(1, 1, 1)).fit()
sarima_model = SARIMAX(treino, order=(1, 1, 1), seasonal_order=(1, 1, 1, 7)).fit()

# Prever
arima_preds = arima_model.forecast(steps=horizon)
sarima_preds = sarima_model.forecast(steps=horizon)

# RMSE
rmse_arima = np.sqrt(mean_squared_error(teste, arima_preds))
rmse_sarima = np.sqrt(mean_squared_error(teste, sarima_preds))

# Plot
plt.figure(figsize=(12, 6))
plt.plot(serie, label='Histórico', color='blue')
plt.plot(teste.index, arima_preds, '--', label=f'ARIMA (RMSE={rmse_arima:.2f})', color='orange')
plt.plot(teste.index, sarima_preds, '--', label=f'SARIMA (RMSE={rmse_sarima:.2f})', color='green')
plt.title("Previsão ARIMA vs SARIMA (usando statsmodels)")
plt.xlabel("Data")
plt.ylabel("Valor")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
