
import os
import requests
import pandas as pd
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("PURPLEAIR_API_KEY")
if not API_KEY:
    raise ValueError("API Key não definida. Verifique seu .env")

SENSOR_ID =  247259
BASE_URL = "https://api.purpleair.com/v1"

def fetch_current(sensor_id: int = SENSOR_ID) -> pd.DataFrame:
    """Retorna dados atuais do sensor PurpleAir pelo sensor_id."""
    url = f"{BASE_URL}/sensors/{sensor_id}"
    headers = {
        "X-API-Key": API_KEY,
        "Accept": "application/json"
    }
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    data = r.json().get("sensor", {})
    if not data:
        return pd.DataFrame()
    # Extrai timestamp e dados principais
    dt = pd.to_datetime(data.get("last_seen", None), unit="s") if data.get("last_seen") else None
    data["dt"] = dt
    return pd.DataFrame([data])

def debug_api_request():
    url = f"{BASE_URL}/sensors/{SENSOR_ID}"
    headers = {
        "X-API-Key": API_KEY,
        "Accept": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as e:
        print(f"Erro de requisição: {e}")
        return

    print("Response Headers:", response.headers)
    print("Response Content:")
    print(response.text)

    try:
        json_response = response.json()
        print("\nJSON Response:")
        print(json_response)
    except requests.exceptions.JSONDecodeError:
        print("Não foi possível decodificar a resposta como JSON")

if __name__ == "__main__":
    debug_api_request()
def fetch_forecast(sensor_id: int = SENSOR_ID) -> pd.DataFrame:
    """
    Retorna as estatísticas do sensor PurpleAir como previsão aproximada.
    Usa o campo 'stats' do JSON de resposta.
    """
    url = f"{BASE_URL}/sensors/{sensor_id}"
    headers = {
        "X-API-Key": API_KEY,
        "Accept": "application/json"
    }
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    data = r.json().get("sensor", {})
    stats = data.get("stats", {})
    if not stats:
        return pd.DataFrame()

    # Extrai timestamp e converte para datetime
    ts = stats.pop("time_stamp", None)
    dt = pd.to_datetime(ts, unit="s") if ts else None

    # Converte o restante do dict em DataFrame
    df_stats = pd.DataFrame([stats])
    df_stats["dt"] = dt

    # Renomeia colunas pm2.5 para pm2_5
    df_stats.rename(columns={c: c.replace("pm2.5", "pm2_5") for c in df_stats.columns}, inplace=True)
    return df_stats