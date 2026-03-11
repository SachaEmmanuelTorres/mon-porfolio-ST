FROM ubuntu:24.04

# Mise à jour des paquets et installation de quelques outils de base optionnels
RUN apt-get update && apt-get upgrade -y

# Installation et configuration de SSH
RUN apt-get install -y openssh-server \
    && mkdir -p /run/sshd \
    && echo 'root:root' | chpasswd \
    && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
    && sed -i 's/UsePAM yes/UsePAM no/' /etc/ssh/sshd_config \
    && sed -i 's/#ListenAddress 0.0.0.0/ListenAddress 0.0.0.0/' /etc/ssh/sshd_config \
    && sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

EXPOSE 22

# Commande pour garder le conteneur actif et démarrer le serveur SSH
CMD ["/usr/sbin/sshd", "-D"]
