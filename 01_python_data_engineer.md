

> **Objectif** : Réviser les compétences Python essentielles pour un test de 60 minutes axé sur le data engineering, l'automatisation et l'analyse de grands ensembles de données.

---

## 1. Manipulation de données avec Pandas

### Définitions

**Pandas** est la bibliothèque standard Python pour la manipulation de données tabulaires. Les deux structures principales :
- **Series** : tableau unidimensionnel indexé (comme une colonne)
- **DataFrame** : tableau bidimensionnel indexé (comme une table SQL)

### Exemples détaillés

**Exemple 1 : Création et exploration**
```python
import pandas as pd
import numpy as np

# Création depuis un dictionnaire
df = pd.DataFrame({
    'employe_id': [1, 2, 3, 4, 5],
    'nom': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
    'departement': ['Finance', 'IT', 'Finance', 'IT', 'RH'],
    'salaire': [75000, 82000, 68000, 90000, 71000],
    'date_embauche': pd.to_datetime(['2020-01-15', '2019-06-01', '2021-03-20', '2018-09-10', '2020-11-05'])
})

# Exploration rapide
print(df.shape)          # (5, 5) — lignes, colonnes
print(df.dtypes)         # types de chaque colonne
print(df.describe())     # statistiques numériques
print(df.info())         # résumé complet (types, non-null)
print(df.head(3))        # 3 premières lignes
```

**Exemple 2 : Filtrage, sélection, transformation**
```python
# Filtrage avec conditions multiples
seniors_it = df[(df['departement'] == 'IT') & (df['salaire'] > 85000)]

# Sélection de colonnes
noms_salaires = df[['nom', 'salaire']]

# Ajout de colonnes calculées
df['anciennete_jours'] = (pd.Timestamp.now() - df['date_embauche']).dt.days
df['salaire_mensuel'] = df['salaire'] / 12
df['tranche_salaire'] = pd.cut(df['salaire'], bins=[0, 70000, 80000, 100000],
                                labels=['Junior', 'Confirmé', 'Senior'])

# Apply pour transformations personnalisées
df['nom_upper'] = df['nom'].apply(lambda x: x.upper())
df['bonus'] = df.apply(lambda row: row['salaire'] * 0.15 if row['departement'] == 'IT' else row['salaire'] * 0.10, axis=1)
```

**Exemple 3 : Groupby et agrégation**
```python
# Agrégation simple
stats_dept = df.groupby('departement').agg(
    nb_employes=('employe_id', 'count'),
    salaire_moyen=('salaire', 'mean'),
    salaire_median=('salaire', 'median'),
    salaire_total=('salaire', 'sum'),
    premier_embauche=('date_embauche', 'min')
).reset_index()

# Agrégation avec fonctions multiples
multi_agg = df.groupby('departement')['salaire'].agg(['mean', 'std', 'min', 'max'])

# Transform : appliquer le résultat du groupe à chaque ligne
df['salaire_moyen_dept'] = df.groupby('departement')['salaire'].transform('mean')
df['ecart_moyenne'] = df['salaire'] - df['salaire_moyen_dept']

# Filtrage par groupe (garder les départements avec salaire moyen > 75000)
df_filtré = df.groupby('departement').filter(lambda x: x['salaire'].mean() > 75000)
```

**Exemple 4 : Jointures (merge) et concaténation**
```python
# Données de commandes
commandes = pd.DataFrame({
    'commande_id': [101, 102, 103, 104],
    'employe_id': [1, 2, 1, 6],  # 6 n'existe pas dans df
    'montant': [500, 300, 700, 200]
})

# INNER JOIN
inner = pd.merge(df, commandes, on='employe_id', how='inner')

# LEFT JOIN
left = pd.merge(df, commandes, on='employe_id', how='left')

# Anti-join (employés sans commande)
merged = pd.merge(df, commandes, on='employe_id', how='left', indicator=True)
sans_commande = merged[merged['_merge'] == 'left_only'][df.columns]

# Concaténation verticale
df_new = pd.DataFrame({'employe_id': [6], 'nom': ['Frank'], 'departement': ['RH'],
                        'salaire': [65000], 'date_embauche': pd.to_datetime(['2022-01-01'])})
df_complet = pd.concat([df, df_new], ignore_index=True)
```

### Exercices

**Exercice 1** : Charger un DataFrame de transactions avec colonnes (txn_id, client_id, montant, date, categorie). Calculer pour chaque client : le nombre de transactions, le montant total, le montant moyen, et la date de la dernière transaction.

<details>
<summary>Solution</summary>

```python
import pandas as pd

transactions = pd.DataFrame({
    'txn_id': range(1, 11),
    'client_id': [1, 2, 1, 3, 2, 1, 3, 2, 1, 3],
    'montant': [100, 250, 75, 300, 150, 200, 50, 175, 125, 400],
    'date': pd.date_range('2026-01-01', periods=10, freq='D'),
    'categorie': ['A', 'B', 'A', 'C', 'B', 'A', 'C', 'B', 'A', 'C']
})

resume_client = transactions.groupby('client_id').agg(
    nb_transactions=('txn_id', 'count'),
    montant_total=('montant', 'sum'),
    montant_moyen=('montant', 'mean'),
    derniere_transaction=('date', 'max')
).reset_index()

print(resume_client)
```
</details>

**Exercice 2** : À partir de deux DataFrames (employes et departements), faire une jointure et identifier les départements sans employé.

<details>
<summary>Solution</summary>

```python
employes = pd.DataFrame({
    'id': [1, 2, 3],
    'nom': ['Alice', 'Bob', 'Charlie'],
    'dept_id': [10, 20, 10]
})

departements = pd.DataFrame({
    'dept_id': [10, 20, 30, 40],
    'dept_nom': ['Finance', 'IT', 'Marketing', 'Legal']
})

# Jointure avec indicateur
merged = pd.merge(departements, employes, on='dept_id', how='left', indicator=True)
depts_vides = merged[merged['_merge'] == 'left_only'][['dept_id', 'dept_nom']]
print(depts_vides)
# dept_id=30 Marketing, dept_id=40 Legal
```
</details>

**Exercice 3** : Créer un tableau croisé (pivot) montrant le montant total des ventes par région (lignes) et par trimestre (colonnes).

<details>
<summary>Solution</summary>

```python
ventes = pd.DataFrame({
    'region': ['Nord', 'Sud', 'Nord', 'Sud', 'Nord', 'Sud', 'Nord', 'Sud'],
    'date': pd.to_datetime(['2025-01-15', '2025-02-20', '2025-04-10', '2025-05-05',
                            '2025-07-12', '2025-08-22', '2025-10-03', '2025-11-18']),
    'montant': [1000, 1500, 2000, 1800, 2200, 1900, 2500, 2100]
})

ventes['trimestre'] = ventes['date'].dt.to_period('Q')

pivot = ventes.pivot_table(
    values='montant',
    index='region',
    columns='trimestre',
    aggfunc='sum',
    fill_value=0
)
print(pivot)
```
</details>

**Exercice 4** : Calculer une moyenne mobile sur 3 périodes pour les ventes mensuelles, et identifier les mois où la vente est inférieure à la moyenne mobile.

<details>
<summary>Solution</summary>

```python
ventes_mensuelles = pd.DataFrame({
    'mois': pd.date_range('2025-01-01', periods=12, freq='MS'),
    'ventes': [100, 120, 90, 150, 130, 110, 160, 140, 170, 120, 180, 190]
})

ventes_mensuelles['moyenne_mobile_3'] = ventes_mensuelles['ventes'].rolling(window=3).mean()
ventes_mensuelles['sous_moyenne'] = ventes_mensuelles['ventes'] < ventes_mensuelles['moyenne_mobile_3']

print(ventes_mensuelles[ventes_mensuelles['sous_moyenne'] == True])
```
</details>

**Exercice 5** : Détecter et traiter les doublons et valeurs manquantes dans un DataFrame de clients.

<details>
<summary>Solution</summary>

```python
clients = pd.DataFrame({
    'id': [1, 2, 3, 2, 4, 5],
    'nom': ['Alice', 'Bob', 'Charlie', 'Bob', 'Diana', None],
    'email': ['alice@mail.com', 'bob@mail.com', None, 'bob@mail.com', 'diana@mail.com', 'eve@mail.com'],
    'age': [30, 25, None, 25, 35, 28]
})

# Identifier les doublons
print(f"Doublons: {clients.duplicated(subset=['id']).sum()}")
print(clients[clients.duplicated(subset=['id'], keep=False)])

# Supprimer les doublons (garder le premier)
clients_unique = clients.drop_duplicates(subset=['id'], keep='first')

# Identifier les valeurs manquantes
print(f"\nValeurs manquantes:\n{clients_unique.isnull().sum()}")

# Traiter les valeurs manquantes
clients_unique['nom'] = clients_unique['nom'].fillna('Inconnu')
clients_unique['email'] = clients_unique['email'].fillna('non_renseigné')
clients_unique['age'] = clients_unique['age'].fillna(clients_unique['age'].median())

print(clients_unique)
```
</details>

---

## 2. Traitement de fichiers et formats de données

### Définitions

| Format | Avantages | Cas d'usage |
|--------|-----------|-------------|
| **CSV** | Simple, universel, lisible | Export/import basique, compatibilité |
| **JSON** | Hiérarchique, flexible | APIs, données semi-structurées |
| **Parquet** | Columnar, compressé, typé | Data lakes, analytics performantes |
| **XML** | Structuré, schéma validable | Systèmes legacy, SOAP APIs |

### Exemples détaillés

**Lecture/écriture CSV optimisée :**
```python
import pandas as pd

# Lecture basique
df = pd.read_csv('data.csv')

# Lecture optimisée (types explicites, colonnes sélectionnées)
df = pd.read_csv('data.csv',
    usecols=['id', 'nom', 'montant', 'date'],  # seulement les colonnes utiles
    dtype={'id': 'int32', 'nom': 'string', 'montant': 'float32'},  # types optimisés
    parse_dates=['date'],
    na_values=['N/A', 'null', ''],
    encoding='utf-8'
)

# Écriture CSV
df.to_csv('output.csv', index=False, encoding='utf-8')
```

**JSON — lecture et aplatissement :**
```python
import json

# Lecture JSON simple
df = pd.read_json('data.json')

# JSON imbriqué — aplatissement
with open('nested.json') as f:
    data = json.load(f)

# Exemple de données imbriquées
data = [
    {"id": 1, "nom": "Alice", "adresse": {"ville": "Paris", "cp": "75001"},
     "commandes": [{"id": 101, "montant": 500}, {"id": 102, "montant": 300}]},
    {"id": 2, "nom": "Bob", "adresse": {"ville": "Lyon", "cp": "69001"},
     "commandes": [{"id": 103, "montant": 700}]}
]

# Aplatir avec json_normalize
df_flat = pd.json_normalize(data, meta=['id', 'nom', ['adresse', 'ville']],
                             record_path='commandes', record_prefix='cmd_')
print(df_flat)
# Colonnes: cmd_id, cmd_montant, id, nom, adresse.ville
```

**Parquet — lecture/écriture performante :**
```python
# Nécessite pyarrow ou fastparquet
# pip install pyarrow

# Écriture Parquet (compression automatique)
df.to_parquet('data.parquet', engine='pyarrow', compression='snappy')

# Lecture Parquet (très rapide grâce au format colonaire)
df = pd.read_parquet('data.parquet', columns=['id', 'montant'])  # lecture sélective

# Lecture de fichiers Parquet partitionnés
df = pd.read_parquet('data/', filters=[('annee', '=', 2025)])
```

**Gestion de gros fichiers — Chunking :**
```python
# Lecture par morceaux (chunks) pour fichiers trop gros pour la RAM
chunk_size = 10000
resultats = []

for chunk in pd.read_csv('gros_fichier.csv', chunksize=chunk_size):
    # Traiter chaque morceau
    chunk_filtre = chunk[chunk['montant'] > 1000]
    stats = chunk_filtre.groupby('categorie')['montant'].sum()
    resultats.append(stats)

# Combiner les résultats
final = pd.concat(resultats).groupby(level=0).sum()
```

**Générateurs pour traitement ligne par ligne :**
```python
import csv

def lire_gros_csv(fichier, seuil_montant=0):
    """Générateur qui lit un CSV ligne par ligne sans charger en mémoire."""
    with open(fichier, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if float(row['montant']) > seuil_montant:
                yield {
                    'id': int(row['id']),
                    'montant': float(row['montant']),
                    'categorie': row['categorie']
                }

# Utilisation : ne charge qu'une ligne à la fois en mémoire
for record in lire_gros_csv('transactions.csv', seuil_montant=500):
    print(record)
```

### Exercices

**Exercice 1** : Lire un fichier CSV de 10 millions de lignes et calculer le montant moyen par catégorie en utilisant le chunking.

<details>
<summary>Solution</summary>

```python
import pandas as pd
from collections import defaultdict

totaux = defaultdict(float)
counts = defaultdict(int)

for chunk in pd.read_csv('gros_fichier.csv', chunksize=50000,
                          usecols=['categorie', 'montant'],
                          dtype={'montant': 'float32'}):
    stats = chunk.groupby('categorie')['montant'].agg(['sum', 'count'])
    for cat, row in stats.iterrows():
        totaux[cat] += row['sum']
        counts[cat] += row['count']

moyennes = {cat: totaux[cat] / counts[cat] for cat in totaux}
print(moyennes)
```
</details>

**Exercice 2** : Convertir un fichier JSON imbriqué (clients avec liste de commandes) en un DataFrame plat avec une ligne par commande.

<details>
<summary>Solution</summary>

```python
import json
import pandas as pd

data = [
    {"client_id": 1, "nom": "Alice",
     "commandes": [
         {"cmd_id": 101, "montant": 500, "date": "2025-01-15"},
         {"cmd_id": 102, "montant": 300, "date": "2025-02-20"}
     ]},
    {"client_id": 2, "nom": "Bob",
     "commandes": [
         {"cmd_id": 103, "montant": 700, "date": "2025-03-10"}
     ]}
]

df = pd.json_normalize(
    data,
    record_path='commandes',
    meta=['client_id', 'nom'],
    record_prefix='cmd_'
)
print(df)
# client_id | nom   | cmd_cmd_id | cmd_montant | cmd_date
# 1         | Alice | 101        | 500         | 2025-01-15
# 1         | Alice | 102        | 300         | 2025-02-20
# 2         | Bob   | 103        | 700         | 2025-03-10
```
</details>

**Exercice 3** : Lire un fichier CSV, convertir en Parquet partitionné par année et mois.

<details>
<summary>Solution</summary>

```python
import pandas as pd

df = pd.read_csv('ventes.csv', parse_dates=['date_vente'])
df['annee'] = df['date_vente'].dt.year
df['mois'] = df['date_vente'].dt.month

# Écriture partitionnée
df.to_parquet('ventes_parquet/', partition_cols=['annee', 'mois'],
              engine='pyarrow', compression='snappy')

# Lecture avec filtre de partition
df_mars = pd.read_parquet('ventes_parquet/',
                           filters=[('annee', '=', 2025), ('mois', '=', 3)])
```
</details>

**Exercice 4** : Écrire un générateur qui lit un fichier XML de produits et yield chaque produit comme dictionnaire.

<details>
<summary>Solution</summary>

```python
import xml.etree.ElementTree as ET

def lire_produits_xml(fichier):
    """Générateur pour lire des produits depuis un XML."""
    tree = ET.parse(fichier)
    root = tree.getroot()

    for produit in root.findall('.//produit'):
        yield {
            'id': int(produit.find('id').text),
            'nom': produit.find('nom').text,
            'prix': float(produit.find('prix').text),
            'categorie': produit.find('categorie').text
        }

# XML attendu :
# <catalogue>
#   <produit><id>1</id><nom>Widget</nom><prix>29.99</prix><categorie>A</categorie></produit>
#   ...
# </catalogue>

for prod in lire_produits_xml('catalogue.xml'):
    print(prod)
```
</details>

**Exercice 5** : Comparer les performances de lecture d'un fichier de 100 000 lignes en CSV vs Parquet.

<details>
<summary>Solution</summary>

```python
import pandas as pd
import time
import numpy as np

# Générer les données de test
n = 100000
df = pd.DataFrame({
    'id': range(n),
    'nom': [f'client_{i}' for i in range(n)],
    'montant': np.random.uniform(10, 10000, n),
    'date': pd.date_range('2020-01-01', periods=n, freq='h'),
    'categorie': np.random.choice(['A', 'B', 'C', 'D'], n)
})

# Sauvegarder dans les deux formats
df.to_csv('test_perf.csv', index=False)
df.to_parquet('test_perf.parquet')

# Benchmark lecture CSV
start = time.time()
df_csv = pd.read_csv('test_perf.csv')
temps_csv = time.time() - start

# Benchmark lecture Parquet
start = time.time()
df_parquet = pd.read_parquet('test_perf.parquet')
temps_parquet = time.time() - start

print(f"CSV:     {temps_csv:.3f}s")
print(f"Parquet: {temps_parquet:.3f}s")
print(f"Parquet est {temps_csv/temps_parquet:.1f}x plus rapide")

# Benchmark lecture sélective (2 colonnes)
start = time.time()
df_csv_sel = pd.read_csv('test_perf.csv', usecols=['id', 'montant'])
temps_csv_sel = time.time() - start

start = time.time()
df_parquet_sel = pd.read_parquet('test_perf.parquet', columns=['id', 'montant'])
temps_parquet_sel = time.time() - start

print(f"\nLecture sélective (2 colonnes):")
print(f"CSV:     {temps_csv_sel:.3f}s")
print(f"Parquet: {temps_parquet_sel:.3f}s")
```
</details>

---

## 3. API REST en Python

### Définitions

- **REST** : Architecture basée sur HTTP (GET, POST, PUT, DELETE)
- **Authentification** : API Key, Bearer Token, OAuth 2.0, Basic Auth
- **Pagination** : offset/limit, cursor-based, page-based
- **Rate limiting** : Nombre de requêtes autorisées par période

### Exemples détaillés

**Exemple 1 : Client API REST complet avec retry**
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

class APIClient:
    """Client API REST avec retry, authentification et pagination."""

    def __init__(self, base_url, api_key, max_retries=3):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })

        # Configuration du retry automatique
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,  # 1s, 2s, 4s...
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def get(self, endpoint, params=None):
        """GET avec gestion d'erreurs."""
        url = f"{self.base_url}/{endpoint}"
        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    def get_paginated(self, endpoint, page_size=100):
        """GET avec pagination automatique (offset/limit)."""
        all_data = []
        offset = 0

        while True:
            params = {'limit': page_size, 'offset': offset}
            data = self.get(endpoint, params=params)

            if not data.get('results'):
                break

            all_data.extend(data['results'])
            offset += page_size

            # Vérifier s'il y a d'autres pages
            if len(data['results']) < page_size:
                break

        return all_data

    def post(self, endpoint, payload):
        """POST avec gestion d'erreurs."""
        url = f"{self.base_url}/{endpoint}"
        response = self.session.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()

# Utilisation
client = APIClient('https://api.example.com/v1', api_key='mon_api_key')
donnees = client.get_paginated('transactions')
```

**Exemple 2 : Client Snowflake REST API**
```python
import requests
import json
import time

class SnowflakeRESTClient:
    """Client pour l'API REST Snowflake SQL (/api/v2/statements)."""

    def __init__(self, account, token):
        self.base_url = f"https://{account}.snowflakecomputing.com"
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Snowflake-Authorization-Token-Type': 'OAUTH'
        }

    def execute_query(self, sql, database, schema, warehouse, timeout=60):
        """Exécuter une requête SQL via l'API REST."""
        url = f"{self.base_url}/api/v2/statements"
        payload = {
            "statement": sql,
            "timeout": timeout,
            "database": database,
            "schema": schema,
            "warehouse": warehouse,
            "resultSetMetaData": {"format": "jsonv2"}
        }

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        result = response.json()

        # Si la requête est asynchrone (statut 202)
        if response.status_code == 202:
            return self._poll_results(result['statementHandle'])

        return result

    def _poll_results(self, statement_handle, max_wait=300):
        """Attendre les résultats d'une requête asynchrone."""
        url = f"{self.base_url}/api/v2/statements/{statement_handle}"
        start = time.time()

        while time.time() - start < max_wait:
            response = requests.get(url, headers=self.headers)
            result = response.json()

            if result.get('statementStatusUrl') is None:
                return result  # Requête terminée

            time.sleep(2)  # Attendre 2 secondes avant de re-vérifier

        raise TimeoutError(f"Requête {statement_handle} timeout après {max_wait}s")

    def get_results_paginated(self, statement_handle):
        """Récupérer tous les résultats paginés."""
        all_data = []
        partition = 0

        while True:
            url = f"{self.base_url}/api/v2/statements/{statement_handle}"
            params = {'partition': partition}
            response = requests.get(url, headers=self.headers, params=params)
            result = response.json()

            all_data.extend(result.get('data', []))

            # Vérifier s'il reste des partitions
            total_partitions = result.get('resultSetMetaData', {}).get('partitionInfo', [])
            if partition >= len(total_partitions) - 1:
                break
            partition += 1

        return all_data

# Utilisation
sf = SnowflakeRESTClient('mon_compte', 'mon_token_oauth')
result = sf.execute_query(
    "SELECT * FROM ma_table LIMIT 100",
    database="MA_DB", schema="PUBLIC", warehouse="COMPUTE_WH"
)
```

**Exemple 3 : Décorateur de retry personnalisé**
```python
import functools
import time
import logging

logger = logging.getLogger(__name__)

def retry(max_attempts=3, delay=1, backoff=2, exceptions=(Exception,)):
    """Décorateur de retry avec backoff exponentiel."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(f"Échec après {max_attempts} tentatives: {e}")
                        raise
                    logger.warning(f"Tentative {attempt}/{max_attempts} échouée: {e}. "
                                   f"Retry dans {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator

# Utilisation
@retry(max_attempts=3, delay=2, exceptions=(requests.RequestException,))
def appeler_api(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()
```

### Exercices

**Exercice 1** : Écrire une fonction qui récupère toutes les données d'une API paginée par cursor (la réponse contient un champ `next_cursor`).

<details>
<summary>Solution</summary>

```python
import requests

def fetch_all_cursor(base_url, endpoint, headers=None):
    """Récupérer toutes les données avec pagination par cursor."""
    all_data = []
    cursor = None

    while True:
        params = {}
        if cursor:
            params['cursor'] = cursor

        response = requests.get(f"{base_url}/{endpoint}",
                                headers=headers, params=params, timeout=30)
        response.raise_for_status()
        result = response.json()

        all_data.extend(result.get('data', []))

        cursor = result.get('next_cursor')
        if not cursor:
            break

    return all_data
```
</details>

**Exercice 2** : Créer un script qui envoie des données en batch à une API POST (envoyer max 100 enregistrements par requête).

<details>
<summary>Solution</summary>

```python
import requests
import math

def envoyer_en_batch(url, donnees, batch_size=100, headers=None):
    """Envoyer des données en batchs à une API POST."""
    total = len(donnees)
    nb_batches = math.ceil(total / batch_size)
    resultats = []

    for i in range(nb_batches):
        debut = i * batch_size
        fin = min(debut + batch_size, total)
        batch = donnees[debut:fin]

        response = requests.post(url, json={'records': batch},
                                 headers=headers, timeout=60)
        response.raise_for_status()
        resultats.append({
            'batch': i + 1,
            'nb_records': len(batch),
            'status': response.status_code
        })
        print(f"Batch {i+1}/{nb_batches}: {len(batch)} enregistrements envoyés")

    return resultats
```
</details>

**Exercice 3** : Écrire un script qui appelle deux APIs en parallèle (données clients + données commandes), puis les joint.

<details>
<summary>Solution</summary>

```python
import requests
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

def fetch_data(url):
    """Récupérer les données d'une URL."""
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()

def fetch_and_join(url_clients, url_commandes):
    """Récupérer deux APIs en parallèle et joindre les résultats."""
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_clients = executor.submit(fetch_data, url_clients)
        future_commandes = executor.submit(fetch_data, url_commandes)

        clients = pd.DataFrame(future_clients.result()['data'])
        commandes = pd.DataFrame(future_commandes.result()['data'])

    # Jointure
    result = pd.merge(commandes, clients, on='client_id', how='left')
    return result

# Utilisation
# df = fetch_and_join('https://api.com/clients', 'https://api.com/commandes')
```
</details>

---

## 4. Automatisation et scripting

### Définitions

- **argparse** : Gestion des arguments en ligne de commande
- **logging** : Journalisation structurée (mieux que print)
- **Context managers** : Gestion automatique des ressources (with)

### Exemples détaillés

**Script ETL complet avec argparse et logging :**
```python
#!/usr/bin/env python3
"""Script ETL : extraction, transformation et chargement de données."""

import argparse
import logging
import sys
import pandas as pd
from datetime import datetime
from pathlib import Path

# Configuration du logging
def setup_logging(log_level, log_file=None):
    """Configurer le logging avec format structuré."""
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=handlers
    )

def extract(source_path):
    """Extraction des données depuis le fichier source."""
    logger = logging.getLogger('ETL.extract')
    logger.info(f"Extraction depuis {source_path}")

    df = pd.read_csv(source_path)
    logger.info(f"  → {len(df)} lignes extraites, {len(df.columns)} colonnes")
    return df

def transform(df):
    """Transformation des données."""
    logger = logging.getLogger('ETL.transform')
    initial_count = len(df)

    # Suppression des doublons
    df = df.drop_duplicates()
    logger.info(f"  Doublons supprimés: {initial_count - len(df)}")

    # Nettoyage des valeurs nulles
    null_counts = df.isnull().sum()
    cols_with_nulls = null_counts[null_counts > 0]
    if not cols_with_nulls.empty:
        logger.warning(f"  Colonnes avec NULL: {dict(cols_with_nulls)}")

    # Transformation des types
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')

    if 'montant' in df.columns:
        df['montant'] = pd.to_numeric(df['montant'], errors='coerce')

    logger.info(f"  → {len(df)} lignes après transformation")
    return df

def load(df, destination_path):
    """Chargement des données vers la destination."""
    logger = logging.getLogger('ETL.load')
    logger.info(f"Chargement vers {destination_path}")

    output_path = Path(destination_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if destination_path.endswith('.parquet'):
        df.to_parquet(destination_path, index=False)
    else:
        df.to_csv(destination_path, index=False)

    logger.info(f"  → {len(df)} lignes chargées")

def main():
    parser = argparse.ArgumentParser(description='Pipeline ETL')
    parser.add_argument('--source', '-s', required=True, help='Fichier source CSV')
    parser.add_argument('--destination', '-d', required=True, help='Fichier destination')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    parser.add_argument('--log-file', help='Fichier de log optionnel')
    args = parser.parse_args()

    setup_logging(args.log_level, args.log_file)
    logger = logging.getLogger('ETL')

    start_time = datetime.now()
    logger.info(f"=== Début du pipeline ETL ===")

    try:
        df = extract(args.source)
        df = transform(df)
        load(df, args.destination)

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"=== Pipeline terminé en {duration:.2f}s ===")
    except Exception as e:
        logger.error(f"Erreur dans le pipeline: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()

# Usage : python etl_script.py --source data/input.csv --destination data/output.parquet --log-level DEBUG
```

**Context managers personnalisés :**
```python
import time
from contextlib import contextmanager

@contextmanager
def timer(label=""):
    """Mesurer le temps d'exécution d'un bloc."""
    start = time.time()
    yield
    elapsed = time.time() - start
    print(f"[{label}] Temps: {elapsed:.3f}s")

@contextmanager
def database_connection(connection_string):
    """Gérer une connexion DB avec fermeture automatique."""
    import snowflake.connector
    conn = snowflake.connector.connect(**connection_string)
    try:
        yield conn
    finally:
        conn.close()

# Utilisation
with timer("Chargement"):
    df = pd.read_csv('gros_fichier.csv')

with timer("Transformation"):
    df = df.dropna().drop_duplicates()
```

### Exercices

**Exercice 1** : Créer un script avec argparse qui accepte un répertoire source, un pattern de fichiers (ex: `*.csv`), et qui fusionne tous les fichiers correspondants en un seul.

<details>
<summary>Solution</summary>

```python
import argparse
import pandas as pd
from pathlib import Path

def fusionner_fichiers(repertoire, pattern, output):
    fichiers = sorted(Path(repertoire).glob(pattern))
    if not fichiers:
        print(f"Aucun fichier trouvé pour {pattern} dans {repertoire}")
        return

    dfs = []
    for f in fichiers:
        print(f"Lecture: {f.name}")
        df = pd.read_csv(f)
        df['source_file'] = f.name
        dfs.append(df)

    result = pd.concat(dfs, ignore_index=True)
    result.to_csv(output, index=False)
    print(f"Fusion terminée: {len(result)} lignes → {output}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fusionner des fichiers CSV')
    parser.add_argument('--dir', required=True, help='Répertoire source')
    parser.add_argument('--pattern', default='*.csv', help='Pattern glob')
    parser.add_argument('--output', required=True, help='Fichier de sortie')
    args = parser.parse_args()
    fusionner_fichiers(args.dir, args.pattern, args.output)
```
</details>

**Exercice 2** : Écrire un script qui monitore un répertoire et traite automatiquement les nouveaux fichiers CSV qui y apparaissent.

<details>
<summary>Solution</summary>

```python
import time
from pathlib import Path
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(message)s')
logger = logging.getLogger()

def traiter_fichier(filepath):
    """Traiter un fichier CSV nouvellement détecté."""
    logger.info(f"Traitement de {filepath.name}")
    df = pd.read_csv(filepath)
    # ... transformation ...
    output = filepath.with_suffix('.parquet')
    df.to_parquet(output, index=False)
    logger.info(f"  → Converti en {output.name} ({len(df)} lignes)")

def monitorer_repertoire(repertoire, interval=5):
    """Surveiller un répertoire pour de nouveaux fichiers CSV."""
    path = Path(repertoire)
    fichiers_traites = set()

    # Initialiser avec les fichiers existants
    for f in path.glob('*.csv'):
        fichiers_traites.add(f.name)

    logger.info(f"Monitoring de {repertoire} (intervalle: {interval}s)")

    while True:
        for f in path.glob('*.csv'):
            if f.name not in fichiers_traites:
                traiter_fichier(f)
                fichiers_traites.add(f.name)
        time.sleep(interval)

if __name__ == '__main__':
    monitorer_repertoire('./inbox')
```
</details>

**Exercice 3** : Créer un context manager qui capture les exceptions, les log, et envoie un résumé d'exécution (nombre de succès/erreurs).

<details>
<summary>Solution</summary>

```python
import logging
from contextlib import contextmanager
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class ExecutionStats:
    total: int = 0
    success: int = 0
    errors: int = 0
    error_details: list = field(default_factory=list)

    def record_success(self):
        self.total += 1
        self.success += 1

    def record_error(self, error):
        self.total += 1
        self.errors += 1
        self.error_details.append(str(error))

    def summary(self):
        return (f"Total: {self.total}, Succès: {self.success}, "
                f"Erreurs: {self.errors} ({self.errors/max(self.total,1)*100:.1f}%)")

@contextmanager
def batch_processor(nom_batch):
    """Context manager pour traitement batch avec stats."""
    stats = ExecutionStats()
    logger.info(f"=== Début batch: {nom_batch} ===")

    yield stats

    logger.info(f"=== Fin batch: {nom_batch} ===")
    logger.info(f"  Résumé: {stats.summary()}")
    if stats.error_details:
        logger.warning(f"  Erreurs: {stats.error_details[:5]}")

# Utilisation
with batch_processor("Import clients") as stats:
    for record in records:
        try:
            process(record)
            stats.record_success()
        except Exception as e:
            stats.record_error(e)
```
</details>

---

## 5. Performance et optimisation Python

### Définitions

- **Vectorisation** : Opérations sur des tableaux entiers au lieu de boucles
- **Profiling** : Mesure du temps passé dans chaque fonction
- **Multiprocessing** : Parallélisme réel (contourne le GIL)
- **Threading** : Concurrence (bon pour I/O, pas pour CPU)

### Exemples détaillés

**Profiling avec cProfile et timeit :**
```python
import cProfile
import timeit

# cProfile : profiler une fonction
def traitement_lourd(n):
    result = []
    for i in range(n):
        result.append(sum(range(i)))
    return result

cProfile.run('traitement_lourd(1000)')

# timeit : mesurer le temps précis d'un snippet
temps_boucle = timeit.timeit(
    'sum([x**2 for x in range(1000)])',
    number=10000
)
temps_numpy = timeit.timeit(
    'np.sum(np.arange(1000)**2)',
    setup='import numpy as np',
    number=10000
)
print(f"Boucle: {temps_boucle:.3f}s, NumPy: {temps_numpy:.3f}s")
```

**Vectorisation Pandas vs boucles :**
```python
import pandas as pd
import numpy as np

df = pd.DataFrame({
    'a': np.random.randint(1, 100, 1_000_000),
    'b': np.random.randint(1, 100, 1_000_000)
})

# ❌ LENT : boucle avec iterrows
def calcul_lent(df):
    results = []
    for _, row in df.iterrows():
        results.append(row['a'] ** 2 + row['b'] * 3)
    return results

# ❌ MOYEN : apply
def calcul_apply(df):
    return df.apply(lambda row: row['a'] ** 2 + row['b'] * 3, axis=1)

# ✅ RAPIDE : vectorisation Pandas
def calcul_vectorise(df):
    return df['a'] ** 2 + df['b'] * 3

# ✅ TRÈS RAPIDE : vectorisation NumPy
def calcul_numpy(df):
    return np.power(df['a'].values, 2) + df['b'].values * 3

# Comparaison approximative pour 1M lignes :
# iterrows: ~30s | apply: ~8s | Pandas vectorisé: ~0.01s | NumPy: ~0.005s
```

**Multiprocessing pour data pipelines :**
```python
from multiprocessing import Pool
from functools import partial
import pandas as pd

def traiter_fichier(filepath, seuil=0):
    """Traiter un fichier individuellement (exécuté dans un process séparé)."""
    df = pd.read_csv(filepath)
    df = df[df['montant'] > seuil]
    df['montant_normalise'] = (df['montant'] - df['montant'].mean()) / df['montant'].std()
    return df

def pipeline_parallele(fichiers, seuil=100, nb_workers=4):
    """Traiter plusieurs fichiers en parallèle."""
    traiter = partial(traiter_fichier, seuil=seuil)

    with Pool(processes=nb_workers) as pool:
        resultats = pool.map(traiter, fichiers)

    return pd.concat(resultats, ignore_index=True)

# Utilisation
# fichiers = [f'data/part_{i}.csv' for i in range(20)]
# df_final = pipeline_parallele(fichiers, seuil=500, nb_workers=8)
```

### Exercices

**Exercice 1** : Réécrire cette fonction avec de la vectorisation Pandas :
```python
def categoriser(df):
    for i, row in df.iterrows():
        if row['age'] < 25:
            df.at[i, 'categorie'] = 'Junior'
        elif row['age'] < 40:
            df.at[i, 'categorie'] = 'Confirmé'
        else:
            df.at[i, 'categorie'] = 'Senior'
```

<details>
<summary>Solution</summary>

```python
def categoriser_vectorise(df):
    conditions = [
        df['age'] < 25,
        (df['age'] >= 25) & (df['age'] < 40),
        df['age'] >= 40
    ]
    choix = ['Junior', 'Confirmé', 'Senior']
    df['categorie'] = np.select(conditions, choix)
    return df

# Ou avec pd.cut :
def categoriser_cut(df):
    df['categorie'] = pd.cut(df['age'], bins=[0, 25, 40, 200],
                              labels=['Junior', 'Confirmé', 'Senior'], right=False)
    return df
```
</details>

**Exercice 2** : Écrire un script qui profile une fonction de traitement de données et affiche les 10 fonctions les plus lentes.

<details>
<summary>Solution</summary>

```python
import cProfile
import pstats
import io

def profiler_fonction(func, *args, **kwargs):
    """Profiler une fonction et afficher les 10 plus lentes."""
    profiler = cProfile.Profile()
    profiler.enable()

    result = func(*args, **kwargs)

    profiler.disable()

    # Formater les résultats
    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats('cumulative')
    stats.print_stats(10)

    print(stream.getvalue())
    return result

# Utilisation
# profiler_fonction(mon_traitement, df)
```
</details>

**Exercice 3** : Implémenter un traitement de données avec un générateur pour traiter 10 GB de données sans tout charger en mémoire.

<details>
<summary>Solution</summary>

```python
import csv
from collections import defaultdict

def stream_aggregate(filepath, group_col, value_col):
    """Agréger de gros fichiers en streaming sans charger en mémoire."""
    totaux = defaultdict(float)
    counts = defaultdict(int)

    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row[group_col]
            val = float(row[value_col])
            totaux[key] += val
            counts[key] += 1

    # Calculer les moyennes
    return {key: {'total': totaux[key], 'count': counts[key],
                   'moyenne': totaux[key] / counts[key]}
            for key in totaux}

# Utilisation : ne charge qu'une ligne à la fois
# stats = stream_aggregate('10gb_file.csv', 'region', 'montant')
```
</details>

---

## 6. Structures de données et algorithmes pour Data Engineers

### Définitions et exemples

**Collections spécialisées :**
```python
from collections import defaultdict, Counter, deque, OrderedDict

# defaultdict : dictionnaire avec valeur par défaut
transactions_par_client = defaultdict(list)
for txn in transactions:
    transactions_par_client[txn['client_id']].append(txn)

# Counter : compteur d'éléments
from collections import Counter
mots = ['python', 'sql', 'python', 'etl', 'sql', 'python']
compteur = Counter(mots)
print(compteur.most_common(2))  # [('python', 3), ('sql', 2)]

# deque : file double avec opérations O(1) aux extrémités
from collections import deque
fenetre_glissante = deque(maxlen=5)
for valeur in stream_de_donnees:
    fenetre_glissante.append(valeur)
    if len(fenetre_glissante) == 5:
        moyenne = sum(fenetre_glissante) / 5
```

**Compréhensions avancées :**
```python
# Dict comprehension avec condition
salaires_eleves = {e['nom']: e['salaire'] for e in employes if e['salaire'] > 80000}

# Nested comprehension (aplatissement)
matrice = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
plat = [val for ligne in matrice for val in ligne]  # [1,2,3,4,5,6,7,8,9]

# Set comprehension pour dédoublonnage
emails_uniques = {e['email'].lower().strip() for e in contacts if e.get('email')}

# Walrus operator (:=) Python 3.8+
resultats = [y for x in data if (y := transform(x)) is not None]
```

**Manipulation de dates :**
```python
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

# Calculs de dates
maintenant = datetime.now()
dans_30_jours = maintenant + timedelta(days=30)
il_y_a_3_mois = maintenant - relativedelta(months=3)
debut_trimestre = maintenant.replace(month=((maintenant.month - 1) // 3) * 3 + 1, day=1)

# Jours ouvrables
import numpy as np
jours_ouvres = np.busday_count('2026-01-01', '2026-04-01')

# Parsing de formats variés
from dateutil import parser
d1 = parser.parse("April 2, 2026")
d2 = parser.parse("02/04/2026", dayfirst=True)
d3 = parser.parse("2026-04-02T14:30:00-04:00")
```

**Regex pour parsing de données :**
```python
import re

# Extraire des montants d'un texte
texte = "Total: $1,234.56 USD, TVA: $185.18, Net: $1,049.38"
montants = re.findall(r'\$[\d,]+\.\d{2}', texte)
# ['$1,234.56', '$185.18', '$1,049.38']

# Parser un log structuré
log = "2026-04-02 14:30:05 [ERROR] Module: db_connector - Connection timeout after 30s"
pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[(\w+)\] Module: (\w+) - (.+)'
match = re.match(pattern, log)
if match:
    date, level, module, message = match.groups()

# Valider un email
def valider_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

# Nettoyer des données avec regex
def nettoyer_telephone(tel):
    """Extraire uniquement les chiffres d'un numéro de téléphone."""
    return re.sub(r'[^0-9]', '', tel)
# nettoyer_telephone("+1 (438) 865-6337") → "14388656337"
```

### Exercices

**Exercice 1** : Utiliser Counter et defaultdict pour analyser un log : compter les erreurs par module et par heure.

<details>
<summary>Solution</summary>

```python
from collections import Counter, defaultdict
import re

logs = [
    "2026-04-02 14:05:12 [ERROR] db_connector - Timeout",
    "2026-04-02 14:10:33 [ERROR] api_client - 503 error",
    "2026-04-02 14:15:44 [WARNING] db_connector - Slow query",
    "2026-04-02 15:05:12 [ERROR] db_connector - Timeout",
    "2026-04-02 15:20:33 [ERROR] etl_pipeline - File not found",
]

pattern = r'(\d{4}-\d{2}-\d{2} (\d{2}):\d{2}:\d{2}) \[(\w+)\] (\w+) - (.+)'

erreurs_par_module = Counter()
erreurs_par_heure = defaultdict(int)

for log in logs:
    match = re.match(pattern, log)
    if match and match.group(3) == 'ERROR':
        module = match.group(4)
        heure = match.group(2)
        erreurs_par_module[module] += 1
        erreurs_par_heure[heure] += 1

print("Erreurs par module:", erreurs_par_module.most_common())
print("Erreurs par heure:", dict(erreurs_par_heure))
```
</details>

**Exercice 2** : Implémenter une fenêtre glissante avec deque pour détecter les anomalies (valeur > 2 écarts-types de la moyenne glissante).

<details>
<summary>Solution</summary>

```python
from collections import deque
import math

def detecter_anomalies(flux_donnees, taille_fenetre=10, seuil_sigma=2):
    """Détection d'anomalies avec fenêtre glissante."""
    fenetre = deque(maxlen=taille_fenetre)
    anomalies = []

    for i, valeur in enumerate(flux_donnees):
        if len(fenetre) >= taille_fenetre:
            moyenne = sum(fenetre) / len(fenetre)
            variance = sum((x - moyenne) ** 2 for x in fenetre) / len(fenetre)
            ecart_type = math.sqrt(variance)

            if abs(valeur - moyenne) > seuil_sigma * ecart_type:
                anomalies.append({
                    'index': i,
                    'valeur': valeur,
                    'moyenne': round(moyenne, 2),
                    'ecart_type': round(ecart_type, 2),
                    'z_score': round((valeur - moyenne) / ecart_type, 2)
                })

        fenetre.append(valeur)

    return anomalies

# Test
import random
donnees = [random.gauss(100, 10) for _ in range(100)]
donnees[50] = 200  # Anomalie injectée
donnees[75] = 30   # Anomalie injectée

anomalies = detecter_anomalies(donnees)
for a in anomalies:
    print(a)
```
</details>

**Exercice 3** : Écrire un parser regex pour extraire les informations structurées d'un fichier de log Apache.

<details>
<summary>Solution</summary>

```python
import re
from collections import Counter

# Format Apache Common Log
log_lines = [
    '192.168.1.1 - admin [02/Apr/2026:14:30:05 +0000] "GET /api/users HTTP/1.1" 200 1234',
    '10.0.0.5 - - [02/Apr/2026:14:30:06 +0000] "POST /api/data HTTP/1.1" 201 567',
    '192.168.1.1 - admin [02/Apr/2026:14:30:07 +0000] "GET /api/users/1 HTTP/1.1" 404 89',
]

pattern = r'(\S+) \S+ (\S+) \[(.+?)\] "(\w+) (\S+) \S+" (\d{3}) (\d+)'

parsed_logs = []
for line in log_lines:
    match = re.match(pattern, line)
    if match:
        parsed_logs.append({
            'ip': match.group(1),
            'user': match.group(2),
            'datetime': match.group(3),
            'method': match.group(4),
            'path': match.group(5),
            'status': int(match.group(6)),
            'size': int(match.group(7))
        })

# Analyses
status_counts = Counter(log['status'] for log in parsed_logs)
ip_counts = Counter(log['ip'] for log in parsed_logs)
erreurs_404 = [log for log in parsed_logs if log['status'] == 404]

print(f"Status codes: {status_counts}")
print(f"IPs: {ip_counts}")
print(f"404 errors: {erreurs_404}")
```
</details>

**Exercice 4** : Calculer le nombre de jours ouvrables entre deux dates en excluant les jours fériés du Québec.

<details>
<summary>Solution</summary>

```python
from datetime import date, timedelta

FERIES_QC_2026 = [
    date(2026, 1, 1),   # Jour de l'An
    date(2026, 4, 3),   # Vendredi Saint
    date(2026, 5, 18),  # Journée nationale des patriotes
    date(2026, 6, 24),  # Saint-Jean-Baptiste
    date(2026, 7, 1),   # Fête du Canada
    date(2026, 9, 7),   # Fête du Travail
    date(2026, 10, 12), # Action de grâce
    date(2026, 12, 25), # Noël
]

def jours_ouvrables(debut, fin, feries=None):
    """Calculer le nombre de jours ouvrables entre deux dates."""
    if feries is None:
        feries = []
    feries_set = set(feries)

    count = 0
    current = debut
    while current <= fin:
        # Vérifier si c'est un jour de semaine (0=lun, 6=dim)
        if current.weekday() < 5 and current not in feries_set:
            count += 1
        current += timedelta(days=1)
    return count

# Test
debut = date(2026, 4, 1)
fin = date(2026, 4, 30)
print(f"Jours ouvrables avril 2026: {jours_ouvrables(debut, fin, FERIES_QC_2026)}")
```
</details>

**Exercice 5** : Implémenter un dédoublonnage intelligent de contacts (noms similaires avec fautes de frappe) en utilisant la distance de Levenshtein.

<details>
<summary>Solution</summary>

```python
def levenshtein(s1, s2):
    """Calculer la distance de Levenshtein entre deux chaînes."""
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def dedoublonner_contacts(contacts, seuil=2):
    """Regrouper les contacts avec noms similaires."""
    groupes = []
    utilises = set()

    for i, c1 in enumerate(contacts):
        if i in utilises:
            continue
        groupe = [c1]
        utilises.add(i)

        for j, c2 in enumerate(contacts):
            if j in utilises:
                continue
            if levenshtein(c1['nom'].lower(), c2['nom'].lower()) <= seuil:
                groupe.append(c2)
                utilises.add(j)

        groupes.append(groupe)

    return groupes

# Test
contacts = [
    {'nom': 'Jean Dupont', 'email': 'jean@mail.com'},
    {'nom': 'Jean Dupon', 'email': 'jdupont@mail.com'},   # faute
    {'nom': 'Marie Martin', 'email': 'marie@mail.com'},
    {'nom': 'Marie Martine', 'email': 'mmartine@mail.com'}, # variante
    {'nom': 'Pierre Bernard', 'email': 'pierre@mail.com'},
]

groupes = dedoublonner_contacts(contacts)
for i, g in enumerate(groupes):
    print(f"Groupe {i+1}: {[c['nom'] for c in g]}")
```
</details>

---

## 7. Connexion aux bases de données

### Définitions

- **snowflake-connector-python** : Connecteur officiel Snowflake
- **SQLAlchemy** : ORM et toolkit SQL universel
- **psycopg2** : Connecteur PostgreSQL
- **Bulk insert** : Insertion de masse pour la performance

### Exemples détaillés

**Snowflake Connector :**
```python
import snowflake.connector
import pandas as pd

# Connexion
conn = snowflake.connector.connect(
    user='mon_user',
    password='mon_password',
    account='mon_compte',
    warehouse='COMPUTE_WH',
    database='MA_DB',
    schema='PUBLIC',
    role='DATA_ENGINEER'
)

try:
    # Exécuter une requête
    cur = conn.cursor()
    cur.execute("SELECT * FROM clients WHERE region = %s LIMIT 100", ('Montreal',))

    # Récupérer les résultats en DataFrame
    df = cur.fetch_pandas_all()

    # Exécution de requêtes DDL
    cur.execute("""
        CREATE TABLE IF NOT EXISTS staging.raw_data (
            id INT AUTOINCREMENT,
            data VARIANT,
            loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
        )
    """)

    # Écrire un DataFrame dans Snowflake
    from snowflake.connector.pandas_tools import write_pandas
    success, nchunks, nrows, _ = write_pandas(
        conn, df, 'MA_TABLE',
        database='MA_DB', schema='PUBLIC',
        auto_create_table=True
    )
    print(f"Chargé: {nrows} lignes en {nchunks} chunks")

finally:
    conn.close()
```

**SQLAlchemy pattern :**
```python
from sqlalchemy import create_engine, text
import pandas as pd

# Création du moteur (pool de connexions)
engine = create_engine(
    'snowflake://user:password@account/database/schema?warehouse=COMPUTE_WH',
    pool_size=5,
    max_overflow=10,
    pool_timeout=30
)

# Lecture avec pandas
df = pd.read_sql(
    "SELECT * FROM ventes WHERE date_vente >= :date_debut",
    engine,
    params={'date_debut': '2025-01-01'}
)

# Écriture bulk
df.to_sql('ma_table', engine, if_exists='append', index=False,
          method='multi', chunksize=5000)

# Exécution de requêtes avec context manager
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM ventes"))
    count = result.scalar()
    print(f"Total: {count} lignes")
```

**Bulk insert optimisé :**
```python
import snowflake.connector
import tempfile
import os

def bulk_insert_snowflake(conn, df, table_name, stage_name='@~'):
    """Insertion en masse via stage interne Snowflake."""
    # 1. Sauvegarder en CSV temporaire
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
        df.to_csv(f, index=False, header=False)
        temp_path = f.name

    try:
        cur = conn.cursor()

        # 2. Upload vers le stage interne
        cur.execute(f"PUT file://{temp_path} {stage_name}")

        # 3. COPY INTO la table
        cur.execute(f"""
            COPY INTO {table_name}
            FROM {stage_name}/{os.path.basename(temp_path)}
            FILE_FORMAT = (TYPE = 'CSV' SKIP_HEADER = 0)
            ON_ERROR = 'CONTINUE'
        """)

        result = cur.fetchall()
        print(f"Bulk insert: {result}")
    finally:
        os.unlink(temp_path)
```

### Exercices

**Exercice 1** : Écrire une fonction qui exécute une requête Snowflake avec retry et renvoie un DataFrame.

<details>
<summary>Solution</summary>

```python
import snowflake.connector
import pandas as pd
import time
import logging

logger = logging.getLogger(__name__)

def query_snowflake(config, sql, params=None, max_retries=3):
    """Exécuter une requête Snowflake avec retry et retourner un DataFrame."""
    for attempt in range(1, max_retries + 1):
        conn = None
        try:
            conn = snowflake.connector.connect(**config)
            cur = conn.cursor()

            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)

            df = cur.fetch_pandas_all()
            logger.info(f"Requête OK: {len(df)} lignes retournées")
            return df

        except snowflake.connector.errors.OperationalError as e:
            logger.warning(f"Tentative {attempt}/{max_retries}: {e}")
            if attempt < max_retries:
                time.sleep(2 ** attempt)
            else:
                raise
        finally:
            if conn:
                conn.close()
```
</details>

**Exercice 2** : Implémenter un pipeline qui lit depuis PostgreSQL et écrit dans Snowflake en utilisant SQLAlchemy.

<details>
<summary>Solution</summary>

```python
from sqlalchemy import create_engine
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def migration_pg_to_snowflake(pg_config, sf_config, table_name, batch_size=10000):
    """Migrer une table de PostgreSQL vers Snowflake."""
    pg_engine = create_engine(
        f"postgresql://{pg_config['user']}:{pg_config['password']}"
        f"@{pg_config['host']}:{pg_config['port']}/{pg_config['database']}"
    )

    sf_engine = create_engine(
        f"snowflake://{sf_config['user']}:{sf_config['password']}"
        f"@{sf_config['account']}/{sf_config['database']}/{sf_config['schema']}"
        f"?warehouse={sf_config['warehouse']}"
    )

    # Lire par batch depuis PostgreSQL
    total_rows = 0
    for chunk in pd.read_sql(f"SELECT * FROM {table_name}",
                              pg_engine, chunksize=batch_size):
        chunk.to_sql(table_name, sf_engine, if_exists='append',
                     index=False, method='multi')
        total_rows += len(chunk)
        logger.info(f"  Migré: {total_rows} lignes")

    logger.info(f"Migration terminée: {total_rows} lignes au total")
    return total_rows
```
</details>

**Exercice 3** : Créer un gestionnaire de connexion thread-safe pour un pool de connexions Snowflake.

<details>
<summary>Solution</summary>

```python
import snowflake.connector
from queue import Queue
from threading import Lock
import logging

logger = logging.getLogger(__name__)

class SnowflakePool:
    """Pool de connexions Snowflake thread-safe."""

    def __init__(self, config, pool_size=5):
        self.config = config
        self.pool = Queue(maxsize=pool_size)
        self.lock = Lock()

        # Pré-créer les connexions
        for _ in range(pool_size):
            conn = snowflake.connector.connect(**config)
            self.pool.put(conn)

        logger.info(f"Pool créé avec {pool_size} connexions")

    def get_connection(self, timeout=30):
        """Obtenir une connexion du pool."""
        return self.pool.get(timeout=timeout)

    def release_connection(self, conn):
        """Remettre une connexion dans le pool."""
        self.pool.put(conn)

    def execute(self, sql, params=None):
        """Exécuter une requête et retourner les résultats."""
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute(sql, params)
            return cur.fetchall()
        finally:
            self.release_connection(conn)

    def close_all(self):
        """Fermer toutes les connexions du pool."""
        while not self.pool.empty():
            conn = self.pool.get_nowait()
            conn.close()
        logger.info("Pool fermé")
```
</details>

---

## 8. Exercices de synthèse type HackerRank

### Exercice HackerRank 1 : Réconciliation de données (Medium - 12 min)

**Énoncé** : Vous recevez deux fichiers CSV — `source.csv` et `target.csv` — avec les mêmes colonnes (id, nom, montant, date). Écrire une fonction qui identifie :
- Les enregistrements présents dans source mais pas dans target (ajouts)
- Les enregistrements présents dans target mais pas dans source (suppressions)
- Les enregistrements présents dans les deux mais avec des valeurs différentes (modifications)

La fonction doit retourner un dictionnaire avec les clés 'ajouts', 'suppressions', 'modifications'.

<details>
<summary>Solution</summary>

```python
import pandas as pd

def reconcilier(source_path, target_path, cle='id'):
    source = pd.read_csv(source_path)
    target = pd.read_csv(target_path)

    merged = pd.merge(source, target, on=cle, how='outer',
                       suffixes=('_src', '_tgt'), indicator=True)

    ajouts = merged[merged['_merge'] == 'left_only'][source.columns].to_dict('records')
    suppressions = merged[merged['_merge'] == 'right_only']

    # Reconstruire les colonnes target
    tgt_cols = {f"{c}_tgt": c for c in target.columns if c != cle}
    suppressions = suppressions.rename(columns=tgt_cols)[target.columns].to_dict('records')

    # Modifications : présent des deux côtés mais différent
    both = merged[merged['_merge'] == 'both']
    modifications = []
    for col in source.columns:
        if col == cle:
            continue
        diff = both[both[f'{col}_src'] != both[f'{col}_tgt']]
        for _, row in diff.iterrows():
            modifications.append({
                'id': row[cle],
                'colonne': col,
                'valeur_source': row[f'{col}_src'],
                'valeur_target': row[f'{col}_tgt']
            })

    return {
        'ajouts': ajouts,
        'suppressions': suppressions,
        'modifications': modifications
    }
```
</details>

### Exercice HackerRank 2 : Fenêtre glissante sur flux (Medium - 12 min)

**Énoncé** : Implémenter une classe `StreamProcessor` qui traite un flux de transactions en temps réel. Pour chaque transaction, calculer :
- La moyenne mobile des montants sur les 5 dernières transactions du même client
- Un flag `alerte` si le montant dépasse 2x la moyenne mobile

Input : liste de tuples (client_id, montant, timestamp)
Output : liste de dicts avec les champs calculés.

<details>
<summary>Solution</summary>

```python
from collections import defaultdict, deque

class StreamProcessor:
    def __init__(self, window_size=5, alert_multiplier=2.0):
        self.window_size = window_size
        self.alert_multiplier = alert_multiplier
        self.historique = defaultdict(lambda: deque(maxlen=window_size))

    def process(self, transactions):
        resultats = []

        for client_id, montant, timestamp in transactions:
            historique_client = self.historique[client_id]

            if len(historique_client) > 0:
                moyenne_mobile = sum(historique_client) / len(historique_client)
                alerte = montant > self.alert_multiplier * moyenne_mobile
            else:
                moyenne_mobile = montant
                alerte = False

            resultats.append({
                'client_id': client_id,
                'montant': montant,
                'timestamp': timestamp,
                'moyenne_mobile': round(moyenne_mobile, 2),
                'alerte': alerte
            })

            historique_client.append(montant)

        return resultats

# Test
transactions = [
    (1, 100, '2026-04-01 10:00'),
    (1, 110, '2026-04-01 10:05'),
    (2, 200, '2026-04-01 10:10'),
    (1, 105, '2026-04-01 10:15'),
    (1, 500, '2026-04-01 10:20'),  # Alerte attendue
    (2, 190, '2026-04-01 10:25'),
]

sp = StreamProcessor()
for r in sp.process(transactions):
    print(r)
```
</details>

### Exercice HackerRank 3 : Aplatissement de hiérarchie (Medium-Hard - 15 min)

**Énoncé** : À partir d'un fichier JSON représentant une hiérarchie d'employés (chaque employé peut avoir des `reports`), créer un DataFrame plat avec les colonnes : id, nom, niveau, manager_nom, chemin_complet.

<details>
<summary>Solution</summary>

```python
import pandas as pd

def aplatir_hierarchie(data, niveau=0, manager_nom=None, chemin=""):
    resultats = []

    for employe in data:
        chemin_courant = f"{chemin}/{employe['nom']}" if chemin else employe['nom']

        resultats.append({
            'id': employe['id'],
            'nom': employe['nom'],
            'niveau': niveau,
            'manager_nom': manager_nom,
            'chemin_complet': chemin_courant
        })

        if 'reports' in employe:
            sub_results = aplatir_hierarchie(
                employe['reports'], niveau + 1,
                employe['nom'], chemin_courant
            )
            resultats.extend(sub_results)

    return resultats

# Test
org = [
    {"id": 1, "nom": "CEO Martin", "reports": [
        {"id": 2, "nom": "VP Finance", "reports": [
            {"id": 4, "nom": "Dir Compta"},
            {"id": 5, "nom": "Dir Audit"}
        ]},
        {"id": 3, "nom": "VP IT", "reports": [
            {"id": 6, "nom": "Dev Lead", "reports": [
                {"id": 7, "nom": "Dev Sophie"},
                {"id": 8, "nom": "Dev Marc"}
            ]}
        ]}
    ]}
]

df = pd.DataFrame(aplatir_hierarchie(org))
print(df)
```
</details>

### Exercice HackerRank 4 : Pipeline ETL mini (Hard - 15 min)

**Énoncé** : Écrire un mini pipeline ETL qui :
1. Lit des transactions depuis une liste de dicts
2. Nettoie les données (supprime doublons, corrige les types, gère les NULL)
3. Enrichit avec un mapping de catégories
4. Agrège par catégorie et mois
5. Retourne le résultat trié

<details>
<summary>Solution</summary>

```python
import pandas as pd
import numpy as np

def pipeline_etl(transactions, mapping_categories):
    # EXTRACT
    df = pd.DataFrame(transactions)

    # TRANSFORM - Nettoyage
    df = df.drop_duplicates(subset=['txn_id'])
    df['montant'] = pd.to_numeric(df['montant'], errors='coerce')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['montant', 'date'])

    # TRANSFORM - Enrichissement
    cat_df = pd.DataFrame(list(mapping_categories.items()),
                           columns=['code_produit', 'categorie'])
    df = pd.merge(df, cat_df, on='code_produit', how='left')
    df['categorie'] = df['categorie'].fillna('Autre')

    # TRANSFORM - Agrégation
    df['mois'] = df['date'].dt.to_period('M')
    resultat = df.groupby(['categorie', 'mois']).agg(
        nb_transactions=('txn_id', 'count'),
        montant_total=('montant', 'sum'),
        montant_moyen=('montant', 'mean')
    ).reset_index()

    resultat = resultat.sort_values(['mois', 'montant_total'], ascending=[True, False])

    return resultat

# Test
transactions = [
    {'txn_id': 1, 'montant': '100.50', 'date': '2025-01-15', 'code_produit': 'A1'},
    {'txn_id': 2, 'montant': '200.00', 'date': '2025-01-20', 'code_produit': 'B1'},
    {'txn_id': 3, 'montant': 'invalid', 'date': '2025-02-10', 'code_produit': 'A1'},
    {'txn_id': 1, 'montant': '100.50', 'date': '2025-01-15', 'code_produit': 'A1'},  # doublon
    {'txn_id': 4, 'montant': '350.00', 'date': '2025-02-15', 'code_produit': 'C1'},
]
mapping = {'A1': 'Electronics', 'B1': 'Food', 'C1': 'Electronics'}

print(pipeline_etl(transactions, mapping))
```
</details>

### Exercice HackerRank 5 : Détection de sessions utilisateur (Hard - 15 min)

**Énoncé** : À partir d'un log d'événements (user_id, timestamp, action), regrouper les événements en sessions. Une session se termine si plus de 30 minutes s'écoulent entre deux événements du même utilisateur. Retourner pour chaque session : user_id, debut, fin, durée_minutes, nb_events.

<details>
<summary>Solution</summary>

```python
import pandas as pd

def detecter_sessions(events, timeout_minutes=30):
    df = pd.DataFrame(events)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(['user_id', 'timestamp'])

    # Calculer le temps depuis l'événement précédent du même user
    df['prev_ts'] = df.groupby('user_id')['timestamp'].shift(1)
    df['gap_minutes'] = (df['timestamp'] - df['prev_ts']).dt.total_seconds() / 60

    # Nouvelle session si gap > timeout ou premier événement
    df['new_session'] = (df['gap_minutes'] > timeout_minutes) | (df['gap_minutes'].isna())
    df['session_id'] = df.groupby('user_id')['new_session'].cumsum()

    # Agréger par session
    sessions = df.groupby(['user_id', 'session_id']).agg(
        debut=('timestamp', 'min'),
        fin=('timestamp', 'max'),
        nb_events=('action', 'count'),
        actions=('action', list)
    ).reset_index()

    sessions['duree_minutes'] = (sessions['fin'] - sessions['debut']).dt.total_seconds() / 60

    return sessions[['user_id', 'debut', 'fin', 'duree_minutes', 'nb_events', 'actions']]

# Test
events = [
    {'user_id': 1, 'timestamp': '2026-04-02 10:00:00', 'action': 'login'},
    {'user_id': 1, 'timestamp': '2026-04-02 10:05:00', 'action': 'view'},
    {'user_id': 1, 'timestamp': '2026-04-02 10:15:00', 'action': 'click'},
    {'user_id': 1, 'timestamp': '2026-04-02 11:00:00', 'action': 'login'},  # Nouvelle session
    {'user_id': 2, 'timestamp': '2026-04-02 10:00:00', 'action': 'login'},
    {'user_id': 2, 'timestamp': '2026-04-02 10:10:00', 'action': 'view'},
]

print(detecter_sessions(events))
```
</details>

---

> **Conseil pour le test** : Sur HackerRank, commencer par lire l'entrée standard (`input()`), utiliser `sys.stdin` pour les gros inputs. Penser à la complexité algorithmique — O(n log n) est souvent la cible. Pandas est généralement disponible sur HackerRank.
