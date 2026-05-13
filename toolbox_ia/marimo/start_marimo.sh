#!/bin/bash

# Correction du chemin OLLAMA_MODELS pour pointer vers le parent de 'blobs' et 'manifests'
export OLLAMA_MODELS="/media/sacha/datas/3w_quebec_23_avril_2026/ibm-granite"
export OLLAMA_HOST="http://127.0.0.1:11434"

echo "🚀 Configuration d'Ollama avec le dossier : $OLLAMA_MODELS"

# Arrêter l'instance système (nécessite sudo) pour utiliser la nôtre
if systemctl is-active --quiet ollama; then
    echo "⚠️  Le service système Ollama est actif. Il peut bloquer votre dossier personnalisé."
    echo "S'il vous plaît, exécutez d'abord : sudo systemctl stop ollama"
fi

# Tenter de redémarrer Ollama proprement pour ce dossier
pgrep -x "ollama" | xargs kill -9 > /dev/null 2>&1
echo "⚡ Démarrage du serveur Ollama..."
ollama serve > /dev/null 2>&1 &
sleep 5

# Vérifier la liste des modèles reconnus
echo "🔍 Modèles reconnus par Ollama dans ce dossier :"
OLLAMA_MODELS=$OLLAMA_MODELS ollama list

# Lancer Marimo
marimo edit notebook.py
