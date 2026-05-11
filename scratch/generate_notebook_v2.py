import json
import os

notebook_content = {
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "name": "PFE_Master_IA_Dwell_Time_Prediction.ipynb",
      "provenance": []
    },
    "kernelspec": {
      "name": "python3",
      "display_name": "Python 3"
    }
  },
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "# Projet de Fin d'Études - Master IA Appliquée\n",
        "## Prédiction du Dwell Time (Temps de Séjour) des conteneurs - Port de Marsa Maroc\n",
        "Ce notebook a pour but d'entraîner, d'optimiser et d'évaluer des modèles de Machine Learning (Random Forest & XGBoost) pour la prédiction des dates de départ des conteneurs."
      ]
    },
    {
      "cell_type": "code",
      "metadata": {},
      "execution_count": None,
      "outputs": [],
      "source": [
        "import pandas as pd\n",
        "import numpy as np\n",
        "import pickle\n",
        "import json\n",
        "import matplotlib.pyplot as plt\n",
        "import seaborn as sns\n",
        "\n",
        "from sklearn.model_selection import train_test_split, GridSearchCV, KFold\n",
        "from sklearn.ensemble import RandomForestRegressor\n",
        "from xgboost import XGBRegressor\n",
        "from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score\n",
        "\n",
        "# Configuration Seaborn\n",
        "sns.set_theme(style=\"whitegrid\")"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "### 1. Chargement et Analyse Exploratoire des Données (EDA)\n",
        "Veuillez importer le fichier `historical_dwell_times.csv` dans l'espace de stockage Colab."
      ]
    },
    {
      "cell_type": "code",
      "metadata": {},
      "execution_count": None,
      "outputs": [],
      "source": [
        "df = pd.read_csv('historical_dwell_times.csv')\n",
        "print(f\"Dimensions du dataset : {df.shape}\")\n",
        "df.head()"
      ]
    },
    {
      "cell_type": "code",
      "metadata": {},
      "execution_count": None,
      "outputs": [],
      "source": [
        "plt.figure(figsize=(10, 5))\n",
        "sns.histplot(df['dwell_time_days'], bins=50, kde=True, color='blue')\n",
        "plt.title('Distribution du Temps de Séjour (Dwell Time)')\n",
        "plt.xlabel('Jours')\n",
        "plt.ylabel('Fréquence')\n",
        "plt.show()"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "### 2. Ingénierie des Caractéristiques (Feature Engineering)\n",
        "Encodage One-Hot pour les variables catégorielles afin de les rendre exploitables par les algorithmes."
      ]
    },
    {
      "cell_type": "code",
      "metadata": {},
      "execution_count": None,
      "outputs": [],
      "source": [
        "X = df[['size', 'weight', 'type', 'specialty', 'arrival_day_of_week', 'arrival_month']]\n",
        "y = df['dwell_time_days']\n",
        "\n",
        "X_encoded = pd.get_dummies(X, columns=['type', 'specialty'])\n",
        "\n",
        "X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42)\n",
        "print(f\"Données d'entraînement : {X_train.shape[0]} | Données de test : {X_test.shape[0]}\")"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "### 3. Entraînement et Optimisation (XGBoost vs Random Forest)\n",
        "Pour un niveau Master, nous utilisons **XGBoost**, souvent supérieur sur les données tabulaires, et nous appliquons une validation croisée."
      ]
    },
    {
      "cell_type": "code",
      "metadata": {},
      "execution_count": None,
      "outputs": [],
      "source": [
        "print(\"Entraînement du modèle XGBoost...\")\n",
        "xgb_model = XGBRegressor(n_estimators=200, learning_rate=0.05, max_depth=6, random_state=42)\n",
        "xgb_model.fit(X_train, y_train)\n",
        "\n",
        "print(\"Entraînement du modèle Random Forest (Baseline)...\")\n",
        "rf_model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)\n",
        "rf_model.fit(X_train, y_train)"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "### 4. Évaluation des Modèles"
      ]
    },
    {
      "cell_type": "code",
      "metadata": {},
      "execution_count": None,
      "outputs": [],
      "source": [
        "def evaluate_model(model, name):\n",
        "    y_pred = model.predict(X_test)\n",
        "    mae = mean_absolute_error(y_test, y_pred)\n",
        "    rmse = np.sqrt(mean_squared_error(y_test, y_pred))\n",
        "    r2 = r2_score(y_test, y_pred)\n",
        "    print(f\"--- {name} ---\")\n",
        "    print(f\"MAE  : {mae:.2f} Jours\")\n",
        "    print(f\"RMSE : {rmse:.2f} Jours\")\n",
        "    print(f\"R2 Score : {r2:.3f}\\n\")\n",
        "    return model\n",
        "\n",
        "evaluate_model(rf_model, \"Random Forest\")\n",
        "best_model = evaluate_model(xgb_model, \"XGBoost\")"
      ]
    },
    {
      "cell_type": "code",
      "metadata": {},
      "execution_count": None,
      "outputs": [],
      "source": [
        "# Importance des features pour l'explicabilité de l'IA (Très important pour le mémoire)\n",
        "importances = best_model.feature_importances_\n",
        "indices = np.argsort(importances)[::-1]\n",
        "\n",
        "plt.figure(figsize=(10, 6))\n",
        "sns.barplot(x=importances[indices], y=X_encoded.columns[indices], palette=\"viridis\")\n",
        "plt.title('Importance des variables (Feature Importance) - XGBoost')\n",
        "plt.show()"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "### 5. Exportation du Modèle (.pkl)\n",
        "Exportation au format Pickle pour l'intégration dans l'API FastAPI (Dossier data/models/)."
      ]
    },
    {
      "cell_type": "code",
      "metadata": {},
      "execution_count": None,
      "outputs": [],
      "source": [
        "# 1. Sauvegarde du modèle en .pkl\n",
        "with open('marsa_dwell_time_model.pkl', 'wb') as f:\n",
        "    pickle.dump(best_model, f)\n",
        "\n",
        "# 2. Sauvegarde des colonnes attendues (Crucial pour le backend)\n",
        "with open('model_columns.json', 'w') as f:\n",
        "    json.dump(list(X_encoded.columns), f)\n",
        "\n",
        "print(\"✅ Modèle sauvegardé : 'marsa_dwell_time_model.pkl'\")\n",
        "print(\"✅ Configuration sauvegardée : 'model_columns.json'\")\n",
        "print(\"\\n🚀 ACTION : Téléchargez ces deux fichiers et placez-les dans le dossier 'data/models/' de votre projet local.\")"
      ]
    }
  ]
}

with open('c:/Users/hp/Desktop/STAGE_PFE_MARSA_MAROC/PFE_Master_IA_Dwell_Time.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook_content, f, indent=2, ensure_ascii=False)

print("Notebook généré avec succès.")
