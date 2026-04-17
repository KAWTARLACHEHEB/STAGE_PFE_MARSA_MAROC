# STAGE_PFE_MARSA_MAROC
<!-- Last automation trigger: 2026-04-17 14:19 -->

## 🚢 Optimisation du Stacking de Conteneurs via Intelligence Artificielle

**Projet de Fin d'Études (PFE) – Marsa Maroc**

---

## 🏗️ Nouvelle Architecture (Full Stack)

Cette version utilise une stack moderne et robuste :
- **Frontend** : React 18 + Vite + Tailwind CSS + Lucide Icons
- **Backend** : Node.js + Express
- **Base de données** : MySQL 8.0

---

## 📁 Structure du Projet

```
STAGE_PFE_MARSA_MAROC/
├── backend/             # API Node.js (Express)
│   ├── server.js        # Serveur principal
│   └── Dockerfile       # Image Backend
├── frontend/            # Interface React
│   ├── src/             # Code source UI
│   └── Dockerfile       # Image Frontend
├── data/
│   └── init.sql         # Script d'initialisation MySQL
├── docker-compose.yml   # Orchestration totale
└── README.md
```

## 🚀 Démarrage Rapide

### 1. Lancer l'environnement complet
```bash
docker-compose up --build
```

### 2. Accéder aux services
- **Frontend** : [http://localhost:5173](http://localhost:5173) (Dashboard Premium)
- **Backend API** : [http://localhost:5000](http://localhost:5000)
- **Base de données** : Port local 3307

## 🛠️ Fonctionnalités implémentées
- [x] Dashboard interactif temps réel
- [x] Connexion automatique à MySQL (Pool de connexions)
- [x] Health check système (API + DB)
- [x] Interface Responsive & Premium (Mode sombre)

## 👩‍💻 Auteur
**KAWTAR LACHEHEB** – Stagiaire PFE Marsa Maroc 2025/2026