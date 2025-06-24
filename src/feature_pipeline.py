import requests
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
CITY = os.getenv("CITY")

def fetch_aqi_data():
    url = f"https://api.waqi.info/feed/{CITY}/?token={API_TOKEN}"
    response = requests.get(url)
    data = response.json()
    if data["status"] != "ok":
        raise Exception("API Error: " + data.get("data", {}).get("message", "Unknown error"))
    return data["data"]

def process_data(raw_data):
    ts = datetime.utcnow()
    aqi = raw_data["aqi"]
    iaqi = raw_data.get("iaqi", {})
    features = {key: iaqi[key]["v"] for key in iaqi}
    features["aqi"] = aqi
    features["timestamp"] = ts
    return pd.DataFrame([features])

if __name__ == "__main__":
    raw = fetch_aqi_data()
    df = process_data(raw)
    os.makedirs("data", exist_ok=True)
    file_path = "data/features_history.csv"
    if os.path.exists(file_path):
        df.to_csv(file_path, mode="a", header=False, index=False)
    else:
        df.to_csv(file_path, index=False)
    print(f"Data appended to {file_path}")
