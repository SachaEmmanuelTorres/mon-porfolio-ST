#!/usr/bin/env bash
set -e

IMAGE_NAME="ubuntu-24-demo"
CONTAINER_NAME="ubuntu-24-demo"

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "Construction de l'image $IMAGE_NAME..."
docker build -t "$IMAGE_NAME" .

echo "Lancement du conteneur $CONTAINER_NAME..."
docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
docker run -d --name "$CONTAINER_NAME" "$IMAGE_NAME"

echo "Le conteneur est prêt."
