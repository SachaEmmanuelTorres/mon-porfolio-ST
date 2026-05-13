# Exercices SQL et Scripts Python (Version 2)

Ce répertoire contient une version refactorisée du projet d'exercices SQL et de scripts Python. L'objectif est d'explorer les requêtes SQL et l'interaction avec une base de données SQLite (`explo.db`) de manière plus organisée, en séparant la logique du code dans un dossier `src`.

## Structure du Projet (v2)

```
v2/
├── .env/
├── .python-version
├── explo.db
├── README.md
├── requirements.txt
└── src/
    ├── constants.py
    ├── exemple_query_script.py
    ├── exercices_SQL.ipynb
    └── populate_db.py
```

## Prérequis

Avant de commencer, assurez-vous d'avoir un environnement Python configuré et les dépendances installées. Toutes les commandes doivent être exécutées depuis le répertoire `v2/`.

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

## Dépannage: Problèmes `pyenv` et Environnement Virtuel

Si vous utilisez `pyenv` et rencontrez l'erreur `pyenv: python: command not found` ou des problèmes similaires lors de l'activation de l'environnement virtuel ou de l'installation des dépendances, cela peut indiquer une interférence de `pyenv` avec la gestion de l'exécutable `python`.

Voici les étapes recommandées pour résoudre ces problèmes et assurer une configuration correcte :

1.  **Assurez-vous que l'environnement virtuel est à la racine du projet** :
    Le répertoire `.env` doit se trouver à la racine de votre projet (au même niveau que `main.py` et le dossier `v2`). Si vous l'avez déplacé, replacez-le à la racine.

2.  **Supprimez et recréez l'environnement virtuel** (si nécessaire) :
    Si votre environnement virtuel est corrompu ou mal configuré, il est souvent plus simple de le recréer :
    ```bash
    rm -rf ./.env
    python3 -m venv ./.env
    ```

3.  **Activez l'environnement virtuel** :
    Depuis la racine de votre projet, activez l'environnement virtuel. Notez que le chemin est `/.env/` et non `v2/.env/` car le `.env` est à la racine.
    ```bash
    source ./.env/bin/activate
    ```

4.  **Installez les dépendances de manière explicite** :
    Pour contourner les interférences potentielles de `pyenv` ou les problèmes d'environnement géré, utilisez le chemin complet de l'exécutable Python de l'environnement virtuel pour installer les dépendances :
    ```bash
    ./.env/bin/python -m pip install -r v2/requirements.txt
    ```

5.  **Vérifiez l'activation et l'exécution** :
    Après ces étapes, votre environnement virtuel devrait être correctement activé et les dépendances installées. Vous devriez pouvoir exécuter `main.py` depuis la racine du projet :
    ```bash
    python main.py
    ```

## Configuration de la Base de Données

Le script `src/populate_db.py` est utilisé pour créer la base de données `explo.db` (située à la racine de `v2/`) et y insérer les schémas de table et les données initiales. C'est une étape essentielle à exécuter avant d'utiliser le notebook Jupyter ou d'autres scripts de requête.

Pour configurer la base de données, exécutez le script Python depuis le répertoire `v2/` :

```bash
python src/populate_db.py
```

Ce script va :
- Supprimer les tables existantes (si elles existent) pour assurer un état propre.
- Créer la base de données `explo.db` (si elle n'existe pas).
- Créer les tables `employees`, `customers`, `orders`, `people` et `products`.
- Insérer des données initiales valides dans ces tables.

## Exemples d'utilisation

Voici deux scénarios d'utilisation typiques de ce projet :

### 1. Utilisation Interactive du Notebook

Ce scénario est idéal pour l'exploration de données, le prototypage de requêtes et l'analyse interactive.

1.  **Lancer Jupyter Notebook** :
    Depuis le répertoire `v2/`, lancez Jupyter Notebook :
    ```bash
    jupyter notebook
    ```
2.  **Ouvrir le Notebook** :
    Dans votre navigateur, naviguez vers le dossier `src/` et ouvrez le fichier `exercices_SQL.ipynb`.
3.  **Gestion des Cellules et des Sorties** :
    *   Lorsque vous ajoutez ou modifiez des requêtes dans le notebook, il est recommandé d'**effacer toutes les sorties** (`Cell > All Output > Clear`) puis de **relancer toutes les cellules** (`Cell > Run All`) pour assurer une exécution propre et à jour.
4.  **Ajouter ou Modifier des Cellules de Requêtes** :
    *   Vous pouvez ajouter de nouvelles cellules de code ou modifier celles existantes.
    *   Utilisez `%%sql` pour des requêtes SQL simples (par exemple, `SELECT * FROM ma_table;`).
    *   Pour des requêtes plus complexes, des jointures, ou pour intégrer les résultats directement dans un DataFrame Pandas, utilisez le pattern Python suivant (exemple générique) :
        ```python
        import pandas as pd

        # Votre requête SQL ici
        my_sql_query = """
        SELECT
            o.order_id,
            c.name AS customer_name,
            p.name AS product_name,
            p.price
        FROM
            orders o
        JOIN
            customers c ON o.customer_id = c.id
        JOIN
            products p ON o.product_id = p.id -- Assurez-vous que 'orders' a une colonne 'product_id'
        WHERE
            p.price > 100;
        """

        # Exécutez la requête et stockez le résultat dans un DataFrame Pandas
        df_result = pd.read_sql_query(my_sql_query, 'sqlite:///../explo.db') # Notez le chemin relatif

        # Affichez le DataFrame
        print("Résultat de la requête en DataFrame :")
        print(df_result)
        ```

### 2. Utilisation des Scripts Python pour la Base de Données et les Requêtes

Ce scénario est utile pour la configuration de la base de données et l'exécution de requêtes prédéfinies via des scripts Python.

1.  **Lancer le Script de Population de la Base de Données** :
    Depuis le répertoire `v2/`, exécutez le script pour créer et peupler la base de données. Cela garantit que votre base de données est prête avec les données initiales.
    ```bash
    python src/populate_db.py
    ```
2.  **Modifier une Requête dans un Script Python** :
    Ouvrez le fichier `src/exemple_query_script.py` et modifiez la valeur de la variable `query` avec la requête SQL de votre choix.
    ```python
    # src/exemple_query_script.py
    import sqlite3
    import pandas as pd
    from constants import DB_NAME # Importation du nom de la base de données

    # ... (autres imports et initialisations)

    # Connexion à la base de données
    conn = sqlite3.connect(DB_NAME) # Utilisation de DB_NAME
    # ...
    ```
3.  **Exécuter le Script Python avec la Nouvelle Requête** :
    Depuis le répertoire `v2/` :
    ```bash
    python src/exemple_query_script.py
    ```

## Exécution des Tests

Le projet inclus des tests unitaires et de performance écrits avec `pytest` pour garantir la qualité et le bon fonctionnement des scripts.

### Prérequis pour les Tests

Assurez-vous que `pytest` est installé dans votre environnement virtuel :
```bash
pip install pytest
```

### Lancer les Tests

Depuis la racine du projet (là où se trouve le dossier `v2/` et le dossier `tests/`), avec votre environnement virtuel activé, vous pouvez exécuter les tests comme suit :

1.  **Tests Unitaires et de Performance pour `populate_db.py`** :
    ```bash
    pytest tests/test_populate_db.py
    ```
    Ce test vérifie la connexion à la base de données, la création des tables, le peuplement des données, l'application des contraintes, et mesure le temps d'exécution du script `populate_db.py`.

2.  **Test de Performance pour les Requêtes SQL du Notebook** :
    ```bash
    pytest -s tests/run_notebook_performance.py
    ```
    Ce test extrait et exécute les requêtes SQL des cellules du notebook `exercices_SQL.ipynb` et mesure le temps total d'exécution, simulant ainsi l'utilisation du notebook.

