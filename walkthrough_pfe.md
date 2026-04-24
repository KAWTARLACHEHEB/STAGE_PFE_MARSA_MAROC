# 🚢 Rapport Technique : Système d'Optimisation Marsa Maroc (PFE)

Ce document résume l'architecture et les innovations du Dashboard de Supervision Intelligent développé pour Marsa Maroc.

## 1. Architecture du Système
Le système repose sur une pile technologique moderne et robuste :
*   **Frontend** : React.js avec Tailwind CSS v4 pour une interface ultra-rapide et responsive.
*   **3D Engine** : Three.js (React Three Fiber) pour la visualisation volumétrique en temps réel.
*   **Backend** : FastAPI (Python) pour des performances de calcul asynchrones optimales.
*   **Base de Données** : MySQL pour la persistance des mouvements et de l'inventaire.

## 2. Le Pipeline de Données (ETL Stratégique)
Avant d'afficher quoi que ce soit, les données passent par un cycle de transformation :
1.  **Data Repair** : Correction automatique des données corrompues (ex: erreurs de saisie des niveaux Z).
2.  **Referentiel Stratégique** : Classification intelligente des zones.
    *   **Zones PLEIN (35%)** : Bridage à 4 niveaux max pour la sécurité et stabilité.
    *   **Zones VIDE (65%)** : Optimisation de l'espace jusqu'à 6 niveaux.
3.  **Simulation TDT (True Departure Time)** : Attribution de dates de départ réalistes pour permettre à l'IA de calculer les priorités de stacking.

## 3. Moteur d'Optimisation IA (Smart Optimizer)
L'algorithme de recommandation de slots utilise un système de scoring basé sur 4 piliers :
*   **Stabilité Physique** : Interdiction de poser un conteneur lourd sur un plus léger.
*   **Respect LIFO** : Les conteneurs partant plus tôt sont placés au sommet de la pile pour éviter les "remuages" (rehandles).
*   **Zonage Spécialisé** : Détection automatique des zones compatibles (Prises Frigo, Zones Danger/IMDG).
*   **Randomisation Intelligente** : Évite la saturation d'une seule travée en répartissant les flux.

## 4. Visualisation 3D (Aide à la Décision)
La vue 3D permet une immersion totale dans le parc :
*   **Code Couleur Industriel** : Bleu (Normal), Orange (Frigo), Rouge (Danger), Violet (OOG).
*   **Survol Interactif** : Affichage instantané des références et caractéristiques au passage de la souris.
*   **Rotation 360°** : Inspection visuelle des piles pour détecter les anomalies de stacking.

## 5. Indicateurs de Performance (KPIs)
Le Dashboard offre une vue analytique sur :
*   **Taux d'Occupation Global** (Real-time).
*   **Vitesse de Calcul de l'IA** (moyenne de 12ms par recommandation).
*   **Historique des Mouvements** : Traçabilité totale de chaque conteneur déplacé par l'IA.

---
> **Note Stratégique pour le PFE** : Le système est conçu pour être "Data-Driven". Il s'adapte automatiquement à tout nouveau fichier de données (CSV) fourni par Marsa Maroc.
