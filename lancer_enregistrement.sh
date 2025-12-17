#!/bin/bash

# Script pour lancer OBS Studio et le script d'enregistrement automatique Twitch.
# A placer au même niveau que le dossier 'projet_obs'.

echo "--- Lancement du script d'enregistrement automatique ---"

# --- Etape 1: Vérifier et lancer OBS ---

# On vérifie si le processus 'obs' est déjà en cours d'exécution.
if ! pgrep -f "obs-studio|com.obsproject.Studio" > /dev/null
then
    echo "OBS Studio n'est pas détecté. Démarrage..."
    # Lance OBS en arrière-plan pour que le script puisse continuer.
    snap run obs-studio &
    echo "Attente de 15 secondes pour l'initialisation d'OBS..."
    sleep 15
else
    echo "OBS Studio est déjà en cours d'exécution."
fi

# --- Etape 2: Lancer le script Python ---

# Trouve le chemin absolu du dossier où se trouve ce script.
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
PROJECT_DIR="$SCRIPT_DIR/projet_obs"

# Vérifie si le dossier du projet existe.
if [ ! -d "$PROJECT_DIR" ]; then
    echo "[ERREUR] Le dossier du projet '$PROJECT_DIR' est introuvable."
    echo "Veuillez vous assurer que ce script est bien placé à côté du dossier 'projet_obs'."
    exit 1
fi

# Se déplace dans le dossier du projet.
cd "$PROJECT_DIR"

# Active l'environnement virtuel Python.
echo "Activation de l'environnement virtuel..."
source .env/bin/activate

# Lance le script principal.
echo "Lancement du script main.py..."
python main.py

echo "--- Le script d'enregistrement a terminé son exécution. ---"