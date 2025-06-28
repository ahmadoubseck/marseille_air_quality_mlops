"""
import streamlit as st
import pandas as pd
import joblib

st.title("Prédictions AQI - Marseille")

model = joblib.load("models/aqi_model.pkl")
df = pd.read_csv("data/features_history.csv")
X = df.drop(columns=["aqi", "timestamp"])
prediction = model.predict(X)

st.write("Prédiction AQI actuelle : ", prediction[0])
st.write(df)
"""
import streamlit as st
import pandas as pd
import joblib
import os # Importation du module os pour manipuler les chemins de fichiers

st.title("Prédictions AQI - Marseille")

# --- Modification des chemins de fichiers ---

# Obtenez le répertoire du script actuel (où se trouve predict_app.py)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construisez le chemin absolu vers le fichier du modèle.
# On remonte d'un niveau (..) depuis 'src' pour atteindre la racine du dépôt,
# puis on descend dans le dossier 'models'.
model_path = os.path.join(current_dir, '..', 'models', 'aqi_model.pkl')

# Construisez le chemin absolu vers le fichier de données CSV.
# Similaire au chemin du modèle, on remonte d'un niveau (..) puis on descend dans 'data'.
data_path = os.path.join(current_dir, '..', 'data', 'features_history.csv')

# --- Chargement des ressources ---

try:
    # Charge le modèle Joblib en utilisant le chemin corrigé
    model = joblib.load(model_path)
    st.success(f"Modèle chargé depuis : {model_path}") # Message de succès pour le débogage
except FileNotFoundError:
    st.error(f"Erreur: Le fichier modèle n'a pas été trouvé à {model_path}. Assurez-vous qu'il est bien présent et poussé sur GitHub.")
    st.stop() # Arrête l'exécution de l'application si le modèle n'est pas trouvé
except Exception as e:
    st.error(f"Une erreur inattendue est survenue lors du chargement du modèle : {e}")
    st.stop()

try:
    # Charge le DataFrame depuis le fichier CSV en utilisant le chemin corrigé
    df = pd.read_csv(data_path)
    st.success(f"Données chargées depuis : {data_path}") # Message de succès pour le débogage
except FileNotFoundError:
    st.error(f"Erreur: Le fichier de données n'a pas été trouvé à {data_path}. Assurez-vous qu'il est bien présent et poussé sur GitHub.")
    st.stop()
except Exception as e:
    st.error(f"Une erreur inattendue est survenue lors du chargement des données : {e}")
    st.stop()

# --- Prédiction et affichage ---

# Assurez-vous que les colonnes 'aqi' et 'timestamp' existent avant de les supprimer
# et que le DataFrame n'est pas vide
if not df.empty and "aqi" in df.columns and "timestamp" in df.columns:
    X = df.drop(columns=["aqi", "timestamp"])
    try:
        prediction = model.predict(X)
        st.write("Prédiction AQI actuelle : ", prediction[0])
    except Exception as e:
        st.error(f"Erreur lors de la prédiction : {e}")
else:
    st.warning("Le fichier de données est vide ou ne contient pas les colonnes attendues ('aqi', 'timestamp'). Impossible de faire la prédiction.")


st.subheader("Données d'Historique utilisées :")
st.write(df)

