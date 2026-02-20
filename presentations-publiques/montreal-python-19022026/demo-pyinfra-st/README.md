# Pyinfra Docker Deployment Demo

This project demonstrates how to deploy a basic application setup on a Dockerized Ubuntu 24.04 container using Pyinfra. It automates package installation, Python dependency management, and file creation.

## Prerequisites

*   **Docker**: Ensure Docker is installed and running on your system.
*   **Pyinfra**: Install Pyinfra globally or in a virtual environment: `pip install pyinfra`

## Setup: Build and Run the Docker Container

First, build the Docker image and start the container. The `start.sh` script handles this:

```bash
./start.sh
```

This will build the `ubuntu-24-demo` image and start a container named `ubuntu-24-demo`.

## Deployment with Pyinfra

Once the Docker container is running, you can execute the Pyinfra deployment script (`deploy.py`) against it. This script will:
*   Update apt packages.
*   Install essential packages (git, python3, python3-pip, htop, net-tools).
*   Copy `requirements.txt` to `/opt/app/requirements.txt`.
*   Install Python dependencies from `requirements.txt`.
*   Create the `/opt/app` directory.
*   Create the `/home/ubuntu` directory.
*   Create a file `/home/ubuntu/demo_finished.txt` with the content "fin de la demo".

Run the deployment using:

```bash
pyinfra @docker/ubuntu-24-demo deploy.py
```

## Verification

To verify that the deployment was successful, you can check the content of `/home/ubuntu/demo_finished.txt` inside the running Docker container:

```bash
docker exec ubuntu-24-demo cat /home/ubuntu/demo_finished.txt
```

The output should be `fin de la demo`.

You can also inspect the installed packages or directory structure:

```bash
docker exec ubuntu-24-demo ls /opt/app
docker exec ubuntu-24-demo python3 -c "import requests"
```

## Cleanup

To stop and remove the Docker container:

```bash
./stop.sh
```

---

# Démonstration de Déploiement Pyinfra avec Docker

Ce projet démontre comment déployer une configuration d'application de base sur un conteneur Ubuntu 24.04 Dockerisé à l'aide de Pyinfra. Il automatise l'installation de paquets, la gestion des dépendances Python et la création de fichiers.

## Prérequis

*   **Docker**: Assurez-vous que Docker est installé et en cours d'exécution sur votre système.
*   **Pyinfra**: Installez Pyinfra globalement ou dans un environnement virtuel : `pip install pyinfra`

## Configuration : Construire et Démarrer le Conteneur Docker

Tout d'abord, construisez l'image Docker et démarrez le conteneur. Le script `start.sh` gère cela :

```bash
./start.sh
```

Cela construira l'image `ubuntu-24-demo` et démarrera un conteneur nommé `ubuntu-24-demo`.

## Déploiement avec Pyinfra

Une fois le conteneur Docker en cours d'exécution, vous pouvez exécuter le script de déploiement Pyinfra (`deploy.py`). Ce script va :
*   Mettre à jour les paquets apt.
*   Installer les paquets essentiels (git, python3, python3-pip, htop, net-tools).
*   Copier `requirements.txt` vers `/opt/app/requirements.txt`.
*   Installer les dépendances Python à partir de `requirements.txt`.
*   Créer le répertoire `/opt/app`.
*   Créer le répertoire `/home/ubuntu`.
*   Créer un fichier `/home/ubuntu/demo_finished.txt` avec le contenu "fin de la demo".

Exécutez le déploiement en utilisant :

```bash
pyinfra @docker/ubuntu-24-demo deploy.py
```

## Vérification

Pour vérifier que le déploiement a réussi, vous pouvez vérifier le contenu de `/home/ubuntu/demo_finished.txt` à l'intérieur du conteneur Docker en cours d'exécution :

```bash
docker exec ubuntu-24-demo cat /home/ubuntu/demo_finished.txt
```

La sortie devrait être `fin de la demo`.

Vous pouvez également inspecter les paquets installés ou la structure des répertoires :

```bash
docker exec ubuntu-24-demo ls /opt/app
docker exec ubuntu-24-demo python3 -c "import requests"
```

## Nettoyage

Pour arrêter et supprimer le conteneur Docker :

```bash
./stop.sh
```
