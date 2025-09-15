# src/model.py

import pandas as pd
from pathlib import Path
from statsmodels.tsa.arima.model import ARIMA

def train_arima(history_csv: str = "data/historical.csv",
                column: str = "pm2.5",
                order: tuple = (1,1,1)):
    """
    Carrega o histórico de qualidade do ar, treina um ARIMA(p,d,q) e retorna o modelo ajustado.
    - history_csv: caminho para data/historical.csv
    - column: nome da coluna de série temporal (ex: 'pm2.5')
    - order: tupla (p, d, q)
    """
    path = Path(history_csv)
    if not path.exists():
        raise FileNotFoundError(f"{history_csv} não encontrado.")
    # 1) Carrega e prepara série temporal
    df = pd.read_csv(path, parse_dates=["dt"])
    df = df.set_index("dt").sort_index()
    ts = df[column].asfreq("H")  # garante frequência horária
    ts = ts.fillna(method="ffill")  # preenche gaps
    
    # 2) Ajusta o modelo
    model = ARIMA(ts, order=order)
    model_fit = model.fit()
    return model_fit

def forecast_arima(model_fit, steps: int = 24):
    """
    Recebe um modelo ARIMA ajustado e faz previsões para as próximas `steps` horas.
    Retorna um DataFrame com colunas ['dt','forecast'].
    """
    # gera forecast
    fc = model_fit.get_forecast(steps=steps)
    df_fc = fc.summary_frame()  # inclui mean, ci_lower, ci_upper
    df_fc = df_fc.reset_index().rename(columns={"index":"dt","mean":"forecast"})
    return df_fc[["dt","forecast","mean_ci_lower","mean_ci_upper"]]

if __name__ == "__main__":
    # Teste rápido
    model = train_arima(order=(1,1,1))
    df_pred = forecast_arima(model, steps=24)
    print(df_pred)
