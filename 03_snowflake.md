# Expert Snowflake — Préparation Morgan Stanley HackerRank

> **Objectif** : Maîtriser l'architecture Snowflake, le SQL spécifique, le chargement de données, les streams/tasks, l'API REST et l'optimisation pour un test de 60 minutes.

---

## 1. Architecture Snowflake

### Définitions complètes

Snowflake est un entrepôt de données cloud natif avec une architecture unique en **3 couches découplées** :

```
┌─────────────────────────────────────────────────┐
│              COUCHE CLOUD SERVICES               │
│  (Authentification, Metadata, Optimisation,      │
│   Parsing, Compilation, Sécurité, Transactions)  │
├─────────────────────────────────────────────────┤
│              COUCHE COMPUTE (Virtual Warehouses)  │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐        │
│  │ WH-1 │  │ WH-2 │  │ WH-3 │  │ WH-4 │        │
│  │ XS   │  │ M    │  │ L    │  │ XL   │        │
│  └──────┘  └──────┘  └──────┘  └──────┘        │
│  (Chaque WH = cluster indépendant de compute)   │
├─────────────────────────────────────────────────┤
│              COUCHE STORAGE                      │
│  ┌──────────────────────────────────────┐       │
│  │  Micro-partitions (columnar, compressé)│      │
│  │  Stockage cloud (S3/Azure Blob/GCS)    │      │
│  └──────────────────────────────────────┘       │
└─────────────────────────────────────────────────┘
```

#### Couche Storage (Stockage)
- Données stockées dans des **micro-partitions** (50-500 MB compressées)
- Format **colonaire** propriétaire, compressé automatiquement
- Stockage sur le cloud du provider (AWS S3, Azure Blob, GCP Cloud Storage)
- **Immuable** : chaque modification crée de nouvelles micro-partitions

#### Couche Compute (Virtual Warehouses)
- **Virtual Warehouse (VW)** : cluster de calcul indépendant
- Tailles : XS (1 serveur), S (2), M (4), L (8), XL (16), 2XL (32), 3XL (64), 4XL (128)
- **Chaque taille double le nombre de serveurs et le coût**
- **Auto-suspend** : s'arrête après N minutes d'inactivité (économies)
- **Auto-resume** : redémarre automatiquement à la prochaine requête
- **Multi-cluster** : scaling horizontal automatique (min/max clusters)
- Les VW ne partagent PAS de cache entre eux

#### Couche Cloud Services
- **Métadonnées** : catalogue d'objets, statistiques, historique de requêtes
- **Optimiseur de requêtes** : plan d'exécution, pruning
- **Sécurité** : authentification, autorisation, chiffrement
- **Gestion des transactions** : ACID complet
- Facturée si > 10% du compute total

### Micro-partitions et Clustering

```
Table "ventes" (100M lignes)
├── Micro-partition 1 (dates: 2024-01 à 2024-03, régions: Est, Nord)
├── Micro-partition 2 (dates: 2024-01 à 2024-02, régions: Ouest, Sud)
├── Micro-partition 3 (dates: 2024-04 à 2024-06, régions: Est, Nord)
├── ...
└── Micro-partition N

Requête: WHERE date_vente = '2024-05-15' AND region = 'Est'
→ Snowflake élimine (prune) les partitions qui ne contiennent pas ces valeurs
→ Seule la micro-partition 3 est lue (pruning efficace)
```

**Clustering Key** : Réorganise les micro-partitions selon les colonnes spécifiées.
```sql
ALTER TABLE ventes CLUSTER BY (date_vente, region);

-- Vérifier l'efficacité du clustering
SELECT SYSTEM$CLUSTERING_INFORMATION('ventes', '(date_vente, region)');
```

### Time Travel et Fail-safe

```
──────────────────────────────────────────────────────→ temps
│← données actuelles →│← Time Travel (0-90j) →│← Fail-safe (7j) →│

Time Travel : l'utilisateur peut requêter/restaurer
Fail-safe   : seul le support Snowflake peut restaurer
```

```sql
-- Requêter les données d'il y a 5 minutes
SELECT * FROM ma_table AT (OFFSET => -60*5);

-- Requêter les données à un moment précis
SELECT * FROM ma_table AT (TIMESTAMP => '2026-04-01 10:00:00'::TIMESTAMP);

-- Requêter avant une requête spécifique
SELECT * FROM ma_table BEFORE (STATEMENT => '01abc-def-ghij');

-- Restaurer une table supprimée
UNDROP TABLE ma_table;

-- Cloner à un point dans le temps (zero-copy)
CREATE TABLE ma_table_backup CLONE ma_table AT (TIMESTAMP => '2026-04-01'::TIMESTAMP);
```

### Data Sharing

```sql
-- Fournisseur : créer un partage
CREATE SHARE mon_partage;
GRANT USAGE ON DATABASE ma_db TO SHARE mon_partage;
GRANT USAGE ON SCHEMA ma_db.public TO SHARE mon_partage;
GRANT SELECT ON TABLE ma_db.public.ventes TO SHARE mon_partage;
ALTER SHARE mon_partage ADD ACCOUNTS = consumer_account;

-- Consommateur : utiliser le partage
CREATE DATABASE donnees_partagees FROM SHARE provider_account.mon_partage;
SELECT * FROM donnees_partagees.public.ventes;
```

### Rôles et sécurité (RBAC)

```
ACCOUNTADMIN
├── SYSADMIN (crée objets)
│   ├── DATA_ENGINEER_ROLE
│   └── ANALYST_ROLE
├── SECURITYADMIN (gère accès)
│   └── USERADMIN (gère utilisateurs)
└── PUBLIC (tous les utilisateurs)
```

```sql
-- Créer un rôle et assigner des privilèges
CREATE ROLE data_engineer;
GRANT USAGE ON WAREHOUSE compute_wh TO ROLE data_engineer;
GRANT USAGE ON DATABASE production_db TO ROLE data_engineer;
GRANT CREATE TABLE ON SCHEMA production_db.staging TO ROLE data_engineer;
GRANT SELECT ON ALL TABLES IN SCHEMA production_db.raw TO ROLE data_engineer;
GRANT ROLE data_engineer TO USER sacha;
```

### QCM rapide (10 questions)

**Q1** : Combien de serveurs un Virtual Warehouse de taille Large utilise-t-il ?
- a) 4  b) 8  c) 16  d) 32

<details><summary>Réponse</summary>b) 8 — XS=1, S=2, M=4, L=8, XL=16</details>

**Q2** : Le Time Travel Enterprise permet de remonter jusqu'à combien de jours ?
- a) 1  b) 7  c) 30  d) 90

<details><summary>Réponse</summary>d) 90 jours (Enterprise edition). Standard = 1 jour max.</details>

**Q3** : Quelle couche gère l'optimisation des requêtes ?
- a) Storage  b) Compute  c) Cloud Services  d) Aucune

<details><summary>Réponse</summary>c) Cloud Services — parsing, compilation, optimisation.</details>

**Q4** : Les micro-partitions ont quelle taille approximative (compressées) ?
- a) 1-5 MB  b) 50-500 MB  c) 1-5 GB  d) 10-50 GB

<details><summary>Réponse</summary>b) 50-500 MB compressées (16 MB non compressé par colonne par partition).</details>

**Q5** : Que se passe-t-il si on supprime accidentellement une table dans Snowflake ?
- a) Les données sont perdues définitivement
- b) On peut la restaurer avec UNDROP TABLE
- c) Il faut contacter le support
- d) Les données sont dans la corbeille Windows

<details><summary>Réponse</summary>b) UNDROP TABLE ma_table; — fonctionne pendant la période de Time Travel.</details>

**Q6** : Le Data Sharing copie-t-il physiquement les données vers le consommateur ?
- a) Oui, une copie complète est créée
- b) Non, c'est un partage en lecture sur les mêmes données
- c) Oui, mais de manière incrémentale
- d) Cela dépend de la taille

<details><summary>Réponse</summary>b) Non — zero-copy, le consommateur accède aux mêmes micro-partitions.</details>

**Q7** : Quel rôle devrait créer les bases de données et les schémas ?
- a) ACCOUNTADMIN  b) SYSADMIN  c) SECURITYADMIN  d) PUBLIC

<details><summary>Réponse</summary>b) SYSADMIN — responsable de la création et gestion des objets.</details>

**Q8** : Auto-suspend d'un warehouse à 5 minutes signifie que :
- a) Le warehouse s'éteint après 5 minutes d'inactivité
- b) Le warehouse fonctionne max 5 minutes
- c) Les requêtes timeout après 5 minutes
- d) Le warehouse redémarre toutes les 5 minutes

<details><summary>Réponse</summary>a) Le warehouse s'éteint après 5 minutes sans activité (pas de requête).</details>

**Q9** : Un clone Snowflake (CLONE) utilise :
- a) Le double d'espace de stockage
- b) Pas d'espace supplémentaire (zero-copy)
- c) 50% de l'espace original
- d) Espace proportionnel aux données lues

<details><summary>Réponse</summary>b) Zero-copy — pointe vers les mêmes micro-partitions. Le stockage n'augmente que pour les modifications ultérieures.</details>

**Q10** : Les caches dans Snowflake incluent :
- a) Result Cache uniquement
- b) Result Cache + Local Disk Cache + Remote Disk Cache
- c) Pas de cache, tout est recalculé
- d) Cache mémoire uniquement

<details><summary>Réponse</summary>b) Trois niveaux : Result Cache (24h, couche Cloud Services), Local Disk Cache (SSD du warehouse), Remote Disk Cache (stockage cloud).</details>

---

## 2. SQL spécifique Snowflake

### Types semi-structurés

```sql
-- VARIANT : peut contenir n'importe quel type (JSON, XML, Avro, etc.)
CREATE TABLE events (
    event_id INT AUTOINCREMENT,
    event_data VARIANT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Insérer du JSON
INSERT INTO events (event_data)
SELECT PARSE_JSON('{
    "user_id": 42,
    "action": "login",
    "metadata": {
        "ip": "192.168.1.1",
        "browser": "Chrome",
        "os": "Windows"
    },
    "tags": ["web", "production"]
}');

-- Accéder aux champs
SELECT
    event_data:user_id::INT AS user_id,           -- Notation : (deux-points)
    event_data:action::STRING AS action,
    event_data:metadata.ip::STRING AS ip,          -- Sous-objet avec .
    event_data:metadata.browser::STRING AS browser,
    event_data:tags[0]::STRING AS premier_tag      -- Array avec [index]
FROM events;
```

### LATERAL FLATTEN

`FLATTEN` transforme un tableau (ARRAY) ou un objet (OBJECT) en lignes. `LATERAL` permet de référencer des colonnes de la table source.

```sql
-- Données JSON avec tableaux imbriqués
CREATE TABLE commandes_json (
    id INT,
    data VARIANT
);

INSERT INTO commandes_json
SELECT 1, PARSE_JSON('{
    "client": "Alice",
    "items": [
        {"produit": "Laptop", "prix": 1200, "quantite": 1},
        {"produit": "Souris", "prix": 25, "quantite": 2},
        {"produit": "Clavier", "prix": 75, "quantite": 1}
    ]
}');

INSERT INTO commandes_json
SELECT 2, PARSE_JSON('{
    "client": "Bob",
    "items": [
        {"produit": "Écran", "prix": 500, "quantite": 2}
    ]
}');

-- FLATTEN pour transformer les items en lignes
SELECT
    c.id AS commande_id,
    c.data:client::STRING AS client,
    f.value:produit::STRING AS produit,
    f.value:prix::NUMBER AS prix,
    f.value:quantite::INT AS quantite,
    f.value:prix::NUMBER * f.value:quantite::INT AS sous_total
FROM commandes_json c,
LATERAL FLATTEN(input => c.data:items) f;

-- Résultat :
-- 1 | Alice | Laptop  | 1200 | 1 | 1200
-- 1 | Alice | Souris  | 25   | 2 | 50
-- 1 | Alice | Clavier | 75   | 1 | 75
-- 2 | Bob   | Écran   | 500  | 2 | 1000
```

**FLATTEN sur JSON doublement imbriqué :**
```sql
-- JSON avec commandes > items > options
INSERT INTO commandes_json
SELECT 3, PARSE_JSON('{
    "client": "Charlie",
    "items": [
        {"produit": "PC", "options": [
            {"nom": "RAM 32GB", "prix": 150},
            {"nom": "SSD 1TB", "prix": 200}
        ]}
    ]
}');

-- Double FLATTEN
SELECT
    c.data:client::STRING AS client,
    items.value:produit::STRING AS produit,
    options.value:nom::STRING AS option_nom,
    options.value:prix::NUMBER AS option_prix
FROM commandes_json c,
LATERAL FLATTEN(input => c.data:items) items,
LATERAL FLATTEN(input => items.value:options) options;
```

### QUALIFY

`QUALIFY` filtre les résultats **après** les fonctions de fenêtrage. Équivalent d'un `WHERE` sur le résultat d'une window function, sans sous-requête.

```sql
-- Sans QUALIFY (sous-requête nécessaire)
SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY departement ORDER BY salaire DESC) AS rn
    FROM employes
) WHERE rn <= 3;

-- Avec QUALIFY (syntaxe Snowflake — plus concis)
SELECT *
FROM employes
QUALIFY ROW_NUMBER() OVER (PARTITION BY departement ORDER BY salaire DESC) <= 3;

-- QUALIFY avec DENSE_RANK
SELECT departement, nom, salaire
FROM employes
QUALIFY DENSE_RANK() OVER (PARTITION BY departement ORDER BY salaire DESC) = 1;
-- Retourne tous les employés avec le salaire le plus élevé par département
```

### Autres fonctions spécifiques

```sql
-- SAMPLE / TABLESAMPLE : échantillonnage
SELECT * FROM grande_table SAMPLE (10);          -- 10% des lignes
SELECT * FROM grande_table TABLESAMPLE (1000 ROWS);  -- 1000 lignes

-- RESULT_SCAN : requêter le résultat de la dernière requête
SHOW TABLES IN SCHEMA my_schema;
SELECT * FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()))
WHERE "rows" > 1000;

-- TRY_PARSE_JSON : ne lève pas d'erreur si le JSON est invalide
SELECT TRY_PARSE_JSON('{"valide": true}');   -- OK
SELECT TRY_PARSE_JSON('pas du json');         -- NULL (pas d'erreur)

-- OBJECT_CONSTRUCT : créer un objet JSON
SELECT OBJECT_CONSTRUCT('nom', 'Alice', 'age', 30, 'ville', 'Montreal');
-- {"age": 30, "nom": "Alice", "ville": "Montreal"}

-- ARRAY_CONSTRUCT : créer un tableau
SELECT ARRAY_CONSTRUCT(1, 2, 3, 4, 5);
-- [1, 2, 3, 4, 5]

-- ARRAY_AGG : agrégation en tableau
SELECT departement, ARRAY_AGG(nom) WITHIN GROUP (ORDER BY nom) AS employes
FROM employes
GROUP BY departement;

-- IFF : version concise de CASE WHEN
SELECT nom, IFF(salaire > 80000, 'Senior', 'Junior') AS niveau FROM employes;
```

### Exercices

**Exercice 1** : À partir d'une table `api_responses` avec une colonne VARIANT `payload`, extraire le nom du client, son email, et le nombre d'items dans sa commande.

```sql
-- payload = {"customer": {"name": "Alice", "email": "alice@mail.com"}, "items": [...]}
```

<details>
<summary>Solution</summary>

```sql
SELECT
    payload:customer.name::STRING AS nom_client,
    payload:customer.email::STRING AS email,
    ARRAY_SIZE(payload:items) AS nb_items
FROM api_responses;
```
</details>

**Exercice 2** : Avec LATERAL FLATTEN, transformer une table de logs JSON (chaque log contient un array `errors`) en une ligne par erreur.

<details>
<summary>Solution</summary>

```sql
SELECT
    l.log_id,
    l.data:timestamp::TIMESTAMP AS log_time,
    l.data:service::STRING AS service,
    f.index AS error_index,
    f.value:code::INT AS error_code,
    f.value:message::STRING AS error_message
FROM logs_json l,
LATERAL FLATTEN(input => l.data:errors) f
ORDER BY log_time, error_index;
```
</details>

**Exercice 3** : Utiliser QUALIFY pour trouver, par département, les 2 employés les plus récemment embauchés.

<details>
<summary>Solution</summary>

```sql
SELECT departement, nom, date_embauche, salaire
FROM employes
QUALIFY ROW_NUMBER() OVER (PARTITION BY departement ORDER BY date_embauche DESC) <= 2
ORDER BY departement, date_embauche DESC;
```
</details>

**Exercice 4** : Transformer un JSON contenant des paires clé-valeur dynamiques en lignes. Le JSON ressemble à `{"metrique_a": 10, "metrique_b": 25, "metrique_c": 7}`.

<details>
<summary>Solution</summary>

```sql
SELECT
    m.id,
    f.key AS nom_metrique,
    f.value::NUMBER AS valeur_metrique
FROM metriques m,
LATERAL FLATTEN(input => m.data) f
ORDER BY m.id, f.key;
```
</details>

**Exercice 5** : Combiner FLATTEN et QUALIFY pour trouver, pour chaque commande JSON, l'item le plus cher.

<details>
<summary>Solution</summary>

```sql
SELECT
    c.id AS commande_id,
    c.data:client::STRING AS client,
    f.value:produit::STRING AS produit,
    f.value:prix::NUMBER AS prix
FROM commandes_json c,
LATERAL FLATTEN(input => c.data:items) f
QUALIFY ROW_NUMBER() OVER (PARTITION BY c.id ORDER BY f.value:prix::NUMBER DESC) = 1;
```
</details>

---

## 3. Chargement de données (Data Loading)

### Stages

Un **stage** est un emplacement de stockage où les fichiers sont déposés avant d'être chargés dans Snowflake.

```sql
-- Stage interne (user stage)
PUT file:///tmp/data.csv @~;                     -- Upload vers user stage

-- Stage interne nommé
CREATE STAGE mon_stage;
PUT file:///tmp/data.csv @mon_stage;

-- Stage externe S3
CREATE STAGE s3_stage
    URL = 's3://mon-bucket/data/'
    CREDENTIALS = (AWS_KEY_ID = 'xxx' AWS_SECRET_KEY = 'yyy');

-- Stage externe Azure
CREATE STAGE azure_stage
    URL = 'azure://moncompte.blob.core.windows.net/container/path/'
    CREDENTIALS = (AZURE_SAS_TOKEN = 'xxx');

-- Lister les fichiers d'un stage
LIST @mon_stage;
LIST @s3_stage/2026/;
```

### COPY INTO

```sql
-- File format réutilisable
CREATE FILE FORMAT mon_csv
    TYPE = 'CSV'
    FIELD_DELIMITER = ','
    SKIP_HEADER = 1
    NULL_IF = ('NULL', 'null', '')
    EMPTY_FIELD_AS_NULL = TRUE
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE;

CREATE FILE FORMAT mon_json
    TYPE = 'JSON'
    STRIP_OUTER_ARRAY = TRUE;

CREATE FILE FORMAT mon_parquet
    TYPE = 'PARQUET';

-- COPY INTO depuis un stage
COPY INTO ma_table
FROM @mon_stage/data/
FILE_FORMAT = (FORMAT_NAME = 'mon_csv')
PATTERN = '.*\.csv'
ON_ERROR = 'CONTINUE'           -- CONTINUE, SKIP_FILE, ABORT_STATEMENT
FORCE = FALSE                    -- FALSE = ne recharge pas les fichiers déjà chargés
PURGE = TRUE;                    -- Supprimer les fichiers après chargement

-- COPY INTO avec transformation (SELECT)
COPY INTO ma_table (col1, col2, col3)
FROM (
    SELECT
        $1::INT,                  -- $1 = première colonne du fichier
        $2::STRING,
        CURRENT_TIMESTAMP()
    FROM @mon_stage/data.csv
)
FILE_FORMAT = (TYPE = 'CSV' SKIP_HEADER = 1);

-- COPY INTO depuis JSON
COPY INTO events_raw
FROM @mon_stage/events/
FILE_FORMAT = (FORMAT_NAME = 'mon_json');

-- Décharger des données (COPY INTO stage)
COPY INTO @mon_stage/export/
FROM (SELECT * FROM ma_table WHERE date >= '2026-01-01')
FILE_FORMAT = (TYPE = 'PARQUET')
HEADER = TRUE;
```

### Snowpipe (chargement continu)

```sql
-- Créer un pipe pour chargement automatique
CREATE PIPE mon_pipe
    AUTO_INGEST = TRUE
AS
COPY INTO ma_table
FROM @s3_stage/incoming/
FILE_FORMAT = (FORMAT_NAME = 'mon_csv');

-- Vérifier le statut du pipe
SELECT SYSTEM$PIPE_STATUS('mon_pipe');

-- Voir l'historique de chargement
SELECT *
FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
    TABLE_NAME => 'ma_table',
    START_TIME => DATEADD(HOURS, -24, CURRENT_TIMESTAMP())
));
```

### Exercices

**Exercice 1** : Écrire les commandes pour charger un fichier CSV depuis S3 dans une table staging, avec gestion des erreurs.

<details>
<summary>Solution</summary>

```sql
-- 1. Créer le stage externe
CREATE OR REPLACE STAGE s3_data_stage
    URL = 's3://ms-data-lake/raw/clients/'
    CREDENTIALS = (AWS_KEY_ID = 'AKIAXXXXXXXX' AWS_SECRET_KEY = 'xxxxx');

-- 2. Créer le file format
CREATE OR REPLACE FILE FORMAT csv_clients
    TYPE = 'CSV'
    FIELD_DELIMITER = ','
    SKIP_HEADER = 1
    NULL_IF = ('NULL', '', 'N/A')
    DATE_FORMAT = 'YYYY-MM-DD'
    FIELD_OPTIONALLY_ENCLOSED_BY = '"';

-- 3. Créer la table staging
CREATE OR REPLACE TABLE staging.raw_clients (
    client_id INT,
    nom VARCHAR(100),
    email VARCHAR(200),
    date_inscription DATE,
    segment VARCHAR(20),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- 4. Charger avec validation
COPY INTO staging.raw_clients (client_id, nom, email, date_inscription, segment)
FROM @s3_data_stage
FILE_FORMAT = (FORMAT_NAME = 'csv_clients')
ON_ERROR = 'SKIP_FILE'
VALIDATION_MODE = 'RETURN_ERRORS';  -- Valider d'abord

-- 5. Charger pour de vrai
COPY INTO staging.raw_clients (client_id, nom, email, date_inscription, segment)
FROM @s3_data_stage
FILE_FORMAT = (FORMAT_NAME = 'csv_clients')
ON_ERROR = 'CONTINUE';

-- 6. Vérifier le résultat
SELECT COUNT(*) FROM staging.raw_clients;
```
</details>

**Exercice 2** : Charger des fichiers Parquet depuis Azure Blob et les transformer pendant le chargement.

<details>
<summary>Solution</summary>

```sql
CREATE OR REPLACE STAGE azure_parquet_stage
    URL = 'azure://msdata.blob.core.windows.net/datalake/transactions/'
    CREDENTIALS = (AZURE_SAS_TOKEN = 'sv=2021...');

COPY INTO analytics.transactions (txn_id, client_id, montant, date_txn, region)
FROM (
    SELECT
        $1:txn_id::INT,
        $1:client_id::INT,
        $1:amount::DECIMAL(12,2),
        $1:transaction_date::TIMESTAMP,
        UPPER($1:region::STRING)
    FROM @azure_parquet_stage
)
FILE_FORMAT = (TYPE = 'PARQUET')
PATTERN = '.*\.parquet';
```
</details>

**Exercice 3** : Créer un Snowpipe pour charger automatiquement les fichiers JSON qui arrivent dans un bucket S3.

<details>
<summary>Solution</summary>

```sql
-- 1. Stage
CREATE STAGE s3_events_stage
    URL = 's3://ms-events/incoming/'
    CREDENTIALS = (AWS_KEY_ID = 'xxx' AWS_SECRET_KEY = 'yyy');

-- 2. Table cible avec VARIANT
CREATE TABLE raw.events (
    event_id INT AUTOINCREMENT,
    raw_data VARIANT,
    source_file VARCHAR(500),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- 3. File format
CREATE FILE FORMAT json_events
    TYPE = 'JSON'
    STRIP_OUTER_ARRAY = TRUE;

-- 4. Pipe avec auto-ingest
CREATE PIPE events_pipe AUTO_INGEST = TRUE AS
COPY INTO raw.events (raw_data, source_file)
FROM (
    SELECT $1, METADATA$FILENAME
    FROM @s3_events_stage
)
FILE_FORMAT = (FORMAT_NAME = 'json_events');

-- 5. Récupérer l'ARN de notification pour configurer S3
SELECT SYSTEM$PIPE_STATUS('events_pipe');
```
</details>

---

## 4. Streams et Tasks

### Streams (Change Data Capture)

Un **stream** enregistre les changements (INSERT, UPDATE, DELETE) sur une table depuis le dernier offset consommé.

```sql
-- Créer un stream sur une table
CREATE STREAM mon_stream ON TABLE source_table;

-- Types de streams
CREATE STREAM append_stream ON TABLE logs APPEND_ONLY = TRUE;  -- Inserts uniquement
CREATE STREAM standard_stream ON TABLE clients;                 -- Tous les changements

-- Colonnes système du stream
SELECT
    *,
    METADATA$ACTION,      -- 'INSERT' ou 'DELETE'
    METADATA$ISUPDATE,    -- TRUE si c'est une UPDATE (INSERT + DELETE du même row)
    METADATA$ROW_ID       -- Identifiant unique de la ligne
FROM mon_stream;
```

**Comprendre les actions d'un stream :**
```
INSERT → METADATA$ACTION = 'INSERT', METADATA$ISUPDATE = FALSE
DELETE → METADATA$ACTION = 'DELETE', METADATA$ISUPDATE = FALSE
UPDATE → Deux lignes :
    1. METADATA$ACTION = 'DELETE', METADATA$ISUPDATE = TRUE  (ancienne valeur)
    2. METADATA$ACTION = 'INSERT', METADATA$ISUPDATE = TRUE  (nouvelle valeur)
```

### Tasks (Scheduling)

Une **task** exécute une instruction SQL selon un horaire (CRON ou intervalle).

```sql
-- Task simple avec intervalle
CREATE TASK traitement_quotidien
    WAREHOUSE = compute_wh
    SCHEDULE = 'USING CRON 0 6 * * * America/Montreal'  -- Chaque jour à 6h
AS
    INSERT INTO analytics.daily_summary
    SELECT DATE(transaction_date), SUM(amount), COUNT(*)
    FROM raw.transactions
    WHERE DATE(transaction_date) = CURRENT_DATE - 1
    GROUP BY DATE(transaction_date);

-- Task avec intervalle en minutes
CREATE TASK traitement_5min
    WAREHOUSE = compute_wh
    SCHEDULE = '5 MINUTE'
AS
    CALL process_new_data();

-- Chaîne de tasks (DAG)
CREATE TASK task_parent
    WAREHOUSE = compute_wh
    SCHEDULE = 'USING CRON 0 2 * * * America/Montreal'
AS SELECT 1;  -- Placeholder

CREATE TASK task_enfant_1
    WAREHOUSE = compute_wh
    AFTER task_parent
AS
    MERGE INTO dim_client ...;

CREATE TASK task_enfant_2
    WAREHOUSE = compute_wh
    AFTER task_parent
AS
    MERGE INTO dim_produit ...;

CREATE TASK task_final
    WAREHOUSE = compute_wh
    AFTER task_enfant_1, task_enfant_2  -- Attend que les deux soient terminées
AS
    INSERT INTO audit_log ...;

-- Activer les tasks (par défaut elles sont SUSPENDED)
ALTER TASK task_final RESUME;
ALTER TASK task_enfant_1 RESUME;
ALTER TASK task_enfant_2 RESUME;
ALTER TASK task_parent RESUME;  -- Activer le parent EN DERNIER
```

### Pattern CDC complet avec Stream + Task

```sql
-- 1. Table source
CREATE TABLE raw.clients (
    client_id INT,
    nom VARCHAR(100),
    ville VARCHAR(50),
    segment VARCHAR(20),
    updated_at TIMESTAMP
);

-- 2. Table dimension cible
CREATE TABLE analytics.dim_client (
    sk_client INT AUTOINCREMENT,
    client_id INT,
    nom VARCHAR(100),
    ville VARCHAR(50),
    segment VARCHAR(20),
    date_debut TIMESTAMP,
    date_fin TIMESTAMP DEFAULT '9999-12-31',
    est_courant BOOLEAN DEFAULT TRUE
);

-- 3. Stream sur la source
CREATE STREAM raw.clients_stream ON TABLE raw.clients;

-- 4. Task qui consomme le stream
CREATE TASK analytics.update_dim_client
    WAREHOUSE = etl_wh
    SCHEDULE = '5 MINUTE'
    WHEN SYSTEM$STREAM_HAS_DATA('raw.clients_stream')  -- Exécute SEULEMENT si le stream a des données
AS
BEGIN
    -- Fermer les anciens enregistrements modifiés
    UPDATE analytics.dim_client d
    SET d.date_fin = CURRENT_TIMESTAMP(), d.est_courant = FALSE
    WHERE d.est_courant = TRUE
    AND d.client_id IN (
        SELECT client_id FROM raw.clients_stream
        WHERE METADATA$ACTION = 'INSERT'
    );

    -- Insérer les nouvelles versions
    INSERT INTO analytics.dim_client (client_id, nom, ville, segment, date_debut)
    SELECT client_id, nom, ville, segment, CURRENT_TIMESTAMP()
    FROM raw.clients_stream
    WHERE METADATA$ACTION = 'INSERT';
END;

ALTER TASK analytics.update_dim_client RESUME;
```

### Exercices

**Exercice 1** : Créer un stream et une task pour maintenir une table `dim_produit` (SCD Type 1) à jour à partir de `raw.produits`.

<details>
<summary>Solution</summary>

```sql
CREATE STREAM raw.produits_stream ON TABLE raw.produits;

CREATE TASK analytics.sync_dim_produit
    WAREHOUSE = etl_wh
    SCHEDULE = '10 MINUTE'
    WHEN SYSTEM$STREAM_HAS_DATA('raw.produits_stream')
AS
    MERGE INTO analytics.dim_produit t
    USING (
        SELECT * FROM raw.produits_stream
        WHERE METADATA$ACTION = 'INSERT'
    ) s
    ON t.produit_id = s.produit_id
    WHEN MATCHED THEN
        UPDATE SET t.nom = s.nom, t.prix = s.prix, t.categorie = s.categorie,
                   t.date_maj = CURRENT_TIMESTAMP()
    WHEN NOT MATCHED THEN
        INSERT (produit_id, nom, prix, categorie, date_maj)
        VALUES (s.produit_id, s.nom, s.prix, s.categorie, CURRENT_TIMESTAMP());

ALTER TASK analytics.sync_dim_produit RESUME;
```
</details>

**Exercice 2** : Créer un DAG de 3 tasks : la première charge les données brutes, la deuxième les transforme, la troisième met à jour les agrégats.

<details>
<summary>Solution</summary>

```sql
-- Task racine : chargement
CREATE TASK etl.load_raw
    WAREHOUSE = etl_wh
    SCHEDULE = 'USING CRON 0 1 * * * America/Montreal'
AS
    COPY INTO raw.transactions FROM @s3_stage
    FILE_FORMAT = (FORMAT_NAME = 'csv_format');

-- Task enfant 1 : transformation
CREATE TASK etl.transform_data
    WAREHOUSE = etl_wh
    AFTER etl.load_raw
AS
    INSERT INTO staging.transactions_clean
    SELECT txn_id, client_id, ROUND(montant, 2), DATE(date_txn)
    FROM raw.transactions
    WHERE montant > 0 AND date_txn IS NOT NULL;

-- Task enfant 2 : agrégation
CREATE TASK etl.aggregate_daily
    WAREHOUSE = etl_wh
    AFTER etl.transform_data
AS
    MERGE INTO analytics.daily_summary t
    USING (
        SELECT DATE(date_txn) AS jour, COUNT(*) AS nb, SUM(montant) AS total
        FROM staging.transactions_clean
        GROUP BY DATE(date_txn)
    ) s ON t.jour = s.jour
    WHEN MATCHED THEN UPDATE SET t.nb = s.nb, t.total = s.total
    WHEN NOT MATCHED THEN INSERT VALUES (s.jour, s.nb, s.total);

-- Activer (du bas vers le haut)
ALTER TASK etl.aggregate_daily RESUME;
ALTER TASK etl.transform_data RESUME;
ALTER TASK etl.load_raw RESUME;
```
</details>

**Exercice 3** : Vérifier que les tasks fonctionnent correctement et consulter l'historique d'exécution.

<details>
<summary>Solution</summary>

```sql
-- Historique d'exécution des tasks
SELECT *
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
    TASK_NAME => 'LOAD_RAW',
    SCHEDULED_TIME_RANGE_START => DATEADD(DAY, -1, CURRENT_TIMESTAMP())
))
ORDER BY SCHEDULED_TIME DESC;

-- Vérifier si un stream a des données
SELECT SYSTEM$STREAM_HAS_DATA('raw.clients_stream');

-- Voir les données dans le stream
SELECT * FROM raw.clients_stream;

-- Exécuter manuellement une task pour test
EXECUTE TASK etl.load_raw;
```
</details>

---

## 5. Snowflake REST API

### Définitions

L'API REST Snowflake permet d'exécuter des requêtes SQL via HTTP, sans avoir besoin du connecteur natif.

**Endpoint principal** : `POST /api/v2/statements`

**Authentification :**
- **Key Pair** : Recommandé pour les applications (JWT)
- **OAuth** : Pour les intégrations SSO
- **Username/Password** : Non recommandé en production

### Exemples détaillés en Python

**Authentification par Key Pair (JWT) :**
```python
import jwt
import time
import hashlib
import base64
from cryptography.hazmat.primitives import serialization

def generer_jwt(account, user, private_key_path):
    """Générer un JWT pour l'API REST Snowflake."""
    # Charger la clé privée
    with open(private_key_path, 'rb') as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)

    # Qualified username
    account_upper = account.upper()
    user_upper = user.upper()
    qualified_username = f"{account_upper}.{user_upper}"

    # Fingerprint de la clé publique
    public_key = private_key.public_key()
    public_key_bytes = public_key.public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo
    )
    sha256_hash = hashlib.sha256(public_key_bytes).digest()
    public_key_fp = "SHA256:" + base64.b64encode(sha256_hash).decode('utf-8')

    # Générer le JWT
    now = int(time.time())
    payload = {
        "iss": f"{qualified_username}.{public_key_fp}",
        "sub": qualified_username,
        "iat": now,
        "exp": now + 3600  # Expire dans 1 heure
    }

    token = jwt.encode(payload, private_key, algorithm='RS256')
    return token
```

**Exécuter une requête via l'API REST :**
```python
import requests
import json
import time

class SnowflakeSQL:
    """Client pour l'API SQL REST Snowflake."""

    def __init__(self, account, jwt_token):
        self.base_url = f"https://{account}.snowflakecomputing.com"
        self.headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'MonApp/1.0',
            'X-Snowflake-Authorization-Token-Type': 'KEYPAIR_JWT'
        }

    def execute(self, sql, database=None, schema=None, warehouse=None,
                timeout=60, async_mode=False):
        """Exécuter une requête SQL."""
        url = f"{self.base_url}/api/v2/statements"
        payload = {
            "statement": sql,
            "timeout": timeout,
            "resultSetMetaData": {
                "format": "jsonv2"
            }
        }
        if database:
            payload["database"] = database
        if schema:
            payload["schema"] = schema
        if warehouse:
            payload["warehouse"] = warehouse

        params = {}
        if async_mode:
            params['async'] = 'true'

        response = requests.post(url, headers=self.headers,
                                  json=payload, params=params)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 202:
            # Requête asynchrone acceptée
            result = response.json()
            statement_handle = result['statementHandle']
            if async_mode:
                return {'statementHandle': statement_handle, 'status': 'running'}
            return self._wait_for_results(statement_handle)
        else:
            response.raise_for_status()

    def _wait_for_results(self, handle, max_wait=300):
        """Attendre et récupérer les résultats d'une requête asynchrone."""
        url = f"{self.base_url}/api/v2/statements/{handle}"
        start = time.time()

        while time.time() - start < max_wait:
            response = requests.get(url, headers=self.headers)
            result = response.json()

            status = result.get('statementStatusUrl')
            if status is None and 'data' in result:
                return result

            code = result.get('code')
            if code and code != '333334':  # 333334 = still running
                return result

            time.sleep(2)

        raise TimeoutError(f"Query {handle} timed out after {max_wait}s")

    def get_partitioned_results(self, handle):
        """Récupérer tous les résultats d'une requête avec plusieurs partitions."""
        url = f"{self.base_url}/api/v2/statements/{handle}"

        # Première requête pour les métadonnées
        response = requests.get(url, headers=self.headers)
        result = response.json()
        all_data = result.get('data', [])

        # Récupérer les partitions supplémentaires
        partitions = result.get('resultSetMetaData', {}).get('partitionInfo', [])
        for i in range(1, len(partitions)):
            part_url = f"{url}?partition={i}"
            part_response = requests.get(part_url, headers=self.headers)
            part_result = part_response.json()
            all_data.extend(part_result.get('data', []))

        return all_data, result.get('resultSetMetaData', {})

    def cancel(self, handle):
        """Annuler une requête en cours."""
        url = f"{self.base_url}/api/v2/statements/{handle}/cancel"
        response = requests.post(url, headers=self.headers)
        return response.json()


# Utilisation
sf = SnowflakeSQL('mon-compte', jwt_token)

# Requête synchrone
result = sf.execute(
    "SELECT departement, COUNT(*) as nb FROM employes GROUP BY departement",
    database="PROD_DB", schema="PUBLIC", warehouse="ANALYTICS_WH"
)

# Parcourir les résultats
colonnes = [col['name'] for col in result['resultSetMetaData']['rowType']]
for row in result['data']:
    print(dict(zip(colonnes, row)))

# Requête asynchrone
async_result = sf.execute(
    "SELECT * FROM grande_table",
    async_mode=True
)
handle = async_result['statementHandle']
# ... plus tard ...
data, metadata = sf.get_partitioned_results(handle)
```

### Exercices

**Exercice 1** : Écrire une fonction Python qui utilise l'API REST pour créer une table, insérer des données, et les requêter.

<details>
<summary>Solution</summary>

```python
def demo_api_rest(client, database, schema, warehouse):
    """Démonstration complète de l'API REST Snowflake."""

    # Créer une table
    client.execute(
        "CREATE OR REPLACE TABLE test_api (id INT, nom STRING, valeur FLOAT)",
        database=database, schema=schema, warehouse=warehouse
    )

    # Insérer des données
    client.execute(
        """INSERT INTO test_api VALUES
           (1, 'Alice', 100.5),
           (2, 'Bob', 200.3),
           (3, 'Charlie', 150.7)""",
        database=database, schema=schema, warehouse=warehouse
    )

    # Requêter
    result = client.execute(
        "SELECT * FROM test_api ORDER BY valeur DESC",
        database=database, schema=schema, warehouse=warehouse
    )

    colonnes = [c['name'] for c in result['resultSetMetaData']['rowType']]
    for row in result['data']:
        print(dict(zip(colonnes, row)))

    # Nettoyer
    client.execute("DROP TABLE test_api",
                    database=database, schema=schema, warehouse=warehouse)
```
</details>

**Exercice 2** : Implémenter une fonction qui exécute plusieurs requêtes en parallèle via l'API REST (mode asynchrone).

<details>
<summary>Solution</summary>

```python
import concurrent.futures
import time

def execute_parallel_queries(client, queries, database, schema, warehouse):
    """Exécuter plusieurs requêtes en parallèle via l'API REST."""
    # 1. Lancer toutes les requêtes en mode asynchrone
    handles = []
    for sql in queries:
        result = client.execute(sql, database=database, schema=schema,
                                warehouse=warehouse, async_mode=True)
        handles.append(result['statementHandle'])

    # 2. Attendre les résultats
    results = {}
    for i, handle in enumerate(handles):
        data, metadata = client.get_partitioned_results(handle)
        colonnes = [c['name'] for c in metadata.get('rowType', [])]
        results[i] = {'colonnes': colonnes, 'data': data}

    return results
```
</details>

**Exercice 3** : Créer une couche de distribution de données simple via l'API REST Snowflake (endpoint qui retourne des données filtrées en JSON).

<details>
<summary>Solution</summary>

```python
from flask import Flask, request, jsonify

app = Flask(__name__)
sf_client = None  # Initialisé au démarrage

@app.route('/api/data/<table_name>', methods=['GET'])
def get_data(table_name):
    """Endpoint REST qui requête Snowflake et retourne les résultats."""
    # Paramètres de filtrage
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    filters = request.args.get('filter', '')

    # Construire la requête
    sql = f"SELECT * FROM {table_name}"
    if filters:
        sql += f" WHERE {filters}"  # Attention : sanitiser en production !
    sql += f" LIMIT {limit} OFFSET {offset}"

    result = sf_client.execute(sql, database="PROD_DB",
                                schema="PUBLIC", warehouse="API_WH")

    colonnes = [c['name'] for c in result['resultSetMetaData']['rowType']]
    rows = [dict(zip(colonnes, row)) for row in result.get('data', [])]

    return jsonify({
        'data': rows,
        'count': len(rows),
        'limit': limit,
        'offset': offset
    })

# GET /api/data/clients?limit=50&offset=0&filter=segment='Gold'
```
</details>

---

## 6. Performance et optimisation

### Clustering Keys

```sql
-- Vérifier le clustering actuel
SELECT SYSTEM$CLUSTERING_INFORMATION('ventes', '(date_vente, region)');
-- Retourne : average_depth, total_partition_count, ...

-- Ajouter un clustering key
ALTER TABLE ventes CLUSTER BY (date_vente, region);

-- Reclustering automatique (activé par défaut)
-- Le reclustering est un processus en arrière-plan géré par Snowflake

-- Supprimer le clustering
ALTER TABLE ventes DROP CLUSTERING KEY;
```

**Quand utiliser le clustering :**
- Tables > 1 TB
- Requêtes fréquentes filtrant sur les mêmes colonnes
- Colonnes de cardinalité moyenne (dates, régions) — pas les IDs uniques

### Search Optimization Service

```sql
-- Activer sur une table
ALTER TABLE clients ADD SEARCH OPTIMIZATION;

-- Optimiser pour des colonnes spécifiques
ALTER TABLE clients ADD SEARCH OPTIMIZATION
ON EQUALITY(client_id, email);

-- Vérifier le statut
SELECT SYSTEM$ESTIMATE_SEARCH_OPTIMIZATION_COSTS('clients');

-- Bénéficie aux requêtes de type :
-- WHERE client_id = 12345
-- WHERE email = 'alice@mail.com'
-- WHERE data:field::STRING = 'value'  (semi-structuré)
```

### Materialized Views

```sql
CREATE MATERIALIZED VIEW mv_ventes_mensuelles AS
SELECT
    DATE_TRUNC('MONTH', date_vente) AS mois,
    region,
    SUM(montant) AS total,
    COUNT(*) AS nb_ventes
FROM ventes
GROUP BY DATE_TRUNC('MONTH', date_vente), region;

-- Automatiquement rafraîchie par Snowflake
-- Utilisée automatiquement par l'optimiseur si pertinente
```

### Caching

```
┌──────────────────────────────────────┐
│  1. Result Cache (Cloud Services)     │
│  - Résultat exact de la même requête  │
│  - Valable 24h si données inchangées  │
│  - Gratuit (pas de compute)           │
├──────────────────────────────────────┤
│  2. Local Disk Cache (Warehouse SSD)  │
│  - Données des micro-partitions lues  │
│  - Disponible tant que le WH est up   │
│  - Perdu si WH suspendu               │
├──────────────────────────────────────┤
│  3. Remote Disk Cache (Storage)       │
│  - Lecture depuis le stockage cloud   │
│  - Plus lent que le local disk cache  │
└──────────────────────────────────────┘
```

### Query Profile

```sql
-- Voir le profil de la dernière requête
SELECT * FROM TABLE(GET_QUERY_OPERATOR_STATS(LAST_QUERY_ID()));

-- Identifier les requêtes lentes
SELECT query_id, query_text, execution_time, rows_produced
FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY(
    DATE_RANGE_START => DATEADD(HOUR, -1, CURRENT_TIMESTAMP()),
    RESULT_LIMIT => 20
))
ORDER BY execution_time DESC;
```

### Bonnes pratiques

```sql
-- ✅ Utiliser QUALIFY au lieu de sous-requêtes
SELECT * FROM employes
QUALIFY ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salaire DESC) = 1;

-- ✅ Filtrer tôt (predicate pushdown)
SELECT * FROM ventes
WHERE date_vente >= '2026-01-01'  -- Filtre avant les jointures
AND region = 'Montreal';

-- ✅ Éviter SELECT *
SELECT client_id, montant, date_vente FROM ventes;

-- ✅ Choisir la bonne taille de warehouse
-- XS pour requêtes simples, L+ pour transformations lourdes
-- Scale UP pour requêtes complexes, Scale OUT pour concurrence

-- ✅ Utiliser des tables transitoires pour le staging
CREATE TRANSIENT TABLE staging.raw_data (...);
-- Pas de Fail-safe = moins de stockage

-- ❌ Éviter ORDER BY sans LIMIT sur les grandes tables
-- ❌ Éviter les UDF scalaires dans les WHERE (pas de pushdown)
-- ❌ Éviter CLUSTER BY sur des colonnes de haute cardinalité (IDs)
```

### Exercices

**Exercice 1** : Une requête sur une table de 500M lignes est lente. La table est filtrée sur `date_transaction` et `type_instrument`. Proposer une stratégie d'optimisation.

<details>
<summary>Solution</summary>

```sql
-- 1. Vérifier le clustering actuel
SELECT SYSTEM$CLUSTERING_INFORMATION('transactions');

-- 2. Ajouter un clustering key sur les colonnes de filtre
ALTER TABLE transactions CLUSTER BY (date_transaction, type_instrument);

-- 3. Vérifier le pruning
EXPLAIN
SELECT * FROM transactions
WHERE date_transaction >= '2026-01-01'
AND type_instrument = 'ACTION';

-- 4. Si des lookups par ID sont fréquents, ajouter Search Optimization
ALTER TABLE transactions ADD SEARCH OPTIMIZATION ON EQUALITY(txn_id);

-- 5. Pour les agrégations fréquentes, créer une Materialized View
CREATE MATERIALIZED VIEW mv_txn_daily AS
SELECT date_transaction, type_instrument,
       COUNT(*) AS nb, SUM(montant) AS total
FROM transactions
GROUP BY date_transaction, type_instrument;

-- 6. Ajuster la taille du warehouse si nécessaire
ALTER WAREHOUSE analytics_wh SET WAREHOUSE_SIZE = 'LARGE';
```
</details>

**Exercice 2** : Expliquer pourquoi cette requête n'utilise pas le Result Cache et comment la corriger.
```sql
SELECT *, CURRENT_TIMESTAMP() AS query_time FROM ventes WHERE region = 'EST';
```

<details>
<summary>Solution</summary>

```sql
-- Le Result Cache ne fonctionne pas car CURRENT_TIMESTAMP() change à chaque exécution
-- La requête n'est jamais identique

-- Solution : retirer la fonction non-déterministe
SELECT * FROM ventes WHERE region = 'EST';

-- Si on a besoin du timestamp, l'ajouter côté application, pas dans la requête SQL

-- Autres fonctions qui empêchent le cache :
-- CURRENT_DATE(), RANDOM(), UUID_STRING(), SEQ fonctions
```
</details>

**Exercice 3** : Concevoir la stratégie de warehouse sizing pour un système avec 3 profils d'utilisation : dashboard BI (beaucoup de petites requêtes concurrentes), ETL batch (grosses transformations), data science (requêtes exploratoires lourdes).

<details>
<summary>Solution</summary>

```sql
-- Warehouse BI : petit mais multi-cluster pour la concurrence
CREATE WAREHOUSE bi_wh
    WAREHOUSE_SIZE = 'SMALL'
    MIN_CLUSTER_COUNT = 1
    MAX_CLUSTER_COUNT = 4
    SCALING_POLICY = 'STANDARD'
    AUTO_SUSPEND = 120        -- 2 min (requêtes fréquentes)
    AUTO_RESUME = TRUE;

-- Warehouse ETL : grand pour les transformations lourdes
CREATE WAREHOUSE etl_wh
    WAREHOUSE_SIZE = 'XLARGE'
    MIN_CLUSTER_COUNT = 1
    MAX_CLUSTER_COUNT = 1     -- Pas besoin de multi-cluster (batch séquentiel)
    AUTO_SUSPEND = 60         -- 1 min (batch terminé → suspend)
    AUTO_RESUME = TRUE;

-- Warehouse Data Science : taille variable
CREATE WAREHOUSE ds_wh
    WAREHOUSE_SIZE = 'MEDIUM'
    MIN_CLUSTER_COUNT = 1
    MAX_CLUSTER_COUNT = 1
    AUTO_SUSPEND = 300        -- 5 min (exploration = pauses entre requêtes)
    AUTO_RESUME = TRUE;

-- Les data scientists peuvent redimensionner si besoin :
-- ALTER WAREHOUSE ds_wh SET WAREHOUSE_SIZE = 'XLARGE';
```
</details>

---

## 7. Gouvernance et sécurité des données

### Row Access Policies

```sql
-- Politique : les utilisateurs ne voient que les données de leur région
CREATE ROW ACCESS POLICY region_policy AS (region_val VARCHAR)
RETURNS BOOLEAN ->
    CURRENT_ROLE() = 'ADMIN'
    OR region_val = CURRENT_SESSION()::VARCHAR
    OR EXISTS (
        SELECT 1 FROM user_regions
        WHERE user_name = CURRENT_USER()
        AND region = region_val
    );

-- Appliquer la politique
ALTER TABLE ventes ADD ROW ACCESS POLICY region_policy ON (region);
```

### Dynamic Data Masking

```sql
-- Masquer les emails sauf pour les admins
CREATE MASKING POLICY email_mask AS (val STRING)
RETURNS STRING ->
    CASE
        WHEN CURRENT_ROLE() IN ('ADMIN', 'COMPLIANCE') THEN val
        ELSE REGEXP_REPLACE(val, '.+@', '***@')
    END;

ALTER TABLE clients MODIFY COLUMN email SET MASKING POLICY email_mask;

-- Masquer partiellement les numéros de carte
CREATE MASKING POLICY card_mask AS (val STRING)
RETURNS STRING ->
    CASE
        WHEN CURRENT_ROLE() = 'ADMIN' THEN val
        ELSE CONCAT('****-****-****-', RIGHT(val, 4))
    END;
```

### Tags et classification

```sql
-- Créer des tags
CREATE TAG pii_type ALLOWED_VALUES 'email', 'phone', 'ssn', 'name';
CREATE TAG data_sensitivity ALLOWED_VALUES 'public', 'internal', 'confidential', 'restricted';

-- Appliquer des tags
ALTER TABLE clients MODIFY COLUMN email SET TAG pii_type = 'email';
ALTER TABLE clients MODIFY COLUMN nom SET TAG pii_type = 'name';
ALTER TABLE clients SET TAG data_sensitivity = 'confidential';

-- Requêter les tags
SELECT * FROM TABLE(INFORMATION_SCHEMA.TAG_REFERENCES('clients', 'TABLE'));
```

### Access History

```sql
-- Voir qui a accédé à quelles données
SELECT
    query_id,
    user_name,
    direct_objects_accessed,
    base_objects_accessed
FROM SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY
WHERE query_start_time >= DATEADD(DAY, -7, CURRENT_TIMESTAMP())
ORDER BY query_start_time DESC
LIMIT 100;
```

### Exercices

**Exercice 1** : Créer une politique de masquage qui affiche le salaire complet pour les RH, arrondi au millier pour les managers, et '***' pour les autres.

<details>
<summary>Solution</summary>

```sql
CREATE MASKING POLICY salary_mask AS (val NUMBER)
RETURNS NUMBER ->
    CASE
        WHEN CURRENT_ROLE() IN ('HR_ADMIN', 'ACCOUNTADMIN') THEN val
        WHEN CURRENT_ROLE() = 'MANAGER' THEN ROUND(val, -3)
        ELSE NULL
    END;

ALTER TABLE employes MODIFY COLUMN salaire SET MASKING POLICY salary_mask;
```
</details>

**Exercice 2** : Configurer une Row Access Policy pour que les analystes de chaque département ne voient que les données de leur département.

<details>
<summary>Solution</summary>

```sql
-- Table de mapping utilisateur → département
CREATE TABLE admin.user_departments (
    username VARCHAR,
    departement VARCHAR
);

-- Politique
CREATE ROW ACCESS POLICY dept_access AS (dept VARCHAR)
RETURNS BOOLEAN ->
    CURRENT_ROLE() = 'ADMIN'
    OR dept IN (
        SELECT departement FROM admin.user_departments
        WHERE username = CURRENT_USER()
    );

ALTER TABLE employes ADD ROW ACCESS POLICY dept_access ON (departement);
ALTER TABLE ventes ADD ROW ACCESS POLICY dept_access ON (departement);
```
</details>

---

## 8. Migration RDBMS vers Snowflake

### Mapping des types de données

| DB2 | SQL Server | PostgreSQL | Snowflake |
|-----|-----------|------------|-----------|
| INTEGER | INT | INTEGER | NUMBER(38,0) |
| BIGINT | BIGINT | BIGINT | NUMBER(38,0) |
| DECIMAL(p,s) | DECIMAL(p,s) | NUMERIC(p,s) | NUMBER(p,s) |
| VARCHAR(n) | VARCHAR(n) | VARCHAR(n) | VARCHAR(n) |
| CHAR(n) | CHAR(n) | CHAR(n) | CHAR(n) |
| DATE | DATE | DATE | DATE |
| TIMESTAMP | DATETIME2 | TIMESTAMP | TIMESTAMP_NTZ |
| CLOB | NVARCHAR(MAX) | TEXT | VARCHAR(16MB) |
| BLOB | VARBINARY(MAX) | BYTEA | BINARY |
| XML | XML | XML | VARIANT |

### Stratégies de migration

```
1. BIG BANG          2. PARALLEL RUN       3. PHASED
┌──────┐            ┌──────┐              Phase 1    Phase 2    Phase 3
│ DB2  │ ──→ SF     │ DB2  │ ──→ les deux │ Table A │ Table B │ Table C │
└──────┘            │      │              │ → SF    │ → SF    │ → SF    │
Coupure nette       │ SF   │              
                    └──────┘
                    Validation
```

### Checklist de migration

```
□ Assessment
  □ Inventaire des tables, vues, procédures stockées
  □ Mapping des types de données
  □ Identification des dépendances
  □ Estimation du volume de données

□ Préparation Snowflake
  □ Création de la structure (databases, schemas)
  □ Configuration des rôles et permissions
  □ Configuration des warehouses
  □ Création des stages et file formats

□ Migration des données
  □ Export des données source (CSV, Parquet)
  □ Upload vers le stage
  □ COPY INTO les tables cibles
  □ Validation des row counts

□ Migration du code
  □ Conversion des procédures stockées → Snowflake Scripting/JavaScript
  □ Conversion des vues
  □ Adaptation des requêtes SQL (syntaxe spécifique)
  □ Migration des jobs ETL (scheduling → Tasks)

□ Validation
  □ Comparaison des row counts source vs cible
  □ Comparaison des checksums/agrégats
  □ Tests de performance
  □ Tests fonctionnels (rapports, dashboards)

□ Cutover
  □ Migration finale (données delta)
  □ Redirection des applications
  □ Monitoring post-migration
```

### Exercices

**Exercice 1** : Convertir cette procédure stockée DB2 en Snowflake Scripting.

```sql
-- DB2
CREATE PROCEDURE update_stats()
BEGIN
    DECLARE v_count INT;
    SELECT COUNT(*) INTO v_count FROM transactions WHERE status = 'NEW';
    IF v_count > 0 THEN
        UPDATE transactions SET status = 'PROCESSED' WHERE status = 'NEW';
        INSERT INTO audit_log VALUES (CURRENT_TIMESTAMP, v_count, 'BATCH');
    END IF;
END;
```

<details>
<summary>Solution</summary>

```sql
-- Snowflake Scripting
CREATE OR REPLACE PROCEDURE update_stats()
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
DECLARE
    v_count INT;
BEGIN
    SELECT COUNT(*) INTO :v_count FROM transactions WHERE status = 'NEW';

    IF (v_count > 0) THEN
        UPDATE transactions SET status = 'PROCESSED' WHERE status = 'NEW';
        INSERT INTO audit_log VALUES (CURRENT_TIMESTAMP(), :v_count, 'BATCH');
        RETURN 'Processed ' || :v_count || ' rows';
    ELSE
        RETURN 'No new rows';
    END IF;
END;
$$;

CALL update_stats();
```
</details>

**Exercice 2** : Écrire un script de validation post-migration qui compare les agrégats entre DB2 (via table exportée) et Snowflake.

<details>
<summary>Solution</summary>

```sql
-- Charger les stats DB2 exportées
CREATE TEMPORARY TABLE validation.db2_stats (
    table_name VARCHAR,
    row_count BIGINT,
    sum_amount DECIMAL(18,2),
    min_date DATE,
    max_date DATE
);

-- Calculer les stats Snowflake
CREATE TEMPORARY TABLE validation.sf_stats AS
SELECT 'transactions' AS table_name,
       COUNT(*) AS row_count,
       SUM(montant) AS sum_amount,
       MIN(date_txn) AS min_date,
       MAX(date_txn) AS max_date
FROM production.transactions;

-- Comparer
SELECT
    d.table_name,
    d.row_count AS db2_rows,
    s.row_count AS sf_rows,
    d.row_count - s.row_count AS diff_rows,
    d.sum_amount AS db2_amount,
    s.sum_amount AS sf_amount,
    d.sum_amount - s.sum_amount AS diff_amount,
    IFF(d.row_count = s.row_count AND d.sum_amount = s.sum_amount,
        '✓ OK', '✗ MISMATCH') AS statut
FROM validation.db2_stats d
JOIN validation.sf_stats s ON d.table_name = s.table_name;
```
</details>

---

## 9. Exercices de synthèse type HackerRank

### Exercice 1 : Analyse de transactions financières (Medium)

**Schéma :**
```sql
CREATE TABLE transactions (
    txn_id INT,
    account_id INT,
    txn_type VARCHAR(10),  -- 'BUY', 'SELL'
    ticker VARCHAR(10),
    quantity INT,
    price DECIMAL(12,4),
    txn_date TIMESTAMP
);
```

**Énoncé** : Pour chaque compte, calculer :
1. La position nette par ticker (quantité achetée - quantité vendue)
2. Le coût moyen pondéré d'achat par ticker
3. Le P&L réalisé (pour les ventes, basé sur le coût moyen d'achat)

<details>
<summary>Solution</summary>

```sql
WITH achats AS (
    SELECT account_id, ticker,
           SUM(quantity) AS qty_achetee,
           SUM(quantity * price) AS cout_total_achat
    FROM transactions WHERE txn_type = 'BUY'
    GROUP BY account_id, ticker
),
ventes AS (
    SELECT account_id, ticker,
           SUM(quantity) AS qty_vendue,
           SUM(quantity * price) AS revenu_total_vente
    FROM transactions WHERE txn_type = 'SELL'
    GROUP BY account_id, ticker
)
SELECT
    a.account_id,
    a.ticker,
    a.qty_achetee - COALESCE(v.qty_vendue, 0) AS position_nette,
    ROUND(a.cout_total_achat / a.qty_achetee, 4) AS cout_moyen_achat,
    COALESCE(v.revenu_total_vente, 0) -
        COALESCE(v.qty_vendue, 0) * (a.cout_total_achat / a.qty_achetee)
        AS pnl_realise
FROM achats a
LEFT JOIN ventes v ON a.account_id = v.account_id AND a.ticker = v.ticker
ORDER BY a.account_id, a.ticker;
```
</details>

### Exercice 2 : JSON semi-structuré avec FLATTEN (Medium)

**Schéma :**
```sql
CREATE TABLE api_logs (
    log_id INT,
    response VARIANT  -- Contient du JSON
);

-- response = {
--   "status": 200,
--   "data": {
--     "accounts": [
--       {"id": 1, "name": "Compte A", "balances": [
--         {"currency": "CAD", "amount": 50000},
--         {"currency": "USD", "amount": 12000}
--       ]},
--       {"id": 2, "name": "Compte B", "balances": [
--         {"currency": "CAD", "amount": 75000}
--       ]}
--     ]
--   }
-- }
```

**Énoncé** : Extraire chaque balance de chaque compte en une ligne plate : log_id, account_id, account_name, currency, amount.

<details>
<summary>Solution</summary>

```sql
SELECT
    l.log_id,
    acct.value:id::INT AS account_id,
    acct.value:name::STRING AS account_name,
    bal.value:currency::STRING AS currency,
    bal.value:amount::NUMBER(12,2) AS amount
FROM api_logs l,
LATERAL FLATTEN(input => l.response:data.accounts) acct,
LATERAL FLATTEN(input => acct.value:balances) bal
WHERE l.response:status::INT = 200
ORDER BY l.log_id, account_id, currency;
```
</details>

### Exercice 3 : Pipeline CDC avec Streams (Medium-Hard)

**Énoncé** : Écrire le code complet pour :
1. Créer une table source `raw.orders` et une dimension `analytics.dim_orders` (SCD Type 2)
2. Créer un stream sur la source
3. Créer une task qui gère les INSERT, UPDATE et DELETE capturés par le stream

<details>
<summary>Solution</summary>

```sql
-- Table source
CREATE TABLE raw.orders (
    order_id INT,
    client_id INT,
    status VARCHAR(20),
    total DECIMAL(10,2),
    updated_at TIMESTAMP
);

-- Dimension SCD Type 2
CREATE TABLE analytics.dim_orders (
    sk INT AUTOINCREMENT,
    order_id INT,
    client_id INT,
    status VARCHAR(20),
    total DECIMAL(10,2),
    effective_from TIMESTAMP,
    effective_to TIMESTAMP DEFAULT '9999-12-31'::TIMESTAMP,
    is_current BOOLEAN DEFAULT TRUE
);

-- Stream
CREATE STREAM raw.orders_stream ON TABLE raw.orders;

-- Task CDC
CREATE TASK analytics.cdc_dim_orders
    WAREHOUSE = etl_wh
    SCHEDULE = '5 MINUTE'
    WHEN SYSTEM$STREAM_HAS_DATA('raw.orders_stream')
AS
BEGIN
    -- Fermer les enregistrements modifiés/supprimés
    MERGE INTO analytics.dim_orders t
    USING (
        SELECT DISTINCT order_id
        FROM raw.orders_stream
        WHERE METADATA$ACTION = 'DELETE'
           OR (METADATA$ACTION = 'INSERT' AND METADATA$ISUPDATE = TRUE)
    ) s ON t.order_id = s.order_id AND t.is_current = TRUE
    WHEN MATCHED THEN
        UPDATE SET t.effective_to = CURRENT_TIMESTAMP(), t.is_current = FALSE;

    -- Insérer les nouvelles versions
    INSERT INTO analytics.dim_orders (order_id, client_id, status, total, effective_from)
    SELECT order_id, client_id, status, total, CURRENT_TIMESTAMP()
    FROM raw.orders_stream
    WHERE METADATA$ACTION = 'INSERT';
END;

ALTER TASK analytics.cdc_dim_orders RESUME;
```
</details>

### Exercice 4 : Optimisation de requête (Hard)

**Énoncé** : Cette requête prend 45 minutes sur une table de 2 milliards de lignes. Identifier les problèmes et proposer une version optimisée.

```sql
SELECT *
FROM transactions t
JOIN clients c ON t.client_id = c.client_id
WHERE YEAR(t.txn_date) = 2025
AND UPPER(c.segment) = 'PREMIUM'
AND t.amount > (SELECT AVG(amount) FROM transactions)
ORDER BY t.txn_date;
```

<details>
<summary>Solution</summary>

```sql
-- Problèmes identifiés :
-- 1. YEAR(t.txn_date) empêche le partition pruning
-- 2. UPPER(c.segment) empêche l'utilisation d'index
-- 3. Sous-requête corrélée recalculée (pas corrélée ici mais exécutée séparément)
-- 4. SELECT * retourne des colonnes inutiles
-- 5. ORDER BY sans LIMIT sur 2B lignes

-- Version optimisée :
WITH avg_amount AS (
    SELECT AVG(amount) AS avg_amt
    FROM transactions
    WHERE txn_date >= '2025-01-01' AND txn_date < '2026-01-01'
)
SELECT
    t.txn_id, t.client_id, t.amount, t.txn_date,
    c.nom, c.segment
FROM transactions t
JOIN clients c ON t.client_id = c.client_id
CROSS JOIN avg_amount a
WHERE t.txn_date >= '2025-01-01' AND t.txn_date < '2026-01-01'  -- Pruning OK
AND c.segment = 'PREMIUM'        -- Pas de fonction, données stockées correctement
AND t.amount > a.avg_amt
ORDER BY t.txn_date
LIMIT 10000;                      -- Limiter si possible

-- Optimisations infrastructure :
-- ALTER TABLE transactions CLUSTER BY (txn_date);
-- ALTER WAREHOUSE SET WAREHOUSE_SIZE = 'XLARGE' pour cette requête
```
</details>

### Exercice 5 : Architecture complète (Hard)

**Énoncé** : Concevoir l'architecture Snowflake pour un système qui :
- Reçoit des données de marché en temps réel (JSON via API)
- Stocke l'historique des positions de portefeuille
- Alimente un dashboard Power BI avec les KPIs quotidiens
- Respecte les règles de gouvernance (masquage des données sensibles, accès par équipe)

<details>
<summary>Solution</summary>

```sql
-- STRUCTURE
CREATE DATABASE market_data;
CREATE SCHEMA market_data.raw;         -- Données brutes
CREATE SCHEMA market_data.staging;     -- Nettoyage
CREATE SCHEMA market_data.analytics;   -- Modèles dimensionnels
CREATE SCHEMA market_data.governance;  -- Politiques

-- WAREHOUSES
CREATE WAREHOUSE ingest_wh WAREHOUSE_SIZE = 'SMALL' AUTO_SUSPEND = 60;
CREATE WAREHOUSE transform_wh WAREHOUSE_SIZE = 'LARGE' AUTO_SUSPEND = 60;
CREATE WAREHOUSE bi_wh WAREHOUSE_SIZE = 'SMALL'
    MIN_CLUSTER_COUNT = 1 MAX_CLUSTER_COUNT = 3 AUTO_SUSPEND = 120;

-- TABLES
CREATE TABLE raw.market_ticks (
    tick_id INT AUTOINCREMENT,
    raw_data VARIANT,
    source_api VARCHAR(50),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE analytics.dim_instrument (
    sk_instrument INT AUTOINCREMENT,
    ticker VARCHAR(10),
    name VARCHAR(200),
    type VARCHAR(20),
    exchange VARCHAR(20),
    effective_from DATE,
    effective_to DATE DEFAULT '9999-12-31',
    is_current BOOLEAN DEFAULT TRUE
);

CREATE TABLE analytics.fact_positions (
    position_date DATE,
    portfolio_id INT,
    sk_instrument INT,
    quantity DECIMAL(18,4),
    market_value DECIMAL(18,2),
    pnl_daily DECIMAL(18,2)
);

CREATE TABLE analytics.fact_daily_kpi (
    kpi_date DATE,
    portfolio_id INT,
    total_aum DECIMAL(18,2),
    total_pnl DECIMAL(18,2),
    sharpe_ratio DECIMAL(8,4),
    max_drawdown DECIMAL(8,4)
);

-- GOUVERNANCE
CREATE MASKING POLICY governance.mask_portfolio_value AS (val NUMBER)
RETURNS NUMBER ->
    CASE
        WHEN CURRENT_ROLE() IN ('PORTFOLIO_MANAGER', 'COMPLIANCE', 'ADMIN') THEN val
        ELSE NULL
    END;

ALTER TABLE analytics.fact_positions
    MODIFY COLUMN market_value SET MASKING POLICY governance.mask_portfolio_value;

CREATE ROW ACCESS POLICY governance.portfolio_access AS (portfolio_id INT)
RETURNS BOOLEAN ->
    CURRENT_ROLE() = 'ADMIN' OR
    portfolio_id IN (
        SELECT portfolio_id FROM governance.user_portfolios
        WHERE username = CURRENT_USER()
    );

ALTER TABLE analytics.fact_positions
    ADD ROW ACCESS POLICY governance.portfolio_access ON (portfolio_id);

-- PIPELINE (Streams + Tasks)
CREATE STREAM raw.ticks_stream ON TABLE raw.market_ticks;

CREATE TASK staging.process_ticks
    WAREHOUSE = transform_wh
    SCHEDULE = '1 MINUTE'
    WHEN SYSTEM$STREAM_HAS_DATA('raw.ticks_stream')
AS
    INSERT INTO staging.parsed_ticks
    SELECT
        raw_data:ticker::STRING,
        raw_data:price::DECIMAL(12,4),
        raw_data:volume::INT,
        raw_data:timestamp::TIMESTAMP
    FROM raw.ticks_stream
    WHERE METADATA$ACTION = 'INSERT';

CREATE TASK analytics.daily_kpi_calc
    WAREHOUSE = transform_wh
    SCHEDULE = 'USING CRON 0 22 * * * America/Montreal'
AS
    MERGE INTO analytics.fact_daily_kpi ...;

-- RÔLES
CREATE ROLE data_engineer;
CREATE ROLE analyst;
CREATE ROLE portfolio_manager;

GRANT USAGE ON WAREHOUSE transform_wh TO ROLE data_engineer;
GRANT USAGE ON WAREHOUSE bi_wh TO ROLE analyst;
GRANT SELECT ON ALL TABLES IN SCHEMA analytics TO ROLE analyst;
```
</details>

---

> **Conseils pour le test** :
> - `QUALIFY` est la fonctionnalité Snowflake la plus utile — utilisez-la systématiquement
> - `LATERAL FLATTEN` est la clé pour les données JSON semi-structurées
> - Pensez au pruning quand vous écrivez des filtres : pas de fonctions sur les colonnes
> - Connaître la syntaxe VARIANT (`:` pour accéder aux champs) est essentiel
