"""
Constantes et paramètres standards pour la planification 4G/5G
Basé sur les spécifications 3GPP et ITU-R

Université Cheikh Anta Diop de Dakar (UCAD) - ESP
M2 SRT - Ingénierie des Réseaux | 2025-2026
"""

# ========== PARAMÈTRES 4G (LTE) ==========
LTE_PARAMS = {
    'frequence_mhz': 1800,
    'puissance_tx_dbm': 43,
    'gain_tx_dbi': 18,
    'gain_rx_dbi': 0,
    'sensibilite_rx_dbm': -110,
    'rsrp_excellent': -75,
    'rsrp_bon': -85,
    'rsrp_moyen': -95,
    'rsrp_faible': -105,
    'rsrp_critique': -110,
}

# ========== PARAMÈTRES 5G (NR) ==========
NR_PARAMS = {
    'frequence_mhz': 3500,
    'puissance_tx_dbm': 40,
    'gain_tx_dbi': 20,
    'gain_rx_dbi': 0,
    'sensibilite_rx_dbm': -100,
    'rsrp_excellent': -70,
    'rsrp_bon': -80,
    'rsrp_moyen': -90,
    'rsrp_faible': -95,
    'rsrp_critique': -100,
}

# ========== PERTES DE PÉNÉTRATION (Building Entry Loss) ==========
# Valeurs basées sur ITU-R P.2109-1
PENETRATION_LOSS = {
    '4G': {
        'fenetre_standard': 10,
        'fenetre_double': 15,
        'mur_leger': 20,
        'mur_standard': 25,
        'mur_epais': 30,
        'beton_renforce': 35,
    },
    '5G': {
        'fenetre_standard': 15,
        'fenetre_double': 20,
        'mur_leger': 25,
        'mur_standard': 30,
        'mur_epais': 35,
        'beton_renforce': 40,
    }
}

# ========== PARAMÈTRES ITU-R P.1411 ==========
ITU_P1411_PARAMS = {
    'hauteur_bs_m': 25,
    'hauteur_ue_m': 1.5,
    'breakpoint_distance_m': 300,
    'path_loss_exponent_los': 2.0,
    'path_loss_exponent_nlos': 4.0,
    'correction_urbaine_db': 10,
}

# ========== TYPES D'ENVIRONNEMENT ==========
ENVIRONMENT_TYPES = {
    'urbain_dense': {
        'description': 'Centre-ville, immeubles hauts',
        'correction_db': 15,
        'probabilite_los': 0.3,
    },
    'urbain': {
        'description': 'Zone urbaine standard',
        'correction_db': 10,
        'probabilite_los': 0.5,
    },
    'suburban': {
        'description': 'Banlieue, bâtiments bas',
        'correction_db': 5,
        'probabilite_los': 0.7,
    },
    'rural': {
        'description': 'Zone rurale',
        'correction_db': 0,
        'probabilite_los': 0.9,
    }
}

# ========== SEUILS DE QUALITÉ DE SERVICE ==========
QOS_THRESHOLDS = {
    'voix': -105,
    'data_basic': -100,
    'video_sd': -95,
    'video_hd': -85,
    'gaming': -75,
}

# ========== CONFIGURATION SMALL CELLS ==========
SMALL_CELL_PARAMS = {
    'puissance_tx_dbm': 24,
    'gain_antenne_dbi': 5,
    'portee_typique_m': 50,
    'cout_installation_euro': 5000,
}

# ========== PARAMÈTRES SHADOWING ==========
SHADOWING_SIGMA = {
    'rural': 4.0,
    'suburban': 6.0,
    'urbain': 8.0,
    'urbain_dense': 10.0
}

# ========== MESSAGES D'AIDE ==========
HELP_MESSAGES = {
    'frequence': "Fréquence porteuse : 1800 MHz (4G) ou 3500 MHz (5G)",
    'distance': "Distance entre la macro-cellule et le point de mesure indoor",
    'penetration': "Type de matériau de la façade du bâtiment",
    'environnement': "Densité urbaine affectant la propagation du signal",
    'rsrp': "Reference Signal Received Power - indicateur de niveau de signal",
    'shadowing': "Variabilité du signal due aux obstacles mobiles",
}