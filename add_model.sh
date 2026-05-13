#!/bin/bash

# Demander le nom du modèle si non fourni
MODEL=$1
if [ -z "$MODEL" ]; then
    read -p "Entrez le nom du modèle ou du dépôt (ex: llama3.2 ou lmstudio-community/gemma-2-2b-it-GGUF) : " MODEL
fi

echo "----------------------------------------------------------"
echo "Outil cible :"
echo "1) Ollama (Pull depuis le hub)"
echo "2) Ollama (Créer depuis un GGUF local)"
echo "3) llama.cpp (Téléchargement direct HF)"
echo "4) llama.cpp (Modèle local)"
read -p "Votre choix (1-4) : " CHOICE

case $CHOICE in
    1)
        CMD="podman exec -it ollama ollama pull $MODEL"
        ;;
    2)
        read -p "Entrez le nom exact du fichier GGUF dans /models : " GGUF_FILE
        echo "FROM /root/.ollama/models/$GGUF_FILE" > Modelfile.tmp
        CMD="podman exec -it ollama ollama create $MODEL -f /root/.ollama/models/Modelfile.tmp"
        echo "Note : Le fichier Modelfile.tmp a été préparé."
        ;;
    3)
        read -p "Entrez le nom du fichier .gguf précis sur Hugging Face : " GGUF_FILE
        CMD="podman exec -it llamacpp ./build/bin/llama-server --hf-repo $MODEL --hf-file $GGUF_FILE --host 0.0.0.0 --port 8090"
        ;;
    4)
        read -p "Entrez le nom du fichier GGUF dans /models : " GGUF_FILE
        CMD="podman exec -it llamacpp ./build/bin/llama-server --model /models/$GGUF_FILE --host 0.0.0.0 --port 8090"
        ;;
    *)
        echo "Choix invalide."
        exit 1
        ;;
esac

echo "----------------------------------------------------------"
echo "Commande générée :"
echo "$CMD"
echo "----------------------------------------------------------"

read -p "Voulez-vous exécuter cette commande maintenant ? (y/n) : " EXEC_NOW
if [[ "$EXEC_NOW" == "y" || "$EXEC_NOW" == "Y" ]]; then
    eval $CMD
else
    echo "Commande annulée. Vous pouvez la copier-coller plus tard."
fi
