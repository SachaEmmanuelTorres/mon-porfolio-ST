# deploy.py - Exemple de déploiement PyInfra

from pyinfra.operations import apt, server, files, python, pip

# Mise à jour du système
apt.update(
    name="Mise à jour de la liste des paquets",
)

# Installation de paquets supplémentaires
apt.packages(
    name="Installation de paquets utiles",
    packages=[
        "git",
        "python3",
        "python3-pip",
        "htop",
        "net-tools",
    ],
    update=True,
)
print("✓ Installation des paquets avec succès!")

# Copier le fichier requirements.txt
files.put(
    name="Copie du fichier requirements.txt",
    src="requirements.txt",
    dest="/opt/app/requirements.txt",
    mode="644",
)
print("✓ Fichier requirements.txt copié avec succès!")

# Installation des dépendances Python
server.shell(
    name="Installation des dépendances Python",
    commands=["pip3 install -r /opt/app/requirements.txt --break-system-packages"],
)
print("✓ Installation des dépendances Python terminée!")



# Créer des répertoires
files.directory(
    name="Créer répertoire d'application",
    path="/opt/app",
    present=True,
    mode="755",
)



# Exemple d'exécution de commande
server.shell(
    name="Vérifier la version Python",
    commands=["python3 --version"],
)
print("✓ vérification version python terminée")

# Créer le répertoire /home/ubuntu si nécessaire
files.directory(
    name="Créer le répertoire /home/ubuntu",
    path="/home/ubuntu",
    present=True,
    mode="755",
)

# Créer le fichier demo_finished.txt
server.shell(
    name="Créer le fichier demo_finished.txt",
    commands=['echo "fin de la demo" > /home/ubuntu/demo_finished.txt'],
)
print("✓ Fichier demo_finished.txt créé avec succès!")

print("✓ Déploiement terminé avec succès!")
