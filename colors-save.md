# Créer un script de sauvegarde pour vos fichiers de configuration

Garder une copie de vos fichiers de configuration (souvent appelés "dotfiles") est une excellente pratique. Cela vous permet de restaurer rapidement votre environnement personnalisé sur une nouvelle machine ou après une réinstallation.

Voici comment créer un script Bash simple pour automatiser cette tâche.

## 1. Création du script de sauvegarde

Créez un nouveau fichier nommé `backup_dotfiles.sh` dans un répertoire de votre choix (par exemple, `~/scripts/`).

```bash
mkdir -p ~/scripts
touch ~/scripts/backup_dotfiles.sh
```

Ouvrez ce fichier et collez-y le code suivant :

```bash
#!/bin/bash

# Script simple pour sauvegarder les fichiers de configuration importants.

# --- Configuration ---
# Répertoire où les sauvegardes seront stockées.
BACKUP_DIR="$HOME/dotfiles_backup"

# Liste des fichiers de configuration à sauvegarder (chemins depuis le répertoire HOME).
FILES_TO_BACKUP=(
    ".bashrc"
    ".dircolors"
    ".gitconfig" # Exemple d'un autre fichier utile à sauvegarder
    ".profile"
)

# --- Exécution ---
echo "Démarrage de la sauvegarde des dotfiles..."

# Crée le répertoire de sauvegarde s'il n'existe pas.
mkdir -p "$BACKUP_DIR"
echo "Le répertoire de sauvegarde est : $BACKUP_DIR"

# Boucle sur chaque fichier à sauvegarder.
for file in "${FILES_TO_BACKUP[@]}"; do
    # Construit le chemin complet du fichier source.
    source_file="$HOME/$file"

    # Vérifie si le fichier source existe avant de le copier.
    if [ -f "$source_file" ]; then
        echo "-> Sauvegarde de $file..."
        # Copie le fichier dans le répertoire de sauvegarde.
        cp "$source_file" "$BACKUP_DIR/"
    else
        echo "-> Attention : Le fichier $source_file n'a pas été trouvé. Ignoré."
    fi
done

echo "Sauvegarde terminée avec succès !"
```

## 2. Rendre le script exécutable

Pour pouvoir lancer le script, vous devez lui donner les permissions d'exécution.

```bash
chmod +x ~/scripts/backup_dotfiles.sh
```

## 3. Lancer la sauvegarde

Vous pouvez maintenant exécuter votre script à tout moment pour sauvegarder vos fichiers.

```bash
~/scripts/backup_dotfiles.sh
```

Les fichiers `.bashrc` et `.dircolors` (et les autres que vous avez listés) seront copiés dans le dossier `~/dotfiles_backup`.

## Bonus : Automatisation avec Cron

Pour une sauvegarde vraiment automatique, vous pouvez utiliser `cron` pour planifier l'exécution de ce script (par exemple, une fois par jour).

1.  Ouvrez l'éditeur de crontab : `crontab -e`
2.  Ajoutez cette ligne pour lancer le script tous les jours à midi :
    `0 12 * * * /bin/bash $HOME/scripts/backup_dotfiles.sh`
