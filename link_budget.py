"""
Module de calcul du bilan de liaison (Link Budget) pour réseaux 4G/5G
VERSION AMÉLIORÉE avec validation et gestion d'erreurs robuste

Améliorations:
- Validation complète des paramètres d'entrée
- Gestion d'erreurs avec messages explicites
- Vérification des limites de validité des modèles
- Logging pour débogage
- Documentation enrichie

Université Cheikh Anta Diop de Dakar (UCAD) - ESP
M2 SRT - Ingénierie des Réseaux | 2025-2026
"""

import math
import logging
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Exception levée lors d'erreurs de validation des paramètres"""
    pass


@dataclass
class LinkBudgetParams:
    """Paramètres d'entrée pour le calcul du bilan de liaison"""
    frequence_mhz: float
    puissance_tx_dbm: float
    gain_tx_dbi: float
    gain_rx_dbi: float
    distance_m: float
    perte_penetration_db: float
    hauteur_bs_m: float = 25.0
    hauteur_ue_m: float = 1.5
    environnement: str = 'urbain'
    is_los: bool = False
    
    def __post_init__(self):
        """Validation automatique après initialisation"""
        self.valider()
    
    def valider(self):
        """Valide tous les paramètres"""
        errors = []
        
        # Validation fréquence
        if not 700 <= self.frequence_mhz <= 6000:
            errors.append(f"Fréquence {self.frequence_mhz} MHz hors limites [700-6000 MHz]")
        
        # Validation puissance
        if not 0 <= self.puissance_tx_dbm <= 60:
            errors.append(f"Puissance TX {self.puissance_tx_dbm} dBm hors limites [0-60 dBm]")
        
        # Validation gains
        if not -10 <= self.gain_tx_dbi <= 30:
            errors.append(f"Gain TX {self.gain_tx_dbi} dBi hors limites [-10-30 dBi]")
        
        if not -10 <= self.gain_rx_dbi <= 10:
            errors.append(f"Gain RX {self.gain_rx_dbi} dBi hors limites [-10-10 dBi]")
        
        # Validation distance
        if not 1 <= self.distance_m <= 50000:
            errors.append(f"Distance {self.distance_m} m hors limites [1-50000 m]")
        
        # Validation perte de pénétration
        if not 0 <= self.perte_penetration_db <= 50:
            errors.append(f"Perte pénétration {self.perte_penetration_db} dB hors limites [0-50 dB]")
        
        # Validation hauteurs
        if not 10 <= self.hauteur_bs_m <= 100:
            errors.append(f"Hauteur BS {self.hauteur_bs_m} m hors limites [10-100 m]")
        
        if not 0.5 <= self.hauteur_ue_m <= 10:
            errors.append(f"Hauteur UE {self.hauteur_ue_m} m hors limites [0.5-10 m]")
        
        # Validation environnement
        envs_valides = ['rural', 'suburban', 'urbain', 'urbain_dense']
        if self.environnement not in envs_valides:
            errors.append(f"Environnement '{self.environnement}' invalide. "
                         f"Valeurs acceptées: {envs_valides}")
        
        if errors:
            raise ValidationError("\n".join(errors))


@dataclass
class LinkBudgetResults:
    """Résultats du calcul du bilan de liaison"""
    puissance_rx_dbm: float
    path_loss_outdoor_db: float
    path_loss_total_db: float
    perte_penetration_db: float
    marge_db: float
    qualite_signal: str
    small_cell_requise: bool
    details: Dict[str, float]
    probabilite_couverture: float = 0.0
    sigma_shadowing_db: float = 8.0
    marge_requise_95: float = 0.0
    warnings: list = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class LinkBudgetCalculator:
    """
    Calculateur de bilan de liaison selon ITU-R P.1411
    VERSION AMÉLIORÉE avec validation robuste
    """
    
    # Limites de validité des modèles
    LIMITES_ITU_P1411 = {
        'frequence_min_mhz': 800,
        'frequence_max_mhz': 6000,
        'distance_min_m': 20,
        'distance_max_m': 5000
    }
    
    LIMITES_COST231 = {
        'frequence_min_mhz': 1500,
        'frequence_max_mhz': 2000,
        'distance_min_m': 1000,
        'distance_max_m': 20000
    }
    
    def __init__(self):
        self.c = 3e8  # Vitesse de la lumière (m/s)
        
        # Paramètres de shadowing selon environnement
        self.sigma_shadowing = {
            'rural': 4.0,
            'suburban': 6.0,
            'urbain': 8.0,
            'urbain_dense': 10.0
        }
        
        logger.info("LinkBudgetCalculator initialisé")
    
    def verifier_validite_modele(self, params: LinkBudgetParams, 
                                  modele: str) -> Tuple[bool, Optional[str]]:
        """
        Vérifie si les paramètres sont dans les limites de validité du modèle
        
        Returns:
            (est_valide, message_warning)
        """
        if modele == 'ITU-P1411':
            limites = self.LIMITES_ITU_P1411
            if not (limites['frequence_min_mhz'] <= params.frequence_mhz <= limites['frequence_max_mhz']):
                return False, (f"Fréquence {params.frequence_mhz} MHz hors limites ITU-P.1411 "
                              f"[{limites['frequence_min_mhz']}-{limites['frequence_max_mhz']} MHz]")
            
            if not (limites['distance_min_m'] <= params.distance_m <= limites['distance_max_m']):
                return False, (f"Distance {params.distance_m} m hors limites ITU-P.1411 "
                              f"[{limites['distance_min_m']}-{limites['distance_max_m']} m]")
        
        elif modele == 'COST-231':
            limites = self.LIMITES_COST231
            if not (limites['frequence_min_mhz'] <= params.frequence_mhz <= limites['frequence_max_mhz']):
                return False, (f"Fréquence {params.frequence_mhz} MHz hors limites COST-231 "
                              f"[{limites['frequence_min_mhz']}-{limites['frequence_max_mhz']} MHz]")
            
            if not (limites['distance_min_m'] <= params.distance_m <= limites['distance_max_m']):
                return False, (f"Distance {params.distance_m} m hors limites COST-231 "
                              f"[{limites['distance_min_m']}-{limites['distance_max_m']} m]")
        
        return True, None
    
    def calcul_path_loss_free_space(self, frequence_mhz: float, distance_m: float) -> float:
        """
        Calcul de la perte en espace libre (Free Space Path Loss - FSPL)
        
        Formule: FSPL(dB) = 32.45 + 20*log10(f_MHz) + 20*log10(d_km)
        
        Args:
            frequence_mhz: Fréquence en MHz
            distance_m: Distance en mètres
            
        Returns:
            Perte en dB
            
        Raises:
            ValueError: Si les paramètres sont invalides
        """
        if distance_m <= 0:
            raise ValueError(f"La distance doit être positive (reçu: {distance_m} m)")
        
        if frequence_mhz <= 0:
            raise ValueError(f"La fréquence doit être positive (reçu: {frequence_mhz} MHz)")
        
        distance_km = distance_m / 1000.0
        
        # Protection contre log10(0)
        if distance_km < 0.001:
            logger.warning(f"Distance très faible ({distance_m} m), FSPL peut être imprécis")
        
        fspl = 32.45 + 20 * math.log10(frequence_mhz) + 20 * math.log10(distance_km)
        
        logger.debug(f"FSPL calculé: {fspl:.2f} dB (f={frequence_mhz} MHz, d={distance_m} m)")
        
        return fspl
    
    def calcul_path_loss_itu_p1411(self, params: LinkBudgetParams) -> float:
        """
        Calcul de la perte de propagation selon ITU-R P.1411
        Modèle pour environnements urbains (street canyon)
        
        Args:
            params: Paramètres du lien radio
            
        Returns:
            Path loss en dB
        """
        # Vérifier validité du modèle
        est_valide, msg_warning = self.verifier_validite_modele(params, 'ITU-P1411')
        if not est_valide:
            logger.warning(f"ITU-P.1411: {msg_warning}")
        
        d = params.distance_m
        h_bs = params.hauteur_bs_m
        h_ue = params.hauteur_ue_m
        
        # Point de rupture (breakpoint)
        d_bp = 4 * h_bs * h_ue * (params.frequence_mhz * 1e6) / self.c
        
        # Protection contre valeurs aberrantes
        if d_bp <= 0:
            logger.error(f"Breakpoint invalide: {d_bp} m")
            d_bp = 100  # Valeur par défaut
        
        # Calcul de la perte de base (FSPL)
        fspl = self.calcul_path_loss_free_space(params.frequence_mhz, d)
        
        # Correction selon la distance par rapport au breakpoint
        if d <= d_bp:
            path_loss = fspl
        else:
            pl_bp = self.calcul_path_loss_free_space(params.frequence_mhz, d_bp)
            exponent = 2.0 if params.is_los else 4.0
            path_loss = pl_bp + 10 * exponent * math.log10(d / d_bp)
        
        # Correction environnement urbain
        correction_env = {
            'rural': 0,
            'suburban': 5,
            'urbain': 10,
            'urbain_dense': 15
        }
        correction = correction_env.get(params.environnement, 10)
        
        path_loss_total = path_loss + correction
        
        logger.info(f"ITU-P.1411: PL={path_loss_total:.2f} dB "
                   f"(d={d}m, d_bp={d_bp:.1f}m, env={params.environnement})")
        
        return path_loss_total
    
    def calcul_path_loss_cost231(self, params: LinkBudgetParams) -> float:
        """
        Calcul de la perte de propagation selon COST-231 Hata
        
        Args:
            params: Paramètres du lien
            
        Returns:
            Path loss en dB
        """
        # Vérifier validité
        est_valide, msg_warning = self.verifier_validite_modele(params, 'COST-231')
        if not est_valide:
            raise ValidationError(f"COST-231 non applicable: {msg_warning}")
        
        freq_mhz = params.frequence_mhz
        d_km = params.distance_m / 1000.0
        h_bs = params.hauteur_bs_m
        h_m = params.hauteur_ue_m
        
        # Facteur de correction hauteur mobile
        a_hm = (1.1 * math.log10(freq_mhz) - 0.7) * h_m - (1.56 * math.log10(freq_mhz) - 0.8)
        
        # Correction environnement
        corrections_env = {
            'rural': -15,
            'suburban': -2,
            'urbain': 0,
            'urbain_dense': 3
        }
        c_m = corrections_env.get(params.environnement, 0)
        
        # Formule COST-231 Hata
        pl = (46.3 + 33.9 * math.log10(freq_mhz) 
              - 13.82 * math.log10(h_bs) 
              - a_hm
              + (44.9 - 6.55 * math.log10(h_bs)) * math.log10(d_km)
              + c_m)
        
        logger.info(f"COST-231: PL={pl:.2f} dB")
        
        return pl
    
    def comparer_modeles(self, params: LinkBudgetParams) -> Dict[str, float]:
        """
        Compare différents modèles de propagation sur le même scénario
        
        Args:
            params: Paramètres du scénario
            
        Returns:
            Dictionnaire {nom_modele: path_loss_db}
        """
        resultats = {}
        
        # FSPL (toujours calculable)
        resultats['FSPL (Théorique)'] = self.calcul_path_loss_free_space(
            params.frequence_mhz, params.distance_m
        )
        
        # ITU-R P.1411
        try:
            resultats['ITU-R P.1411'] = self.calcul_path_loss_itu_p1411(params)
        except Exception as e:
            logger.error(f"Erreur ITU-P.1411: {e}")
            resultats['ITU-R P.1411'] = None
        
        # COST-231 (uniquement si dans limites de validité)
        try:
            est_valide, _ = self.verifier_validite_modele(params, 'COST-231')
            if est_valide:
                resultats['COST-231 Hata'] = self.calcul_path_loss_cost231(params)
            else:
                logger.info("COST-231 non applicable (hors limites de validité)")
        except Exception as e:
            logger.error(f"Erreur COST-231: {e}")
        
        # Modèle urbain simplifié
        resultats['Urbain Simple'] = resultats['FSPL (Théorique)'] + 15
        
        return resultats
    
    def calcul_rsrp(self, params: LinkBudgetParams) -> float:
        """
        Calcul du RSRP (Reference Signal Received Power)
        
        Formule: P_rx = P_tx + G_tx + G_rx - PL_outdoor - PL_penetration
        
        Args:
            params: Paramètres du lien
            
        Returns:
            RSRP en dBm
        """
        eirp = params.puissance_tx_dbm + params.gain_tx_dbi
        pl_outdoor = self.calcul_path_loss_itu_p1411(params)
        rsrp = eirp + params.gain_rx_dbi - pl_outdoor - params.perte_penetration_db
        
        logger.info(f"RSRP calculé: {rsrp:.2f} dBm "
                   f"(EIRP={eirp:.1f}, PL_out={pl_outdoor:.1f}, PL_pen={params.perte_penetration_db})")
        
        return rsrp
    
    def evaluer_qualite_signal(self, rsrp_dbm: float, technologie: str = '4G') -> str:
        """
        Évalue la qualité du signal selon les seuils standard 3GPP
        
        Args:
            rsrp_dbm: Niveau RSRP mesuré
            technologie: '4G' ou '5G'
            
        Returns:
            Qualité : 'Excellent', 'Bon', 'Moyen', 'Faible', 'Critique'
        """
        if technologie == '5G':
            seuils = [(-70, 'Excellent'), (-80, 'Bon'), (-90, 'Moyen'), 
                     (-95, 'Faible'), (-200, 'Critique')]
        else:
            seuils = [(-75, 'Excellent'), (-85, 'Bon'), (-95, 'Moyen'), 
                     (-105, 'Faible'), (-200, 'Critique')]
        
        for seuil, qualite in seuils:
            if rsrp_dbm >= seuil:
                return qualite
        
        return 'Critique'
    
    def decision_small_cell(self, rsrp_dbm: float, seuil_dbm: float) -> Tuple[bool, float]:
        """
        Détermine si une Small Cell est nécessaire
        
        Args:
            rsrp_dbm: RSRP calculé
            seuil_dbm: Seuil minimum requis
            
        Returns:
            (requise: bool, marge: float en dB)
        """
        marge = rsrp_dbm - seuil_dbm
        requise = rsrp_dbm < seuil_dbm
        
        logger.info(f"Décision Small Cell: {'REQUISE' if requise else 'NON REQUISE'} "
                   f"(marge={marge:.2f} dB)")
        
        return requise, marge
    
    def calculer_probabilite_couverture(self, rsrp_moyen_dbm: float, 
                                       seuil_dbm: float,
                                       sigma_shadowing_db: float = 8.0) -> float:
        """
        Calcule la probabilité que le signal réel dépasse le seuil
        en tenant compte du Shadowing (Log-Normal fading)
        
        Args:
            rsrp_moyen_dbm: RSRP moyen calculé
            seuil_dbm: Seuil minimum requis
            sigma_shadowing_db: Écart-type du shadowing
        
        Returns:
            Probabilité en pourcentage (0-100%)
        """
        # Protection contre division par zéro
        if sigma_shadowing_db == 0:
            logger.warning("Sigma = 0, utilisation de valeur minimale 0.1 dB")
            sigma_shadowing_db = 0.1
        
        marge_db = rsrp_moyen_dbm - seuil_dbm
        probabilite = 0.5 * math.erfc(-marge_db / (math.sqrt(2) * sigma_shadowing_db))
        
        # Forcer dans [0, 100]
        probabilite = max(0, min(1, probabilite)) * 100
        
        logger.info(f"Probabilité de couverture: {probabilite:.1f}% "
                   f"(RSRP_moy={rsrp_moyen_dbm:.1f}, seuil={seuil_dbm}, σ={sigma_shadowing_db})")
        
        return probabilite
    
    def calculer_marge_probabiliste(self, probabilite_cible: float,
                                    sigma_shadowing_db: float = 8.0) -> float:
        """
        Calcule la marge requise pour atteindre une probabilité de couverture cible
        
        Args:
            probabilite_cible: Probabilité souhaitée (0-100%)
            sigma_shadowing_db: Écart-type du shadowing
        
        Returns:
            Marge requise en dB
        """
        # Table de correspondance probabilité -> z-score
        if probabilite_cible >= 99:
            z_score = 2.33
        elif probabilite_cible >= 95:
            z_score = 1.645
        elif probabilite_cible >= 90:
            z_score = 1.28
        elif probabilite_cible >= 75:
            z_score = 0.67
        elif probabilite_cible >= 50:
            z_score = 0.0
        else:
            z_score = -1.0 * (50 - probabilite_cible) / 25.0
        
        marge_requise_db = z_score * sigma_shadowing_db
        
        return marge_requise_db
    
    def generer_distribution_rsrp(self, rsrp_moyen_dbm: float,
                                  sigma_shadowing_db: float = 8.0,
                                  n_samples: int = 1000) -> Tuple[list, list]:
        """
        Génère une distribution statistique du RSRP pour visualisation
        
        Args:
            rsrp_moyen_dbm: RSRP moyen
            sigma_shadowing_db: Écart-type
            n_samples: Nombre de points
        
        Returns:
            (rsrp_values, pdf_values)
        """
        # Protection
        if sigma_shadowing_db == 0:
            sigma_shadowing_db = 0.1
        
        rsrp_min = rsrp_moyen_dbm - 4 * sigma_shadowing_db
        rsrp_max = rsrp_moyen_dbm + 4 * sigma_shadowing_db
        
        rsrp_values = []
        pdf_values = []
        
        for i in range(n_samples):
            rsrp = rsrp_min + (rsrp_max - rsrp_min) * i / (n_samples - 1)
            exponent = -0.5 * ((rsrp - rsrp_moyen_dbm) / sigma_shadowing_db) ** 2
            pdf = (1 / (sigma_shadowing_db * math.sqrt(2 * math.pi))) * math.exp(exponent)
            
            rsrp_values.append(rsrp)
            pdf_values.append(pdf)
        
        return rsrp_values, pdf_values
    
    def calculer_bilan_complet(self, params: LinkBudgetParams, 
                               seuil_rsrp_dbm: float,
                               analyse_probabiliste: bool = True) -> LinkBudgetResults:
        """
        Effectue le calcul complet du bilan de liaison avec validation
        
        Args:
            params: Paramètres d'entrée
            seuil_rsrp_dbm: Seuil minimum acceptable
            analyse_probabiliste: Inclure calcul probabiliste
            
        Returns:
            Résultats détaillés du calcul
            
        Raises:
            ValidationError: Si les paramètres sont invalides
        """
        logger.info("="*50)
        logger.info(f"DÉBUT CALCUL BILAN DE LIAISON - {datetime.now()}")
        logger.info("="*50)
        
        warnings = []
        
        try:
            # Validation des paramètres (déjà faite dans __post_init__)
            # Mais on peut ajouter des warnings supplémentaires
            
            # Calcul des pertes
            pl_outdoor = self.calcul_path_loss_itu_p1411(params)
            pl_total = pl_outdoor + params.perte_penetration_db
            
            # Calcul RSRP moyen
            rsrp = self.calcul_rsrp(params)
            
            # Qualité du signal
            technologie = '5G' if params.frequence_mhz > 3000 else '4G'
            qualite = self.evaluer_qualite_signal(rsrp, technologie)
            
            # Décision Small Cell
            small_cell_req, marge = self.decision_small_cell(rsrp, seuil_rsrp_dbm)
            
            # Détails complémentaires
            details = {
                'eirp_dbm': params.puissance_tx_dbm + params.gain_tx_dbi,
                'fspl_db': self.calcul_path_loss_free_space(
                    params.frequence_mhz, params.distance_m
                ),
                'distance_breakpoint_m': 4 * params.hauteur_bs_m * params.hauteur_ue_m * 
                                         (params.frequence_mhz * 1e6) / self.c,
            }
            
            # Analyse probabiliste
            probabilite_couverture = 0.0
            marge_requise_95 = 0.0
            sigma = 8.0
            
            if analyse_probabiliste:
                sigma = self.sigma_shadowing.get(params.environnement, 8.0)
                probabilite_couverture = self.calculer_probabilite_couverture(
                    rsrp, seuil_rsrp_dbm, sigma
                )
                marge_requise_95 = self.calculer_marge_probabiliste(95.0, sigma)
                
                # Warning si probabilité faible
                if probabilite_couverture < 50:
                    warnings.append("⚠️ Probabilité de couverture très faible (<50%)")
            
            # Warning sur qualité signal
            if qualite in ['Faible', 'Critique']:
                warnings.append(f"⚠️ Qualité du signal {qualite}")
            
            logger.info("CALCUL TERMINÉ AVEC SUCCÈS")
            
            return LinkBudgetResults(
                puissance_rx_dbm=rsrp,
                path_loss_outdoor_db=pl_outdoor,
                path_loss_total_db=pl_total,
                perte_penetration_db=params.perte_penetration_db,
                marge_db=marge,
                qualite_signal=qualite,
                small_cell_requise=small_cell_req,
                details=details,
                probabilite_couverture=probabilite_couverture,
                sigma_shadowing_db=sigma,
                marge_requise_95=marge_requise_95,
                warnings=warnings
            )
            
        except Exception as e:
            logger.error(f"ERREUR LORS DU CALCUL: {str(e)}", exc_info=True)
            raise


# Fonctions utilitaires
def dbm_to_watt(dbm: float) -> float:
    """Convertit dBm en Watt"""
    return 10 ** ((dbm - 30) / 10)


def watt_to_dbm(watt: float) -> float:
    """Convertit Watt en dBm"""
    if watt <= 0:
        raise ValueError("La puissance en Watt doit être positive")
    return 10 * math.log10(watt) + 30


def db_to_linear(db: float) -> float:
    """Convertit dB en échelle linéaire"""
    return 10 ** (db / 10)


def linear_to_db(linear: float) -> float:
    """Convertit échelle linéaire en dB"""
    if linear <= 0:
        raise ValueError("La valeur linéaire doit être positive")
    return 10 * math.log10(linear)


def calculer_distance_gps(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcule la distance en mètres entre deux points GPS (formule de Haversine)
    
    Args:
        lat1, lon1: Coordonnées du point 1 (degrés décimaux)
        lat2, lon2: Coordonnées du point 2 (degrés décimaux)
    
    Returns:
        Distance en mètres
    
    Raises:
        ValueError: Si les coordonnées sont invalides
    """
    # Validation coordonnées
    if not -90 <= lat1 <= 90 or not -90 <= lat2 <= 90:
        raise ValueError(f"Latitudes invalides: {lat1}, {lat2}")
    
    if not -180 <= lon1 <= 180 or not -180 <= lon2 <= 180:
        raise ValueError(f"Longitudes invalides: {lon1}, {lon2}")
    
    R = 6371000  # Rayon de la Terre en mètres
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2)**2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    
    logger.info(f"Distance GPS calculée: {distance:.1f} m")
    
    return distance


def calculer_distance_3d(lat1: float, lon1: float, alt1: float,
                         lat2: float, lon2: float, alt2: float) -> float:
    """
    Calcule la distance 3D entre deux points GPS avec altitude
    
    Args:
        lat1, lon1, alt1: Coordonnées et altitude du point 1
        lat2, lon2, alt2: Coordonnées et altitude du point 2
    
    Returns:
        Distance 3D en mètres
    """
    # Distance horizontale
    dist_horiz = calculer_distance_gps(lat1, lon1, lat2, lon2)
    
    # Distance verticale
    dist_vert = abs(alt2 - alt1)
    
    # Distance 3D (Pythagore)
    dist_3d = math.sqrt(dist_horiz**2 + dist_vert**2)
    
    logger.info(f"Distance 3D: {dist_3d:.1f} m (horiz={dist_horiz:.1f}m, vert={dist_vert:.1f}m)")
    
    return dist_3d
