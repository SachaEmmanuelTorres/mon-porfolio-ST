# Fake Data DB API

Ce projet fournit une API FastAPI pour générer et servir des données fictives pour l'entraînement de bases de données et d'APIs.

## Fonctionnalités

*   **Génération de données dynamique** : Configurez vos tables de données et leurs champs à l'aide de simples fichiers `.txt` dans le répertoire `input_fields/`.
*   **Intégration Faker** : Tirez parti de la puissante bibliothèque Faker pour générer des données fictives réalistes pour divers types de données.
*   **Base de données DuckDB persistante** : Les données sont stockées et interrogées efficacement dans une base de données DuckDB nommée `fake_data_db.duckdb`. Cette base de données est recréée à chaque démarrage du serveur pour garantir des données fraîches.
*   **Endpoints FastAPI** : Accédez à vos données générées via des endpoints d'API paginés.
*   **Swagger UI par défaut** : Une interface Swagger UI interactive est disponible pour explorer l'API.

## Structure du projet

```
.
├── __init__.py
├── classes_out.py          # (Commenté) Modèles de données originaux
├── generate_fake_data.py   # Logique principale pour la génération dynamique de données fictives
├── main.py                 # Application FastAPI et endpoints d'API
├── input_fields/           # Répertoire contenant les fichiers .txt pour les configurations de tables de données
│   └── fields.txt          # Exemple de fichier de configuration de champs
├── tests/
│   ├── conftest.py         # Configuration Pytest pour la gestion des chemins
│   └── test_faker_generator.py # Tests unitaires pour l'application
└── fake_data_db.duckdb     # Fichier de base de données DuckDB (généré au démarrage)
```

## Configuration et installation

1.  **Cloner le dépôt (si applicable) :**
    ```bash
    git clone <repository_url>
    cd data_faker_server_fastapi
    ```

2.  **Créer un environnement virtuel (recommandé, surtout avec `pyenv`) :**
    Assurez-vous d'utiliser la version de Python souhaitée (par exemple, 3.12.11) avec `pyenv`.
    ```bash
    # Exemple pour les utilisateurs de pyenv :
    # pyenv local 3.12.11
    python -m venv venv
    source venv/bin/activate  # Sous Windows : `venv\Scripts\activate`
    ```

3.  **Installer les dépendances :**
    ```bash
    pip install -r requirements.txt
    ```
    (Note : Vous devrez peut-être créer `requirements.txt` d'abord s'il n'existe pas. Voir "Création de `requirements.txt`" ci-dessous.)

### Création de `requirements.txt`

Si `requirements.txt` n'existe pas, vous pouvez le créer en exécutant :
```bash
pip freeze > requirements.txt
```
Cela listera tous les paquets actuellement installés et leurs versions.

## Comment lancer le serveur

Pour démarrer le serveur FastAPI, **après avoir activé votre environnement virtuel**, exécutez la commande suivante depuis la racine du projet :

```bash
uvicorn main:app --reload --port 8001
```

*   `uvicorn main:app` : Indique à Uvicorn d'exécuter l'objet `app` dans `main.py`.
*   `--reload` : Active le rechargement automatique du serveur lorsque des modifications de code sont détectées (utile pour le développement).
*   `--port 8000` : Spécifie le port sur lequel le serveur doit écouter.

Le serveur s'exécutera généralement sur `http://127.0.0.1:8000`.

## Accéder à l'API et à l'interface Swagger UI

Une fois le serveur lancé :

*   **Swagger UI** : Ouvrez votre navigateur web et naviguez vers `http://127.0.0.1:8000/docs`. Vous y trouverez la documentation interactive de l'API.
*   **Regénérer les données** : L'endpoint POST `/regenerate-all-data` permet de regénérer toutes les données à partir des fichiers de configuration. Vous pouvez l'appeler via l'interface Swagger UI.
*   **Accéder aux données** : Utilisez l'endpoint GET `/data/{table_name}` (par exemple, `http://127.0.0.1:8000/data/fields`) pour récupérer les données fictives paginées d'une table spécifique.

## Configuration des données fictives

La génération de données fictives est configurée via des fichiers `.txt` situés dans le répertoire `input_fields/`.

1.  **Créez un nouveau fichier** dans le répertoire `input_fields/` (par exemple, `input_fields/users.txt`). Le nom du fichier (sans l'extension `.txt`) sera le nom de votre table de données.
2.  **Définissez les champs** dans le fichier `.txt`, un champ par ligne, en utilisant le format `nom_champ:fournisseur_faker`.

    **Exemple `input_fields/users.txt` :**
    ```
    user_id:unique.random_int
    first_name:first_name
    last_name:last_name
    email:email
    address:address
    phone_number:phone_number
    created_at:date_time_this_century
    ```

    Consultez la [documentation de Faker](https://faker.readthedocs.io/en/master/providers.html) pour une liste complète des fournisseurs disponibles.

3.  **Regénérer les données** : Après avoir ajouté ou modifié un fichier `.txt`, appelez l'endpoint POST `/regenerate-all-data` via l'interface Swagger UI pour appliquer vos modifications et générer de nouvelles données.

## Exécution des tests

Pour exécuter les tests unitaires du projet, accédez à la racine du projet et exécutez :

```bash
pytest
```

Cela découvrira et exécutera tous les tests dans le répertoire `tests/`.