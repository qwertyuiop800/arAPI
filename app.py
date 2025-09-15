# ...existing imports...
from pathlib import Path
import time
from src.collectors import fetch_current, fetch_forecast
from src.model import train_arima, forecast_arima
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import streamlit as st
import plotly.graph_objs as go
# Atualiza a cada 5 minutos (300000 ms)
st_autorefresh(interval=300000, limit=None, key="refresh")

# -------------------------------------------------------
# Funções para histórico da API
# -------------------------------------------------------
def persist_api_history(df_new, path="data/api_history.csv"):
    if not Path(path).exists() or Path(path).stat().st_size == 0:
        df_new.to_csv(path, index=False)
    else:
        df_old = pd.read_csv(path, parse_dates=["dt"])
        df = pd.concat([df_old, df_new], ignore_index=True)
        df = df.drop_duplicates(subset=["dt"]).sort_values("dt")
        df.to_csv(path, index=False)

def load_api_history(path="data/api_history.csv"):
    if not Path(path).exists():
        return pd.DataFrame()
    df = pd.read_csv(path, parse_dates=["dt"])
    return df

# -------------------------------------------------------
# Carregamento de dados
# -------------------------------------------------------
SENSOR_ID = 247259  # Defina o sensor desejado

def load_historical(path: str = "data/historical.csv") -> pd.DataFrame:
    if not Path(path).exists():
        return pd.DataFrame()
    df = pd.read_csv(path, parse_dates=["dt"])
    df = df.set_index("dt").sort_index()
    return df

def load_current(sensor_id: int) -> pd.DataFrame:
    return fetch_current(sensor_id)

def load_forecast_api(sensor_id: int) -> pd.DataFrame:
    return fetch_forecast(sensor_id)

df_historical    = load_historical()
df_current       = load_current(SENSOR_ID)
model            = train_arima()
df_forecast_arima = forecast_arima(model)
df_forecast_api   = load_forecast_api(SENSOR_ID)

# Salva e carrega histórico da API
persist_api_history(df_forecast_api)
df_api_history = load_api_history()



# ...existing imports and code...

col_names = ["pm2_5", "pm2.5", "pm25", "pm_2_5"]
col1, col2, col3, col4 = st.columns([3,3,3,3])

# ----- Coluna 1: Valor atual de PM2.5 -----
with col1:
    st.subheader("Agora (PM2.5)")
    col_name = next((c for c in col_names if c in df_current.columns), None)
    valor = df_current[col_name].iloc[0] if (col_name and not df_current.empty) else 0
    st.metric(label="Qualidade do Ar", value=valor)

# ----- Coluna 2: Histórico -----
with col2:
    st.subheader("Histórico")
    col_name_hist = next((c for c in col_names if c in df_historical.columns), None)
    if not df_historical.empty and col_name_hist:
        st.line_chart(df_historical[[col_name_hist]])
    else:
        st.write("Nenhum dado histórico disponível.")

# ----- Coluna 3: Previsão ARIMA -----
with col3:
    st.subheader("Previsão ARIMA")
    if not df_forecast_arima.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_forecast_arima["dt"],
            y=df_forecast_arima["forecast"],
            mode="lines",
            name="Previsão",
            line=dict(color="blue")
        ))
        fig.add_trace(go.Scatter(
            x=list(df_forecast_arima["dt"]) + list(df_forecast_arima["dt"][::-1]),
            y=list(df_forecast_arima["mean_ci_upper"]) + list(df_forecast_arima["mean_ci_lower"][::-1]),
            fill="toself",
            fillcolor="rgba(0,100,80,0.2)",
            line=dict(color="rgba(255,255,255,0)"),
            hoverinfo="skip",
            showlegend=False
        ))
        fig.update_layout(
            xaxis_title="Data/Hora",
            yaxis_title="PM2.5",
            margin=dict(t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("Nenhuma previsão ARIMA disponível.")

# ----- Coluna 4: Histórico da API (PurpleAir) -----
with col4:
    st.subheader("Histórico da API (PurpleAir)")
    if not df_api_history.empty:
        fig_api = go.Figure()
        for c in df_api_history.columns:
            if c != "dt":
                fig_api.add_trace(go.Scatter(
                    x=df_api_history["dt"],
                    y=df_api_history[c],
                    mode="lines",
                    name=c
                ))
        fig_api.update_layout(
            xaxis_title="Data/Hora",
            yaxis_title="Valor",
            legend_title="Métricas",
            margin=dict(t=20, b=20)
        )
        st.plotly_chart(fig_api, use_container_width=True)
    else:
        st.write("Nenhum histórico da API disponível.")