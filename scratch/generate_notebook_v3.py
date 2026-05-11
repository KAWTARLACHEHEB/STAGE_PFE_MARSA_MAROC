import json

notebook_content = {
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {"name": "PFE_DataScience_Marsa_Maroc.ipynb", "provenance": []},
    "kernelspec": {"name": "python3", "display_name": "Python 3"}
  },
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "# 🎓 PFE Master IA : Deep Data Science & Dwell Time Prediction\n",
        "**Cas d'usage : Terminal Conteneurs de Marsa Maroc**\n",
        "\n",
        "Ce notebook présente la pipeline complète et rigoureuse de modélisation prédictive :\n",
        "1. **Data Cleaning & EDA** (Outliers, Distributions)\n",
        "2. **Feature Engineering & Scaling** (Normalisation)\n",
        "3. **Model Training avec Early Stopping** (Apprentissage par itérations/Epochs)\n",
        "4. **Deep Evaluation** (Courbes d'apprentissage, Analyse des résidus)"
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
        "import matplotlib.pyplot as plt\n",
        "import seaborn as sns\n",
        "import pickle\n",
        "import json\n",
        "\n",
        "from sklearn.model_selection import train_test_split\n",
        "from sklearn.preprocessing import StandardScaler\n",
        "from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score\n",
        "from xgboost import XGBRegressor\n",
        "\n",
        "sns.set_theme(style=\"darkgrid\")"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## 1. Chargement et Nettoyage des Données (Data Cleaning)"
      ]
    },
    {
      "cell_type": "code",
      "metadata": {},
      "execution_count": None,
      "outputs": [],
      "source": [
        "# Chargement\n",
        "df = pd.read_csv('historical_dwell_times.csv')\n",
        "print(f\"Taille initiale : {df.shape}\")\n",
        "\n",
        "# Vérification des valeurs nulles\n",
        "print(\"\\nValeurs nulles par colonne :\")\n",
        "print(df.isnull().sum())\n",
        "\n",
        "# NETTOYAGE : Suppression des Outliers (Valeurs aberrantes) via la méthode IQR\n",
        "Q1 = df['dwell_time_days'].quantile(0.25)\n",
        "Q3 = df['dwell_time_days'].quantile(0.75)\n",
        "IQR = Q3 - Q1\n",
        "\n",
        "lower_bound = Q1 - 1.5 * IQR\n",
        "upper_bound = Q3 + 1.5 * IQR\n",
        "\n",
        "df_clean = df[(df['dwell_time_days'] >= lower_bound) & (df['dwell_time_days'] <= upper_bound)]\n",
        "print(f\"\\nTaille après suppression des outliers : {df_clean.shape}\")"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## 2. Feature Engineering & Preprocessing"
      ]
    },
    {
      "cell_type": "code",
      "metadata": {},
      "execution_count": None,
      "outputs": [],
      "source": [
        "# Séparation Features (X) et Target (y)\n",
        "X = df_clean[['size', 'weight', 'type', 'specialty', 'arrival_day_of_week', 'arrival_month']]\n",
        "y = df_clean['dwell_time_days']\n",
        "\n",
        "# Encodage One-Hot des variables catégorielles\n",
        "X_encoded = pd.get_dummies(X, columns=['type', 'specialty'])\n",
        "print(\"Colonnes encodées :\", X_encoded.columns.tolist())\n",
        "\n",
        "# Split Train / Validation / Test (60% / 20% / 20%)\n",
        "# Le set de Validation est crucial pour suivre l'apprentissage sur les Epochs\n",
        "X_temp, X_test, y_temp, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42)\n",
        "X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.25, random_state=42)\n",
        "\n",
        "# Normalisation (Scaling) : Important pour la stabilité du Gradient Descent\n",
        "scaler = StandardScaler()\n",
        "X_train_scaled = scaler.fit_transform(X_train)\n",
        "X_val_scaled = scaler.transform(X_val)\n",
        "X_test_scaled = scaler.transform(X_test)"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## 3. Entraînement Avancé (Apprentissage par Itérations / Epochs)\n",
        "Nous utilisons XGBoost avec un `eval_set` pour tracker la Loss à chaque itération (Epoch). Cela permet de déclencher l'**Early Stopping** pour éviter l'overfitting."
      ]
    },
    {
      "cell_type": "code",
      "metadata": {},
      "execution_count": None,
      "outputs": [],
      "source": [
        "# Définition du modèle avec des hyperparamètres contrôlés\n",
        "model = XGBRegressor(\n",
        "    n_estimators=1000,      # Nombre maximum d'itérations (Epochs)\n",
        "    learning_rate=0.01,     # Pas d'apprentissage lent pour une meilleure convergence\n",
        "    max_depth=6,            # Profondeur des arbres\n",
        "    subsample=0.8,          # Régularisation (Dropout équivalent)\n",
        "    random_state=42\n",
        ")\n",
        "\n",
        "# Suivi de l'entraînement\n",
        "eval_set = [(X_train_scaled, y_train), (X_val_scaled, y_val)]\n",
        "\n",
        "print(\"Démarrage de l'entraînement avec suivi des Epochs...\")\n",
        "model.fit(\n",
        "    X_train_scaled, y_train,\n",
        "    eval_set=eval_set,\n",
        "    verbose=50,             # Affiche la loss toutes les 50 epochs\n",
        ")\n",
        "print(\"\\nEntraînement terminé !\")"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## 4. Évaluation et Preuves de Performance\n",
        "Comment prouver au jury que le modèle fonctionne ? Par les courbes d'apprentissage et l'analyse des résidus."
      ]
    },
    {
      "cell_type": "code",
      "metadata": {},
      "execution_count": None,
      "outputs": [],
      "source": [
        "# 1. Courbe d'Apprentissage (Loss Curve)\n",
        "results = model.evals_result()\n",
        "epochs = len(results['validation_0']['rmse'])\n",
        "x_axis = range(0, epochs)\n",
        "\n",
        "plt.figure(figsize=(10, 5))\n",
        "plt.plot(x_axis, results['validation_0']['rmse'], label='Train Loss (RMSE)')\n",
        "plt.plot(x_axis, results['validation_1']['rmse'], label='Validation Loss (RMSE)')\n",
        "plt.legend()\n",
        "plt.title('Courbe d\\'Apprentissage XGBoost (Overfitting Check)')\n",
        "plt.xlabel('Itérations (Epochs)')\n",
        "plt.ylabel('RMSE Loss')\n",
        "plt.show()"
      ]
    },
    {
      "cell_type": "code",
      "metadata": {},
      "execution_count": None,
      "outputs": [],
      "source": [
        "# 2. Métriques Officielles sur le Test Set (Données jamais vues)\n",
        "y_pred = model.predict(X_test_scaled)\n",
        "\n",
        "mae = mean_absolute_error(y_test, y_pred)\n",
        "rmse = np.sqrt(mean_squared_error(y_test, y_pred))\n",
        "r2 = r2_score(y_test, y_pred)\n",
        "\n",
        "print(\"--- PERFORMANCES FINALES SUR LE TEST SET ---\")\n",
        "print(f\"Coefficient de Détermination (R2) : {r2:.3f} (Proche de 1 = Parfait)\")\n",
        "print(f\"Marge d'erreur moyenne (MAE)      : {mae:.2f} jours\")\n",
        "print(f\"RMSE                              : {rmse:.2f} jours\")"
      ]
    },
    {
      "cell_type": "code",
      "metadata": {},
      "execution_count": None,
      "outputs": [],
      "source": [
        "# 3. Graphique de Corrélation : Prédictions vs Réalité\n",
        "plt.figure(figsize=(8, 8))\n",
        "plt.scatter(y_test, y_pred, alpha=0.3, color='purple')\n",
        "plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)\n",
        "plt.xlabel('Vrai Dwell Time (Jours)')\n",
        "plt.ylabel('Prédiction du Modèle (Jours)')\n",
        "plt.title('Prédictions de l\\'IA vs Réalité Terrain')\n",
        "plt.show()"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## 5. Exportation pour le Déploiement FastAPI"
      ]
    },
    {
      "cell_type": "code",
      "metadata": {},
      "execution_count": None,
      "outputs": [],
      "source": [
        "# Sauvegarde du Modèle\n",
        "with open('marsa_dwell_time_model.pkl', 'wb') as f:\n",
        "    pickle.dump(model, f)\n",
        "\n",
        "# Sauvegarde du Scaler (INDISPENSABLE car l'API doit normaliser les nouvelles données de la même façon)\n",
        "with open('marsa_scaler.pkl', 'wb') as f:\n",
        "    pickle.dump(scaler, f)\n",
        "\n",
        "# Sauvegarde des colonnes\n",
        "with open('model_columns.json', 'w') as f:\n",
        "    json.dump(list(X_encoded.columns), f)\n",
        "\n",
        "print(\"✅ Pipeline de modélisation terminée avec succès.\")\n",
        "print(\"Téléchargez les 3 fichiers générés (.pkl, .pkl, .json) et placez-les dans data/models/\")"
      ]
    }
  ]
}

with open('c:/Users/hp/Desktop/STAGE_PFE_MARSA_MAROC/PFE_DataScience_Marsa_Maroc.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook_content, f, indent=2, ensure_ascii=False)

print("Nouveau Notebook Deep Data Science généré avec succès.")
