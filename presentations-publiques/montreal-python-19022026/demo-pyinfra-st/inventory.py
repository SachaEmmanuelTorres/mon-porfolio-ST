# inventory.py - Configuration PyInfra pour conteneur Docker Ubuntu 24.04

# Définition de l'inventaire pour le conteneur Docker Ubuntu 24.04 via dockerssh
# Assurez-vous que le conteneur "ubuntu-24-demo" est en cours d'exécution et a un serveur SSH
# configuré et accessible.
# hosts = {
#     "@dockerssh/ubuntu-24-demo": {
#         "ssh_user": "root",
#         "ssh_password": "root",
#     }
# }

# Les sections commentées ci-dessous sont des exemples d'autres configurations possibles
# Configuration avec docker CLI directement (pour cibler un conteneur existant par son nom)
hosts = [
    "@docker/ubuntu-24-demo",
]

# Configuration avec données supplémentaires (pour ajouter des variables à l'hôte)
# hosts = {
#     "@dockerssh/ubuntu-24-demo": {
#         "data": {
#             "env": "dev",
#             "role": "app-server",
#         }
#     }
# }


# Configuration avec docker CLI directement
# ubuntu_container = {
#     "@docker/ubuntu-24-demo": {
#         "ssh_hostname": "ubuntu-24-demo",
#     }
# }

# Configuration avec données supplémentaires
# ubuntu_container = {
#     "@docker/ubuntu-24-demo": {
#         "data": {
#             "env": "dev",
#             "role": "app-server",
#         }
#     }
# }
