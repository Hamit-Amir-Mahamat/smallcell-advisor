# SmallCell Advisor - Documentation Complète

## 📡 Description

**SmallCell Advisor** est un outil d'aide à la décision pour la planification RF des réseaux 4G/5G. Il permet de déterminer si le déploiement d'une Small Cell est nécessaire pour assurer une couverture indoor satisfaisante.

### Développé par
- **Auteur**: Hamit Amir MAHAMAT
- **Formation**: M2 SRT-Ingénierie des Réseaux | 2025-2026

---

## 🎯 Fonctionnalités Principales

### 1. Calcul de Bilan de Liaison
- Implémentation du modèle **ITU-R P.1411** (propagation urbaine micro-cellulaire)
- Calcul de **RSRP** (Reference Signal Received Power)
- Prise en compte des pertes de pénétration (Building Entry Loss)
- Support 4G (LTE) et 5G (NR)

### 2. Analyse Probabiliste
- Modélisation du **shadowing** (Log-Normal Fading)
- Calcul de la **probabilité de couverture** avec écart-type configurable (σ)
- Estimation de la **marge requise** pour 95% de fiabilité

### 3. Comparaison Multi-Modèles
- **FSPL** (Free Space Path Loss) - modèle théorique
- **ITU-R P.1411** - modèle urbain micro-cellulaire
- **COST-231 Hata** - modèle empirique macro-cellulaire (si applicable)
- **Modèle urbain simplifié**

### 4. Aide à la Décision
- Recommandation automatique : Small Cell **REQUISE**, **RECOMMANDÉE**, ou **NON NÉCESSAIRE**
- Basée sur la probabilité de couverture :
  - ≥ 95% → Couverture macro suffisante
  - 80-95% → Small Cell recommandée
  - < 80% → Small Cell obligatoire

### 5. Visualisations Interactives
- Graphique en cascade (Waterfall) du bilan de liaison
- Distribution log-normale du RSRP
- Comparaison des modèles de propagation

### 6. Export des Résultats
- Export CSV pour analyse dans Excel
- Export Markdown pour documentation
- Synthèse prête pour rapport technique

---

## 📋 Prérequis

### Logiciels
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Dépendances Python
Toutes les dépendances sont listées dans `requirements.txt`:

```
streamlit>=1.28.0      # Interface utilisateur
numpy>=1.24.0          # Calculs scientifiques
pandas>=2.0.0          # Traitement de données
plotly>=5.17.0         # Visualisations interactives
tabulate>=0.9.0        # Formatage de tableaux
```

---

## 🚀 Installation

### 1. Cloner ou Télécharger le Projet

```bash
git clone https://github.com/votre-repo/smallcell-advisor.git
cd smallcell-advisor
```

### 2. Créer un Environnement Virtuel (Recommandé)

**Windows :**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac :**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les Dépendances

```bash
pip install -r requirements.txt
```

---

## 💻 Utilisation

### Lancer l'Application

```bash
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur par défaut à l'adresse `http://localhost:8501`.

### Configuration du Scénario

#### 1. **Sidebar - Paramètres Système**

**Technologie** :
- 4G (LTE) - 1800 MHz par défaut
- 5G (NR) - 3500 MHz par défaut

**Paramètres Radio** :
- Fréquence (MHz)
- Puissance TX (dBm)
- Gain antenne TX (dBi)
- Gain antenne RX (dBi)

**Qualité de Service** :
- Type de service (Voix, Data, Vidéo, Gaming)
- Seuil RSRP minimum personnalisable

**Analyse Probabiliste** :
- Activation/désactivation
- Écart-type σ du shadowing (4-12 dB)

#### 2. **Zone Principale - Scénario**

**Localisation** :
- Distance Macro → Bâtiment (50-2000 m)
- Calculateur GPS intégré
- Type d'environnement (rural, suburban, urbain, urbain dense)
- Line of Sight (LOS/NLOS)

**Bâtiment** :
- Type de façade (fenêtre, mur léger, mur standard, béton)
- Hauteur antenne BS (10-50 m)
- Hauteur utilisateur (0.5-5 m)

#### 3. **Lancer le Calcul**

Cliquez sur le bouton **"Lancer le Calcul"** pour obtenir :
- Résultats métriques (RSRP, qualité, path loss)
- Recommandation technique
- Graphiques interactifs
- Synthèse pour rapport
- Export CSV/Markdown

---

## 📊 Interprétation des Résultats

### Métriques Affichées

| Métrique | Description | Unité |
|----------|-------------|-------|
| **RSRP Moyen** | Puissance du signal reçu | dBm |
| **Qualité Signal** | Excellent / Bon / Moyen / Faible / Critique | - |
| **Path Loss Outdoor** | Perte de propagation extérieure | dB |
| **Path Loss Total** | Perte totale (outdoor + pénétration) | dB |
| **Probabilité Couverture** | Fiabilité du signal (avec shadowing) | % |

### Seuils de Qualité

**4G (LTE)** :
- Excellent : RSRP ≥ -75 dBm
- Bon : -85 ≤ RSRP < -75 dBm
- Moyen : -95 ≤ RSRP < -85 dBm
- Faible : -105 ≤ RSRP < -95 dBm
- Critique : RSRP < -105 dBm

**5G (NR)** :
- Excellent : RSRP ≥ -70 dBm
- Bon : -80 ≤ RSRP < -70 dBm
- Moyen : -90 ≤ RSRP < -80 dBm
- Faible : -95 ≤ RSRP < -90 dBm
- Critique : RSRP < -95 dBm

### Décision Small Cell

**🟢 Couverture Macro Suffisante** (Probabilité ≥ 95%)
- La macro-cellule assure une couverture fiable
- Aucune Small Cell nécessaire
- Économie d'investissement

**🟠 Small Cell Recommandée** (80% ≤ Probabilité < 95%)
- Couverture limite avec risques de coupures
- Installation recommandée pour garantir la QoS
- Amélioration de l'expérience utilisateur

**🔴 Small Cell Requise** (Probabilité < 80%)
- Déficit de couverture critique
- Déploiement obligatoire pour assurer la QoS
- Risque élevé de mauvaise expérience utilisateur

---

## 🔬 Fondements Théoriques

### Modèle ITU-R P.1411

Le modèle ITU-R P.1411 est spécifiquement conçu pour les **environnements urbains micro-cellulaires**.

**Formule générale** :
```
PL(d) = FSPL(d_bp) + 10 * n * log10(d / d_bp) + C_env
```

Où :
- `d_bp` = point de rupture (breakpoint) = `4 * h_BS * h_UE * f / c`
- `n` = exposant de perte (2 pour LOS, 4 pour NLOS)
- `C_env` = correction environnement (0-15 dB)

**Domaine de validité** :
- Fréquence : 800-6000 MHz
- Distance : 20-5000 m
- Hauteur BS : 10-50 m

### Shadowing (Log-Normal Fading)

Le shadowing modélise les **variations du signal** dues aux obstacles mobiles (véhicules, piétons, végétation).

**Distribution log-normale** :
```
RSRP_réel ~ N(RSRP_moyen, σ²)
```

**Probabilité de couverture** :
```
P(RSRP > Seuil) = Q((Seuil - RSRP_moyen) / σ)
```

**Valeurs typiques de σ** :
- Rural : 4 dB
- Suburban : 6 dB
- Urbain : 8 dB
- Urbain dense : 10 dB

### Perte de Pénétration

La perte de pénétration (Building Entry Loss) dépend du **type de façade**.

**Valeurs 4G** :
| Matériau | Perte (dB) |
|----------|------------|
| Fenêtre standard | 10 |
| Fenêtre double vitrage | 15 |
| Mur léger | 20 |
| Mur standard | 25 |
| Mur épais | 30 |
| Béton renforcé | 35 |

**Valeurs 5G** : +5 dB par rapport à 4G (atténuation accrue en haute fréquence)

---

## 🧪 Tests Unitaires

### Exécuter les Tests

```bash
python test_link_budget.py
```

ou avec pytest :

```bash
pytest test_link_budget.py -v
```

### Couverture des Tests

Les tests couvrent :
- ✅ Conversions d'unités (dBm ↔ Watt)
- ✅ Calcul de distance GPS
- ✅ Validation des paramètres
- ✅ Calcul FSPL
- ✅ Calcul RSRP
- ✅ Évaluation qualité signal
- ✅ Décision Small Cell
- ✅ Probabilité de couverture
- ✅ Comparaison de modèles
- ✅ Bilan complet

---

## 📁 Structure du Projet

```
smallcell-advisor/
│
├── app.py                     # Interface Streamlit principale
├── link_budget.py             # Moteur de calcul 
├── constants.py               # Paramètres standards 3GPP
├── requirements.txt           # Dépendances Python
├──README.md                  # Ce fichier
│
└── 
```

---

## 🎓 Cas d'Usage

### Scénario 1 : Couverture Indoor Immeuble de Bureaux

**Contexte** :
- Bâtiment à 300 m d'une macro 4G
- Façade en mur standard
- Zone urbaine dense

**Configuration** :
- Technologie : 4G (1800 MHz)
- Distance : 300 m
- Matériau : Mur standard (25 dB)
- Environnement : Urbain dense

**Résultat attendu** :
- RSRP : -95 dBm environ
- Probabilité : 60-80%
- **Décision** : Small Cell recommandée

### Scénario 2 : Couverture 5G Centre Commercial

**Contexte** :
- Centre commercial avec façade vitrée
- Macro 5G à 500 m
- Zone urbaine

**Configuration** :
- Technologie : 5G (3500 MHz)
- Distance : 500 m
- Matériau : Fenêtre double (20 dB)
- Environnement : Urbain

**Résultat attendu** :
- RSRP : -85 dBm environ
- Probabilité : 75-90%
- **Décision** : Small Cell recommandée (border case)

### Scénario 3 : Zone Rurale Proximité BS

**Contexte** :
- Bâtiment à 100 m de la BS
- Zone rurale avec LOS
- Façade légère

**Configuration** :
- Technologie : 4G (1800 MHz)
- Distance : 100 m
- Matériau : Fenêtre standard (10 dB)
- Environnement : Rural
- LOS : Oui

**Résultat attendu** :
- RSRP : -65 dBm environ
- Probabilité : >95%
- **Décision** : Macro suffisante

---

## 🐛 Dépannage

### Problème : L'application ne démarre pas

**Solution** :
```bash
# Vérifier que Streamlit est installé
pip show streamlit

# Réinstaller les dépendances
pip install -r requirements.txt --upgrade
```

### Problème : Erreurs de calcul

**Causes possibles** :
- Paramètres hors limites de validité
- Distance trop faible ou trop élevée
- Fréquence incompatible avec le modèle

**Solution** : Vérifier les messages d'avertissement dans l'interface

### Problème : Graphiques ne s'affichent pas

**Solution** :
```bash
# Vérifier Plotly
pip install plotly --upgrade

# Vider le cache Streamlit
streamlit cache clear
```

---

## 🔄 Améliorations Futures

### Court Terme
- [ ] Export PDF professionnel
- [ ] Mode batch (calcul multi-scénarios)
- [ ] Historique des calculs
- [ ] Carte thermique de couverture (heatmap)

### Moyen Terme
- [ ] Optimisation position Small Cell
- [ ] Analyse coût-bénéfice économique
- [ ] Interface multilingue (FR/EN)
- [ ] API REST pour intégration

### Long Terme
- [ ] Intégration données terrain (measurements)
- [ ] Machine Learning pour prédiction
- [ ] Optimisation réseau multi-cellules
- [ ] Planification automatique

---

## 📚 Références

### Standards et Recommandations
- **ITU-R P.1411** : Propagation data and prediction methods for the planning of short-range outdoor radiocommunication systems
- **3GPP TS 36.942** : Radio Frequency (RF) system scenarios (LTE)
- **3GPP TS 38.901** : Study on channel model for frequencies from 0.5 to 100 GHz (5G NR)
- **ITU-R P.2109** : Building entry loss

### Documentation Technique
- [ITU Radiocommunication Sector](https://www.itu.int/en/ITU-R/Pages/default.aspx)
- [3GPP Specifications](https://www.3gpp.org/specifications)
- [Streamlit Documentation](https://docs.streamlit.io)
- [Plotly Python Graphing Library](https://plotly.com/python/)

---

## 👥 Contribution

### Comment Contribuer

1. **Forker** le projet
2. Créer une **branche** pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. **Commiter** vos changements (`git commit -m 'Add some AmazingFeature'`)
4. **Pusher** vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une **Pull Request**

### Guidelines
- Code documenté (docstrings)
- Tests unitaires pour nouvelles fonctionnalités
- Respect des standards PEP 8
- Messages de commit descriptifs

---

## 📄 Licence

Ce projet est développé dans un cadre du cours Ingenerie des Réseaux à l'Ecole Supérieure Polytechnique de l'Université Cheikh Anta Diop de Dakar (UCAD).

**Usage :**
- ✅ Usage académique et recherche
- ✅ Modification et amélioration
- ⚠️ Attribution requise pour usage commercial
- ⚠️ Contacter les auteurs pour déploiement professionnel

---

## 📞 Contact

**Auteur** : Hamit Amir MAHAMAT  
**Encadrant** : Dr. Mangoné FALL   
**Email** : mahamathamitamir@esp.sn

---

## 📈 Changelog

### Version 1.0 (Janvier 2026)
- ✨ Première version fonctionnelle
- 📊 Implémentation ITU-R P.1411
- 🎲 Analyse probabiliste avec shadowing
- 📈 Visualisations Plotly interactives
- 💾 Export CSV/Markdown

### Version 1.1 (À venir)
- 🐛 Corrections de bugs
- ✅ Validation robuste des entrées
- 📝 Tests unitaires complets
- 📖 Documentation enrichie

---

**SmallCell Advisor** - Optimisez vos déploiements RF avec confiance 📡
