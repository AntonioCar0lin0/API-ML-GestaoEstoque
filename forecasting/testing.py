import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pmdarima import auto_arima
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
arima = auto_arima(treino, seasonal=False)
sarima = auto_arima(treino, seasonal=True, m=7)

# Prever
arima_preds = arima.predict(n_periods=horizon)
sarima_preds = sarima.predict(n_periods=horizon)

# RMSE
rmse_arima = np.sqrt(mean_squared_error(teste, arima_preds))
rmse_sarima = np.sqrt(mean_squared_error(teste, sarima_preds))

# Plot
plt.figure(figsize=(12, 6))
plt.plot(serie, label='Histórico', color='blue')
plt.plot(teste.index, arima_preds, '--', label=f'ARIMA (RMSE={rmse_arima:.2f})', color='orange')
plt.plot(teste.index, sarima_preds, '--', label=f'SARIMA (RMSE={rmse_sarima:.2f})', color='green')
plt.title("Previsão ARIMA vs SARIMA")
plt.xlabel("Data")
plt.ylabel("Valor")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()