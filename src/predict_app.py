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
import requests # Pour faire des requêtes HTTP à l'API
import json # Pour parser la réponse JSON de l'API

# --- Configuration de la page Streamlit ---
st.set_page_config(
    layout="wide", # Utilise toute la largeur de l'écran pour un design plus pro
    page_title="Qualité de l'Air - Marseille : Temps Réel & Prédictions",
    page_icon="☀️" # Soleil pour le thème marseillais
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
        color: #00567A; /* Bleu plus profond */
        text-align: center;
        padding-bottom: 25px;
        border-bottom: 3px solid #00567A;
        margin-bottom: 30px;
        font-size: 2.8em;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .stApp {
        background: linear-gradient(to bottom, #EBF5FF, #F8FFFF); /* Dégradé doux ciel */
    }
    .stSidebar {
        background-color: #C3E6F3; /* Bleu clair pour la sidebar */
        border-right: 2px solid #0077B6;
        border-radius: 15px;
        padding: 25px;
        margin: 15px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.1);
    }
    .stButton>button {
        background-color: #0077B6; /* Bleu bouton */
        color: white;
        border-radius: 15px;
        border: none;
        padding: 12px 25px;
        font-weight: bold;
        box-shadow: 3px 3px 8px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
        width: 100%; /* Bouton pleine largeur */
        margin-top: 20px;
    }
    .stButton>button:hover {
        background-color: #0288D1; /* Bleu plus clair au survol */
        box-shadow: 6px 6px 15px rgba(0,0,0,0.4);
        transform: translateY(-2px);
    }
    .stTextInput>div>div>input, .stSlider>div>div>div>div {
        border-radius: 10px;
        border: 1px solid #0077B6;
        padding: 8px;
    }
    .stTabs [data-baseweb="tab-list"] button {
        background-color: #E0F2F7;
        color: #0077B6;
        border-radius: 12px 12px 0 0;
        border-bottom: 4px solid transparent;
        transition: all 0.3s ease;
        font-weight: 600;
        padding: 15px 25px;
        box-shadow: 2px -2px 5px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-list"] button:hover {
        border-bottom: 4px solid #0077B6;
        color: #0288D1;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        border-bottom: 4px solid #0288D1;
        color: #0288D1;
        font-weight: bold;
        background-color: #FFF;
    }
    .aqi-box {
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 6px 6px 15px rgba(0,0,0,0.2);
        border: 2px solid rgba(0,0,0,0.1);
        transition: all 0.5s ease;
    }
    .aqi-box:hover {
        transform: translateY(-5px);
        box-shadow: 8px 8px 20px rgba(0,0,0,0.3);
    }
    .aqi-good { background-color: #CFFFD9; color: #1E8449; border-color: #1E8449; } /* Vert doux */
    .aqi-moderate { background-color: #FFFADD; color: #D68910; border-color: #D68910; } /* Jaune orangé doux */
    .aqi-sensitive { background-color: #FFEFCC; color: #D46A00; border-color: #D46A00; } /* Orange plus prononcé */
    .aqi-unhealthy { background-color: #FFC0CB; color: #CB4335; border-color: #CB4335; } /* Rouge rosé */
    .aqi-very-unhealthy { background-color: #E6B0EE; color: #7D3C98; border-color: #7D3C98; } /* Violet doux */
    .aqi-hazardous { background-color: #FADBD8; color: #641E16; border-color: #641E16; } /* Rouge foncé */

    .aqi-legend-item {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
    }
    .aqi-legend-color-box {
        width: 30px;
        height: 30px;
        border-radius: 8px;
        margin-right: 12px;
        border: 1px solid #ccc;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.1);
    }
    .stInfo, .stWarning, .stError, .stSuccess {
        border-radius: 10px;
        padding: 15px;
        margin-top: 15px;
        margin-bottom: 15px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    }
    .stInfo { background-color: #E0F2F7; border-left: 5px solid #0077B6; }
    .stWarning { background-color: #FFF3E0; border-left: 5px solid #E67E22; }
    .stError { background-color: #FFEBEE; border-left: 5px solid #C0392B; }
    .stSuccess { background-color: #E8F8F5; border-left: 5px solid #2E8B57; }

    .footer {
        text-align: center;
        font-size: 0.85em;
        color: #777;
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid #ccc;
    }
</style>
""", unsafe_allow_html=True)


# --- En-tête de l'application ---
st.markdown("<h1 class='main-header'>☀️ Qualité de l'Air à Marseille : Analyse & Prédiction 🌊</h1>", unsafe_allow_html=True)

st.markdown(
    """
    Bienvenue sur l'application dédiée à la surveillance et la prédiction de la qualité de l'air (AQI - Air Quality Index) pour la ville de **Marseille**.
    Que vous soyez résident, visiteur, ou simplement soucieux de votre santé respiratoire, cette interface vous offre des informations précieuses.
    Notre modèle d'apprentissage automatique, nourri par des données environnementales, estime l'indice de qualité de l'air pour vous aider à prendre des décisions éclairées.
    """
)
st.markdown("---")

# --- Fonction d'aide pour interpréter l'AQI et les conseils médicaux ---
def get_aqi_category_and_advice(aqi_value):
    category_info = {}
    if aqi_value >= 301:
        category_info = {
            "category": "Dangereux",
            "color_class": "aqi-hazardous",
            "description": "L'air est en état d'urgence sanitaire. **Toute la population est susceptible d'être gravement affectée** par des effets aigus et chroniques sur la santé. Fort risque de décès prématurés.",
            "advice": """
                **Conseils médicaux urgents :**
                * **Absolument AUCUNE activité physique en extérieur.**
                * **Restez à l'intérieur** avec les fenêtres fermées et utilisez des purificateurs d'air avec filtres HEPA si disponibles.
                * Évitez toute source de pollution intérieure (bougies, encens, tabac).
                * **Consultez un médecin** ou les urgences en cas de symptômes respiratoires ou cardiaques graves (difficultés à respirer, douleurs thoraciques, étourdissements).
                * **Impacts possibles :** Aggravation très sévère de l'asthme, des BPCO, des maladies cardiaques, augmentation des AVC et des infarctus. Les PM2.5, PM10, SO2 et NO2 sont probablement à des niveaux critiques, causant une inflammation systémique et des lésions cellulaires profondes.
            """
        }
    elif aqi_value >= 201:
        category_info = {
            "category": "Très Mauvais",
            "color_class": "aqi-very-unhealthy",
            "description": "**Avertissement de santé majeur :** Tout le monde peut ressentir des effets sur la santé. Les membres des groupes sensibles peuvent subir des effets très graves et potentiellement mortels.",
            "advice": """
                **Conseils médicaux stricts :**
                * **Évitez toute activité physique en extérieur.**
                * **Les groupes sensibles (enfants, personnes âgées, personnes souffrant d'asthme, de BPCO, de maladies cardiaques ou pulmonaires) doivent impérativement rester à l'intérieur.**
                * Maintenez les fenêtres fermées.
                * **Impacts possibles :** Augmentation significative des crises d'asthme et des problèmes respiratoires chroniques. Risque accru de complications cardiovasculaires. Forte présence de PM2.5, PM10 et potentiellement d'Ozone (O3) en été, ou NO2/SO2 en hiver.
            """
        }
    elif aqi_value >= 151:
        category_info = {
            "category": "Mauvais",
            "color_class": "aqi-unhealthy",
            "description": "Les membres des groupes sensibles peuvent ressentir des effets sur la santé (irritations, difficultés respiratoires). Le grand public est également susceptible d'être affecté par des symptômes légers.",
            "advice": """
                **Conseils de précaution :**
                * **Réduisez les activités physiques intenses en extérieur.**
                * **Les personnes sensibles** (asthmatiques, cardiaques, jeunes enfants, personnes âgées) devraient limiter leurs activités en extérieur et éviter les zones à forte circulation.
                * **Impacts possibles :** Irritation des yeux et des voies respiratoires, toux, difficultés respiratoires pour les sujets sensibles. Polluants comme les PM2.5, PM10 et NO2 sont souvent élevés.
            """
        }
    elif aqi_value >= 101:
        category_info = {
            "category": "Moyennement Mauvais pour les Groupes Sensibles",
            "color_class": "aqi-sensitive",
            "description": "La qualité de l'air est acceptable, mais un risque modéré pour la santé peut exister pour un très petit nombre de personnes particulièrement sensibles (par exemple, asthmatiques, personnes âgées).",
            "advice": """
                **Conseils pour les personnes sensibles :**
                * Les personnes très sensibles aux polluants devraient **réduire les efforts intenses** en extérieur et surveiller leurs symptômes.
                * Le grand public n'est généralement pas affecté.
                * **Impacts possibles :** Légère irritation pour les sujets très sensibles. Les niveaux d'Ozone (O3) ou de PM2.5 peuvent être légèrement élevés.
            """
        }
    elif aqi_value >= 51:
        category_info = {
            "category": "Modéré",
            "color_class": "aqi-moderate",
            "description": "La qualité de l'air est acceptable. Pour la plupart des gens, il n'y a pas de risque majeur. Un très petit nombre d'individus exceptionnellement sensibles pourrait ressentir des effets légers.",
            "advice": """
                **Conseils généraux :**
                * La plupart des individus peuvent profiter des activités de plein air.
                * Les personnes très sensibles peuvent envisager de réduire les efforts intenses si elles ressentent une gêne.
                * **Impacts possibles :** Effets minimes, généralement imperceptibles pour la population générale.
            """
        }
    else: # AQI 0-50
        category_info = {
            "category": "Bon",
            "color_class": "aqi-good",
            "description": "La qualité de l'air est excellente. La pollution de l'air présente peu ou pas de risque pour la santé.",
            "advice": """
                **Conseils du médecin :**
                * Respirez à pleins poumons ! C'est une journée idéale pour toutes vos activités en extérieur. Profitez-en !
                * **Impacts possibles :** Aucun effet néfaste attendu sur la santé dû à la pollution de l'air.
            """
        }
    return category_info

# --- Section d'affichage de l'AQI ---
def display_aqi_section(title, aqi_value, timestamp, is_real_time=False):
    info = get_aqi_category_and_advice(aqi_value)
    
    st.markdown(f"### {title}")
    st.markdown(f"<p style='font-size: 1.1em; text-align: center;'><b>{timestamp}</b></p>", unsafe_allow_html=True)
    
    st.markdown(
        f"""
        <div class="aqi-box {info['color_class']}">
            <h2 style='margin-bottom: 5px; color: {info['color_class'].split('-')[1]};'>Indice AQI : {aqi_value:.2f}</h2>
            <h3 style='margin-top: 0; color: {info['color_class'].split('-')[1]};'>{info['category']}</h3>
            <p style='color: {info['color_class'].split('-')[1]};'>{info['description']}</p>
        </div>
        """, unsafe_allow_html=True
    )
    
    st.markdown(f"**Conseils santé pour une qualité d'air '{info['category']}' :**")
    st.info(info['advice'])

# --- Section Comprendre l'AQI ---
st.header("📖 Comprendre l'Indice de Qualité de l'Air (AQI)")
with st.expander("Cliquez ici pour une explication détaillée de l'AQI et ses impacts sur la santé"):
    st.markdown("""
    L'**Indice de Qualité de l'Air (AQI)** est une mesure standardisée utilisée pour communiquer la qualité de l'air aux citoyens.
    Il traduit les concentrations de divers polluants (particules fines PM2.5 et PM10, ozone O3, dioxyde d'azote NO2, monoxyde de carbone CO, etc.) en une seule valeur compréhensible.
    Un AQI plus bas indique une meilleure qualité de l'air.
    """)

    st.markdown("### Légende des Niveaux d'AQI :")
    aqi_levels = [
        {"range": "0 - 50", "category": "Bon", "color": "#CFFFD9", "text_color": "#1E8449", "description": "L'air est satisfaisant. Peu ou pas de risque pour la santé."},
        {"range": "51 - 100", "category": "Modéré", "color": "#FFFADD", "text_color": "#D68910", "description": "Qualité de l'air acceptable. Risque modéré pour les personnes très sensibles."},
        {"range": "101 - 150", "category": "Moyennement Mauvais pour les Groupes Sensibles", "color": "#FFEFCC", "text_color": "#D46A00", "description": "Les personnes sensibles (maladies respiratoires, enfants, seniors) peuvent subir des effets."},
        {"range": "151 - 200", "category": "Mauvais", "color": "#FFC0CB", "text_color": "#CB4335", "description": "Effets sur la santé pour tous. Groupes sensibles plus fortement affectés."},
        {"range": "201 - 300", "category": "Très Mauvais", "color": "#E6B0EE", "text_color": "#7D3C98", "description": "Avertissement de santé. Tout le monde peut être affecté de manière grave."},
        {"range": "301+", "category": "Dangereux", "color": "#FADBD8", "text_color": "#641E16", "description": "Urgence. Toute la population est susceptible d'être gravement affectée."}
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

# --- Section AQI en Temps Réel (via API externe) ---
st.header("⚡ Qualité de l'Air Actuelle à Marseille (Temps Réel)")
st.info("""
    **Source des données :** World Air Quality Index (AQICN.org).
    *Pour que cette section fonctionne, vous devez obtenir un token API gratuit sur [aqicn.org/data-platform/token/](https://aqicn.org/data-platform/token/) et remplacer `YOUR_WAQI_API_TOKEN` dans le code.*
""")

WAQI_API_TOKEN = "99eb2e79a8e940328229282ecb62b9eafaaf64e7" # <<< REMPLACER CECI PAR VOTRE VRAI TOKEN API >>>
MARSEILLE_STATION_ID = "@11649" # ID de station pour Marseille (par exemple, "Marseille St Louis" ou une autre station pertinente)
# Vous pouvez trouver d'autres stations via https://aqicn.org/map/
# ou en cherchant "Marseille" sur https://api.waqi.info/feed/A398956/?token=YOUR_TOKEN

@st.cache_data(ttl=3600) # Met en cache la réponse pendant 1 heure pour éviter les appels API excessifs
def get_realtime_aqi(token, station_id):
    url = f"https://api.waqi.info/feed/{station_id}/?token={token}"
    try:
        response = requests.get(url)
        response.raise_for_status() # Lève une exception pour les codes d'erreur HTTP
        data = response.json()
        
        if data['status'] == 'ok':
            aqi_value = data['data']['aqi']
            timestamp_str = data['data']['time']['s'] # Exemple: "2025-06-29 15:00:00"
            
            # Tente de convertir le timestamp en objet datetime pour un affichage convivial
            try:
                # Gérer le cas où le timestamp peut ne pas inclure les secondes ou avoir un format légèrement différent
                fetched_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                fetched_time = datetime.now() # Fallback si le format API change

            city_name = data['data']['city']['name']
            
            # Extraire les polluants pour une explication plus détaillée si nécessaire
            pollutants_info = {}
            if 'iaqi' in data['data']:
                for pollutant_code, pollutant_data in data['data']['iaqi'].items():
                    if 'v' in pollutant_data:
                        pollutants_info[pollutant_code] = pollutant_data['v']
            
            return aqi_value, fetched_time, city_name, pollutants_info
        else:
            st.error(f"❌ Erreur de l'API WAQI : {data.get('data', 'Pas de message d\'erreur spécifique de l\'API.')}")
            return None, None, None, None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erreur de connexion à l'API WAQI. Vérifiez votre connexion Internet ou votre clé API. Détails : {e}")
        return None, None, None, None
    except json.JSONDecodeError as e:
        st.error(f"❌ Erreur de décodage de la réponse de l'API WAQI. La réponse n'est pas un JSON valide. Détails : {e}")
        return None, None, None, None
    except Exception as e:
        st.error(f"❌ Une erreur inattendue est survenue lors de la récupération des données en temps réel : {e}")
        return None, None, None, None

if WAQI_API_TOKEN == "YOUR_WAQI_API_TOKEN":
    st.warning("⚠️ **Attention :** Veuillez remplacer `YOUR_WAQI_API_TOKEN` par votre vraie clé API dans le code pour activer la section 'Temps Réel'.")
else:
    with st.spinner("Chargement des données de qualité de l'air en temps réel pour Marseille..."):
        aqi_realtime, time_realtime, city_name_realtime, pollutants_realtime = get_realtime_aqi(WAQI_API_TOKEN, MARSEILLE_STATION_ID)
    
    if aqi_realtime is not None:
        display_aqi_section(
            f"Qualité de l'Air Actuelle à {city_name_realtime}",
            aqi_realtime,
            f"Mise à jour le : {time_realtime.strftime('%d/%m/%Y à %H:%M')}",
            is_real_time=True
        )
        if pollutants_realtime:
            st.markdown("##### Niveaux des principaux polluants (μg/m³ ou ppm) :")
            pollutant_cols = st.columns(6)
            col_idx = 0
            for pollutant, value in pollutants_realtime.items():
                if pollutant in ['pm25', 'pm10', 'o3', 'no2', 'so2', 'co']: # Filtrer pour les polluants pertinents
                    pollutant_cols[col_idx % 6].metric(label=pollutant.upper(), value=f"{value:.1f}")
                    col_idx += 1
        st.markdown("---")
    else:
        st.error("Impossible de récupérer les données AQI en temps réel pour l'instant. Veuillez réessayer plus tard ou vérifier votre clé API.")


# --- Section Prédiction Initiale (basée sur les données historiques) ---
st.header("📅 Données Historiques & Prédiction de Référence")

if not df.empty and "aqi" in df.columns and "timestamp" in df.columns:
    # Récupérer la dernière ligne pour la prédiction "actuelle"
    latest_data = df.iloc[-1]
    X_historical_full = df.drop(columns=["aqi", "timestamp"])

    try:
        prediction_historical = model.predict(X_historical_full)[-1] # Prendre la dernière prédiction
        
        latest_timestamp_str = latest_data["timestamp"]
        try:
            latest_time = pd.to_datetime(latest_timestamp_str, errors='coerce')
            if pd.isna(latest_time):
                latest_time = datetime.now() # Fallback
        except Exception:
            latest_time = datetime.now() # Fallback

        display_aqi_section(
            "Dernière Prédiction basée sur nos Données Historiques",
            prediction_historical,
            f"Basé sur les données du : {latest_time.strftime('%d/%m/%Y à %H:%M')}"
        )

    except Exception as e:
        st.error(f"❌ Erreur lors de la prédiction avec les données historiques : {e}")
        st.info("💡 **Conseil technique :** Vérifiez que la structure de `X_historical_full` correspond aux attentes du modèle (noms et ordre des colonnes).")
else:
    st.warning("⚠️ Le fichier de données historiques est vide ou ne contient pas les colonnes attendues ('aqi', 'timestamp'). Impossible de faire la prédiction historique.")

st.subheader("📚 Aperçu des Données Historiques Utilisées")
with st.expander("Cliquez pour voir les données"):
    st.dataframe(df) # Utilisation de st.dataframe pour un affichage interactif

# --- Section de prédiction interactive (Simulation) ---
st.markdown("---") # Séparateur visuel
st.header("✨ Simuler une Prédiction AQI (Marseille)")
st.markdown("Ajustez les paramètres environnementaux ci-dessous pour **simuler** comment la qualité de l'air pourrait évoluer. Explorez l'impact des polluants et conditions météorologiques sur l'indice AQI.")

# Sidebars pour les inputs utilisateur
st.sidebar.header("🎚️ Ajuster les Paramètres de Simulation")
st.sidebar.markdown("""
    **Note importante :** Les noms et le nombre de ces paramètres
    doivent correspondre *exactement* aux caractéristiques
    (`co`, `h`, `no2`, `o3`, `p`, `pm10`, `pm25`, `so2`, `t`, `w`, `wg`)
    sur lesquelles votre modèle a été entraîné.
    Ajustez les plages de valeurs si nécessaire pour refléter
    les données réelles de Marseille.
""")

# Input fields for new prediction - Mise à jour pour correspondre aux noms de caractéristiques du modèle
st.sidebar.subheader("💨 Niveaux de Polluants")
co_input = st.sidebar.slider("Monoxyde de carbone (co) [mg/m³]", min_value=0.0, max_value=50.0, value=5.0, step=0.1, help="Concentration de Monoxyde de carbone")
no2_input = st.sidebar.slider("Dioxyde d'azote (no2) [µg/m³]", min_value=0.0, max_value=200.0, value=40.0, step=1.0, help="Concentration de Dioxyde d'azote")
o3_input = st.sidebar.slider("Ozone (o3) [µg/m³]", min_value=0.0, max_value=200.0, value=60.0, step=1.0, help="Concentration d'Ozone")
pm10_input = st.sidebar.slider("Particules PM10 (pm10) [µg/m³]", min_value=0.0, max_value=300.0, value=50.0, step=1.0, help="Concentration de Particules en suspension de moins de 10 micromètres")
pm25_input = st.sidebar.slider("Particules PM2.5 (pm25) [µg/m³]", min_value=0.0, max_value=200.0, value=30.0, step=1.0, help="Concentration de Particules en suspension de moins de 2.5 micromètres")
so2_input = st.sidebar.slider("Dioxyde de soufre (so2) [µg/m³]", min_value=0.0, max_value=100.0, value=10.0, step=0.1, help="Concentration de Dioxyde de soufre")

st.sidebar.subheader("☁️ Conditions Météorologiques")
t_input = st.sidebar.slider("Température (°C) (t)", min_value=-20.0, max_value=50.0, value=15.0, step=0.1, help="Température ambiante en degrés Celsius")
h_input = st.sidebar.slider("Humidité (%) (h)", min_value=0, max_value=100, value=70, step=1, help="Humidité relative de l'air")
p_input = st.sidebar.slider("Pression (hPa) (p)", min_value=900.0, max_value=1100.0, value=1013.0, step=0.1, help="Pression atmosphérique en hectopascals")
w_input = st.sidebar.slider("Vitesse du Vent (km/h) (w)", min_value=0.0, max_value=100.0, value=10.0, step=0.1, help="Vitesse moyenne du vent")
wg_input = st.sidebar.slider("Rafale de Vent (km/h) (wg)", min_value=0.0, max_value=150.0, value=20.0, step=0.1, help="Vitesse maximale des rafales de vent")


# Créer un DataFrame pour l'entrée utilisateur avec les noms de colonnes corrects
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

        st.success("✅ Prédiction simulée réussie ! (Simulateur)")
        st.markdown(f"### Résultat de votre Prédiction AQI simulée :")
        display_aqi_section(
            "", # Pas de titre spécifique car déjà dans le H3
            simulated_prediction,
            f"Simulé le : {datetime.now().strftime('%d/%m/%Y à %H:%M')}"
        )

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