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
import os # Gardons le module 'os' ici pour une solution robuste aux chemins, même si le code actuel ne l'utilise pas explicitement.
          # C'est une bonne pratique pour l'avenir.

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
st.sidebar.info("**Important :** Les noms et le nombre de ces paramètres *doivent correspondre* exactement aux caractéristiques sur lesquelles votre modèle a été entraîné. Ajustez les plages de valeurs si nécessaire pour refléter les données d'entraînement de votre modèle.")

# Input fields for new prediction - Mise à jour pour correspondre aux noms de caractéristiques du modèle
# Les noms de features sont tirés de votre message d'erreur : ['co', 'h', 'no2', 'o3', 'p', 'pm10', 'pm25', 'so2', 't', 'w', 'wg']

st.sidebar.subheader("Polluants")
co_input = st.sidebar.slider("Monoxyde de carbone (co)", min_value=0.0, max_value=50.0, value=5.0, step=0.1)
no2_input = st.sidebar.slider("Dioxyde d'azote (no2)", min_value=0.0, max_value=200.0, value=40.0, step=1.0)
o3_input = st.sidebar.slider("Ozone (o3)", min_value=0.0, max_value=200.0, value=60.0, step=1.0)
pm10_input = st.sidebar.slider("Particules PM10 (pm10)", min_value=0.0, max_value=300.0, value=50.0, step=1.0)
pm25_input = st.sidebar.slider("Particules PM2.5 (pm25)", min_value=0.0, max_value=200.0, value=30.0, step=1.0)
so2_input = st.sidebar.slider("Dioxyde de soufre (so2)", min_value=0.0, max_value=100.0, value=10.0, step=0.1)

st.sidebar.subheader("Conditions Météo")
t_input = st.sidebar.slider("Température (°C) (t)", min_value=-20.0, max_value=50.0, value=15.0, step=0.1)
h_input = st.sidebar.slider("Humidité (%) (h)", min_value=0, max_value=100, value=70, step=1)
p_input = st.sidebar.slider("Pression (hPa) (p)", min_value=900.0, max_value=1100.0, value=1013.0, step=0.1)
w_input = st.sidebar.slider("Vitesse du Vent (km/h) (w)", min_value=0.0, max_value=100.0, value=10.0, step=0.1)
wg_input = st.sidebar.slider("Rafale de Vent (km/h) (wg)", min_value=0.0, max_value=150.0, value=20.0, step=0.1)


# Créer un DataFrame pour l'entrée utilisateur avec les noms de colonnes corrects
# IMPORTANT: L'ordre des colonnes ici DOIT correspondre à l'ordre attendu par votre modèle
# lors de l'entraînement. Si vous n'êtes pas sûr de l'ordre, il est préférable de le récupérer
# du DataFrame d'entraînement X_historical si possible. Pour l'instant, nous utilisons l'ordre alphabétique
# des features données dans l'erreur, ou l'ordre que vous avez en tête pour votre modèle.
# Voici l'ordre tel qu'il apparaît dans votre message d'erreur pour les features attendues par le modèle:
# ['co', 'h', 'no2', 'o3', 'p', 'pm10', 'pm25', 'so2', 't', 'w', 'wg']
user_input_data = {
    'co': [co_input],
    'h': [h_input],
    'no2': [no2_input],
    'o3': [o3_input],
    'p': [p_input],
    'pm10': [pm10_input],
    'pm25': [pm25_input],
    'so2': [so2_input],
    't': [t_input],
    'w': [w_input],
    'wg': [wg_input]
}
user_input_df = pd.DataFrame(user_input_data)

st.write("---")
# Bouton pour déclencher la prédiction simulée
if st.button("🚀 Faire la prédiction simulée"):
    try:
        simulated_prediction = model.predict(user_input_df)
        st.success("✅ Prédiction simulée réussie !")
        st.markdown(f"### Prédiction AQI simulée :")
        st.markdown(f"<h1 style='text-align: center; color: #FFD700;'>{simulated_prediction[0]:.2f}</h1>", unsafe_allow_html=True)
        st.info("Ceci est une prédiction basée sur les paramètres que vous avez définis.")
    except Exception as e:
        st.error(f"❌ Erreur lors de la prédiction simulée. Veuillez vérifier que les paramètres du panneau latéral sont corrects et correspondent aux attentes de votre modèle. Détails de l'erreur : {e}")
        st.info("💡 **Conseil :** L'erreur 'feature_names mismatch' indique que les noms de colonnes ou leur ordre ne correspondent pas à ce que le modèle a appris. Assurez-vous que les sliders correspondent aux caractéristiques d'entraînement.")

st.markdown("---")
st.markdown("🌐 Application développée pour l'analyse de la qualité de l'air à Marseille.")
st.markdown("Pour toute question, contactez le support.")
