import streamlit as st
import pandas as pd
import re

# --- CONFIGURATION & STYLE ---
st.set_page_config(layout="wide", page_title="Homologation Suisse")

# Custom CSS to mimic the official ASTRA document look
st.markdown("""
    <style>
    .report-container {
        border: 1px solid #000;
        padding: 30px;
        font-family: 'Arial', sans-serif;
        background-color: white;
        color: black;
        line-height: 1.2;
    }
    .header-grey {
        background-color: #e0e0e0;
        padding: 10px;
        border-bottom: 2px solid black;
        font-weight: bold;
        display: flex;
        justify-content: space-between;
    }
    .section-title {
        text-decoration: underline;
        font-weight: bold;
        margin-top: 15px;
        margin-bottom: 5px;
        font-size: 14px;
    }
    .data-row {
        display: flex;
        font-size: 13px;
        margin-bottom: 2px;
    }
    .label { width: 40px; font-weight: bold; }
    .value { flex-grow: 1; }
    .remarks-box {
        margin-top: 30px;
        font-size: 12px;
        border-top: 1px solid #ccc;
        padding-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA LOADING ---
@st.cache_data
def load_data():
    # Attempt to load your files. Adjust filenames if they differ.
    try:
        # We load TAS Automobile as default
        df = pd.read_csv("data/TAS_automobile.csv", low_memory=False, sep=None, engine='python')
        return df
    except Exception as e:
        st.error(f"Erreur de chargement: {e}")
        return None

# Placeholder for Remark Codes (You can expand this list or load from CODE_ROH.csv)
CODE_BOOK = {
    "138": "protections: protection du bord sur face inférieure des rampes, jusqu'à la cale",
    "168": "assurer: rampes d'accès relevées",
    "236": "transport seulement admis avec engins de travail suivants:",
    # Add more codes here based on your ASTRA documentation
}

def translate_remarks(text):
    if pd.isna(text): return ""
    found_codes = re.findall(r'\b\d{3}\b', str(text))
    translations = []
    for code in found_codes:
        if code in CODE_BOOK:
            translations.append(f"<b>{code}</b> - {CODE_BOOK[code]}")
    return "<br>".join(translations) if translations else text

df = load_data()

if df is not None:
    # --- SIDEBAR SEARCH ---
    st.sidebar.image("https://www.astra.admin.ch/etc.clientlibs/fisp/clientlibs/clientlib-site/resources/images/logo_astra.svg", width=150)
    st.sidebar.header("Recherche de Véhicule")
    
    # 1. Filter by Brand
    brands = sorted(df['MARKE'].unique().astype(str))
    sel_brand = st.sidebar.selectbox("Marque", brands)
    
    # 2. Filter by Model
    models = sorted(df[df['MARKE'] == sel_brand]['HANDELSBEZEICHNUNG'].unique().astype(str))
    sel_model = st.sidebar.selectbox("Modèle", models)
    
    # 3. Filter by TG Number
    tgnrs = sorted(df[(df['MARKE'] == sel_brand) & (df['HANDELSBEZEICHNUNG'] == sel_model)]['TGNR'].unique().astype(str))
    sel_tg = st.sidebar.selectbox("Numéro d'homologation (TG)", tgnrs)

    # --- MAIN DISPLAY ---
    if sel_tg:
        # Get the specific row
        res = df[df['TGNR'] == sel_tg].iloc[0]

        # Template based on your photo
        st.markdown(f"""
        <div class="report-container">
            <div class="header-grey">
                <span>Réception suisse par type</span>
                <span>CH {res.get('TGNR', '')}</span>
            </div>

            <div style="margin-top: 15px;">
                <div class="data-row"><div class="label">01</div><div class="value">{res.get('FAHRZEUGART_FR', 'N/A')}</div></div>
                <div class="data-row"><div class="label">04</div><div class="value">{res.get('MARKE', '')} {res.get('HANDELSBEZEICHNUNG', '')}</div></div>
            </div>

            <div style="display: flex; gap: 50px;">
                <!-- Left Column -->
                <div style="flex: 1;">
                    <div class="section-title">13 Châssis</div>
                    <div class="data-row">14 Essieux / Roues: {res.get('ANZ_ACHSEN', '')} / {res.get('ANZ_REIFEN', '')}</div>
                    <div class="data-row">15 Suspension: {res.get('FEDERUNG_FR', '-')}</div>
                    <div class="data-row">17 Vmax: {res.get('VMAX', '-')} km/h</div>
                    
                    <div class="section-title">21 Pneus et jantes</div>
                    <div style="font-size:12px;">{res.get('BEREIFUNG', 'Voir remarques')}</div>
                </div>

                <!-- Right Column -->
                <div style="flex: 1;">
                    <div class="section-title">22 Dimensions</div>
                    <div class="data-row">23 Longueur: {res.get('LAENGE', '-')} mm</div>
                    <div class="data-row">24 Largeur: {res.get('BREITE', '-')} mm</div>
                    <div class="data-row">25 Hauteur: {res.get('HOEHE', '-')} mm</div>
                    <div class="data-row">26 Porte-à-faux AV: {res.get('UEBERHANG_VORNE', '-')} mm</div>

                    <div class="section-title">37 Poids / Garanties</div>
                    <div class="data-row">38 Poids à vide: {res.get('LEERGEWICHT', '-')} kg</div>
                    <div class="data-row">39 Poids garanti: {res.get('GESAMTGEWICHT', '-')} kg</div>
                    <div class="data-row">40 Charge remorquable: {res.get('ANHAENGELAST', '-')} kg</div>
                </div>
            </div>

            <div class="remarks-box">
                <b>Remarques, conditions officielles etc.</b><br>
                {translate_remarks(res.get('BEMERKUNGEN', ''))}
            </div>
            
            <div style="margin-top:50px; font-size:10px; display:flex; justify-content: space-between;">
                <div>Réception par type délivrée le: {res.get('AUSSTELLUNGSDATUM', 'N/A')}</div>
                <div>Positions: {res.get('POSITIONS', 'N/A')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.warning("⚠️ Fichier TAS non trouvé. Assurez-vous que 'TAS_automobile.csv' est dans le dossier 'data'.")
