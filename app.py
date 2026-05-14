import streamlit as st
import pandas as pd
import glob
import os

# --- PAGE CONFIG ---
st.set_page_config(layout="wide", page_title="Swiss Car Homologation Lookup")

# Custom CSS to mimic the photo layout
st.markdown("""
    <style>
    .report-container {
        border: 1px solid #000;
        padding: 20px;
        font-family: 'Courier New', Courier, monospace;
        background-color: white;
        color: black;
    }
    .header-box {
        background-color: #d3d3d3;
        padding: 5px;
        font-weight: bold;
        border-bottom: 2px solid black;
    }
    .section-title {
        text-decoration: underline;
        font-weight: bold;
        margin-top: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA LOADING ---
@st.cache_data
def load_astra_data():
    # In the cloud, we will point to your GitHub folder
    # For now, it looks for CSVs in the local 'data' folder
    df_index = pd.read_csv("data/TYP_ROH.csv", low_memory=False)
    df_specs = pd.read_csv("data/eDatenblatt.csv", low_memory=False)
    df_codes = pd.read_csv("data/CODE_ROH.csv", low_memory=False)
    return df_index, df_specs, df_codes

try:
    df_idx, df_det, df_codes = load_astra_data()
except:
    st.error("Please upload the CSV files to the /data folder.")
    st.stop()

# --- SIDEBAR SEARCH ---
st.sidebar.header("🔍 Recherche")
all_brands = sorted(df_idx['MARKE'].unique().astype(str))
selected_brand = st.sidebar.selectbox("Marque", all_brands)

models = sorted(df_idx[df_idx['MARKE'] == selected_brand]['HANDELSBEZEICHNUNG'].unique().astype(str))
selected_model = st.sidebar.selectbox("Modèle", models)

# Filter TG numbers based on Brand + Model
tg_list = df_idx[(df_idx['MARKE'] == selected_brand) & 
                (df_idx['HANDELSBEZEICHNUNG'] == selected_model)]['TGNR'].unique()
selected_tg = st.sidebar.selectbox("Numéro d'homologation (TG)", tg_list)

# --- MAIN DISPLAY (Matching your Photo) ---
if selected_tg:
    # Get the specific car data
    car_specs = df_det[df_det['TGNR'] == selected_tg].iloc[0]
    
    # UI Layout
    st.markdown(f"""
    <div class="report-container">
        <div class="header-box">
            <span style="float: left;">Réception suisse par type</span>
            <span style="float: right;">CH {selected_tg}</span>
            <div style="clear: both;"></div>
        </div>
        
        <div style="margin-top:10px;">
            <b>01</b> {car_specs.get('FAHRZEUGART_FR', 'N/A')} <br>
            <b>04</b> {selected_brand} {selected_model}
        </div>

        <div style="display: flex; justify-content: space-between; margin-top: 20px;">
            <div style="width: 45%;">
                <div class="section-title">13 Châssis</div>
                14 Essieux / Roues: {car_specs.get('ANZ_ACHSEN', '-')} / {car_specs.get('ANZ_REIFEN', '-')} <br>
                15 Suspension: {car_specs.get('FEDERUNG_FR', '-')} <br>
                17 Vmax: {car_specs.get('VMAX', '-')} km/h <br>
                
                <div class="section-title">21 Pneus et jantes</div>
                {car_specs.get('BEREIFUNG', 'Voir remarques')}
            </div>
            
            <div style="width: 45%;">
                <div class="section-title">22 Dimensions</div>
                23 Longueur: {car_specs.get('LAENGE', '-')} mm <br>
                24 Largeur: {car_specs.get('BREITE', '-')} mm <br>
                25 Hauteur: {car_specs.get('HOEHE', '-')} mm <br>
                
                <div class="section-title">37 Poids / Garanties</div>
                38 Poids à vide: {car_specs.get('LEERGEWICHT', '-')} kg <br>
                39 Poids garanti: {car_specs.get('GESAMTGEWICHT', '-')} kg <br>
                40 Charge remorquable: {car_specs.get('ANHAENGELAST', '-')} kg
            </div>
        </div>

        <div class="section-title" style="margin-top:30px;">Remarques, conditions officielles etc.</div>
        <div style="font-size: 12px; color: #333;">
            {car_specs.get('BEMERKUNGEN', 'Aucune remarque particulière')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- REMARK CODE TRANSLATION LOGIC ---
    st.markdown("### 📋 Détails des Codes (ASTRA)")
    # Logic to find codes in the text and pull descriptions from CODE_ROH.csv
    # Example: If text contains '138', lookup 138 in df_codes
