# OBS Twitch Auto Recorder
Comme tout  amateur de stream Twitch, vous ne voulez pas manquer une seule diffusion .
Probleme : votre createur de contenues favori diffuse depuis une localisation geographique avec un decalage horaire par rapport a vous .

Question: Comment faire ?
Reponse : enregistrer en direct puis visonner en differer pour preserver votre sommeil.

Ce script Python surveille une chaîne Twitch spécifique et déclenche automatiquement l'enregistrement dans OBS Studio lorsque la chaîne passe en direct, puis l'arrête lorsque la chaîne revient hors ligne.

## Fonctionnalités

- Démarre l'enregistrement sur OBS dès que le stream Twitch commence.
- Arrête l'enregistrement dès que le stream Twitch se termine.
- Change automatiquement vers une scène OBS prédéfinie avant de lancer l'enregistrement.
- Configuration sécurisée via des variables d'environnement.

## Prérequis

- Python 3.8+
- OBS Studio
- Le plugin `obs-websocket` pour OBS Studio (généralement inclus par défaut dans les versions récentes d'OBS).
- pyenv install 3.12.10
    ```
3.  **Définissez Python 3.12.10 pour ce projet** et créez un environnement virtuel local :
    ```bash
    pyenv local 3.12.10
    python -m venv .env
    
Assurez-vous que le serveur WebSocket est activé dans OBS : `Outils -> Paramètres du serveur WebSocket`.

## Installation

1.  Clonez ce dépôt sur votre machine locale.
2.  Naviguez dans le dossier du projet :
    ```bash
    cd projet_obs
    ```
3.  Créez un environnement virtuel :
    ```bash
    python -m venv .env
    ```
4.  Activez l'environnement virtuel :
    -   **Windows** : `.\.env\Scripts\activate`
    -   **Linux/macOS** : `source .env/bin/activate`
5.  Installez les dépendances :
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

Ce projet se configure via des variables d'environnement. Vous avez deux manières de les définir.

### Option 1 (Recommandée) : Fichier `.env`

La méthode la plus simple est de créer un fichier nommé `.env` à la racine du projet.

1.  Créez le fichier `.env`.
2.  Copiez-collez le contenu ci-dessous et remplacez les valeurs par les vôtres :

    ```dotenv
    TWITCH_CLIENT_ID="votre_client_id_twitch"
    TWITCH_CLIENT_SECRET="votre_client_secret_twitch"
    NOM_CHAINE_TWITCH="nom_de_la_chaine_a_surveiller"
    OBS_HOST="localhost"
    OBS_PORT="4455"
    OBS_PASSWORD="votre_mot_de_passe_obs_websocket"
    NOM_SCENE_OBS="nom_de_votre_scene_obs"
    ```

### Option 2 : Variables d'environnement système

Si vous ne souhaitez pas utiliser de fichier `.env`, vous pouvez définir ces variables directement dans votre terminal avant de lancer le script.

#### Sous Linux et macOS

```bash
export TWITCH_CLIENT_ID="votre_client_id"
export TWITCH_CLIENT_SECRET="votre_client_secret"
export NOM_CHAINE_TWITCH="recalbox"
export OBS_HOST="localhost"
export OBS_PORT="4455"
export OBS_PASSWORD="votre_mot_de_passe"
export NOM_SCENE_OBS="Scene"
```

#### Sous Windows (Command Prompt)

```batch
set TWITCH_CLIENT_ID="votre_client_id"
set OBS_HOST="localhost"
:: ... et ainsi de suite pour chaque variable
```

#### Sous Windows (PowerShell)

```powershell
$env:TWITCH_CLIENT_ID="votre_client_id"
$env:OBS_HOST="localhost"
# ... et ainsi de suite pour chaque variable
```

## Utilisation

Une fois l'environnement configuré, lancez le script principal :

```bash
python main.py
```

Le script se connectera à OBS et commencera à surveiller la chaîne Twitch.


## Automatisation (Linux) 
Pour une utilisation entièrement automatisée sous Linux, deux scripts shell sont fournis pour lancer l'application et la planifier. 

### Scripts d'automatisation 
lancer_enregistrement.sh: Ce script principal d'automatisation vérifie si OBS Studio est en cours d'exécution, le lance si nécessaire, puis exécute le script Python main.py. Il est conçu pour être appelé par une tâche planifiée (comme cron). 

+- test_obs_launch.sh: Un script de test simple pour vérifier que la commande de lancement d'OBS Studio fonctionne correctement sur votre système. 
+ +
### Placement des scripts 

Ces deux scripts (lancer_enregistrement.sh et test_obs_launch.sh) doivent être placés dans le répertoire parent du dossier projet_obs.

Exemple de structure : 
``` +/home/sacha/Bureau/projets/
├── launch_recording.sh
├── test_obs_launch.sh 
└── projet_obs/
    ├── main.py
    ├── README.md
    └── ... ```

### Rendre les scripts exécutables 
Avant de pouvoir utiliser ces scripts, vous devez leur donner la permission d'exécution. 

Ouvrez un terminal et exécutez les commandes suivantes :
 bash  chmod +x /home/sacha/Bureau/projets/launch_recording.sh 
       chmod +x /home/sacha/Bureau/projets/test_obs_launch.sh 

 Une fois ces étapes réalisées, vous pouvez utiliser lancer_enregistrement.sh dans une tâche cron pour une automatisation complète.


