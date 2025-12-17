# Projet de Génération de Données Fictives

Ce projet fournit des scripts Python pour générer des données fictives (fake data).
Il permet de creer des fichiers de donnees en donnant une liste de noms de colonnes 
et retourne un ficheir csv ou dans un autre format de fichier.

## Prequies 
**Creer un python-version en 3.12.11 avec pyenv:**
``` bash
 pyenv install 3.12.11
 pyenv local 3.12.11
```

**activer le virtual environement .env :**
 ```bash
 source .env/bin/activate
 ```

**installer le s paquets python pour les generateurs de data :**
```bash
 pip install -r generator_requirements.txt
```

**Avant de lancer les commandes de generation des data,** 
**il faut lancer le fake_server qui se trouve**

**Consulter le data_faker_server_fastapi/README.md pour le lancement du fake_server FastApi.**


## Utilisation de `fake_forge.py`

Ce script génère un fichier de données fictives au format CSV.

**Commande :**
```bash
python fake_forge.py
```

**Input :**
Le script utilise une liste de colonnes définie dans un fichier `.txt` situé dans le dossier `input_list_columns/`.

**Output :**
Le fichier CSV résultant est sauvegardé dans le dossier `Data/`.

## Utilisation de `generic_faker.py`

Ce script génère également des données fictives, mais permet de choisir le format du fichier de sortie.

**Commande :**
```bash
python generic_faker.py
```

**Input :**
Comme pour le script précédent, la liste des colonnes est lue depuis un fichier `.txt` dans le dossier `input_list_columns/`.

**Output :**
Le fichier généré est sauvegardé dans le dossier `Data/`. L'utilisateur peut choisir le format de sortie (par exemple, JSON, Parquet, XML, etc.).
