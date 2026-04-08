# Guide Utilisateur — Environnement SQL Data Ingenieur

## Architecture

```
preparation_ms/
├── docker-compose.yml              # PostgreSQL 16 + pgAdmin + SQL Workbench
├── web/                             # Interface web SQL Workbench
│   ├── app.py                       # Backend Flask
│   ├── templates/index.html         # Frontend (editeur SQL, explorateur, exercices)
│   ├── Dockerfile
│   └── requirements.txt
├── exercices.ipynb                   # Exercices Python/Pandas/SQL/Snowflake/ETL
├── exercices_sql_corriges.ipynb      # Exercices SQL corriges (base + avance)
├── sql/
│   ├── init/                         # Auto-execute au 1er demarrage du container
│   │   ├── 01_create_databases.sql
│   │   ├── 02_crud_db.sql
│   │   ├── 03_sql_avance.sql
│   │   └── 04_etl_warehouse.sql
│   ├── csv_data/                     # Deposer les CSV ici (import/export)
│   │   ├── exemple_clients.csv
│   │   └── exemple_transactions.csv
│   └── scripts/                      # Scripts SQL manuels
│       ├── import_csv.sql
│       ├── export_csv.sql
│       └── procedures_triggers.sql
```

### Les 3 bases de donnees

| Base | Contenu | Usage |
|------|---------|-------|
| `crud_db` | employes, departements, projets, affectations | CRUD, JOINs, GROUP BY, sous-requetes |
| `sql_avance` | ventes, organisation, connexions, clients, comptes, transactions, ventes_mensuelles | Window Functions, CTE recursives, Gaps & Islands, PIVOT, procedures, triggers |
| `etl_warehouse` | schemas staging + dwh (dim_date, dim_client, dim_produit, fait_transactions) | ETL, modele etoile, SCD Type 2, MERGE |

---

## 1. Demarrage

```bash
# Lancer tous les services (PostgreSQL + pgAdmin + SQL Workbench)
docker compose up -d --build

# Verifier que tout tourne
docker compose ps
```

Trois interfaces sont disponibles :

| Interface | URL / Commande | Usage |
|-----------|---------------|-------|
| **SQL Workbench** (web) | http://localhost:5000 | Editeur SQL, explorateur, exercices, import/export CSV |
| **pgAdmin** | http://localhost:8080 | Administration visuelle complete |
| **psql** (CLI) | `docker exec -it ms_postgres psql -U dataeng -d crud_db` | Ligne de commande directe |

---

## 2. Utilisation via la ligne de commande (psql)

### Se connecter a une base

```bash
# Base CRUD
docker exec -it ms_postgres psql -U dataeng -d crud_db

# Base SQL Avance
docker exec -it ms_postgres psql -U dataeng -d sql_avance

# Base ETL Warehouse
docker exec -it ms_postgres psql -U dataeng -d etl_warehouse
```

### Commandes psql utiles

```
\l              -- Lister toutes les bases
\c nom_base     -- Changer de base
\dt             -- Lister les tables du schema courant
\dt staging.*   -- Lister les tables du schema staging
\dt dwh.*       -- Lister les tables du schema dwh
\d nom_table    -- Decrire une table (colonnes, types, contraintes)
\dn             -- Lister les schemas
\dv             -- Lister les vues
\df             -- Lister les fonctions
\di             -- Lister les index
\q              -- Quitter psql
```

### Executer des requetes

```bash
# Requete directe depuis le terminal
docker exec -it ms_postgres psql -U dataeng -d sql_avance -c "SELECT * FROM ventes LIMIT 5;"

# Executer un fichier SQL
docker exec -it ms_postgres psql -U dataeng -d sql_avance -f /sql_scripts/procedures_triggers.sql

# Executer une requete multi-lignes
docker exec -it ms_postgres psql -U dataeng -d crud_db -c "
SELECT departement, COUNT(*) AS nb, ROUND(AVG(salaire),2) AS salaire_moy
FROM employes
GROUP BY departement
ORDER BY salaire_moy DESC;
"
```

### Importer un CSV

```bash
# Methode 1 : via le script pre-fait
docker exec -it ms_postgres psql -U dataeng -d etl_warehouse -f /sql_scripts/import_csv.sql

# Methode 2 : commande COPY directe
docker exec -it ms_postgres psql -U dataeng -d etl_warehouse -c "
COPY staging.raw_clients (data_source, client_id, nom, email, telephone, adresse, ville, pays, segment, date_inscription)
FROM '/csv_data/exemple_clients.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',', NULL '');
"

# Methode 3 : deposer un fichier dans sql/csv_data/ puis COPY
# (le dossier sql/csv_data/ est monte dans le container sur /csv_data/)
cp mon_fichier.csv sql/csv_data/
docker exec -it ms_postgres psql -U dataeng -d crud_db -c "
COPY ma_table FROM '/csv_data/mon_fichier.csv' WITH (FORMAT csv, HEADER true);
"
```

### Exporter vers CSV

```bash
# Methode 1 : script pre-fait
docker exec -it ms_postgres psql -U dataeng -d etl_warehouse -f /sql_scripts/export_csv.sql
# Le fichier CSV apparait dans sql/csv_data/

# Methode 2 : export direct
docker exec -it ms_postgres psql -U dataeng -d sql_avance -c "
COPY (SELECT * FROM ventes WHERE region = 'Nord') TO '/csv_data/ventes_nord.csv' WITH (FORMAT csv, HEADER true);
"
# Recuperer le fichier : il est dans sql/csv_data/ventes_nord.csv
```

### Creer des tables, procedures, triggers

```bash
# Creer un fichier SQL dans sql/scripts/
cat > sql/scripts/ma_table.sql << 'EOF'
CREATE TABLE IF NOT EXISTS ma_table (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100),
    valeur DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW()
);
INSERT INTO ma_table (nom, valeur) VALUES ('test', 42.0);
EOF

# L'executer
docker exec -it ms_postgres psql -U dataeng -d crud_db -f /sql_scripts/ma_table.sql
```

---

## 3. Utilisation via l'interface web (SQL Workbench)

Ouvrir http://localhost:5000

### Editeur SQL

- **Ecrire une requete** dans l'editeur central (coloration syntaxique, autocompletion)
- **Executer** : cliquer sur `Run` ou appuyer sur `Ctrl+Enter`
- **Selection partielle** : selectionner une partie du texte avant Ctrl+Enter pour n'executer que la selection
- **Changer de base** : menu deroulant "Database" en haut a gauche
- **Formater** : bouton `Format` pour mettre les mots-cles SQL en majuscules
- **Redimensionner** : glisser la barre entre l'editeur et les resultats

### Explorateur de base (panneau gauche)

- Affiche les **schemas**, **tables** et **colonnes** de la base selectionnee
- **Cliquer** sur un schema/table pour le deplier
- **Double-cliquer** sur un nom de table ou colonne pour l'inserer dans l'editeur
- Bouton **Refresh** pour recharger apres des modifications

### Panneau d'exercices (panneau droit)

- 15 exercices : **A1-A5** (SQL de base) et **B1-B10** (SQL avance)
- **Filtrer** par partie (All / Part A / Part B)
- **Load** : charge l'enonce dans l'editeur et selectionne automatiquement la bonne base
- **Hint** : affiche un indice pour chaque exercice

### Import CSV

1. Cliquer sur **Import CSV** dans la barre d'outils
2. Choisir la base, le schema, le nom de table
3. Mode : `Create` (cree la table) ou `Append` (insere dans une table existante)
4. Selectionner le fichier CSV
5. Cliquer sur **Import**

### Export CSV

1. Ecrire et executer une requete SELECT
2. Cliquer sur **Export CSV** — le fichier se telecharge automatiquement

---

## 4. Utilisation de pgAdmin

Ouvrir http://localhost:8080

### Connexion

- **Email** : `admin@ms.local`
- **Mot de passe** : `admin2024`

### Ajouter le serveur PostgreSQL (premiere fois)

1. Clic droit sur "Servers" > "Register" > "Server"
2. Onglet **General** : Name = `MS Postgres`
3. Onglet **Connection** :
   - Host : `postgres`
   - Port : `5432`
   - Username : `dataeng`
   - Password : `dataeng2024`
   - Cocher "Save password"
4. Cliquer sur **Save**

### Naviguer

- Servers > MS Postgres > Databases > (crud_db / sql_avance / etl_warehouse)
- Chaque base > Schemas > Tables
- Clic droit sur une table > "View/Edit Data" pour voir les donnees
- "Tools" > "Query Tool" pour ouvrir un editeur SQL

---

## 5. Workflow type pour les exercices

### Exercice SQL en ligne de commande

```bash
# 1. Se connecter
docker exec -it ms_postgres psql -U dataeng -d sql_avance

# 2. Explorer les tables
\dt
\d ventes

# 3. Ecrire et tester des requetes
SELECT region, SUM(montant * quantite) AS ca
FROM ventes
GROUP BY region
ORDER BY ca DESC;

# 4. Ou creer un fichier et l'executer
# Ecrire dans sql/scripts/exo_b1.sql puis :
\i /sql_scripts/exo_b1.sql
```

### Exercice SQL via le web

1. Ouvrir http://localhost:5000
2. Cliquer sur un exercice dans le panneau droit (ex: B2)
3. L'editeur se charge avec l'enonce, la base est selectionnee
4. Ecrire la requete sous l'enonce
5. `Ctrl+Enter` pour executer
6. Comparer le resultat avec les corrections dans `exercices_sql_corriges.ipynb`

### Exercice ETL (import CSV)

```bash
# 1. Deposer un CSV dans sql/csv_data/
cp nouvelles_transactions.csv sql/csv_data/

# 2. Via CLI
docker exec -it ms_postgres psql -U dataeng -d etl_warehouse -c "
COPY staging.raw_transactions (data_source, transaction_id, client_id, produit_id, quantite, montant, date_transaction, canal, statut)
FROM '/csv_data/nouvelles_transactions.csv' WITH (FORMAT csv, HEADER true);
"

# 3. Ou via l'interface web : bouton Import CSV
```

---

## 6. Gestion du container

```bash
# Voir les logs
docker compose logs -f postgres
docker compose logs -f sqlweb

# Arreter
docker compose down

# Arreter et supprimer toutes les donnees (reset complet)
docker compose down -v

# Relancer (les scripts init se re-executent si les volumes sont supprimes)
docker compose up -d --build

# Redemarrer un service
docker compose restart postgres
docker compose restart sqlweb
```

---

## 7. Aide-memoire rapide

| Action | CLI | Web |
|--------|-----|-----|
| Executer une requete | `psql -c "SELECT ..."` | Ctrl+Enter |
| Changer de base | `\c sql_avance` | Menu deroulant |
| Lister les tables | `\dt` | Panneau gauche |
| Decrire une table | `\d ventes` | Deplier table dans l'explorateur |
| Importer un CSV | `COPY ... FROM '/csv_data/...'` | Bouton Import CSV |
| Exporter en CSV | `COPY (...) TO '/csv_data/...'` | Bouton Export CSV |
| Executer un script | `\i /sql_scripts/mon_script.sql` | Copier-coller dans l'editeur |
| Voir un exercice | Ouvrir `exercices_sql_corriges.ipynb` | Panneau droit + Load |
