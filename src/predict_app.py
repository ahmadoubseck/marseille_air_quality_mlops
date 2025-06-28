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
# Le module 'os' a été retiré ici, comme demandé, mais cela peut réintroduire FileNotFoundError sur Streamlit Cloud.
# Pour une solution robuste, référez-vous à la version précédente qui utilisait 'os.path'.

st.set_page_config(layout="centered", page_title="Prédictions AQI Marseille", page_icon="🍃")

st.title("☀️ Prédictions AQI - Marseille")

# Description de l'application
st.markdown(
    """
    Bienvenue sur l'application de prédiction de la qualité de l'air (AQI) pour Marseille.
    Cette application utilise un modèle d'apprentissage automatique pour prévoir l'indice de qualité de l'air.
    """
)

# --- Chargement des ressources (reverté à l'original, ce qui risque de causer une FileNotFoundError) ---
# ATTENTION: Les chemins ci-dessous sont relatifs et peuvent échouer sur Streamlit Cloud si les fichiers
# ne sont pas à la racine de l'exécution ou s'ils ne sont pas poussés sur GitHub.
# Si vous rencontrez "FileNotFoundError", veuillez utiliser la méthode 'os.path' de la version précédente
# pour rendre les chemins robustes.
try:
    model = joblib.load("models/aqi_model.pkl")
    # st.success("Modèle chargé (chemin d'origine)") # Ce message n'est pas affiché pour garder l'interface propre
except FileNotFoundError:
    st.error("❌ Erreur: Le fichier modèle 'models/aqi_model.pkl' n'a pas été trouvé. Assurez-vous qu'il est bien présent dans votre dépôt GitHub et que le chemin est correct.")
    st.info("💡 **Solution possible:** Si vous voyez cette erreur sur Streamlit Cloud, vos fichiers ne sont peut-être pas poussés sur GitHub ou le chemin relatif est incorrect. Référez-vous aux étapes précédentes pour le `.gitignore` et les chemins absolus (`os.path`).")
    st.stop() # Arrête l'exécution de l'application si le modèle n'est pas trouvé
except Exception as e:
    st.error(f"❌ Une erreur inattendue est survenue lors du chargement du modèle : {e}")
    st.stop()

try:
    df = pd.read_csv("data/features_history.csv")
    # st.success("Données chargées (chemin d'origine)") # Ce message n'est pas affiché pour garder l'interface propre
except FileNotFoundError:
    st.error("❌ Erreur: Le fichier de données 'data/features_history.csv' n'a pas été trouvé. Assurez-vous qu'il est bien présent dans votre dépôt GitHub et que le chemin est correct.")
    st.info("💡 **Solution possible:** Similaire au modèle, vérifiez que le fichier de données est bien poussé et que son chemin est correct.")
    st.stop()
except Exception as e:
    st.error(f"❌ Une erreur inattendue est survenue lors du chargement des données : {e}")
    st.stop()
# --- Fin du chargement des ressources (reverté) ---

# --- Prédiction initiale et affichage (basé sur les données historiques) ---
st.header("📊 Données Historiques et Prédiction Initiale")

if not df.empty and "aqi" in df.columns and "timestamp" in df.columns:
    X_historical = df.drop(columns=["aqi", "timestamp"])
    try:
        prediction_historical = model.predict(X_historical)
        st.write("---")
        st.markdown(f"### 📈 Prédiction AQI basée sur les données historiques :")
        st.markdown(f"<h1 style='text-align: center; color: #4CAF50;'>{prediction_historical[0]:.2f}</h1>", unsafe_allow_html=True)
        st.write("Cet indice représente la qualité de l'air pour la période la plus récente dans les données historiques.")
        st.write("---")
    except Exception as e:
        st.error(f"❌ Erreur lors de la prédiction avec les données historiques : {e}")
else:
    st.warning("⚠️ Le fichier de données historiques est vide ou ne contient pas les colonnes attendues ('aqi', 'timestamp'). Impossible de faire la prédiction historique.")

st.subheader("Visualisation des Données Historiques")
st.dataframe(df) # Utilisation de st.dataframe pour un affichage interactif

# --- Amélioration du front : Section de prédiction interactive ---
st.markdown("---") # Séparateur visuel
st.header("✨ Faire une Nouvelle Prédiction AQI (Simulation)")
st.write("Utilisez le panneau latéral pour ajuster les paramètres environnementaux et simuler une prédiction de la qualité de l'air.")

# Sidebars pour les inputs utilisateur
st.sidebar.header("🎚️ Paramètres pour la Simulation")
st.sidebar.info("**Note:** Les noms et le nombre de ces paramètres (`température`, `humidité`, etc.) *doivent correspondre* exactement aux caractéristiques que votre modèle (`aqi_model.pkl`) a appris à partir de vos données d'entraînement. Ajustez-les si nécessaire.")

# Input fields for new prediction - exemples basés sur des features communes
# Ajustez ces sliders pour qu'ils correspondent aux caractéristiques réelles de votre modèle
temp_input = st.sidebar.slider("Température (°C)", min_value=-20.0, max_value=50.0, value=15.0, step=0.1)
humidity_input = st.sidebar.slider("Humidité (%)", min_value=0, max_value=100, value=70, step=1)
wind_speed_input = st.sidebar.slider("Vitesse du Vent (km/h)", min_value=0.0, max_value=100.0, value=10.0, step=0.1)
# Si votre modèle utilise d'autres caractéristiques (ex: niveaux de polluants spécifiques), ajoutez-les ici.
# Exemple:
pm25_input = st.sidebar.slider("Niveau de PM2.5 (µg/m³)", min_value=0.0, max_value=200.0, value=30.0, step=1.0)
# Ajoutez d'autres sliders ou entrées numériques si votre modèle utilise plus de caractéristiques

# Créer un DataFrame pour l'entrée utilisateur
# IMPORTANT: Les noms de colonnes doivent ABSOLUMENT correspondre aux noms des caractéristiques
# que votre modèle attend. Modifiez 'temperature', 'humidity', 'wind_speed', 'pm25_level'
# pour qu'ils correspondent à vos noms de caractéristiques réels.
user_input_data = {
    'temperature': [temp_input],
    'humidity': [humidity_input],
    'wind_speed': [wind_speed_input],
    'pm25_level': [pm25_input] # Assurez-vous que ce nom correspond à une caractéristique de votre modèle
}
user_input_df = pd.DataFrame(user_input_data)

st.write("---")
# Bouton pour déclencher la prédiction simulée
if st.button("🚀 Faire la prédiction simulée"):
    try:
        # Assurez-vous que les colonnes de user_input_df correspondent à celles attendues par le modèle
        # Cela est crucial. Si les colonnes ne sont pas les mêmes ou ne sont pas dans le bon ordre,
        # la prédiction échouera ou sera incorrecte.
        # Idéalement, vous devriez recharger les noms des colonnes du X_historical si disponible
        # ou utiliser les noms de colonnes spécifiques de votre modèle.
        # Pour cet exemple, nous supposons que user_input_df a déjà les bonnes colonnes dans le bon ordre.

        simulated_prediction = model.predict(user_input_df)
        st.success("✅ Prédiction simulée réussie !")
        st.markdown(f"### Prédiction AQI simulée :")
        st.markdown(f"<h1 style='text-align: center; color: #FFD700;'>{simulated_prediction[0]:.2f}</h1>", unsafe_allow_html=True)
        st.info("Ceci est une prédiction basée sur les paramètres que vous avez définis.")
    except Exception as e:
        st.error(f"❌ Erreur lors de la prédiction simulée. Veuillez vérifier que les paramètres du panneau latéral sont corrects et correspondent aux attentes de votre modèle. Détails de l'erreur : {e}")

st.markdown("---")
st.markdown("🌐 Application développée pour l'analyse de la qualité de l'air à Marseille.")
st.markdown("Pour toute question, contactez le support.")
