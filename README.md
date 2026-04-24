# 🚢 Marsa Maroc Terminal Optimizer & Dashboard (PFE)

> **Système Intelligent de Supervision et d'Optimisation du Stacking de Conteneurs**

Ce projet est une solution de **Jumeau Numérique (Digital Twin)** développée pour moderniser la gestion des opérations au sol des terminaux Marsa Maroc (TC3 & TCE). Il combine l'intelligence artificielle, l'ingénierie des données et la visualisation 3D pour optimiser l'espace de stockage et l'efficacité opérationnelle.

---

## 🌟 Fonctionnalités Clés

### 1. 🧠 SmartOptimizer (IA)
Algorithme de recommandation de slots multi-critères :
*   **Respect du LIFO** (Last-In First-Out) basé sur les dates de départ prédites.
*   **Gestion de la Stabilité** : Empilement sécurisé en fonction du poids des conteneurs.
*   **Zonage Intelligent** : Respect des spécialités (Frigo, Danger/IMDG, Hors-Gabarit).

### 2. 🧊 Visualisation Volumétrique 3D
Moteur de rendu 3D intégré pour une supervision immersive :
*   Représentation fidèle des piles de conteneurs via **Three.js**.
*   Code couleur industriel : Bleu (Normal), Orange (Frigo), Rouge (Danger).
*   Interaction au survol pour consulter les métadonnées de chaque unité.

### 3. ⚙️ Pipeline ETL Stratégique
Chaîne de traitement de données robuste :
*   **Data Repair** : Correction automatique des erreurs de saisie et nettoyage des doublons.
*   **Référentiel Dynamique** : Classification automatique des zones (Ratio 65/35 Plein/Vide).
*   **Synchronisation MySQL** : Mise à jour en temps réel de l'état du parc.

### 4. 📊 Dashboard de Supervision
Interface premium en Dark Mode (Tailwind v4) offrant :
*   Suivi du taux d'occupation par terminal et par type.
*   Historique complet des mouvements avec exportation CSV.
*   Moniteurs de performance et de congestion.

---

## 🛠️ Stack Technique

| Composant | Technologie |
| :--- | :--- |
| **Frontend** | React 18, Tailwind CSS v4, Framer Motion |
| **3D Engine** | Three.js (@react-three/fiber, @react-three/drei) |
| **Backend API** | FastAPI (Python 3.13), SQLAlchemy |
| **Data Engine** | Pandas, NumPy |
| **Base de Données**| MySQL 8.0 |

---

## 🚀 Installation et Lancement

### Préréglages
*   Python 3.13+
*   Node.js 20+
*   Serveur MySQL (Port 3307 recommandé)

### Lancement Rapide (Windows)
Exécutez simplement le fichier batch à la racine du projet :
```powershell
.\Lancer_Projet_Marsa.bat
```

### Lancement Manuel

1. **Initialisation de la base de données** :
```powershell
cd app/etl
py pipeline.py
```

2. **Démarrage du Backend (FastAPI)** :
```powershell
cd app
$env:PYTHONPATH = ".."
py main.py
```

3. **Démarrage du Frontend (React)** :
```powershell
cd frontend
npm install
npm run dev
```

---

## 📁 Structure du Projet
*   `/app` : Code source du Backend (FastAPI, Optimiseur, AI).
*   `/app/etl` : Scripts de nettoyage et de synchronisation des données.
*   `/frontend` : Interface utilisateur React et composants 3D.
*   `/data` : Données brutes et traitées (CSV).
*   `/docs` : Documentation technique du projet.

---
*Réalisé dans le cadre d'un Stage de Fin d'Études (PFE) pour Marsa Maroc.*