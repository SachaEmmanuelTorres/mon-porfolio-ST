#!/usr/bin/env bash
CONTAINER_NAME="ubuntu-24-demo"

echo "Arrêt et suppression du conteneur $CONTAINER_NAME..."
docker rm -f "$CONTAINER_NAME"
echo "Terminé."
