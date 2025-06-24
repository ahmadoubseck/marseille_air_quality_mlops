import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(0)
rows = []
for i in range(100):
    ts = datetime.utcnow() - timedelta(hours=i)
    row = {
        "co": np.random.uniform(0, 1),
        "h": np.random.uniform(30, 70),
        "no2": np.random.uniform(5, 50),
        "o3": np.random.uniform(10, 60),
        "p": np.random.uniform(1000, 1020),
        "pm10": np.random.uniform(10, 50),
        "pm25": np.random.uniform(10, 50),
        "so2": np.random.uniform(0, 1),
        "t": np.random.uniform(10, 30),
        "w": np.random.uniform(0, 10),
        "wg": np.random.uniform(0, 20),
        "aqi": np.random.uniform(30, 100),
        "timestamp": ts
    }
    rows.append(row)

df = pd.DataFrame(rows)
df.to_csv("data/features_history2.csv", index=False)
print("Faux dataset généré : data/features_history2.csv")
