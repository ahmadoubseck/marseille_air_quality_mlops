import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import joblib
import os

def load_data():
    df = pd.read_csv("data/features_history.csv")
    X = df.drop(columns=["aqi", "timestamp"], errors="ignore")
    y = df["aqi"]
    return X, y

def train_model(X, y):
    # Split : 80% entraînement, 20% test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    model = xgb.XGBRegressor()
    model.fit(X_train, y_train)
    
    # Évaluation
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    mae_train = mean_absolute_error(y_train, y_pred_train)
    mae_test = mean_absolute_error(y_test, y_pred_test)
    
    print(f"MAE sur les données d'entraînement : {mae_train:.2f}")
    print(f"MAE sur les données de test : {mae_test:.2f}")
    
    # Sauvegarde
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/aqi_model.pkl")
    print("✅ Modèle sauvegardé dans models/aqi_model.pkl")

if __name__ == "__main__":
    X, y = load_data()
    train_model(X, y)
