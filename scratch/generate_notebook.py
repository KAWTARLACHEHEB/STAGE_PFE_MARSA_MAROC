import json
import os

notebook_content = {
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "name": "Marsa_Maroc_Dwell_Time_Prediction.ipynb",
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
        "# Modèle de Prédiction de Temps de Séjour (Dwell Time) - Marsa Maroc\n",
        "Ce notebook entraîne un modèle de Machine Learning (Random Forest) pour prédire le temps de séjour d'un conteneur dans le terminal, basé sur ses caractéristiques.\n",
        "## 1. Importation des bibliothèques"
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
        "from sklearn.model_selection import train_test_split\n",
        "from sklearn.ensemble import RandomForestRegressor\n",
        "from sklearn.metrics import mean_absolute_error, mean_squared_error\n",
        "import joblib\n",
        "import matplotlib.pyplot as plt\n",
        "import seaborn as sns"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## 2. Chargement des données\n",
        "**Action Requise :** Cliquez sur l'icône de dossier à gauche dans Colab et uploadez le fichier `historical_dwell_times.csv` que nous avons généré dans le projet."
      ]
    },
    {
      "cell_type": "code",
      "metadata": {},
      "execution_count": None,
      "outputs": [],
      "source": [
        "# Charger le dataset\n",
        "df = pd.read_csv('historical_dwell_times.csv')\n",
        "print(f\"Taille du dataset : {df.shape}\")\n",
        "df.head()"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## 3. Préparation des données (Preprocessing)\n",
        "Nous devons convertir les variables catégorielles (Type, Spécialité) en valeurs numériques."
      ]
    },
    {
      "cell_type": "code",
      "metadata": {},
      "execution_count": None,
      "outputs": [],
      "source": [
        "# Variables d'entrée (Features)\n",
        "X = df[['size', 'weight', 'type', 'specialty', 'arrival_day_of_week', 'arrival_month']]\n",
        "\n",
        "# Variable cible (Target)\n",
        "y = df['dwell_time_days']\n",
        "\n",
        "# Encodage One-Hot (get_dummies) pour les catégories\n",
        "X_encoded = pd.get_dummies(X, columns=['type', 'specialty'])\n",
        "\n",
        "# Afficher les nouvelles colonnes créées\n",
        "print(\"Colonnes du modèle :\")\n",
        "print(list(X_encoded.columns))\n",
        "\n",
        "# Séparation Entraînement (80%) / Test (20%)\n",
        "X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42)"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## 4. Entraînement du Modèle d'IA (Random Forest)"
      ]
    },
    {
      "cell_type": "code",
      "metadata": {},
      "execution_count": None,
      "outputs": [],
      "source": [
        "print(\"Entraînement en cours...\")\n",
        "# Initialisation du Random Forest avec des hyperparamètres optimisés\n",
        "rf_model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)\n",
        "\n",
        "# Entraînement\n",
        "rf_model.fit(X_train, y_train)\n",
        "print(\"Entraînement terminé !\")"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## 5. Évaluation des Performances"
      ]
    },
    {
      "cell_type": "code",
      "metadata": {},
      "execution_count": None,
      "outputs": [],
      "source": [
        "# Prédictions sur l'ensemble de test\n",
        "y_pred = rf_model.predict(X_test)\n",
        "\n",
        "mae = mean_absolute_error(y_test, y_pred)\n",
        "rmse = np.sqrt(mean_squared_error(y_test, y_pred))\n",
        "\n",
        "print(f\"Erreur Absolue Moyenne (MAE) : {mae:.2f} jours\")\n",
        "print(f\"Erreur Quadratique Moyenne (RMSE) : {rmse:.2f} jours\")\n",
        "\n",
        "# Importance des variables (Ce qui influence le plus le temps de séjour)\n",
        "feature_importance = pd.DataFrame({\n",
        "    'Feature': X_encoded.columns,\n",
        "    'Importance': rf_model.feature_importances_\n",
        "}).sort_values(by='Importance', ascending=False)\n",
        "\n",
        "plt.figure(figsize=(10, 6))\n",
        "sns.barplot(x='Importance', y='Feature', data=feature_importance)\n",
        "plt.title('Importance des Caractéristiques dans la Prédiction')\n",
        "plt.tight_layout()\n",
        "plt.show()"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## 6. Sauvegarde du Modèle pour intégration dans FastAPI\n",
        "Nous allons sauvegarder le modèle entraîné ainsi que l'ordre exact des colonnes utilisé pour l'encodage."
      ]
    },
    {
      "cell_type": "code",
      "metadata": {},
      "execution_count": None,
      "outputs": [],
      "source": [
        "import json\n",
        "\n",
        "# 1. Sauvegarder le modèle\n",
        "joblib.dump(rf_model, 'marsa_dwell_time_model.joblib')\n",
        "\n",
        "# 2. Sauvegarder l'ordre des colonnes (Indispensable pour l'API)\n",
        "model_columns = list(X_encoded.columns)\n",
        "with open('model_columns.json', 'w') as f:\n",
        "    json.dump(model_columns, f)\n",
        "\n",
        "print(\"Modèle et configuration sauvegardés !\")\n",
        "print(\"==> TÉLÉCHARGEZ les fichiers 'marsa_dwell_time_model.joblib' et 'model_columns.json' depuis le dossier Colab à gauche.\")"
      ]
    }
  ]
}

with open('c:/Users/hp/Desktop/STAGE_PFE_MARSA_MAROC/Colab_Marsa_Dwell_Time.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook_content, f, indent=2, ensure_ascii=False)

print("Notebook Colab généré avec succès.")
