#!/usr/bin/env bash
CONTAINER_NAME="ubuntu-24-demo"

echo "Connexion au conteneur $CONTAINER_NAME..."
docker exec -it "$CONTAINER_NAME" bash
