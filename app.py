"""
Application Streamlit-Outil d'Aide à la Décision 4G/5G
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

try:
    from link_budget import (
        LinkBudgetCalculator, 
        LinkBudgetParams,
        dbm_to_watt,
        calculer_distance_gps
    )
    from constants import (
        LTE_PARAMS, 
        NR_PARAMS, 
        PENETRATION_LOSS,
        ENVIRONMENT_TYPES,
        QOS_THRESHOLDS
    )
except ImportError as e:
    st.error(f"Erreur d'import des modules : {e}")
    st.info("Assurez-vous que link_budget.py et constants.py sont dans le même répertoire.")
    st.stop()

# ========== CONFIGURATION PAGE ==========
st.set_page_config(
    page_title="SmallCell Advisor",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== STYLE CSS UCAD ==========
st.markdown("""
<style>
    /* Sidebar style*/
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #4b4040 0%, #5a4a42 100%);
    }
    
    /* Forcer le texte en blanc pour les labels */
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p {
        color: white !important;
    }
    
    /* Labels des formulaires en blanc */
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stNumberInput label,
    [data-testid="stSidebar"] .stSlider label,
    [data-testid="stSidebar"] .stCheckbox label {
        color: #f5f5f5 !important;
        font-weight: 600;
    }
    
    /* IMPORTANT:les options des selectbox en NOIR GRAS */
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div,
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] .stNumberInput input {
        color: #000000 !important;
        font-weight: bold !important;
        background-color: white !important;
    }
    
    /* Options du dropdown en noir gras */
    [data-baseweb="popover"] {
        color: #000000 !important;
    }
    
    [data-baseweb="popover"] li {
        color: #000000 !important;
        font-weight: bold !important;
    }
    
    /* Checkbox text en blanc */
    [data-testid="stSidebar"] .stCheckbox span {
        color: white !important;
    }
    
    /* Header */
    .ucad-header {
        background: linear-gradient(90deg, #4b4040 0%, #5a4a42 50%, #4b4040 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(75, 64, 64, 0.3);
    }
    
    .ucad-title {
        color: white;
        font-size: 2.2rem;
        font-weight: 700;
        text-align: center;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .ucad-subtitle {
        color: #f5f5f5;
        font-size: 1.1rem;
        text-align: center;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    .ucad-institution {
        color: #e0e0e0;
        font-size: 0.9rem;
        text-align: center;
        margin-top: 0.3rem;
    }
    
    /* Bouton principal style*/
    .stButton>button {
        background: linear-gradient(135deg, #5a4a42 0%, #6d5d52 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-size: 1.05rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(90, 74, 66, 0.3);
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #6d5d52 0%, #7d6d62 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(90, 74, 66, 0.5);
    }
    
    /* Métriques */
    [data-testid="stMetricValue"] {
        color: #4b4040;
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        color: #5a4a42;
        font-weight: 600;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f0f0;
        color: #4b4040;
        border-radius: 5px 5px 0 0;
        font-weight: 600;
        padding: 0.5rem 1.5rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(180deg, #5a4a42 0%, #6d5d52 100%);
        color: white;
    }
    
    /* Messages success/warning/error professionnels */
    .stSuccess {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 1rem;
    }
    
    .stWarning {
        background-color: #fff3e0;
        border-left: 4px solid #FDB913;
        padding: 1rem;
    }
    
    .stError {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 1rem;
    }
    
    /* Divider style bibliothèque */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #5a4a42, transparent);
        margin: 2rem 0;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #f5f5f5;
        border-left: 3px solid #5a4a42;
        font-weight: 600;
        color: #4b4040;
    }
    
    /* Footer style bibliothèque */
    .ucad-footer {
        background: linear-gradient(90deg, #4b4040 0%, #5a4a42 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 8px;
        text-align: center;
        margin-top: 3rem;
    }
    
    .ucad-footer a {
        color: #f5f5f5;
        text-decoration: none;
    }
</style>
""", unsafe_allow_html=True)

# ========== HEADER  ==========
st.markdown("""
<div class="ucad-header">
    <h1 class="ucad-title"> SmallCell Advisor</h1>
    <p class="ucad-subtitle">Outil d'Aide à la Décision pour Planification 4G/5G</p>
    <p class="ucad-subtitle">Évaluation de la Couverture Indoor et Recommandation Small Cell</p>
</div>
""", unsafe_allow_html=True)

# ========== INITIALISATION SESSION STATE ==========
if 'distance_calculee' not in st.session_state:
    st.session_state.distance_calculee = 200.0

if 'historique_calculs' not in st.session_state:
    st.session_state.historique_calculs = []

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown("### ⚙️ Configuration du Système")
    
    # Choix technologie
    technologie = st.selectbox(
        "Technologie",
        options=['4G (LTE)', '5G (NR)'],
        help="Sélectionnez la technologie de réseau mobile"
    )
    
    is_5g = '5G' in technologie
    params_tech = NR_PARAMS if is_5g else LTE_PARAMS
    tech_label = '5G' if is_5g else '4G'
    
    st.markdown("---")
    
    # Paramètres radio
    st.markdown("### 📻 Paramètres Radio")
    
    frequence = st.number_input(
        "Fréquence (MHz)",
        min_value=700.0,
        max_value=6000.0,
        value=float(params_tech['frequence_mhz']),
        step=100.0,
        help="Fréquence porteuse du signal"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        puissance_tx = st.number_input(
            "P_TX (dBm)",
            min_value=20.0,
            max_value=50.0,
            value=float(params_tech['puissance_tx_dbm']),
            step=1.0,
            help="Puissance d'émission"
        )
    
    with col2:
        gain_tx = st.number_input(
            "G_TX (dBi)",
            min_value=0.0,
            max_value=25.0,
            value=float(params_tech['gain_tx_dbi']),
            step=1.0,
            help="Gain antenne émettrice"
        )
    
    gain_rx = st.number_input(
        "Gain RX (dBi)",
        min_value=-5.0,
        max_value=5.0,
        value=float(params_tech['gain_rx_dbi']),
        step=0.5,
        help="Gain antenne réceptrice"
    )
    
    st.markdown("---")
    
    # Seuil QoS
    st.markdown("### 📊 Qualité de Service")
    
    qos_type = st.selectbox(
        "Type de service",
        options=['Voix (VoLTE/VoNR)', 'Data Basic', 'Vidéo SD', 'Vidéo HD', 'Gaming/VR'],
        index=1,
        help="Sélectionnez le type de service à garantir"
    )
    
    qos_mapping = {
        'Voix (VoLTE/VoNR)': 'voix',
        'Data Basic': 'data_basic',
        'Vidéo SD': 'video_sd',
        'Vidéo HD': 'video_hd',
        'Gaming/VR': 'gaming'
    }
    
    seuil_rsrp = st.number_input(
        "Seuil RSRP minimum (dBm)",
        min_value=-120.0,
        max_value=-60.0,
        value=float(QOS_THRESHOLDS[qos_mapping[qos_type]]),
        step=1.0,
        help="Niveau minimum de signal requis"
    )
    
    st.markdown("---")
    
    # Analyse probabiliste
    st.markdown("### 🎲 Analyse Probabiliste")
    
    mode_avance = st.checkbox(
        "Activer l'analyse stochastique",
        value=True,
        help="Modélisation du shadowing (Log-Normal Fading)"
    )
    
    if mode_avance:
        st.info("💡 Le shadowing modélise les variations du signal dues aux obstacles mobiles (véhicules, piétons, etc.).")
        
        sigma_personnalise = st.slider(
            "Écart-type σ (dB)",
            min_value=4.0,
            max_value=12.0,
            value=8.0,
            step=0.5,
            help="Rural=4dB | Urbain=8dB | Urbain dense=10dB"
        )

# ========== ZONE PRINCIPALE ==========
st.markdown("## 🌍 Configuration du Scénario")

col_scenario1, col_scenario2 = st.columns(2)

with col_scenario1:
    st.markdown("### Localisation")
    
    # Calculateur GPS
    with st.expander("🗺️ Calculer distance via coordonnées GPS"):
        col_gps1, col_gps2 = st.columns(2)
        with col_gps1:
            st.markdown("**Antenne Macro**")
            lat_bs = st.number_input("Latitude BS", value=14.6928, format="%.5f", key="lat_bs")
            lon_bs = st.number_input("Longitude BS", value=-17.4467, format="%.5f", key="lon_bs")
        with col_gps2:
            st.markdown("**Point Client**")
            lat_ue = st.number_input("Latitude Client", value=14.6935, format="%.5f", key="lat_ue")
            lon_ue = st.number_input("Longitude Client", value=-17.4475, format="%.5f", key="lon_ue")
        
        if st.button("🧮 Calculer la distance"):
            try:
                dist_calc = calculer_distance_gps(lat_bs, lon_bs, lat_ue, lon_ue)
                st.session_state.distance_calculee = dist_calc
                st.success(f"Distance calculée : {dist_calc:.1f} mètres")
            except Exception as e:
                st.error(f"Erreur de calcul GPS : {e}")
    
    val_defaut = st.session_state.get('distance_calculee', 200.0)
    
    distance = st.slider(
        "Distance Macro-Cellule ↔ Bâtiment (m)",
        min_value=50.0,
        max_value=2000.0,
        value=float(val_defaut),
        step=10.0,
        help="Distance entre la macro-cellule et le point de mesure indoor"
    )
    
    environnement = st.selectbox(
        "Type d'environnement",
        options=list(ENVIRONMENT_TYPES.keys()),
        format_func=lambda x: f"{x.replace('_', ' ').title()} - {ENVIRONMENT_TYPES[x]['description']}",
        index=1,
        help="Densité urbaine affectant la propagation"
    )
    
    is_los = st.checkbox("Line of Sight (LOS)", value=False, 
                         help="Cocher si visibilité directe entre antenne et client")

with col_scenario2:
    st.markdown("### Caractéristiques du Bâtiment")
    
    materiau_facade = st.selectbox(
        "Type de façade",
        options=list(PENETRATION_LOSS[tech_label].keys()),
        format_func=lambda x: f"{x.replace('_', ' ').title()} ({PENETRATION_LOSS[tech_label][x]} dB)",
        index=2,
        help="Type de matériau de la façade du bâtiment"
    )
    
    perte_penetration = PENETRATION_LOSS[tech_label][materiau_facade]
    
    st.info(f"📉 Perte de pénétration : **{perte_penetration} dB**")
    
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        hauteur_bs = st.number_input(
            "Hauteur BS (m)", 
            min_value=10.0, 
            max_value=50.0, 
            value=25.0, 
            step=5.0,
            help="Hauteur de l'antenne macro"
        )
    with col_h2:
        hauteur_ue = st.number_input(
            "Hauteur UE (m)", 
            min_value=0.5, 
            max_value=5.0, 
            value=1.5, 
            step=0.5,
            help="Hauteur du terminal utilisateur"
        )

st.markdown("---")

# ========== BOUTON CALCUL ==========
if st.button("Lancer le Calcul", type="primary", width="stretch"):
    
    try:
        # Créer les paramètres
        params = LinkBudgetParams(
            frequence_mhz=frequence,
            puissance_tx_dbm=puissance_tx,
            gain_tx_dbi=gain_tx,
            gain_rx_dbi=gain_rx,
            distance_m=distance,
            perte_penetration_db=perte_penetration,
            hauteur_bs_m=hauteur_bs,
            hauteur_ue_m=hauteur_ue,
            environnement=environnement,
            is_los=is_los
        )
        
        # Créer le calculateur
        calculator = LinkBudgetCalculator()
        
        # Effectuer le calcul
        with st.spinner('Calcul en cours...'):
            results = calculator.calculer_bilan_complet(params, seuil_rsrp, analyse_probabiliste=mode_avance)
        
        # Ajouter à l'historique
        if mode_avance:
                    # Décision basée sur la probabilité
                    if results.probabilite_couverture >= 95:
                        decision_finale = "Macro OK"
                    elif results.probabilite_couverture >= 80:
                        decision_finale = "Small Cell Recommandée"
                    else:
                        decision_finale = "Small Cell Requise"
                    
                    proba_str = f"{results.probabilite_couverture:.1f}%"
        else:
                    # Décision basée sur RSRP seul
                    decision_finale = 'Small Cell Requise' if results.small_cell_requise else 'Macro OK'
                    proba_str = "N/A"
                
        st.session_state.historique_calculs.append({
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'technologie': tech_label,
                    'distance': distance,
                    'rsrp': f"{results.puissance_rx_dbm:.2f}",
                    'qualite': results.qualite_signal,
                    'probabilite': proba_str,
                    'decision': decision_finale
                })
        
        # ========== RÉSULTATS ==========
        st.markdown("## 📊Résultats du Calcul")
        
        if mode_avance:
            col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
        else:
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        with col_m1:
            st.metric("RSRP Moyen", f"{results.puissance_rx_dbm:.2f} dBm", 
                     delta=f"{results.marge_db:.2f} dB",
                     delta_color="normal" if results.marge_db >= 0 else "inverse")
        with col_m2:
            st.metric("Qualité Signal", results.qualite_signal)
        with col_m3:
            st.metric("Path Loss Outdoor", f"{results.path_loss_outdoor_db:.2f} dB")
        with col_m4:
            st.metric("Path Loss Total", f"{results.path_loss_total_db:.2f} dB")
        
        if mode_avance:
            with col_m5:
                st.metric("Probabilité Couverture", f"{results.probabilite_couverture:.1f}%",
                         help="Fiabilité du signal en tenant compte du shadowing")
        
        st.markdown("---")
        
        # ========== DÉCISION ==========
        st.markdown("## Recommandation Technique")
        
        if mode_avance:
            col_dec1, col_dec2 = st.columns([2, 1])
            
            with col_dec1:
                if results.probabilite_couverture >= 95:
                    st.success(f"""
                    **COUVERTURE MACRO-CELLULE SUFFISANTE**
                    
                    - RSRP moyen : **{results.puissance_rx_dbm:.2f} dBm**
                    - Probabilité de couverture : **{results.probabilite_couverture:.1f}%** (σ = {results.sigma_shadowing_db} dB)
                    - {results.probabilite_couverture:.0f}% des utilisateurs bénéficient d'un signal satisfaisant
                    
                    **Décision :** Aucune Small Cell nécessaire. La macro-cellule assure une couverture fiable.
                    """)
                elif results.probabilite_couverture >= 80:
                    st.warning(f"""
                    **COUVERTURE LIMITE-SMALL CELL RECOMMANDÉE**
                    
                    - RSRP moyen : **{results.puissance_rx_dbm:.2f} dBm**
                    - Probabilité de couverture : **{results.probabilite_couverture:.1f}%** (σ = {results.sigma_shadowing_db} dB)
                    - {100-results.probabilite_couverture:.1f}% des utilisateurs risquent des coupures
                    
                    **Décision :** Installation d'une Small Cell recommandée pour garantir 95% de fiabilité.
                    """)
                else:
                    st.error(f"""
                    **SMALL CELL REQUISE**
                    
                    - RSRP moyen : **{results.puissance_rx_dbm:.2f} dBm**
                    - Probabilité de couverture : **{results.probabilite_couverture:.1f}%** (σ = {results.sigma_shadowing_db} dB)
                    - Déficit : **{abs(results.marge_db):.2f} dB**
                    
                    **Décision :** Déploiement d'une Small Cell OBLIGATOIRE pour assurer la QoS.
                    """)
            
            with col_dec2:
                st.metric("Marge requise (95%)", f"{results.marge_requise_95:.1f} dB")
                deficit = results.marge_requise_95 - results.marge_db
                if deficit > 0:
                    st.error(f"Déficit : {deficit:.1f} dB")
                else:
                    st.success(f"Excédent : {abs(deficit):.1f} dB")
        
        else:
            if results.small_cell_requise:
                st.error(f"""
                **SMALL CELL REQUISE**
                
                RSRP ({results.puissance_rx_dbm:.2f} dBm) < Seuil ({seuil_rsrp:.2f} dBm)
                
                Déficit de couverture : {abs(results.marge_db):.2f} dB
                """)
            else:
                st.success(f"""
                **COUVERTURE SUFFISANTE**
                
                RSRP ({results.puissance_rx_dbm:.2f} dBm) > Seuil ({seuil_rsrp:.2f} dBm)
                
                Marge de sécurité : {results.marge_db:.2f} dB
                """)
        
        # ========== DÉTAILS TECHNIQUES ==========
        with st.expander("🔬 Détails Techniques du Calcul"):
            col_d1, col_d2 = st.columns(2)
            
            with col_d1:
                st.markdown("**Paramètres d'entrée**")
                st.write(f"Fréquence : {frequence} MHz")
                st.write(f"EIRP : {results.details['eirp_dbm']:.2f} dBm")
                st.write(f"Distance : {distance} m")
                st.write(f"Environnement : {environnement}")
                st.write(f"Type liaison : {'LOS' if is_los else 'NLOS'}")
            
            with col_d2:
                st.markdown("**Pertes calculées**")
                st.write(f"FSPL (espace libre) : {results.details['fspl_db']:.2f} dB")
                st.write(f"Path Loss outdoor : {results.path_loss_outdoor_db:.2f} dB")
                st.write(f"Perte pénétration : {perte_penetration} dB")
                st.write(f"Path Loss total : {results.path_loss_total_db:.2f} dB")
                st.write(f"Distance breakpoint : {results.details['distance_breakpoint_m']:.1f} m")
        
        # ========== GRAPHIQUES ==========
        st.markdown("## 📈 Analyses Graphiques")
        
        tab1, tab2, tab3 = st.tabs(["Bilan de Liaison", "Distribution Probabiliste", "Comparaison Modèles"])
        
        with tab1:
            categories = ['EIRP', 'PL Outdoor', 'PL Pénétration', 'Gain RX', 'RSRP Final']
            values = [results.details['eirp_dbm'], -results.path_loss_outdoor_db, -results.perte_penetration_db, gain_rx, results.puissance_rx_dbm]
            
            fig = go.Figure(go.Waterfall(
                x=categories, y=values,
                measure=['absolute', 'relative', 'relative', 'relative', 'total'],
                text=[f"{v:+.1f} dB" for v in values],
                textposition="outside",
                connector={"line": {"color": "#4b4040", "width": 2}},
                decreasing={"marker": {"color": "#d32f2f"}},
                increasing={"marker": {"color": "#388e3c"}},
                totals={"marker": {"color": "#5a4a42"}}
            ))
            
            fig.add_hline(y=seuil_rsrp, line_dash="dash", line_color="#d32f2f", 
                         annotation_text=f"Seuil QoS ({seuil_rsrp} dBm)", line_width=2)
            fig.update_layout(title="Bilan de Liaison - Décomposition", 
                            yaxis_title="Puissance (dBm)", showlegend=False, height=500)
            st.plotly_chart(fig, width="stretch")
        
        with tab2:
            if mode_avance:
                rsrp_vals, pdf_vals = calculator.generer_distribution_rsrp(
                    results.puissance_rx_dbm, results.sigma_shadowing_db
                )
                pdf_percent = [p / max(pdf_vals) * 100 for p in pdf_vals]
                
                fig2 = go.Figure()
                
                # 1. la zone verte est en premier pour être en arrière-plan indique la Couverture
                fig2.add_vrect(
                    x0=seuil_rsrp, 
                    x1=max(rsrp_vals), 
                    fillcolor="rgba(76, 175, 80, 0.2)", 
                    line_width=0,
                    layer="below",  # 
                    annotation_text=f"Couverture {results.probabilite_couverture:.1f}%",
                    annotation_position="top",
                    annotation_font_size=11,
                    annotation_font_color="#2e7d32"
                )
                
                # 2. la zone rouge indique le déficit
                if seuil_rsrp > min(rsrp_vals):
                    fig2.add_vrect(
                        x0=min(rsrp_vals), 
                        x1=seuil_rsrp, 
                        fillcolor="rgba(244, 67, 54, 0.15)", 
                        line_width=0,
                        layer="below",
                        annotation_text=f" Déficit {100-results.probabilite_couverture:.1f}%",
                        annotation_position="top",
                        annotation_font_size=11,
                        annotation_font_color="#c62828"
                    )
                
                # 3. PUIS : Tracer la courbe de distribution (par-dessus)
                fig2.add_trace(go.Scatter(
                    x=rsrp_vals, 
                    y=pdf_percent, 
                    mode='lines',
                    line=dict(color='#5a4a42', width=3),
                    fill='tozeroy',
                    fillcolor='rgba(90, 74, 66, 0.1)', 
                    name='Distribution RSRP',
                    hovertemplate='<b>RSRP:</b> %{x:.1f} dBm<br><b>Densité:</b> %{y:.1f}%<extra></extra>'
                ))
                
                # 4. ENFIN : Lignes verticales (par-dessus tout)
                fig2.add_vline(
                    x=results.puissance_rx_dbm, 
                    line_dash="dash", 
                    line_color="#1976d2",  
                    line_width=2,
                    annotation_text=f"μ = {results.puissance_rx_dbm:.1f} dBm",
                    annotation_position="top right",
                    annotation_font_size=11,
                    annotation_font_color="#1976d2"
                )
                
                fig2.add_vline(
                    x=seuil_rsrp, 
                    line_dash="dot", 
                    line_color="#d32f2f",
                    line_width=3,
                    annotation_text=f"Seuil = {seuil_rsrp:.0f} dBm",
                    annotation_position="bottom left",
                    annotation_font_size=11,
                    annotation_font_color="#d32f2f"
                )
                
                # Configuration finale
                fig2.update_layout(
                    title={
                        'text': f"Distribution Log-Normale du RSRP (σ = {results.sigma_shadowing_db} dB)",
                        'x': 0.5,
                        'xanchor': 'center'
                    },
                    xaxis_title="RSRP (dBm)", 
                    yaxis_title="Densité de Probabilité (%)", 
                    height=550,
                    showlegend=False,
                    hovermode='x unified',
                    plot_bgcolor='white',
                    xaxis=dict(
                        showgrid=True,
                        gridcolor='lightgray',
                        zeroline=True
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor='lightgray'
                    )
                )
                
                st.plotly_chart(fig2, width="stretch")
                
                # Légende explicative en bas
                col_leg1, col_leg2 = st.columns(2)
                with col_leg1:
                    st.success(f"🟢 **Zone verte** : {results.probabilite_couverture:.1f}% des utilisateurs ont un signal ≥ {seuil_rsrp:.0f} dBm")
                with col_leg2:
                    st.error(f"🔴 **Zone rouge** : {100-results.probabilite_couverture:.1f}% des utilisateurs ont un signal < {seuil_rsrp:.0f} dBm")
                    
            else:
                st.warning("Activez l'analyse probabiliste pour cette visualisation")
                
        with tab3:
            comparaison = calculator.comparer_modeles(params)
            
            # Filtrer les valeurs None
            comparaison_filtree = {k: v for k, v in comparaison.items() if v is not None}
            
            fig3 = go.Figure(go.Bar(
                x=list(comparaison_filtree.keys()),
                y=list(comparaison_filtree.values()),
                text=[f"{pl:.1f} dB" for pl in comparaison_filtree.values()],
                textposition='outside',
                marker=dict(color='#5a4a42')
            ))
            fig3.update_layout(title="Comparaison des Modèles de Propagation", 
                             yaxis_title="Path Loss (dB)", height=500)
            st.plotly_chart(fig3, width="stretch")
            
            pl_min, pl_max = min(comparaison_filtree.values()), max(comparaison_filtree.values())
            incertitude = pl_max - pl_min
            
            st.info(f" **Incertitude de modélisation :** {incertitude:.1f} dB | "
                   f"Modèle pessimiste : {pl_max:.1f} dB | Modèle optimiste : {pl_min:.1f} dB")
        

        # ========== SYNTHÈSE RAPPORT ==========
        st.markdown("## 📝 Synthèse pour le Rapport")

        # DÉCISION COHÉRENTE avec l'analyse probabiliste
        if mode_avance:
            # Basée sur la probabilité
            if results.probabilite_couverture >= 95:
                txt_resultat = "excellente"
                recommandation = "Le réseau macro-cellulaire existant assure une couverture fiable et satisfaisante."
                emoji_decision = "✅"
            elif results.probabilite_couverture >= 80:
                txt_resultat = "limite mais acceptable"
                recommandation = "L'installation d'une Small Cell est recommandée pour améliorer la fiabilité et atteindre 95% de couverture."
                emoji_decision = "⚠️"
            else:
                txt_resultat = "insuffisante"
                recommandation = "Le déploiement d'une Small Cell est techniquement justifié et nécessaire pour garantir la qualité de service."
                emoji_decision = "❌"
        else:
            # Basée sur le RSRP seul
            if not results.small_cell_requise:
                txt_resultat = "satisfaisante"
                recommandation = "Le réseau macro-cellulaire existant assure une couverture satisfaisante."
                emoji_decision = "✅"
            else:
                txt_resultat = "insuffisante"
                recommandation = "Le déploiement d'une Small Cell est techniquement justifié pour garantir la qualité de service."
                emoji_decision = "❌"

        # Synthèse cohérente
        synthese = f"""
        {emoji_decision} Dans un environnement **{environnement}** à une distance de **{distance} mètres**, l'utilisation de la technologie 
        **{tech_label}** ({frequence} MHz) avec une façade de type **{materiau_facade.replace('_', ' ')}** ({perte_penetration} dB) 
        conduit à une couverture **{txt_resultat}**.

        """

        if mode_avance:
            synthese += f"L'analyse probabiliste indique une fiabilité de **{results.probabilite_couverture:.1f}%**. "
        else:
            synthese += f"Le RSRP calculé est de **{results.puissance_rx_dbm:.2f} dBm** (seuil: {seuil_rsrp:.0f} dBm). "

        synthese += recommandation

        st.info(synthese)

        
        # ========== EXPORT ==========
        st.markdown("## 💾Export des Résultats")
        
        # Déterminer la décision pour l'export
        if mode_avance:
            if results.probabilite_couverture >= 95:
                decision_export = "Non nécessaire"
            elif results.probabilite_couverture >= 80:
                decision_export = "Recommandée"
            else:
                decision_export = "Requise"
        else:
            decision_export = "Requise" if results.small_cell_requise else "Non nécessaire"

        # Créer le DataFrame pour export
        df_results = pd.DataFrame({
            'Paramètre': [
                'Technologie', 
                'Fréquence (MHz)', 
                'Distance (m)', 
                'Environnement', 
                'Matériau Façade',
                'Perte Pénétration (dB)',
                'EIRP (dBm)', 
                'Path Loss Outdoor (dB)', 
                'RSRP (dBm)', 
                'Seuil QoS (dBm)', 
                'Marge (dB)', 
                'Qualité Signal',
                'Probabilité Couverture (%)',
                'Small Cell'
            ],
            'Valeur': [
                tech_label, 
                frequence, 
                distance, 
                environnement, 
                materiau_facade.replace('_', ' ').title(),
                perte_penetration,
                f"{results.details['eirp_dbm']:.2f}", 
                f"{results.path_loss_outdoor_db:.2f}", 
                f"{results.puissance_rx_dbm:.2f}", 
                f"{seuil_rsrp:.2f}", 
                f"{results.marge_db:.2f}", 
                results.qualite_signal,
                f"{results.probabilite_couverture:.1f}" if mode_avance else "N/A",
                decision_export  # ← Corrigé
            ]
        })
        
        col1, col2 = st.columns(2)
        with col1:
            # Bouton CSV 
            st.download_button(
                "📥 Télécharger CSV", 
                data=df_results.to_csv(index=False).encode('utf-8'),
                file_name=f"rf_planning_{tech_label}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", 
                width="stretch"
            )

        with col2:
            # Générer le PDF directement sans bouton intermédiaire
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.lib.units import cm
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
            from io import BytesIO
            
            # Créer le buffer PDF en mémoire
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, 
                                   rightMargin=2*cm, leftMargin=2*cm,
                                   topMargin=2*cm, bottomMargin=2*cm)
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#4b4040'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#5a4a42'),
                spaceAfter=12
            )
            
            # Contenu du PDF
            story = []
            
            # Titre
            story.append(Paragraph("SmallCell Advisor - Rapport d'Analyse Radiofrequence", title_style))
            story.append(Spacer(1, 0.5*cm))
            
            # Informations générales
            story.append(Paragraph("Informations Générales", heading_style))
            info_data = [
                ['Paramètre', 'Valeur'],
                ['Date', datetime.now().strftime("%d/%m/%Y %H:%M:%S")],
                ['Technologie', tech_label],
                ['Fréquence', f"{frequence} MHz"],
                ['Distance', f"{distance} m"],
                ['Environnement', environnement.replace('_', ' ').title()],
                ['Type de façade', materiau_facade.replace('_', ' ').title()],
                ['Type de liaison', 'LOS' if is_los else 'NLOS']
            ]
            
            info_table = Table(info_data, colWidths=[8*cm, 8*cm])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#5a4a42')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            story.append(info_table)
            story.append(Spacer(1, 1*cm))
            
            # Résultats du calcul
            story.append(Paragraph("Résultats du Calcul", heading_style))
            
            results_data = [
                ['Paramètre', 'Valeur'],
                ['EIRP', f"{results.details['eirp_dbm']:.2f} dBm"],
                ['Path Loss Outdoor', f"{results.path_loss_outdoor_db:.2f} dB"],
                ['Perte de Pénétration', f"{perte_penetration} dB"],
                ['Path Loss Total', f"{results.path_loss_total_db:.2f} dB"],
                ['RSRP Calculé', f"{results.puissance_rx_dbm:.2f} dBm"],
                ['Seuil QoS', f"{seuil_rsrp:.2f} dBm"],
                ['Marge', f"{results.marge_db:.2f} dB"],
                ['Qualité du Signal', results.qualite_signal]
            ]
            
            if mode_avance:
                results_data.extend([
                    ['Probabilité de Couverture', f"{results.probabilite_couverture:.1f}%"],
                    ['Écart-type Shadowing', f"{results.sigma_shadowing_db} dB"],
                    ['Marge requise (95%)', f"{results.marge_requise_95:.1f} dB"]
                ])
            
            results_table = Table(results_data, colWidths=[10*cm, 6*cm])
            results_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#5a4a42')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            story.append(results_table)
            story.append(Spacer(1, 1*cm))
            
            # Décision
            story.append(Paragraph("Recommandation Technique", heading_style))
            
            # Déterminer couleur selon décision
            if mode_avance:
                if results.probabilite_couverture >= 95:
                    decision_text = "✓ Couverture Macro Suffisante"
                    decision_color = colors.green
                    decision_detail = f"La probabilité de couverture est de {results.probabilite_couverture:.1f}%, ce qui est excellent. Aucune Small Cell n'est nécessaire."
                elif results.probabilite_couverture >= 80:
                    decision_text = "⚠ Small Cell Recommandée"
                    decision_color = colors.orange
                    decision_detail = f"La probabilité de couverture est de {results.probabilite_couverture:.1f}%, ce qui est limite. Une Small Cell est recommandée pour améliorer la fiabilité."
                else:
                    decision_text = "✗ Small Cell Requise"
                    decision_color = colors.red
                    decision_detail = f"La probabilité de couverture est de {results.probabilite_couverture:.1f}%, ce qui est insuffisant. Le déploiement d'une Small Cell est obligatoire."
            else:
                if results.small_cell_requise:
                    decision_text = "✗ Small Cell Requise"
                    decision_color = colors.red
                    decision_detail = f"Le RSRP ({results.puissance_rx_dbm:.2f} dBm) est inférieur au seuil ({seuil_rsrp:.2f} dBm). Une Small Cell est nécessaire."
                else:
                    decision_text = "✓ Couverture Macro Suffisante"
                    decision_color = colors.green
                    decision_detail = f"Le RSRP ({results.puissance_rx_dbm:.2f} dBm) est supérieur au seuil ({seuil_rsrp:.2f} dBm). La macro-cellule suffit."
        
            decision_data = [
                ['Décision', 'Détails'],
                [Paragraph(decision_text, styles['Normal']), 
                 Paragraph(decision_detail, styles['Normal'])]  # ← Utiliser Paragraph pour wrapping
            ]

            decision_table = Table(decision_data, colWidths=[5*cm, 11*cm])  # ← Ajuster les largeurs
            decision_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#5a4a42')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 1), (-1, -1), 10),      # ← Ajout padding
                ('BOTTOMPADDING', (0, 1), (-1, -1), 10),   # ← Ajout padding
                ('BACKGROUND', (0, 1), (0, 1), decision_color),
                ('TEXTCOLOR', (0, 1), (0, 1), colors.whitesmoke),
                ('FONTNAME', (0, 1), (0, 1), 'Helvetica-Bold'),
                ('BACKGROUND', (1, 1), (1, 1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('WORDWRAP', (0, 0), (-1, -1), True)      # ← Force le retour à la ligne
            ]))
            story.append(decision_table)
            story.append(Spacer(1, 1*cm))
            
                       # Synthèse
            story.append(Paragraph("Synthèse", heading_style))

            # Déterminer la recommandation textuelle
            if mode_avance:
                if results.probabilite_couverture >= 95:
                    recommandation_finale = "Aucune Small Cell n'est nécessaire. La macro-cellule assure une couverture excellente."
                    emoji_recommandation = "✓"
                elif results.probabilite_couverture >= 80:
                    recommandation_finale = "L'installation d'une Small Cell est <b>recommandée</b> pour améliorer la fiabilité et atteindre 95% de couverture."
                    emoji_recommandation = "⚠"
                else:
                    recommandation_finale = "Le déploiement d'une Small Cell est <b>obligatoire</b> pour garantir la qualité de service."
                    emoji_recommandation = "✗"
            else:
                if results.small_cell_requise:
                    recommandation_finale = "Le déploiement d'une Small Cell est <b>obligatoire</b> pour garantir la qualité de service."
                    emoji_recommandation = "✗"
                else:
                    recommandation_finale = "Aucune Small Cell n'est nécessaire. La macro-cellule assure une couverture satisfaisante."
                    emoji_recommandation = "✓"

            # Texte de synthèse complet
            synthese_text = f"""
            <b>{emoji_recommandation} Synthèse de l'Analyse</b><br/><br/>

            Dans un environnement <b>{environnement.replace('_', ' ')}</b> à une distance de <b>{distance} mètres</b>, 
            l'utilisation de la technologie <b>{tech_label}</b> ({frequence} MHz) avec une façade de type 
            <b>{materiau_facade.replace('_', ' ')}</b> ({perte_penetration} dB) conduit à un RSRP de 
            <b>{results.puissance_rx_dbm:.2f} dBm</b>.
            """

            if mode_avance:
                synthese_text += f"""<br/><br/>
                L'analyse probabiliste indique une fiabilité de <b>{results.probabilite_couverture:.1f}%</b> 
                avec un écart-type de shadowing de {results.sigma_shadowing_db} dB.
                """

            synthese_text += f"""<br/><br/>
            <b>Recommandation :</b> {recommandation_finale}
            """

            story.append(Paragraph(synthese_text, styles['Normal']))
            story.append(Spacer(1, 0.5*cm))
            
            # Footer
            story.append(Spacer(1, 2*cm))
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
            story.append(Paragraph(
                "SmallCell Advisor<br/>Hamit Amir MAHAMAT", 
                footer_style
            ))
            
            # Générer le PDF
            doc.build(story)
            
            # Récupérer le PDF
            pdf_data = buffer.getvalue()
            buffer.close()
            
            # Bouton de téléchargement DIRECT (sans bouton intermédiaire)
            st.download_button(
                label="📥 Télécharger PDF",
                data=pdf_data,
                file_name=f"rapport_rf_{tech_label}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                width="stretch"
            )
    
    except ValueError as e:
        st.error(f"❌ **Erreur de validation des paramètres**")
        st.error(str(e))
        st.info("💡 Vérifiez que tous les paramètres sont dans les limites acceptables.")
    
    except Exception as e:
        st.error(f"❌ **Erreur inattendue lors du calcul**")
        st.error(str(e))
        st.info("💡 Veuillez vérifier vos paramètres et réessayer. Si l'erreur persiste, contactez le support.")
        import traceback
        with st.expander("🔍 Détails techniques de l'erreur"):
            st.code(traceback.format_exc())

# ========== HISTORIQUE ==========
if len(st.session_state.historique_calculs) > 0:
    with st.expander(f"📚 Historique des Calculs ({len(st.session_state.historique_calculs)} calculs)"):
        df_hist = pd.DataFrame(st.session_state.historique_calculs)
        st.dataframe(df_hist, width='stretch')
        
        if st.button("Effacer l'historique"):
            st.session_state.historique_calculs = []
            st.rerun()

# ========== FOOTER ==========
st.write("---")
st.markdown(
    """
    <div style="text-align: center; padding: 10px 0; font-family: 'Arial', sans-serif; font-size: 0.9rem; color: #555;">
        <p style="margin: 0; line-height: 1.4;">
            <b style="color: #004a99; font-size: 1.1rem;">SmallCell Advisor</b> <br> 
             <b> Hamit Amir MAHAMAT</b> sous la direction du <b>Dr. Mangoné FALL</b>
        </p>
        <p style="margin: 5px 0 0 0; font-size: 0.8rem; color: #777;">
            Modèle : <a href="https://www.itu.int" target="_blank" style="text-decoration: none; color: #004a99;">ITU-R P.1411</a> | 
            Méthode : Analyse Probabiliste Multi-Modèles
        </p>

    </div>
""", unsafe_allow_html=True)
