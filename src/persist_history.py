# src/persist_history.py

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from collectors import fetch_current # importa sua função de coleta

load_dotenv()  # carrega OPENWEATHER_API_KEY do .env

def persist_history(lat: float, lon: float, 
                    file_path: str = "data/historical.csv") -> None:
    """
    Busca a leitura atual de qualidade do ar e salva (append) em CSV.
    - Se o CSV não existir, cria com cabeçalho.
    - Se existir, faz append, removendo eventuais duplicatas por timestamp.
    """
    # 1) Coleta a linha atual
    df_new = fetch_current(sensor_id=247259)
    if df_new.empty:
        print("Nenhuma leitura disponível para persistir.")
        return

    # 2) Garante que a pasta existe
    data_file = Path(file_path)
    data_file.parent.mkdir(parents=True, exist_ok=True)

    # 3) Se o CSV já existe, carrega e concatena
    if data_file.exists():
        df_old = pd.read_csv(data_file, parse_dates=["dt"])
        df = pd.concat([df_old, df_new], ignore_index=True)
        # remove duplicatas de timestamp
        df = df.drop_duplicates(subset=["dt"]).sort_values("dt")
    else:
        df = df_new

    # 4) Salva de volta
    df.to_csv(data_file, index=False)
    print(f"Persistidos {len(df_new)} registros em {data_file}")

if __name__ == "__main__":
    # Exemplo para Rio de Janeiro
    LAT, LON = -22.90, -43.20
    persist_history(LAT, LON)
