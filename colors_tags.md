# Méthodes pour colorer les dossiers dans le terminal

Voici deux approches pour personnaliser les couleurs des dossiers et fichiers dans le terminal d'Ubuntu et le terminal intégré de VS Code.

---

## Méthode 1 : Personnaliser les couleurs de base de la commande `ls`

Cette méthode modifie la configuration de la commande `ls` pour changer la couleur de tous les répertoires. C'est simple et efficace pour différencier les dossiers des fichiers.

### Étape 1 : Générer le fichier de configuration des couleurs

Ouvrez un terminal et exécutez la commande suivante. Elle crée un fichier `~/.dircolors` avec la configuration par défaut, que nous pourrons ensuite modifier.

```bash
dircolors -p > ~/.dircolors
```

### Étape 2 : Modifier la couleur des dossiers

Maintenant, ouvrez ce nouveau fichier avec un éditeur de texte comme `gedit` ou `nano`.

```bash
gedit ~/.dircolors
```

Cherchez la ligne qui commence par `DIR`. Par défaut, elle ressemble à ceci :

```
DIR 01;34 # directory
```

Le code `01;34` signifie "gras (01) et bleu (34)". Vous pouvez le changer. Voici quelques codes de couleur :
*   `31` : Rouge
*   `32` : Vert
*   `33` : Jaune
*   `35` : Magenta
*   `36` : Cyan

Par exemple, pour avoir des dossiers en cyan gras, changez la ligne pour :

```
DIR 01;36
```

### Étape 3 : Charger automatiquement cette configuration

Pour que votre terminal utilise votre fichier `~/.dircolors` à chaque démarrage, ajoutez le code suivant à la fin de votre fichier `~/.bashrc`.

```bash
# Charger les couleurs personnalisées pour ls si le fichier existe
if [ -r ~/.dircolors ]; then
    eval "$(dircolors -b ~/.dircolors)"
fi
```

Assurez-vous aussi que l'alias pour `ls` est activé dans `~/.bashrc` (c'est généralement le cas par défaut) :

```bash
alias ls='ls --color=auto'
```

### Étape 4 : Appliquer les changements

Pour voir le résultat immédiatement, exécutez :

```bash
source ~/.bashrc
```

---

## Méthode 2 : Utiliser `eza` pour une coloration avancée (Recommandé)

Si vous voulez une coloration plus intelligente et contextuelle (différentes couleurs selon les permissions, le statut Git, etc.), un outil moderne comme `eza` est la meilleure solution.

### Étape 1 : Installer `eza`

```bash
sudo mkdir -p /etc/apt/keyrings
wget -qO- https://raw.githubusercontent.com/eza-community/eza/main/deb.asc | sudo gpg --dearmor -o /etc/apt/keyrings/gierens.gpg
echo "deb [signed-by=/etc/apt/keyrings/gierens.gpg] http://deb.gierens.de stable main" | sudo tee /etc/apt/sources.list.d/gierens.list
sudo chmod 644 /etc/apt/keyrings/gierens.gpg /etc/apt/sources.list.d/gierens.list
sudo apt update
sudo apt install -y eza
```

### Étape 2 : Configurer des alias pour remplacer `ls`

Ajoutez ces alias à la fin de votre fichier `~/.bashrc` pour remplacer `ls` par `eza` avec des options utiles.

```bash
# Alias pour eza (remplacement moderne de ls)
alias ls='eza --icons --color=always --group-directories-first'
alias ll='eza -l --icons --git' # vue longue avec détails git
alias la='eza -la --icons --git' # comme ll, mais avec les fichiers cachés
alias l='ll' # alias court
alias lt='eza --tree --level=2' # vue en arborescence
```

### Étape 3 : Installer une "Nerd Font" (Recommandé)

Pour que les icônes (`--icons`) s'affichent, vous devez installer et configurer une police compatible comme **FiraCode Nerd Font**.

1.  Téléchargez la police depuis nerdfonts.com.
2.  Installez-la sur votre système.
3.  Configurez votre **Terminal Ubuntu** (`Préférences > Profil > Texte`) et **VS Code** (`terminal.integrated.fontFamily`) pour utiliser cette police.

### Étape 4 : Appliquer les changements

Activez les changements avec :

```bash
source ~/.bashrc
```

Désormais, `ls`, `ll`, etc., utiliseront `eza` pour un affichage riche en couleurs et en icônes.
