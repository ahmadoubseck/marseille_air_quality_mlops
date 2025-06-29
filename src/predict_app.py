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
import os
from datetime import datetime

# --- Configuration de la page Streamlit ---
st.set_page_config(
    layout="wide", # Utilise toute la largeur de l'écran pour un design plus pro
    page_title="Prédictions Qualité de l'Air - Marseille",
    page_icon="🌊" # Vague pour le thème méditerranéen
)

# --- CSS personnalisé pour un design attrayant et thématique ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #333;
    }
    .main-header {
        color: #0077B6; /* Bleu foncé méditerranéen */
        text-align: center;
        padding-bottom: 20px;
        border-bottom: 2px solid #0077B6;
    }
    .stApp {
        background: linear-gradient(to bottom, #E0F2F7, #F0F8FF); /* Dégradé doux ciel */
    }
    .stSidebar {
        background-color: #ADD8E6; /* Bleu clair pour la sidebar */
        border-right: 1px solid #0077B6;
        border-radius: 10px;
        padding: 20px;
        margin: 10px;
    }
    .stButton>button {
        background-color: #0077B6; /* Bleu bouton */
        color: white;
        border-radius: 12px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #0288D1; /* Bleu plus clair au survol */
        box-shadow: 4px 4px 10px rgba(0,0,0,0.3);
    }
    .stTextInput>div>div>input, .stSlider>div>div>div>div {
        border-radius: 8px;
        border: 1px solid #0077B6;
    }
    .stTabs [data-baseweb="tab-list"] button {
        background-color: #E0F2F7;
        color: #0077B6;
        border-radius: 10px 10px 0 0;
        border-bottom: 3px solid transparent;
        transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab-list"] button:hover {
        border-bottom: 3px solid #0077B6;
        color: #0288D1;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        border-bottom: 3px solid #0288D1;
        color: #0288D1;
        font-weight: bold;
    }
    .aqi-box {
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.1);
        border: 1px solid rgba(0,0,0,0.1);
    }
    .aqi-good { background-color: #CCEECC; color: #2E8B57; border: 1px solid #2E8B57; }
    .aqi-moderate { background-color: #FFEBCC; color: #E67E22; border: 1px solid #E67E22; }
    .aqi-sensitive { background-color: #FFDDAA; color: #D35400; border: 1px solid #D35400; }
    .aqi-unhealthy { background-color: #FFCCCC; color: #C0392B; border: 1px solid #C0392B; }
    .aqi-very-unhealthy { background-color: #EEBBEE; color: #8E44AD; border: 1px solid #8E44AD; }
    .aqi-hazardous { background-color: #FFDDDD; color: #6C3483; border: 1px solid #6C3483; }

    .aqi-legend-item {
        display: flex;
        align-items: center;
        margin-bottom: 8px;
    }
    .aqi-legend-color-box {
        width: 25px;
        height: 25px;
        border-radius: 5px;
        margin-right: 10px;
        border: 1px solid #ccc;
    }
</style>
""", unsafe_allow_html=True)


# --- En-tête de l'application ---
st.markdown("<h1 class='main-header'>🌊 Prédictions Qualité de l'Air - Marseille ☀️</h1>", unsafe_allow_html=True)

# Description de l'application
st.markdown(
    """
    Bienvenue sur l'application de prédiction de la qualité de l'air (AQI - Air Quality Index) pour la ville de **Marseille**.
    Notre modèle d'apprentissage automatique estime l'indice de qualité de l'air en se basant sur divers polluants et conditions météorologiques.
    Restez informé pour mieux protéger votre santé !
    """
)
st.markdown("---")

# --- Fonction d'aide pour interpréter l'AQI ---
def get_aqi_category_and_advice(aqi_value):
    if aqi_value >= 301:
        category = "Dangereux"
        color_class = "aqi-hazardous"
        description = "L'air est en état d'urgence. Toute la population est susceptible d'être gravement affectée."
        advice = "**Conseils :** Évitez toute activité physique en extérieur. Restez à l'intérieur avec les fenêtres fermées. Utilisez des purificateurs d'air si possible. Les personnes malades doivent chercher un abri sûr."
    elif aqi_value >= 201:
        category = "Très Mauvais"
        color_class = "aqi-very-unhealthy"
        description = "Avertissement de santé : Tout le monde peut ressentir des effets sur la santé ; les membres des groupes sensibles peuvent ressentir des effets plus graves."
        advice = "**Conseils :** Évitez toute activité physique en extérieur. Restez à l'intérieur avec les fenêtres fermées. Les personnes sensibles (enfants, personnes âgées, personnes souffrant de maladies respiratoires ou cardiaques) doivent absolument rester à l'intérieur."
    elif aqi_value >= 151:
        category = "Mauvais"
        color_class = "aqi-unhealthy"
        description = "Les membres des groupes sensibles peuvent ressentir des effets sur la santé. Le grand public est également susceptible d'être affecté."
        advice = "**Conseils :** Réduisez les activités physiques intenses en extérieur. Les personnes sensibles devraient limiter leurs activités en extérieur."
    elif aqi_value >= 101:
        category = "Moyennement Mauvais pour les Groupes Sensibles"
        color_class = "aqi-sensitive"
        description = "La qualité de l'air est acceptable, mais certains polluants peuvent poser un risque modéré pour la santé d'un très petit nombre de personnes particulièrement sensibles."
        advice = "**Conseils :** Les personnes très sensibles aux polluants devraient réduire les efforts intenses en extérieur."
    elif aqi_value >= 51:
        category = "Modéré"
        color_class = "aqi-moderate"
        description = "La qualité de l'air est acceptable; cependant, pour certains polluants, il peut y avoir un problème de santé modéré pour un très petit nombre de personnes qui sont exceptionnellement sensibles à la pollution de l'air."
        advice = "**Conseils :** La plupart des individus peuvent profiter des activités de plein air. Les personnes très sensibles peuvent envisager de réduire les efforts intenses."
    else: # AQI 0-50
        category = "Bon"
        color_class = "aqi-good"
        description = "La qualité de l'air est considérée comme satisfaisante et la pollution de l'air présente peu ou pas de risque."
        advice = "**Conseils :** Profitez pleinement de vos activités de plein air !"
    
    return category, color_class, description, advice

# --- Chargement des ressources ---
# ATTENTION: Les chemins ci-dessous sont relatifs et peuvent échouer sur Streamlit Cloud si les fichiers
# ne sont pas à la racine de l'exécution ou s'ils ne sont pas poussés sur GitHub.
# Pour une solution robuste, référez-vous à la méthode 'os.path' de la version précédente.
try:
    # Pour rendre les chemins robustes en production et localement
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, '..', 'models', 'aqi_model.pkl')
    data_path = os.path.join(current_dir, '..', 'data', 'features_history.csv')

    model = joblib.load(model_path)
except FileNotFoundError:
    st.error("❌ Erreur: Un fichier essentiel (modèle ou données) n'a pas été trouvé. Assurez-vous qu'il est bien présent dans votre dépôt GitHub et que le chemin est correct.")
    st.info("💡 **Solution possible:** Vérifiez votre `.gitignore` et assurez-vous que les fichiers 'models/aqi_model.pkl' et 'data/features_history.csv' sont poussés sur GitHub.")
    st.stop()
except Exception as e:
    st.error(f"❌ Une erreur inattendue est survenue lors du chargement des ressources : {e}")
    st.stop()

try:
    df = pd.read_csv(data_path)
except Exception as e:
    st.error(f"❌ Une erreur inattendue est survenue lors du chargement des données : {e}")
    st.stop()


# --- Section Comprendre l'AQI ---
st.header("📖 Comprendre l'Indice de Qualité de l'Air (AQI)")
with st.expander("Cliquez ici pour une explication détaillée de l'AQI"):
    st.markdown("""
    L'**Indice de Qualité de l'Air (AQI)** est une mesure standardisée utilisée pour communiquer la qualité de l'air aux citoyens.
    Il traduit les concentrations de divers polluants (particules fines PM2.5 et PM10, ozone O3, dioxyde d'azote NO2, etc.) en une seule valeur compréhensible.
    Un AQI plus bas indique une meilleure qualité de l'air.
    """)

    st.markdown("### Légende des Niveaux d'AQI :")
    aqi_levels = [
        {"range": "0 - 50", "category": "Bon", "color": "#CCEECC", "text_color": "#2E8B57", "description": "L'air est satisfaisant. Peu ou pas de risque pour la santé."},
        {"range": "51 - 100", "category": "Modéré", "color": "#FFEBCC", "text_color": "#E67E22", "description": "Qualité de l'air acceptable. Risque modéré pour les personnes très sensibles."},
        {"range": "101 - 150", "category": "Moyennement Mauvais pour les Groupes Sensibles", "color": "#FFDDAA", "text_color": "#D35400", "description": "Les personnes sensibles (maladies respiratoires, enfants, seniors) peuvent subir des effets."},
        {"range": "151 - 200", "category": "Mauvais", "color": "#FFCCCC", "text_color": "#C0392B", "description": "Effets sur la santé pour tous. Groupes sensibles plus fortement affectés."},
        {"range": "201 - 300", "category": "Très Mauvais", "color": "#EEBBEE", "text_color": "#8E44AD", "description": "Avertissement de santé. Tout le monde peut être affecté de manière grave."},
        {"range": "301+", "category": "Dangereux", "color": "#FFDDDD", "text_color": "#6C3483", "description": "Urgence. Toute la population est susceptible d'être gravement affectée."}
    ]

    for level in aqi_levels:
        st.markdown(
            f"""
            <div class="aqi-legend-item">
                <div class="aqi-legend-color-box" style="background-color: {level['color']}; border-color: {level['text_color']};"></div>
                <p style="margin: 0; color: {level['text_color']};"><b>AQI {level['range']} : {level['category']}</b> - {level['description']}</p>
            </div>
            """, unsafe_allow_html=True
        )
st.markdown("---")


# --- Prédiction initiale et affichage (basé sur les données historiques) ---
st.header("📊 Qualité de l'Air Actuelle à Marseille")

if not df.empty and "aqi" in df.columns and "timestamp" in df.columns:
    # Récupérer la dernière ligne pour la prédiction "actuelle"
    latest_data = df.iloc[-1]
    X_historical = df.drop(columns=["aqi", "timestamp"])

    try:
        prediction_historical = model.predict(X_historical)[-1] # Prendre la dernière prédiction si multiple
        
        # Obtenir la date et l'heure de la dernière entrée
        latest_timestamp_str = latest_data["timestamp"]
        # Assurez-vous que le format de timestamp est correct pour parsing
        try:
            # Essayer plusieurs formats si le format exact n'est pas connu
            latest_time = pd.to_datetime(latest_timestamp_str, errors='coerce')
            if pd.isna(latest_time):
                latest_time = datetime.now() # Fallback si le format est inconnu
        except Exception:
            latest_time = datetime.now() # Fallback si erreur de parsing

        category, color_class, description, advice = get_aqi_category_and_advice(prediction_historical)

        st.markdown(f"### 📈 Prédiction AQI basée sur les données les plus récentes :")
        st.markdown(f"<p style='font-size: 1.1em; text-align: center;'><b>Données du : {latest_time.strftime('%d/%m/%Y à %H:%M')}</b></p>", unsafe_allow_html=True)
        
        st.markdown(
            f"""
            <div class="aqi-box {color_class}">
                <h2 style='margin-bottom: 5px; color: {get_aqi_category_and_advice(prediction_historical)[1].split('-')[1]};'>Indice AQI : {prediction_historical:.2f}</h2>
                <h3 style='margin-top: 0; color: {get_aqi_category_and_advice(prediction_historical)[1].split('-')[1]};'>{category}</h3>
                <p style='color: {get_aqi_category_and_advice(prediction_historical)[1].split('-')[1]};'>{description}</p>
            </div>
            """, unsafe_allow_html=True
        )
        
        st.markdown(f"**Conseils pour une qualité d'air '{category}' :**")
        st.info(advice)


        st.write("---")
    except Exception as e:
        st.error(f"❌ Erreur lors de la prédiction avec les données historiques : {e}")
else:
    st.warning("⚠️ Le fichier de données historiques est vide ou ne contient pas les colonnes attendues ('aqi', 'timestamp'). Impossible de faire la prédiction historique.")

st.subheader("📚 Aperçu des Données Historiques")
st.dataframe(df) # Utilisation de st.dataframe pour un affichage interactif

# --- Amélioration du front : Section de prédiction interactive ---
st.markdown("---") # Séparateur visuel
st.header("✨ Simuler une Prédiction AQI (Marseille)")
st.write("Explorez l'impact des différents paramètres environnementaux sur la qualité de l'air en ajustant les curseurs ci-dessous.")

# Sidebars pour les inputs utilisateur
st.sidebar.header("🎚️ Ajuster les Paramètres de Simulation")
st.sidebar.markdown("""
    **Note importante :** Les noms et le nombre de ces paramètres
    doivent correspondre *exactement* aux caractéristiques
    sur lesquelles votre modèle a été entraîné.
    Ajustez les plages de valeurs si nécessaire pour refléter
    les données réelles de Marseille.
""")

# Input fields for new prediction - Mise à jour pour correspondre aux noms de caractéristiques du modèle
# Les noms de features sont tirés de votre message d'erreur : ['co', 'h', 'no2', 'o3', 'p', 'pm10', 'pm25', 'so2', 't', 'w', 'wg']

st.sidebar.subheader("💨 Polluants")
co_input = st.sidebar.slider("Monoxyde de carbone (co)", min_value=0.0, max_value=50.0, value=5.0, step=0.1, help="Concentration de Monoxyde de carbone")
no2_input = st.sidebar.slider("Dioxyde d'azote (no2)", min_value=0.0, max_value=200.0, value=40.0, step=1.0, help="Concentration de Dioxyde d'azote")
o3_input = st.sidebar.slider("Ozone (o3)", min_value=0.0, max_value=200.0, value=60.0, step=1.0, help="Concentration d'Ozone")
pm10_input = st.sidebar.slider("Particules PM10 (pm10)", min_value=0.0, max_value=300.0, value=50.0, step=1.0, help="Concentration de Particules en suspension de moins de 10 micromètres")
pm25_input = st.sidebar.slider("Particules PM2.5 (pm25)", min_value=0.0, max_value=200.0, value=30.0, step=1.0, help="Concentration de Particules en suspension de moins de 2.5 micromètres")
so2_input = st.sidebar.slider("Dioxyde de soufre (so2)", min_value=0.0, max_value=100.0, value=10.0, step=0.1, help="Concentration de Dioxyde de soufre")

st.sidebar.subheader("☁️ Conditions Météo")
t_input = st.sidebar.slider("Température (°C) (t)", min_value=-20.0, max_value=50.0, value=15.0, step=0.1, help="Température ambiante en degrés Celsius")
h_input = st.sidebar.slider("Humidité (%) (h)", min_value=0, max_value=100, value=70, step=1, help="Humidité relative de l'air")
p_input = st.sidebar.slider("Pression (hPa) (p)", min_value=900.0, max_value=1100.0, value=1013.0, step=0.1, help="Pression atmosphérique en hectopascals")
w_input = st.sidebar.slider("Vitesse du Vent (km/h) (w)", min_value=0.0, max_value=100.0, value=10.0, step=0.1, help="Vitesse moyenne du vent")
wg_input = st.sidebar.slider("Rafale de Vent (km/h) (wg)", min_value=0.0, max_value=150.0, value=20.0, step=0.1, help="Vitesse maximale des rafales de vent")


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
if st.button("🚀 Obtenir la Prédiction Simulée"):
    try:
        simulated_prediction = model.predict(user_input_df)[0] # Prend la première (unique) prédiction
        
        category, color_class, description, advice = get_aqi_category_and_advice(simulated_prediction)

        st.success("✅ Prédiction simulée réussie !")
        st.markdown(f"### Résultat de la Prédiction AQI simulée :")
        st.markdown(
            f"""
            <div class="aqi-box {color_class}">
                <h2 style='margin-bottom: 5px; color: {get_aqi_category_and_advice(simulated_prediction)[1].split('-')[1]};'>Indice AQI : {simulated_prediction:.2f}</h2>
                <h3 style='margin-top: 0; color: {get_aqi_category_and_advice(simulated_prediction)[1].split('-')[1]};'>{category}</h3>
                <p style='color: {get_aqi_category_and_advice(simulated_prediction)[1].split('-')[1]};'>{description}</p>
            </div>
            """, unsafe_allow_html=True
        )
        st.markdown(f"**Conseils pour une qualité d'air '{category}' :**")
        st.info(advice)

    except Exception as e:
        st.error(f"❌ Erreur lors de la prédiction simulée. Veuillez vérifier que les paramètres du panneau latéral sont corrects et correspondent aux attentes de votre modèle. Détails de l'erreur : {e}")
        st.info("💡 **Conseil :** L'erreur 'feature_names mismatch' indique que les noms de colonnes ou leur ordre ne correspondent pas à ce que le modèle a appris. Assurez-vous que les sliders correspondent aux caractéristiques d'entraînement.")
        
st.markdown("---")
st.markdown(f"""
<div class="footer">
    Développé avec passion pour l'analyse de la qualité de l'air à Marseille 💙. <br>
    Par **Mouhamadou Seck** | <a href="https://www.linkedin.com/in/mouhamadou-seck-7276111b7/" target="_blank" style="color: #0077B6;">LinkedIn</a> | Contact: ahmadoubseck06@gmail.com <br>
    Ce projet est une démonstration de compétences en Machine Learning et MLOps, visant à un impact concret sur la santé publique.
</div>
""", unsafe_allow_html=True)