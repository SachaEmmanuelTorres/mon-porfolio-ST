# Exercices SQL et Scripts Python

Ce répertoire contient un ensemble d'exercices SQL et de scripts Python conçus pour explorer les requêtes SQL et l'interaction avec une base de données SQLite (`explo.db`). Il inclut un script Python pour la configuration initiale de la base de données et un notebook Jupyter pour l'exécution interactive des requêtes et l'analyse des données.

## Prérequis

Avant de commencer, assurez-vous d'avoir un environnement Python configuré et les dépendances installées :

1.  **Activer l'environnement virtuel** :
    ```bash
    source ./.env/bin/activate
    ```

2.  **Installer les dépendances Python** :
    ```bash
    pip install -r requirements.txt
    ```
    Si vous rencontrez des problèmes avec l'extension `ipython-sql` dans le notebook, vous pouvez essayer de la réinstaller :
    ```bash
    pip uninstall -y ipython-sql && pip install ipython-sql
    ```

## Configuration de la Base de Données

Le script `populate_db.py` est utilisé pour créer la base de données `explo.db` et y insérer les schémas de table et les données initiales. C'est une étape essentielle à exécuter avant d'utiliser le notebook Jupyter.

Pour configurer la base de données, exécutez le script Python :

```bash
python populate_db.py
```

Ce script va :
- Supprimer les tables existantes (si elles existent) pour assurer un état propre.
- Créer la base de données `explo.db` (si elle n'existe pas).
- Créer les tables `employees`, `customers`, `orders`, `people` et `products`.
- Insérer des données initiales valides dans ces tables.

## Utilisation du Notebook Jupyter

Le notebook `exercices_SQL.ipynb` est conçu pour l'exploration interactive des données et l'exécution de requêtes SQL.

1.  **Lancer Jupyter Notebook** :
    ```bash
    jupyter notebook exercices_SQL.ipynb
    ```

2.  **Dans le Notebook** :
    *   Assurez-vous que l'extension `sql` est chargée (`%load_ext sql`).
    *   La configuration `autopandas` est activée (`%config SqlMagic.autopandas = True`) pour retourner les résultats des requêtes SQL directement en DataFrames Pandas.
    *   Connectez-vous à la base de données `explo.db` (`%sql sqlite:///explo.db`).
    *   Exécutez les cellules de code pour explorer les différentes requêtes SQL.
    *   Notez que les requêtes `INSERT` ont été retirées du notebook pour éviter les doublons avec le script de population.
    *   Les requêtes de `JOIN` et autres `SELECT` complexes utilisent `pandas.read_sql_query` pour une meilleure robustesse et une intégration directe avec les DataFrames.

## Exemples d'utilisation

Voici deux scénarios d'utilisation typiques de ce projet :

### 1. Utilisation Interactive du Notebook

Ce scénario est idéal pour l'exploration de données, le prototypage de requêtes et l'analyse interactive.

1.  **Lancer Jupyter Notebook** :
    ```bash
    jupyter notebook exercices_SQL.ipynb
    ```
2.  **Ouvrir le Notebook** :
    Dans votre navigateur, ouvrez le fichier `exercices_SQL.ipynb`.
3.  **Ajouter ou Modifier des Cellules de Requêtes** :
    *   Vous pouvez ajouter de nouvelles cellules de code ou modifier celles existantes.
    *   Utilisez `%%sql` pour des requêtes SQL simples (par exemple, `SELECT * FROM ma_table;`).
    *   Pour des requêtes plus complexes, des jointures, ou pour intégrer les résultats directement dans un DataFrame Pandas, utilisez le format Python avec `pandas.read_sql_query` :
        ```python
        import pandas as pd
        query = "SELECT col1, col2 FROM table1 JOIN table2 ON table1.id = table2.id;"
        df_result = pd.read_sql_query(query, 'sqlite:///explo.db')
        print(df_result)
        ```

### 2. Utilisation des Scripts Python pour la Base de Données et les Requêtes

Ce scénario est utile pour la configuration de la base de données et l'exécution de requêtes prédéfinies via des scripts Python.

1.  **Lancer le Script de Population de la Base de Données** :
    À la racine du projet, exécutez le script pour créer et peupler la base de données. Cela garantit que votre base de données est prête avec les données initiales.
    ```bash
    python populate_db.py
    ```
2.  **Modifier une Requête dans un Script Python** :
    Ouvrez le fichier `exemple_query_script.py` et modifiez la valeur de la variable `query` avec la requête SQL de votre choix.
    ```python
    # exemple_query_script.py
    import sqlite3
    import pandas as pd

    DATABASE = 'explo.db'
    query = "SELECT name, department FROM employees WHERE department = 'HR';" # Modifiez cette ligne

    conn = sqlite3.connect(DATABASE)
    df = pd.read_sql_query(query, conn)
    print(df)
    conn.close()
    ```
3.  **Exécuter le Script Python avec la Nouvelle Requête** :
    ```bash
    python exemple_query_script.py
    ```

## Structure du Répertoire

-   `exercices_SQL.ipynb`: Le notebook Jupyter contenant les exercices SQL.
-   `populate_db.py`: Script Python pour la création et le remplissage initial de la base de données.
-   `explo.db`: La base de données SQLite générée par `populate_db.py`.
-   `requirements.txt`: Liste des dépendances Python.
-   `.env/`: Répertoire de l'environnement virtuel.
-   `SQL_queries_scripts/`: Contient des fichiers `.sql` individuels pour référence ou exécution manuelle.

