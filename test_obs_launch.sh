#!/bin/bash

# Script de test simple pour vérifier le lancement d'OBS Studio.

echo "--- Test de lancement d'OBS Studio ---"

# 1. Vérifier si OBS est déjà lancé
if pgrep -f "obs-studio|com.obsproject.Studio" > /dev/null; then
    echo "INFO : OBS Studio est déjà en cours d'exécution."
    echo "Pour un test complet, veuillez d'abord fermer OBS."
    exit 0
fi

# 2. Tenter de lancer OBS
echo "OBS n'est pas détecté. Tentative de démarrage..."

# Lance OBS en arrière-plan.
flatpak run com.obsproject.Studio &

# Attendre quelques secondes pour que le processus démarre
sleep 5

# 3. Vérifier si le lancement a réussi
if pgrep -f "obs-studio|com.obsproject.Studio" > /dev/null; then
    echo "SUCCÈS : Le processus 'obs' a été lancé correctement."
else
    echo "ÉCHEC : Impossible de démarrer OBS. Vérifiez que la commande 'obs' est correcte et accessible depuis votre PATH."
fi

echo "--- Fin du test ---"
