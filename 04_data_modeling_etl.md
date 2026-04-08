

> **Objectif** : Maîtriser la modélisation dimensionnelle, relationnelle, les SCD, les concepts ETL/ELT, les outils Talend/Informatica, la gouvernance et l'architecture de données pour un test de 60 minutes.

---

## 1. Modélisation dimensionnelle (Kimball)

### Définitions complètes

La méthodologie **Kimball** (bottom-up) est centrée sur les besoins métier. L'entrepôt est constitué de **data marts** dimensionnels reliés par des dimensions conformes.

#### Tables de faits

| Type | Description | Exemple |
|------|-------------|---------|
| **Factuelle (transactionnelle)** | Une ligne par événement, contient des mesures | Ventes, transactions, clics |
| **Sans fait (factless)** | Enregistre des événements sans mesure numérique | Présences, inscriptions à des cours |
| **Accumulante (accumulating snapshot)** | Suit le cycle de vie d'un processus | Pipeline de vente (étapes), traitement de commande |
| **Périodique (periodic snapshot)** | Photo à intervalles réguliers | Solde mensuel, stock quotidien |

#### Tables de dimensions

| Type | Description | Exemple |
|------|-------------|---------|
| **Conforme** | Partagée entre plusieurs faits/data marts | dim_client utilisée par ventes ET service client |
| **Junk dimension** | Regroupe des attributs à faible cardinalité | Combinaisons de flags (est_premium, est_actif, canal) |
| **Role-playing** | Même dimension utilisée plusieurs fois | dim_date pour date_commande, date_livraison, date_paiement |
| **Dégénérée** | Attribut de dimension stocké dans la table de faits | Numéro de commande, numéro de facture |
| **Outrigger** | Dimension liée à une autre dimension (pas à un fait) | dim_ville liée à dim_client |
| **Mini-dimension** | Sous-ensemble fréquemment modifié d'une grande dimension | Segment démographique séparé de dim_client |

#### Schéma en étoile vs en flocon

```
ÉTOILE (Star Schema)                    FLOCON (Snowflake Schema)
─────────────────────                   ─────────────────────────

   dim_client                              dim_ville
       │                                      │
   dim_date ── FAIT_VENTES ── dim_produit  dim_client
       │                                      │
   dim_magasin                         dim_date ── FAIT ── dim_produit
                                          │                    │
                                      dim_mois            dim_categorie
                                          │                    │
                                      dim_annee           dim_famille

Star : dimensions dénormalisées (1 JOIN)
Snowflake : dimensions normalisées (multiple JOINs, moins de redondance)
```

**En pratique** : Morgan Stanley → Star Schema pour la performance des requêtes analytiques.

#### Bus Matrix

| Processus métier | dim_client | dim_date | dim_produit | dim_compte | dim_instrument |
|---|:---:|:---:|:---:|:---:|:---:|
| Transactions | X | X | | X | X |
| Positions | | X | | X | X |
| Ouverture compte | X | X | | X | |
| Ventes produits | X | X | X | | |

### Exemples détaillés

**Modèle étoile — Données financières bancaires :**
```sql
-- Dimension date (role-playing)
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,           -- Format YYYYMMDD
    full_date DATE,
    jour INT,
    mois INT,
    trimestre INT,
    annee INT,
    nom_jour VARCHAR(10),               -- 'Lundi', 'Mardi'...
    nom_mois VARCHAR(15),               -- 'Janvier'...
    est_jour_ouvre BOOLEAN,
    est_fin_mois BOOLEAN,
    est_fin_trimestre BOOLEAN,
    semaine_iso INT,
    jour_annee INT
);

-- Dimension client
CREATE TABLE dim_client (
    sk_client INT PRIMARY KEY,           -- Surrogate key
    client_id INT,                       -- Business key
    nom VARCHAR(100),
    prenom VARCHAR(100),
    segment VARCHAR(20),                 -- 'Retail', 'Wealth', 'Institutional'
    pays VARCHAR(50),
    ville VARCHAR(50),
    date_ouverture DATE,
    gestionnaire VARCHAR(100),
    -- SCD Type 2
    date_debut DATE,
    date_fin DATE DEFAULT '9999-12-31',
    est_courant BOOLEAN DEFAULT TRUE
);

-- Dimension instrument financier
CREATE TABLE dim_instrument (
    sk_instrument INT PRIMARY KEY,
    ticker VARCHAR(10),
    nom_instrument VARCHAR(200),
    type_instrument VARCHAR(30),         -- 'ACTION', 'OBLIGATION', 'OPTION', 'ETF'
    devise VARCHAR(3),
    bourse VARCHAR(20),
    secteur VARCHAR(50),
    pays_emission VARCHAR(50),
    date_emission DATE,
    date_echeance DATE                   -- NULL pour les actions
);

-- Dimension compte
CREATE TABLE dim_compte (
    sk_compte INT PRIMARY KEY,
    numero_compte VARCHAR(20),
    type_compte VARCHAR(30),             -- 'Épargne', 'Courtage', 'REER', 'CELI'
    devise_base VARCHAR(3),
    date_ouverture DATE,
    statut VARCHAR(10)                   -- 'Actif', 'Fermé', 'Gelé'
);

-- Fait transactions
CREATE TABLE fait_transaction (
    txn_key BIGINT PRIMARY KEY,
    date_key INT REFERENCES dim_date(date_key),           -- Role-playing: date_transaction
    date_reglement_key INT REFERENCES dim_date(date_key), -- Role-playing: date_règlement
    sk_client INT REFERENCES dim_client(sk_client),
    sk_instrument INT REFERENCES dim_instrument(sk_instrument),
    sk_compte INT REFERENCES dim_compte(sk_compte),
    -- Dimension dégénérée
    numero_ordre VARCHAR(20),
    -- Mesures
    quantite DECIMAL(18,4),
    prix_unitaire DECIMAL(18,6),
    montant_brut DECIMAL(18,2),
    commission DECIMAL(18,2),
    montant_net DECIMAL(18,2),
    type_operation VARCHAR(10)           -- 'ACHAT', 'VENTE'
);
```

**Modèle étoile — Données RH :**
```sql
CREATE TABLE dim_employe (
    sk_employe INT PRIMARY KEY,
    employe_id INT,
    nom VARCHAR(100),
    poste VARCHAR(100),
    departement VARCHAR(50),
    niveau VARCHAR(20),                  -- 'Junior', 'Senior', 'VP', 'MD'
    manager_id INT,
    date_embauche DATE,
    -- SCD Type 2
    date_debut DATE,
    date_fin DATE DEFAULT '9999-12-31',
    est_courant BOOLEAN DEFAULT TRUE
);

CREATE TABLE fait_performance (
    performance_key INT PRIMARY KEY,
    date_key INT REFERENCES dim_date(date_key),
    sk_employe INT REFERENCES dim_employe(sk_employe),
    -- Mesures
    objectif_realise_pct DECIMAL(5,2),
    note_evaluation INT,                 -- 1 à 5
    nb_projets_completes INT,
    heures_formation DECIMAL(5,1),
    bonus DECIMAL(18,2)
);

-- Fait sans mesure (factless): présence aux formations
CREATE TABLE fait_presence_formation (
    date_key INT,
    sk_employe INT,
    formation_id INT,
    -- Pas de mesure — l'existence de la ligne = présence
    PRIMARY KEY (date_key, sk_employe, formation_id)
);
```

### Exercices

**Exercice 1** : Concevoir un modèle dimensionnel pour analyser les appels au service client (durée, résolution, satisfaction). Identifier les dimensions et les mesures.

<details>
<summary>Solution</summary>

```
DIMENSIONS :
- dim_date (date_appel)
- dim_client (appelant)
- dim_agent (agent du service client)
- dim_categorie_appel (type de problème, sous-catégorie)
- dim_canal (téléphone, chat, email)

FAIT : fait_appel
- date_key → dim_date
- sk_client → dim_client
- sk_agent → dim_agent
- sk_categorie → dim_categorie_appel
- sk_canal → dim_canal
- numero_ticket (dimension dégénérée)
- duree_secondes (mesure)
- duree_attente_secondes (mesure)
- est_resolu_premier_appel (mesure : 1 ou 0)
- note_satisfaction (mesure : 1 à 5)
- nb_transferts (mesure)
```

```sql
CREATE TABLE fait_appel (
    appel_key BIGINT,
    date_key INT,
    sk_client INT,
    sk_agent INT,
    sk_categorie INT,
    sk_canal INT,
    numero_ticket VARCHAR(20),
    duree_secondes INT,
    duree_attente_secondes INT,
    est_resolu_premier_appel BOOLEAN,
    note_satisfaction SMALLINT,
    nb_transferts SMALLINT
);
```
</details>

**Exercice 2** : Concevoir un modèle pour tracker les positions de portefeuille quotidiennes (periodic snapshot). Quelles sont les mesures semi-additives ?

<details>
<summary>Solution</summary>

```sql
-- FAIT PERIODIC SNAPSHOT (une ligne par compte × instrument × jour)
CREATE TABLE fait_position_quotidienne (
    date_key INT,
    sk_compte INT,
    sk_instrument INT,
    -- Mesures SEMI-ADDITIVES (ne s'additionnent PAS sur la dimension date)
    quantite DECIMAL(18,4),           -- Solde = pas de somme sur le temps
    valeur_marche DECIMAL(18,2),      -- Solde = pas de somme sur le temps
    cout_base DECIMAL(18,2),          -- Solde
    -- Mesures ADDITIVES (s'additionnent sur toutes les dimensions)
    pnl_jour DECIMAL(18,2),           -- P&L du jour = additif
    volume_jour INT,                   -- Volume du jour = additif
    PRIMARY KEY (date_key, sk_compte, sk_instrument)
);

-- ATTENTION : Pour les mesures semi-additives :
-- ✅ SUM(valeur_marche) GROUP BY date_key → total portefeuille un jour donné
-- ❌ SUM(valeur_marche) GROUP BY sk_compte → N'A PAS DE SENS (somme sur le temps)
-- ✅ Utiliser AVG ou LAST_VALUE pour agréger sur le temps
```
</details>

**Exercice 3** : Expliquer ce qu'est une junk dimension et en créer une pour les transactions (type_op, canal, est_en_ligne, devise, est_interne).

<details>
<summary>Solution</summary>

```sql
-- Junk dimension : regroupe des attributs de faible cardinalité
-- pour éviter d'encombrer la table de faits

CREATE TABLE dim_attributs_transaction (
    sk_attribut INT PRIMARY KEY,
    type_operation VARCHAR(10),    -- 'ACHAT', 'VENTE'  (2 valeurs)
    canal VARCHAR(20),             -- 'Web', 'Mobile', 'Trading desk'  (3 valeurs)
    est_en_ligne BOOLEAN,          -- TRUE/FALSE  (2 valeurs)
    devise VARCHAR(3),             -- 'CAD', 'USD', 'EUR'  (3 valeurs)
    est_interne BOOLEAN            -- TRUE/FALSE  (2 valeurs)
);

-- Nombre total de combinaisons : 2 × 3 × 2 × 3 × 2 = 72 lignes
-- Beaucoup mieux que 5 colonnes de flags dans la table de faits

-- Pré-remplir toutes les combinaisons
INSERT INTO dim_attributs_transaction
SELECT
    ROW_NUMBER() OVER (ORDER BY t.type_operation, c.canal, e.est_en_ligne, d.devise, i.est_interne),
    t.type_operation, c.canal, e.est_en_ligne, d.devise, i.est_interne
FROM (SELECT 'ACHAT' UNION SELECT 'VENTE') t(type_operation)
CROSS JOIN (SELECT 'Web' UNION SELECT 'Mobile' UNION SELECT 'Trading desk') c(canal)
CROSS JOIN (SELECT TRUE UNION SELECT FALSE) e(est_en_ligne)
CROSS JOIN (SELECT 'CAD' UNION SELECT 'USD' UNION SELECT 'EUR') d(devise)
CROSS JOIN (SELECT TRUE UNION SELECT FALSE) i(est_interne);

-- Dans la table de faits : une seule FK au lieu de 5 colonnes
-- fait_transaction.sk_attribut → dim_attributs_transaction.sk_attribut
```
</details>

**Exercice 4** : Concevoir un modèle de type accumulating snapshot pour le processus d'ouverture de compte (demande → vérification → approbation → activation).

<details>
<summary>Solution</summary>

```sql
CREATE TABLE fait_ouverture_compte (
    demande_key INT PRIMARY KEY,
    sk_client INT,
    sk_type_compte INT,
    -- Dates jalons (role-playing dim_date)
    date_demande_key INT,
    date_verification_key INT,      -- NULL si pas encore atteint
    date_approbation_key INT,       -- NULL si pas encore atteint
    date_activation_key INT,        -- NULL si pas encore atteint
    date_rejet_key INT,             -- NULL si pas rejeté
    -- Mesures de durée (calculées)
    jours_demande_a_verif INT,
    jours_verif_a_approbation INT,
    jours_approbation_a_activation INT,
    jours_total INT,
    -- Statut courant
    statut_courant VARCHAR(20),     -- 'En attente', 'En vérification', 'Approuvé', 'Actif', 'Rejeté'
    -- Mesures
    montant_depot_initial DECIMAL(18,2)
);

-- L'accumulating snapshot est MIS À JOUR à chaque changement d'étape
-- (contrairement au transactionnel qui ajoute des lignes)
```
</details>

**Exercice 5** : Créer une Bus Matrix pour Morgan Stanley avec au moins 5 processus métier et 6 dimensions.

<details>
<summary>Solution</summary>

```
| Processus métier      | dim_date | dim_client | dim_compte | dim_instrument | dim_agent | dim_region | dim_devise |
|----------------------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Transactions marché  |  X  |  X  |  X  |  X  |     |  X  |  X  |
| Positions portefeuille|  X  |  X  |  X  |  X  |     |     |  X  |
| Ouverture compte     |  X  |  X  |  X  |     |  X  |  X  |  X  |
| Service client       |  X  |  X  |  X  |     |  X  |     |     |
| Conformité/KYC       |  X  |  X  |  X  |     |  X  |  X  |     |
| Fees & Commissions   |  X  |  X  |  X  |  X  |     |  X  |  X  |
| Performance fonds    |  X  |     |     |  X  |     |  X  |  X  |

Dimensions conformes partagées entre data marts :
- dim_date : calendrier commun (jours ouvrables, fériés, fin de trimestre)
- dim_client : vue 360° du client
- dim_compte : tous les comptes
```
</details>

---

## 2. Modélisation relationnelle (3NF / Inmon)

### Formes normales

| Forme | Règle | Élimine |
|-------|-------|---------|
| **1NF** | Valeurs atomiques, pas de groupes répétitifs | Tableaux dans des colonnes |
| **2NF** | 1NF + chaque attribut dépend de TOUTE la clé primaire | Dépendances partielles |
| **3NF** | 2NF + pas de dépendance transitive | A → B → C (C dépend de A via B) |
| **BCNF** | Chaque déterminant est une clé candidate | Anomalies subtiles |

**Exemple de normalisation :**
```
NON NORMALISÉ :
commande_id | client_nom | client_ville | produit1 | prix1 | produit2 | prix2
    1       | Alice      | Montreal     | Laptop   | 1200  | Souris   | 25

1NF (atomique, pas de groupes répétitifs) :
commande_id | client_nom | client_ville | produit | prix
    1       | Alice      | Montreal     | Laptop  | 1200
    1       | Alice      | Montreal     | Souris  | 25

2NF (tout dépend de TOUTE la PK = commande_id + produit) :
Table commandes:     commande_id | client_nom | client_ville
Table lignes:        commande_id | produit    | prix

3NF (pas de dépendance transitive : client_ville dépend de client_nom, pas de commande_id) :
Table clients:       client_id | client_nom | client_ville
Table commandes:     commande_id | client_id
Table lignes:        commande_id | produit_id | prix
Table produits:      produit_id  | nom_produit
```

### Quand utiliser 3NF vs dimensionnel

| Critère | 3NF (Inmon) | Dimensionnel (Kimball) |
|---------|-------------|------------------------|
| Objectif | Source de vérité unique | Performance analytique |
| Redondance | Minimale | Acceptée (dénormalisé) |
| Complexité requêtes | JOINs complexes | JOINs simples (étoile) |
| Chargement | Plus simple (insert) | Plus complexe (SCD) |
| Cas d'usage | ODS, système source | Data mart, reporting |
| Approche | Top-down (entreprise) | Bottom-up (par sujet) |

### Enterprise Data Warehouse (EDW) — Pattern Inmon

```
Sources → Staging → ODS (3NF) → Data Marts (Dimensionnel) → Reporting
              │         │               │
         Extract    Intégration     Agrégation
         Nettoyage  Historisation   Étoile/Flocon
```

### Exercices

**Exercice 1** : Normaliser cette table en 3NF :

| order_id | customer_name | customer_city | customer_segment | product_name | product_category | quantity | price |
|----------|---------------|---------------|------------------|--------------|------------------|----------|-------|

<details>
<summary>Solution</summary>

```sql
-- Table clients (3NF)
CREATE TABLE clients (
    client_id INT PRIMARY KEY,
    nom VARCHAR(100),
    ville VARCHAR(50),
    segment VARCHAR(20)
);

-- Table produits (3NF)
CREATE TABLE produits (
    produit_id INT PRIMARY KEY,
    nom VARCHAR(100),
    categorie VARCHAR(50)
);

-- Table commandes
CREATE TABLE commandes (
    commande_id INT PRIMARY KEY,
    client_id INT REFERENCES clients(client_id),
    date_commande DATE
);

-- Table lignes de commande
CREATE TABLE lignes_commande (
    commande_id INT REFERENCES commandes(commande_id),
    produit_id INT REFERENCES produits(produit_id),
    quantite INT,
    prix_unitaire DECIMAL(10,2),
    PRIMARY KEY (commande_id, produit_id)
);
```
</details>

**Exercice 2** : Identifier les dépendances fonctionnelles et la forme normale actuelle :
```
employe_id → nom, departement_id
departement_id → nom_departement, localisation
employe_id, projet_id → heures_travaillees
```

<details>
<summary>Solution</summary>

```
Dépendances fonctionnelles :
1. employe_id → nom, departement_id                   (DF directe)
2. departement_id → nom_departement, localisation      (DF directe)
3. employe_id → nom_departement, localisation          (DF TRANSITIVE via departement_id)
4. (employe_id, projet_id) → heures_travaillees        (DF composite)

Si tout est dans une seule table : c'est en 2NF (pas en 3NF à cause de la dépendance transitive 3.)

Solution 3NF :
- Table employes (employe_id PK, nom, departement_id FK)
- Table departements (departement_id PK, nom_departement, localisation)
- Table affectations (employe_id FK, projet_id FK, heures_travaillees) PK composite
```
</details>

**Exercice 3** : Pour un système bancaire, dessiner un modèle 3NF (ODS) avec les entités : Client, Compte, Transaction, Produit, Agence.

<details>
<summary>Solution</summary>

```sql
CREATE TABLE agences (
    agence_id INT PRIMARY KEY,
    nom VARCHAR(100),
    adresse VARCHAR(200),
    ville VARCHAR(50),
    code_postal VARCHAR(10)
);

CREATE TABLE clients (
    client_id INT PRIMARY KEY,
    nom VARCHAR(100),
    prenom VARCHAR(100),
    date_naissance DATE,
    email VARCHAR(200),
    telephone VARCHAR(20),
    agence_id INT REFERENCES agences(agence_id),
    date_creation DATE
);

CREATE TABLE produits (
    produit_id INT PRIMARY KEY,
    nom VARCHAR(100),
    type VARCHAR(30),        -- 'Épargne', 'Courtage', 'REER'
    description TEXT,
    frais_annuels DECIMAL(8,2)
);

CREATE TABLE comptes (
    compte_id INT PRIMARY KEY,
    numero VARCHAR(20) UNIQUE,
    client_id INT REFERENCES clients(client_id),
    produit_id INT REFERENCES produits(produit_id),
    date_ouverture DATE,
    date_fermeture DATE,
    statut VARCHAR(10),
    devise VARCHAR(3)
);

CREATE TABLE transactions (
    txn_id BIGINT PRIMARY KEY,
    compte_id INT REFERENCES comptes(compte_id),
    type_txn VARCHAR(20),    -- 'DEBIT', 'CREDIT', 'TRANSFERT'
    montant DECIMAL(18,2),
    devise VARCHAR(3),
    date_txn TIMESTAMP,
    description VARCHAR(200),
    compte_contrepartie_id INT REFERENCES comptes(compte_id)
);
```
</details>

---

## 3. Slowly Changing Dimensions (SCD)

### Définitions complètes

| Type | Stratégie | Historique conservé ? | Complexité |
|------|-----------|----------------------|------------|
| **Type 0** | Ne jamais modifier | Non (valeur originale conservée) | Nulle |
| **Type 1** | Écraser l'ancienne valeur | Non | Faible |
| **Type 2** | Ajouter une nouvelle ligne | Oui (complet) | Élevée |
| **Type 3** | Colonne pour l'ancienne valeur | Partiel (1 version précédente) | Moyenne |
| **Type 4** | Table historique séparée | Oui (dans une table annexe) | Moyenne |
| **Type 6** | Hybride (1 + 2 + 3) | Oui + valeur courante | Élevée |

### Type 1 — Écrasement

```sql
-- Simplement UPDATE la ligne existante
MERGE INTO dim_client t
USING stg_client s ON t.client_id = s.client_id
WHEN MATCHED THEN
    UPDATE SET t.ville = s.ville, t.segment = s.segment, t.date_maj = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN
    INSERT (client_id, nom, ville, segment, date_maj)
    VALUES (s.client_id, s.nom, s.ville, s.segment, CURRENT_TIMESTAMP());
```

### Type 2 — Historisation complète

```sql
-- Structure
CREATE TABLE dim_client_scd2 (
    sk_client INT AUTOINCREMENT,    -- Surrogate key (PK)
    client_id INT,                   -- Business key (NK)
    nom VARCHAR(100),
    ville VARCHAR(50),
    segment VARCHAR(20),
    date_debut DATE,                 -- Début de validité
    date_fin DATE DEFAULT '9999-12-31',  -- Fin de validité
    est_courant BOOLEAN DEFAULT TRUE
);

-- Étape 1 : Fermer les anciens enregistrements
UPDATE dim_client_scd2 t
SET t.date_fin = CURRENT_DATE() - 1,
    t.est_courant = FALSE
FROM stg_client s
WHERE t.client_id = s.client_id
AND t.est_courant = TRUE
AND (t.ville != s.ville OR t.segment != s.segment);

-- Étape 2 : Insérer les nouvelles versions + nouveaux clients
INSERT INTO dim_client_scd2 (client_id, nom, ville, segment, date_debut)
SELECT s.client_id, s.nom, s.ville, s.segment, CURRENT_DATE()
FROM stg_client s
LEFT JOIN dim_client_scd2 t
    ON s.client_id = t.client_id AND t.est_courant = TRUE
WHERE t.sk_client IS NULL;
```

### Type 3 — Colonne précédente

```sql
CREATE TABLE dim_client_scd3 (
    client_id INT PRIMARY KEY,
    nom VARCHAR(100),
    segment_courant VARCHAR(20),
    segment_precedent VARCHAR(20),    -- Une seule version précédente
    date_changement_segment DATE
);

-- Mise à jour
UPDATE dim_client_scd3
SET segment_precedent = segment_courant,
    segment_courant = 'Platinum',
    date_changement_segment = CURRENT_DATE()
WHERE client_id = 42;
```

### Type 6 — Hybride (1 + 2 + 3)

```sql
CREATE TABLE dim_client_scd6 (
    sk_client INT AUTOINCREMENT,
    client_id INT,
    nom VARCHAR(100),
    segment_courant VARCHAR(20),      -- Type 1 : toujours à jour (même sur les anciennes lignes)
    segment_historique VARCHAR(20),    -- Type 2 : valeur au moment de cette version
    date_debut DATE,                   -- Type 2
    date_fin DATE DEFAULT '9999-12-31',
    est_courant BOOLEAN DEFAULT TRUE
);

-- Quand le segment change :
-- 1. Mettre à jour segment_courant sur TOUTES les lignes du client (Type 1)
-- 2. Fermer l'ancienne ligne et en créer une nouvelle (Type 2)
```

### Implémentation SCD Type 2 avec Snowflake Streams

```sql
-- Stream sur la table source
CREATE STREAM src.clients_stream ON TABLE src.clients;

-- La task qui gère le SCD Type 2
CREATE TASK etl.scd2_clients
    WAREHOUSE = etl_wh
    SCHEDULE = '10 MINUTE'
    WHEN SYSTEM$STREAM_HAS_DATA('src.clients_stream')
AS
BEGIN
    -- Fermer les versions périmées
    MERGE INTO analytics.dim_client t
    USING (
        SELECT client_id FROM src.clients_stream
        WHERE METADATA$ACTION = 'INSERT' AND METADATA$ISUPDATE = TRUE
    ) s ON t.client_id = s.client_id AND t.est_courant = TRUE
    WHEN MATCHED THEN
        UPDATE SET t.date_fin = CURRENT_DATE() - 1, t.est_courant = FALSE;

    -- Insérer les nouvelles versions
    INSERT INTO analytics.dim_client (client_id, nom, ville, segment, date_debut)
    SELECT client_id, nom, ville, segment, CURRENT_DATE()
    FROM src.clients_stream
    WHERE METADATA$ACTION = 'INSERT';
END;
```

### Exercices

**Exercice 1** : Implémenter un SCD Type 2 complet pour une dimension `dim_employe` (champs: employe_id, nom, poste, departement, salaire_tranche).

<details>
<summary>Solution</summary>

```sql
CREATE TABLE dim_employe (
    sk_employe INT AUTOINCREMENT,
    employe_id INT,
    nom VARCHAR(100),
    poste VARCHAR(100),
    departement VARCHAR(50),
    salaire_tranche VARCHAR(20),
    date_debut DATE,
    date_fin DATE DEFAULT '9999-12-31',
    est_courant BOOLEAN DEFAULT TRUE
);

-- Procédure de mise à jour
CREATE OR REPLACE PROCEDURE update_dim_employe()
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
BEGIN
    -- Fermer les enregistrements modifiés
    UPDATE dim_employe d
    SET d.date_fin = CURRENT_DATE() - 1, d.est_courant = FALSE
    FROM stg_employe s
    WHERE d.employe_id = s.employe_id
    AND d.est_courant = TRUE
    AND (d.poste != s.poste OR d.departement != s.departement
         OR d.salaire_tranche != s.salaire_tranche);

    -- Insérer nouvelles versions + nouveaux employés
    INSERT INTO dim_employe (employe_id, nom, poste, departement, salaire_tranche, date_debut)
    SELECT s.employe_id, s.nom, s.poste, s.departement, s.salaire_tranche, CURRENT_DATE()
    FROM stg_employe s
    LEFT JOIN dim_employe d ON s.employe_id = d.employe_id AND d.est_courant = TRUE
    WHERE d.sk_employe IS NULL;

    RETURN 'OK';
END;
$$;
```
</details>

**Exercice 2** : Écrire une requête qui retrouve le département d'un client au 15 mars 2025 (SCD Type 2).

<details>
<summary>Solution</summary>

```sql
SELECT client_id, nom, ville, segment
FROM dim_client
WHERE client_id = 42
AND date_debut <= '2025-03-15'
AND date_fin >= '2025-03-15';

-- Ou pour joindre avec un fait à une date spécifique :
SELECT f.*, d.segment
FROM fait_transaction f
JOIN dim_client d ON f.sk_client = d.sk_client
WHERE d.date_debut <= f.date_transaction
AND d.date_fin >= f.date_transaction;
```
</details>

**Exercice 3** : Expliquer quand choisir chaque type de SCD pour un champ `adresse_client` et un champ `date_naissance`.

<details>
<summary>Solution</summary>

```
ADRESSE_CLIENT :
→ SCD Type 2 si on doit analyser les ventes PAR adresse historique
  (ex: "combien de ventes quand le client habitait à Montreal?")
→ SCD Type 1 si seule l'adresse courante importe
  (ex: pour l'envoi de courrier)
→ SCD Type 3 si on veut juste l'adresse précédente
  (ex: pour vérification lors d'un déménagement récent)

DATE_NAISSANCE :
→ SCD Type 0 (ne jamais modifier)
  La date de naissance ne change pas. Si elle est corrigée (erreur de saisie),
  on pourrait utiliser Type 1 (écrasement) car l'ancienne valeur était une erreur.
```
</details>

---

## 4. Concepts ETL / ELT

### ETL vs ELT

```
ETL (Extract-Transform-Load)          ELT (Extract-Load-Transform)
─────────────────────────────          ─────────────────────────────
Source → [Serveur ETL] → DW           Source → DW → [Transformation dans DW]
         ↑ Transform                                  ↑ Transform
         
Transformation AVANT chargement        Transformation APRÈS chargement
Serveur ETL fait le travail            Le DW fait le travail (compute)

✅ Données propres dans le DW          ✅ Plus rapide (pas de goulot serveur)
✅ Moins de stockage DW                ✅ Flexible (re-transformer possible)
❌ Goulot d'étranglement serveur       ✅ Adapté au cloud (Snowflake, BigQuery)
❌ Moins flexible                      ❌ Données brutes dans le DW
```

**Morgan Stanley utilise probablement : ELT** avec Snowflake comme moteur de transformation.

### Extraction

| Méthode | Description | Quand l'utiliser |
|---------|-------------|-----------------|
| **Full Extract** | Extraction complète à chaque fois | Petites tables référentielles |
| **Incremental** | Seulement les lignes modifiées depuis le dernier run | Tables avec timestamp de modification |
| **CDC** | Capture des changements via logs | Temps réel, tables sans timestamp |

```sql
-- Extraction incrémentale avec high watermark
-- Sauvegarder le dernier timestamp traité
SELECT MAX(date_modification) AS watermark FROM audit.last_extract WHERE table_name = 'clients';

-- Extraire les nouvelles données
SELECT * FROM source.clients
WHERE date_modification > :watermark;
```

### Transformation

| Opération | Description | Exemple |
|-----------|-------------|---------|
| **Mapping** | Correspondance champs source → cible | `source.cust_nm` → `target.nom_client` |
| **Cleansing** | Nettoyage des données | Trim, upper/lower, correction formats |
| **Deduplication** | Suppression des doublons | GROUP BY ou QUALIFY ROW_NUMBER |
| **Enrichment** | Ajout de données depuis une référence | Ajout du nom de pays depuis le code |
| **Derivation** | Calcul de nouvelles colonnes | `montant_ttc = montant_ht * 1.15` |
| **Aggregation** | Résumé des données | SUM, AVG, COUNT par période |
| **Pivoting** | Restructuration lignes ↔ colonnes | PIVOT / UNPIVOT |
| **Validation** | Vérification des règles métier | Montant > 0, date dans le futur = rejet |

### Loading

| Méthode | Description | Quand |
|---------|-------------|-------|
| **Full Refresh** | Vider et recharger | Petites tables, données recalculées |
| **Incremental Append** | Ajouter les nouvelles lignes | Faits transactionnels |
| **Upsert (MERGE)** | Insert ou Update | Dimensions (SCD Type 1) |
| **SCD Type 2** | Historisation | Dimensions avec historique |

### Data Quality

```sql
-- Règles de validation
WITH validation AS (
    SELECT
        txn_id,
        -- Complétude
        IFF(client_id IS NULL, 'client_id manquant', NULL) AS err_completude,
        -- Validité
        IFF(montant <= 0, 'montant invalide', NULL) AS err_validite,
        -- Unicité
        IFF(COUNT(*) OVER (PARTITION BY txn_id) > 1, 'doublon', NULL) AS err_unicite,
        -- Cohérence
        IFF(date_transaction > CURRENT_DATE(), 'date future', NULL) AS err_coherence
    FROM staging.transactions
)
SELECT * FROM validation
WHERE err_completude IS NOT NULL
   OR err_validite IS NOT NULL
   OR err_unicite IS NOT NULL
   OR err_coherence IS NOT NULL;
```

### Exercices

**Exercice 1** : Concevoir un pipeline ETL pour charger des données de transactions bancaires depuis un fichier CSV vers une table de faits Snowflake, incluant les étapes de validation et de transformation.

<details>
<summary>Solution</summary>

```sql
-- 1. EXTRACT : Chargement dans staging
COPY INTO staging.raw_transactions
FROM @s3_stage/transactions/
FILE_FORMAT = (FORMAT_NAME = 'csv_format')
ON_ERROR = 'CONTINUE';

-- 2. VALIDATE : Identifier les erreurs
CREATE OR REPLACE TABLE staging.transactions_errors AS
SELECT *, 'montant_negatif' AS erreur
FROM staging.raw_transactions WHERE montant < 0
UNION ALL
SELECT *, 'date_future'
FROM staging.raw_transactions WHERE date_txn > CURRENT_DATE()
UNION ALL
SELECT *, 'client_inconnu'
FROM staging.raw_transactions r
WHERE NOT EXISTS (SELECT 1 FROM dim_client c WHERE c.client_id = r.client_id AND c.est_courant);

-- 3. TRANSFORM : Nettoyer et enrichir
CREATE OR REPLACE TABLE staging.transactions_clean AS
SELECT
    t.txn_id,
    t.client_id,
    dc.sk_client,
    di.sk_instrument,
    dd.date_key,
    ROUND(t.montant, 2) AS montant,
    UPPER(TRIM(t.type_txn)) AS type_txn,
    t.date_txn
FROM staging.raw_transactions t
JOIN dim_client dc ON t.client_id = dc.client_id AND dc.est_courant = TRUE
JOIN dim_instrument di ON t.ticker = di.ticker AND di.is_current = TRUE
JOIN dim_date dd ON DATE(t.date_txn) = dd.full_date
WHERE t.txn_id NOT IN (SELECT txn_id FROM staging.transactions_errors)
AND t.montant > 0;

-- 4. LOAD : Insérer dans la table de faits
INSERT INTO analytics.fait_transaction
SELECT * FROM staging.transactions_clean;

-- 5. AUDIT : Logger le résultat
INSERT INTO audit.etl_log (table_name, rows_loaded, rows_rejected, run_time)
SELECT 'fait_transaction',
       (SELECT COUNT(*) FROM staging.transactions_clean),
       (SELECT COUNT(*) FROM staging.transactions_errors),
       CURRENT_TIMESTAMP();
```
</details>

**Exercice 2** : Implémenter une extraction incrémentale avec gestion du high watermark.

<details>
<summary>Solution</summary>

```sql
-- Table de contrôle des watermarks
CREATE TABLE audit.watermarks (
    table_name VARCHAR(100) PRIMARY KEY,
    last_watermark TIMESTAMP,
    last_run TIMESTAMP
);

-- Procédure d'extraction incrémentale
CREATE OR REPLACE PROCEDURE etl.extract_incremental(source_table VARCHAR, target_table VARCHAR)
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
DECLARE
    v_watermark TIMESTAMP;
    v_new_watermark TIMESTAMP;
    v_count INT;
BEGIN
    -- Récupérer le dernier watermark
    SELECT last_watermark INTO :v_watermark
    FROM audit.watermarks WHERE table_name = :source_table;

    IF (v_watermark IS NULL) THEN
        v_watermark := '1900-01-01'::TIMESTAMP;
    END IF;

    -- Extraire les nouvelles données
    EXECUTE IMMEDIATE
        'INSERT INTO staging.' || :target_table ||
        ' SELECT * FROM source.' || :source_table ||
        ' WHERE updated_at > ''' || :v_watermark || '''';

    -- Mettre à jour le watermark
    EXECUTE IMMEDIATE
        'SELECT MAX(updated_at) FROM staging.' || :target_table
        INTO :v_new_watermark;

    MERGE INTO audit.watermarks t
    USING (SELECT :source_table AS tn, :v_new_watermark AS wm, CURRENT_TIMESTAMP() AS rt) s
    ON t.table_name = s.tn
    WHEN MATCHED THEN UPDATE SET t.last_watermark = s.wm, t.last_run = s.rt
    WHEN NOT MATCHED THEN INSERT VALUES (s.tn, s.wm, s.rt);

    RETURN 'Extracted rows with watermark > ' || :v_watermark;
END;
$$;
```
</details>

**Exercice 3** : Créer un mécanisme de réconciliation qui compare les données source et cible après un chargement ETL.

<details>
<summary>Solution</summary>

```sql
CREATE OR REPLACE PROCEDURE etl.reconciliation(source_table VARCHAR, target_table VARCHAR, date_run DATE)
RETURNS TABLE (check_name VARCHAR, source_value VARCHAR, target_value VARCHAR, status VARCHAR)
LANGUAGE SQL
AS
$$
DECLARE
    res RESULTSET;
BEGIN
    res := (
        SELECT 'row_count' AS check_name,
               src.cnt::VARCHAR AS source_value,
               tgt.cnt::VARCHAR AS target_value,
               IFF(src.cnt = tgt.cnt, 'PASS', 'FAIL') AS status
        FROM (SELECT COUNT(*) AS cnt FROM IDENTIFIER(:source_table) WHERE DATE(date_txn) = :date_run) src,
             (SELECT COUNT(*) AS cnt FROM IDENTIFIER(:target_table) WHERE date_key = TO_NUMBER(TO_CHAR(:date_run, 'YYYYMMDD'))) tgt

        UNION ALL

        SELECT 'sum_amount',
               src.total::VARCHAR,
               tgt.total::VARCHAR,
               IFF(ABS(src.total - tgt.total) < 0.01, 'PASS', 'FAIL')
        FROM (SELECT SUM(montant) AS total FROM IDENTIFIER(:source_table) WHERE DATE(date_txn) = :date_run) src,
             (SELECT SUM(montant_net) AS total FROM IDENTIFIER(:target_table) WHERE date_key = TO_NUMBER(TO_CHAR(:date_run, 'YYYYMMDD'))) tgt
    );
    RETURN TABLE(res);
END;
$$;
```
</details>

---

## 5. Outils ETL : Talend et Informatica (concepts)

### Talend

**Architecture** : Talend génère du code Java à partir d'un environnement graphique. Chaque job = un programme Java compilé.

**Composants principaux :**

| Composant | Rôle |
|-----------|------|
| `tInput` (tFileInputDelimited, tDBInput) | Lire des données depuis une source |
| `tOutput` (tFileOutputDelimited, tDBOutput) | Écrire des données vers une cible |
| `tMap` | Transformation, jointure, filtrage (composant central) |
| `tJoin` | Jointure simple entre deux flux |
| `tAggregateRow` | Agrégation (GROUP BY) |
| `tFilterRow` | Filtrage conditionnel |
| `tUniqRow` | Dédoublonnage |
| `tSortRow` | Tri |
| `tNormalize` / `tDenormalize` | Normalisation/dénormalisation |
| `tLogRow` | Affichage dans la console (debug) |
| `tSnowflakeInput` / `tSnowflakeOutput` | Connexion Snowflake |

**Flux type Talend :**
```
tDBInput → tMap (transformation + jointure) → tDBOutput
              ↑
         tFileInputDelimited (données de référence)
```

### Informatica PowerCenter

**Architecture** : Client-serveur. Les mappings sont exécutés par un moteur central (Integration Service).

| Concept | Description |
|---------|-------------|
| **Source Qualifier** | Lit les données source |
| **Mapping** | Définit les transformations (source → cible) |
| **Session** | Instance d'exécution d'un mapping |
| **Workflow** | Orchestration de sessions (séquence, parallélisme) |
| **Worklet** | Sous-workflow réutilisable |

**Transformations Informatica :**

| Transformation | Rôle | Équivalent SQL |
|----------------|------|----------------|
| Source Qualifier | Lecture source | FROM |
| Filter | Filtrage | WHERE |
| Expression | Calcul de colonnes | SELECT col1*col2 AS... |
| Lookup | Recherche dans une table | LEFT JOIN |
| Joiner | Jointure de 2 flux | JOIN |
| Aggregator | Agrégation | GROUP BY |
| Sorter | Tri | ORDER BY |
| Router | Routage conditionnel | CASE WHEN (vers différentes cibles) |
| Rank | Top-N | ROW_NUMBER / QUALIFY |
| Sequence Generator | Génération de surrogate keys | AUTOINCREMENT |
| Update Strategy | Détermine INSERT/UPDATE/DELETE | MERGE |
| Normalizer / Denormalizer | Restructuration | FLATTEN / PIVOT |

### Comparaison

| Critère | Talend | Informatica | Python (custom) |
|---------|--------|-------------|-----------------|
| Type | Code-generated (Java) | Engine-based | Script |
| Interface | GUI (Studio) | GUI (PowerCenter Client) | Code |
| Performance | Bonne | Excellente | Variable |
| Courbe d'apprentissage | Moyenne | Élevée | Faible (si dev Python) |
| Coût | Open Source (CE) / Payant (EE) | Payant (cher) | Gratuit |
| Snowflake | Connecteur natif | Connecteur natif | snowflake-connector |
| Orchestration | Talend Administration Center | Workflow Manager | Airflow, Cron |
| CDC | Via composants CDC | PowerExchange CDC | Streams Snowflake |

### QCM (10 questions)

**Q1** : Quel composant Talend est utilisé pour les jointures et transformations complexes ?
- a) tJoin  b) tMap  c) tAggregateRow  d) tFilterRow

<details><summary>Réponse</summary>b) tMap — c'est le composant central pour les jointures, transformations, et filtrage dans un seul composant.</details>

**Q2** : Dans Informatica, quelle est la différence entre un Mapping et une Session ?
- a) Aucune différence
- b) Le Mapping définit la logique, la Session est une instance d'exécution
- c) La Session définit la logique, le Mapping est une instance d'exécution
- d) Le Mapping est pour les sources, la Session pour les cibles

<details><summary>Réponse</summary>b) Le Mapping définit la logique de transformation, la Session est une instance d'exécution configurée (connexions, logging, performance).</details>

**Q3** : Quel est l'équivalent Informatica de la clause SQL GROUP BY ?
- a) Sorter  b) Filter  c) Aggregator  d) Joiner

<details><summary>Réponse</summary>c) Aggregator — effectue les agrégations (SUM, COUNT, AVG, etc.) avec regroupement.</details>

**Q4** : Talend génère du code dans quel langage ?
- a) Python  b) SQL  c) Java  d) C++

<details><summary>Réponse</summary>c) Java — les jobs Talend sont compilés en code Java exécutable.</details>

**Q5** : Pour implémenter un SCD Type 2 dans Informatica, quelle transformation est essentielle ?
- a) Filter  b) Lookup + Router + Update Strategy  c) Sorter  d) Expression

<details><summary>Réponse</summary>b) Lookup (vérifier si le record existe), Router (diriger vers insert ou update), Update Strategy (définir l'opération).</details>

**Q6** : ETL vs ELT : dans quel cas ELT est-il préférable ?
- a) Quand la source est un mainframe  b) Quand le DW est cloud (Snowflake)
- c) Quand les données sont très petites  d) Quand on n'a pas de DW

<details><summary>Réponse</summary>b) ELT est idéal avec un DW cloud comme Snowflake qui a une puissance de compute élastique pour les transformations.</details>

**Q7** : Quelle méthode d'extraction est la plus efficace pour les grandes tables transactionnelles ?
- a) Full Extract  b) Incremental (watermark)  c) Toujours CDC  d) Random sampling

<details><summary>Réponse</summary>b) Incremental avec watermark — extrait uniquement les lignes modifiées. CDC est plus complexe mais meilleur pour le temps réel.</details>

**Q8** : Dans Talend, pour dédoublonner des lignes, quel composant utiliser ?
- a) tFilterRow  b) tUniqRow  c) tMap  d) tSortRow

<details><summary>Réponse</summary>b) tUniqRow — supprime les doublons basé sur des colonnes clés.</details>

**Q9** : Qu'est-ce qu'un Workflow dans Informatica PowerCenter ?
- a) Une transformation  b) Un mapping  c) Une orchestration de sessions  d) Un fichier de configuration

<details><summary>Réponse</summary>c) Un Workflow orchestre l'exécution de sessions (séquentiellement ou en parallèle), avec gestion des dépendances et des conditions.</details>

**Q10** : Pour un pipeline en temps réel vers Snowflake, quelle approche est recommandée ?
- a) Talend batch toutes les heures  b) Informatica batch quotidien
- c) Snowpipe + Streams + Tasks  d) Extraction manuelle

<details><summary>Réponse</summary>c) Snowpipe pour le chargement continu, Streams pour le CDC, Tasks pour l'orchestration — solution native Snowflake en quasi temps réel.</details>

---

## 6. Gouvernance et qualité des données

### Data Lineage (Traçabilité)

Le **lineage** trace le parcours des données de la source jusqu'à la consommation.

```
Source (DB2) → Stage (S3) → Raw (Snowflake) → Staging → Analytics → Power BI
     │              │            │                │           │          │
   Extract       Upload       COPY INTO      Transform    Aggregate  Dashboard
```

```sql
-- Dans Snowflake : Access History pour le lineage
SELECT
    query_id,
    user_name,
    direct_objects_accessed,
    base_objects_accessed,
    objects_modified
FROM SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY
WHERE query_start_time >= DATEADD(DAY, -7, CURRENT_TIMESTAMP());
```

### Dimensions de la qualité des données

| Dimension | Description | Vérification |
|-----------|-------------|-------------|
| **Accuracy** | Les données reflètent la réalité | Comparaison avec source |
| **Completeness** | Pas de valeurs manquantes critiques | COUNT NULL / NOT NULL |
| **Consistency** | Cohérence entre systèmes | Jointures croisées |
| **Timeliness** | Données disponibles à temps | SLA de chargement |
| **Uniqueness** | Pas de doublons | COUNT DISTINCT vs COUNT |
| **Validity** | Valeurs dans les plages acceptables | CHECK constraints, regex |

```sql
-- Dashboard de qualité des données
CREATE VIEW data_quality.dashboard AS
SELECT
    'fait_transaction' AS table_name,
    COUNT(*) AS total_rows,
    -- Completeness
    ROUND(COUNT(client_id) * 100.0 / COUNT(*), 2) AS pct_client_complete,
    ROUND(COUNT(montant) * 100.0 / COUNT(*), 2) AS pct_montant_complete,
    -- Uniqueness
    COUNT(DISTINCT txn_id) AS distinct_txn,
    COUNT(*) - COUNT(DISTINCT txn_id) AS doublons,
    -- Validity
    SUM(IFF(montant < 0, 1, 0)) AS montants_negatifs,
    SUM(IFF(date_txn > CURRENT_DATE(), 1, 0)) AS dates_futures,
    -- Timeliness
    MAX(loaded_at) AS dernier_chargement,
    DATEDIFF(MINUTE, MAX(loaded_at), CURRENT_TIMESTAMP()) AS minutes_depuis_chargement
FROM analytics.fait_transaction;
```

### Exercices

**Exercice 1** : Concevoir un framework de règles de qualité pour une table de transactions financières.

<details>
<summary>Solution</summary>

```sql
-- Table de règles de qualité
CREATE TABLE data_quality.rules (
    rule_id INT,
    table_name VARCHAR(100),
    rule_name VARCHAR(100),
    rule_type VARCHAR(20),       -- 'completeness', 'validity', 'uniqueness', etc.
    sql_check VARCHAR(2000),
    threshold_pct DECIMAL(5,2),  -- Seuil d'acceptabilité (ex: 99.5%)
    severity VARCHAR(10)         -- 'CRITICAL', 'WARNING', 'INFO'
);

INSERT INTO data_quality.rules VALUES
(1, 'fait_transaction', 'client_id_not_null', 'completeness',
 'SELECT COUNT(*) FILTER (WHERE client_id IS NULL) * 100.0 / COUNT(*) FROM fait_transaction',
 0.1, 'CRITICAL'),
(2, 'fait_transaction', 'montant_positif', 'validity',
 'SELECT COUNT(*) FILTER (WHERE montant <= 0) * 100.0 / COUNT(*) FROM fait_transaction',
 0.0, 'CRITICAL'),
(3, 'fait_transaction', 'txn_id_unique', 'uniqueness',
 'SELECT (COUNT(*) - COUNT(DISTINCT txn_id)) * 100.0 / COUNT(*) FROM fait_transaction',
 0.0, 'CRITICAL'),
(4, 'fait_transaction', 'date_valide', 'validity',
 'SELECT COUNT(*) FILTER (WHERE date_txn > CURRENT_DATE() OR date_txn < ''2000-01-01'') * 100.0 / COUNT(*) FROM fait_transaction',
 0.0, 'WARNING');
```
</details>

**Exercice 2** : Créer un processus de réconciliation source-cible automatisé.

<details>
<summary>Solution</summary>

```sql
-- Procédure de réconciliation
CREATE OR REPLACE PROCEDURE data_quality.reconcile(
    source_table VARCHAR, target_table VARCHAR, join_key VARCHAR, date_col VARCHAR, run_date DATE
)
RETURNS TABLE (metric VARCHAR, source_val VARCHAR, target_val VARCHAR, match BOOLEAN)
LANGUAGE SQL
AS
$$
BEGIN
    RETURN TABLE(
        -- Row count
        SELECT 'row_count' AS metric,
               (SELECT COUNT(*)::VARCHAR FROM IDENTIFIER(:source_table)
                WHERE IDENTIFIER(:date_col) = :run_date) AS source_val,
               (SELECT COUNT(*)::VARCHAR FROM IDENTIFIER(:target_table)
                WHERE IDENTIFIER(:date_col) = :run_date) AS target_val,
               source_val = target_val AS match

        UNION ALL

        -- Missing in target
        SELECT 'missing_in_target',
               (SELECT COUNT(*)::VARCHAR FROM IDENTIFIER(:source_table) s
                WHERE s.IDENTIFIER(:date_col) = :run_date
                AND NOT EXISTS (SELECT 1 FROM IDENTIFIER(:target_table) t
                                WHERE t.IDENTIFIER(:join_key) = s.IDENTIFIER(:join_key))),
               '0', source_val = '0'
    );
END;
$$;
```
</details>

**Exercice 3** : Implémenter un système de scoring de qualité des données (note globale 0-100%).

<details>
<summary>Solution</summary>

```sql
CREATE OR REPLACE VIEW data_quality.score_global AS
WITH checks AS (
    SELECT
        -- Complétude (poids: 30%)
        (COUNT(client_id) + COUNT(montant) + COUNT(date_txn)) * 100.0 /
        (COUNT(*) * 3) AS completeness_score,
        -- Unicité (poids: 25%)
        COUNT(DISTINCT txn_id) * 100.0 / NULLIF(COUNT(*), 0) AS uniqueness_score,
        -- Validité (poids: 25%)
        (COUNT(*) - SUM(IFF(montant <= 0 OR date_txn > CURRENT_DATE(), 1, 0))) * 100.0 /
        NULLIF(COUNT(*), 0) AS validity_score,
        -- Fraîcheur (poids: 20%)
        IFF(DATEDIFF(HOUR, MAX(loaded_at), CURRENT_TIMESTAMP()) <= 24, 100,
            GREATEST(0, 100 - DATEDIFF(HOUR, MAX(loaded_at), CURRENT_TIMESTAMP()))) AS timeliness_score
    FROM analytics.fait_transaction
)
SELECT
    ROUND(completeness_score, 2) AS completude,
    ROUND(uniqueness_score, 2) AS unicite,
    ROUND(validity_score, 2) AS validite,
    ROUND(timeliness_score, 2) AS fraicheur,
    ROUND(
        completeness_score * 0.30 +
        uniqueness_score * 0.25 +
        validity_score * 0.25 +
        timeliness_score * 0.20, 2
    ) AS score_global
FROM checks;
```
</details>

---

## 7. Patterns d'architecture de données

### Comparaison

| Concept | Stockage | Traitement | Cas d'usage |
|---------|----------|------------|-------------|
| **Data Warehouse** | Structuré (SQL) | ETL batch | BI, reporting |
| **Data Lake** | Brut (fichiers) | Schema-on-read | Data science, exploration |
| **Data Lakehouse** | Hybride (Delta/Iceberg) | ETL + streaming | Tous |

### Medallion Architecture (Bronze / Silver / Gold)

```
┌─────────┐     ┌─────────┐     ┌──────────┐
│ BRONZE  │ ──→ │ SILVER  │ ──→ │  GOLD    │
│ (Raw)   │     │ (Clean) │     │ (Business)│
└─────────┘     └─────────┘     └──────────┘
  Données         Nettoyé,        Agrégé,
  brutes,         dédoublonné,    modélisé,
  telles que      typé,           prêt pour
  reçues          validé          l'analyse
```

```sql
-- Implémentation Snowflake
CREATE SCHEMA bronze;   -- raw.
CREATE SCHEMA silver;   -- staging.
CREATE SCHEMA gold;     -- analytics.

-- Bronze : chargement brut
CREATE TABLE bronze.transactions_raw (
    raw_data VARIANT,
    source VARCHAR(50),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Silver : nettoyé et typé
CREATE TABLE silver.transactions_clean (
    txn_id INT,
    client_id INT,
    montant DECIMAL(18,2),
    date_txn TIMESTAMP,
    type_txn VARCHAR(20),
    loaded_at TIMESTAMP
);

-- Gold : modèle dimensionnel
CREATE TABLE gold.fait_transaction (...);  -- Star schema
CREATE TABLE gold.dim_client (...);
```

### Data Vault 2.0

```
┌─────────┐     ┌─────────┐     ┌───────────┐
│   HUB   │ ←── │  LINK   │ ──→ │    HUB    │
│ (Client)│     │(Client- │     │ (Compte)  │
│   BK    │     │ Compte) │     │    BK     │
└─────────┘     └─────────┘     └───────────┘
     │                                │
     ↓                                ↓
┌─────────┐                    ┌───────────┐
│   SAT   │                    │    SAT    │
│(Client  │                    │ (Compte   │
│ détails)│                    │  détails) │
└─────────┘                    └───────────┘

Hub = Business keys (identifiants métier)
Link = Relations entre Hubs
Satellite = Attributs descriptifs (historisés)
```

```sql
-- Hub (business key + metadata)
CREATE TABLE hub_client (
    h_client_key BINARY(32),     -- Hash de la business key
    client_id INT,                -- Business key
    load_date TIMESTAMP,
    record_source VARCHAR(50)
);

-- Satellite (attributs, historisés)
CREATE TABLE sat_client_details (
    h_client_key BINARY(32),
    load_date TIMESTAMP,
    nom VARCHAR(100),
    ville VARCHAR(50),
    segment VARCHAR(20),
    hash_diff BINARY(32),        -- Hash des attributs (pour détecter les changements)
    record_source VARCHAR(50)
);

-- Link (relation)
CREATE TABLE link_client_compte (
    h_link_key BINARY(32),
    h_client_key BINARY(32),
    h_compte_key BINARY(32),
    load_date TIMESTAMP,
    record_source VARCHAR(50)
);
```

### Exercices

**Exercice 1** : Concevoir une architecture Medallion pour les données de Morgan Stanley (transactions marché, données clients, données de référence instruments).

<details>
<summary>Solution</summary>

```sql
-- BRONZE (raw) : données telles que reçues
CREATE TABLE bronze.market_ticks (raw VARIANT, source VARCHAR, loaded_at TIMESTAMP);
CREATE TABLE bronze.client_feed (raw VARIANT, source VARCHAR, loaded_at TIMESTAMP);
CREATE TABLE bronze.instrument_ref (raw VARIANT, source VARCHAR, loaded_at TIMESTAMP);

-- SILVER (clean) : nettoyé, typé, validé
CREATE TABLE silver.transactions (
    txn_id INT, client_id INT, ticker VARCHAR(10),
    type_txn VARCHAR(10), quantite DECIMAL(18,4),
    prix DECIMAL(18,6), date_txn TIMESTAMP,
    _loaded_at TIMESTAMP, _source VARCHAR
);
CREATE TABLE silver.clients (
    client_id INT, nom VARCHAR, segment VARCHAR, ville VARCHAR,
    _loaded_at TIMESTAMP, _is_current BOOLEAN
);
CREATE TABLE silver.instruments (
    ticker VARCHAR, nom VARCHAR, type VARCHAR, devise VARCHAR,
    _loaded_at TIMESTAMP
);

-- GOLD (business) : modèle dimensionnel pour l'analyse
CREATE TABLE gold.dim_date (...);
CREATE TABLE gold.dim_client (...);       -- SCD Type 2
CREATE TABLE gold.dim_instrument (...);
CREATE TABLE gold.dim_compte (...);
CREATE TABLE gold.fait_transaction (...); -- Star schema
CREATE TABLE gold.fait_position_daily (...); -- Periodic snapshot

-- Streams et Tasks pour automatiser Bronze → Silver → Gold
```
</details>

**Exercice 2** : Comparer Lambda et Kappa architecture. Laquelle est mieux adaptée pour Morgan Stanley et pourquoi ?

<details>
<summary>Solution</summary>

```
LAMBDA ARCHITECTURE :
┌──────────────────────────────────────┐
│ Source → Batch Layer (historique)     │→ Serving Layer → Query
│       → Speed Layer (temps réel)     │→               →
└──────────────────────────────────────┘
- Deux pipelines séparés (batch + streaming)
- Complexité de maintenance (code dupliqué)
- Résultats cohérents une fois le batch terminé

KAPPA ARCHITECTURE :
┌──────────────────────────────────────┐
│ Source → Stream Processing → Serving │→ Query
│          (un seul pipeline)          │
└──────────────────────────────────────┘
- Un seul pipeline (streaming)
- Plus simple à maintenir
- Reprocessing en rejouant le stream

POUR MORGAN STANLEY :
→ Lambda est plus adapté car :
1. Les données financières nécessitent une réconciliation batch précise
   (les positions de fin de journée doivent être exactes)
2. Le batch layer assure la cohérence réglementaire
3. Le speed layer fournit les données en quasi temps réel pour le trading
4. La complexité est justifiée par les exigences réglementaires

En pratique avec Snowflake :
- Batch : Tasks + COPY INTO (nuit)
- Speed : Snowpipe + Streams (continu)
- Serving : Materialized Views + dim/fact tables
```
</details>

**Exercice 3** : Quand utiliser Data Vault vs Star Schema ?

<details>
<summary>Solution</summary>

```
DATA VAULT :
✅ Quand : multiples sources à intégrer, besoin d'auditabilité complète,
           environnement réglementé, schéma source changeant fréquemment
✅ Avantages : chargement parallèle, historique complet, traçabilité
❌ Inconvénients : requêtes complexes (beaucoup de JOINs), performance lecture

STAR SCHEMA :
✅ Quand : reporting/BI, requêtes analytiques, performance de lecture critique
✅ Avantages : simple à comprendre, requêtes rapides, Power BI friendly
❌ Inconvénients : transformation complexe pour le chargement, moins flexible

POUR MORGAN STANLEY :
→ Data Vault dans la couche d'intégration (Silver)
  - Intègre les données de multiples sources (DB2, APIs, fichiers)
  - Maintient l'auditabilité (exigence réglementaire)
  - Facilite le chargement parallèle

→ Star Schema dans la couche de présentation (Gold)
  - Alimente Power BI avec des modèles simples
  - Performance optimale pour le reporting
  - Modèles sémantiques pour les utilisateurs métier
```
</details>

---

## 8. Migration RDBMS vers Cloud (DB2 → Snowflake)

### Mapping des types DB2 → Snowflake

| DB2 | Snowflake | Notes |
|-----|-----------|-------|
| SMALLINT | NUMBER(5,0) | |
| INTEGER | NUMBER(10,0) | |
| BIGINT | NUMBER(19,0) | |
| DECIMAL(p,s) | NUMBER(p,s) | |
| REAL | FLOAT | |
| DOUBLE | FLOAT | |
| CHAR(n) | CHAR(n) | Max 16MB dans Snowflake |
| VARCHAR(n) | VARCHAR(n) | |
| CLOB | VARCHAR(16777216) | Max 16MB |
| DATE | DATE | |
| TIME | TIME | |
| TIMESTAMP | TIMESTAMP_NTZ | Vérifier timezone |
| BLOB | BINARY | |
| XML | VARIANT | Via PARSE_JSON/PARSE_XML |

### Conversion de procédures stockées

```sql
-- DB2
CREATE PROCEDURE calc_balance(IN p_account INT, OUT p_balance DECIMAL)
BEGIN
    SELECT SUM(CASE WHEN type = 'CREDIT' THEN amount ELSE -amount END)
    INTO p_balance
    FROM transactions
    WHERE account_id = p_account;
END;

-- Snowflake
CREATE OR REPLACE PROCEDURE calc_balance(p_account INT)
RETURNS DECIMAL(18,2)
LANGUAGE SQL
AS
$$
DECLARE
    p_balance DECIMAL(18,2);
BEGIN
    SELECT SUM(IFF(type = 'CREDIT', amount, -amount))
    INTO :p_balance
    FROM transactions
    WHERE account_id = :p_account;
    RETURN p_balance;
END;
$$;
```

### Checklist de migration détaillée

```
PHASE 1 — ASSESSMENT (1-2 semaines)
□ Inventaire complet des objets DB2
  □ Tables (nombre, taille, partitionnement)
  □ Vues
  □ Procédures stockées et fonctions
  □ Triggers
  □ Séquences
  □ Index
□ Analyse des dépendances entre objets
□ Identification des types non supportés directement
□ Estimation du volume de données total
□ Identification des fenêtres de migration (downtime acceptable)

PHASE 2 — DESIGN (1-2 semaines)
□ Mapping des types de données
□ Conception de l'architecture cible (schemas, warehouses)
□ Plan de sécurité (rôles, policies)
□ Stratégie de chargement (full vs incrémental)
□ Plan de test et validation

PHASE 3 — BUILD (2-4 semaines)
□ Création de l'infrastructure Snowflake
□ Conversion DDL (tables, vues)
□ Conversion des procédures stockées
□ Développement des pipelines de chargement
□ Tests unitaires

PHASE 4 — MIGRATION (1-2 semaines)
□ Chargement initial des données
□ Validation (row counts, checksums, sampling)
□ Migration des données delta (changements pendant la migration)
□ Tests de performance
□ Tests fonctionnels (rapports, dashboards)

PHASE 5 — CUTOVER
□ Gel des modifications source
□ Migration finale delta
□ Validation finale
□ Redirection des applications
□ Monitoring intensif (72h)
□ Rollback plan si problèmes
```

### Exercices

**Exercice 1** : Écrire le script de migration DDL pour convertir 3 tables DB2 en Snowflake.

<details>
<summary>Solution</summary>

```sql
-- DB2 source
-- CREATE TABLE DB2.ACCOUNTS (
--     ACCOUNT_ID INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
--     CUSTOMER_ID INTEGER NOT NULL,
--     ACCOUNT_TYPE CHAR(3) NOT NULL,
--     BALANCE DECIMAL(15,2) DEFAULT 0,
--     OPEN_DATE DATE NOT NULL,
--     STATUS CHAR(1) DEFAULT 'A',
--     LAST_ACTIVITY TIMESTAMP
-- )

-- Snowflake cible
CREATE TABLE accounts (
    account_id INT AUTOINCREMENT NOT NULL,
    customer_id INT NOT NULL,
    account_type CHAR(3) NOT NULL,
    balance NUMBER(15,2) DEFAULT 0,
    open_date DATE NOT NULL,
    status CHAR(1) DEFAULT 'A',
    last_activity TIMESTAMP_NTZ,
    -- Metadata migration
    _migrated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    _source_system VARCHAR DEFAULT 'DB2_PROD'
);

-- Index DB2 → Clustering key Snowflake (si pertinent)
ALTER TABLE accounts CLUSTER BY (open_date);
```
</details>

**Exercice 2** : Concevoir un plan de validation post-migration avec des requêtes de comparaison.

<details>
<summary>Solution</summary>

```sql
-- Script de validation exhaustif
CREATE OR REPLACE PROCEDURE migration.validate_table(table_name VARCHAR)
RETURNS TABLE (check_name VARCHAR, db2_value VARCHAR, sf_value VARCHAR, status VARCHAR)
LANGUAGE SQL
AS
$$
BEGIN
    RETURN TABLE(
        -- 1. Row count
        SELECT 'Row Count', db2.cnt::VARCHAR, sf.cnt::VARCHAR,
               IFF(db2.cnt = sf.cnt, 'PASS', 'FAIL')
        FROM migration.db2_counts db2
        JOIN (SELECT COUNT(*) cnt FROM IDENTIFIER(:table_name)) sf
        ON db2.table_name = :table_name

        UNION ALL

        -- 2. Null count per column
        SELECT 'Null check - ' || column_name,
               db2_nulls::VARCHAR, sf_nulls::VARCHAR,
               IFF(db2_nulls = sf_nulls, 'PASS', 'FAIL')
        FROM migration.null_comparison
        WHERE table_name = :table_name

        UNION ALL

        -- 3. Min/Max dates
        SELECT 'Date range', db2_range, sf_range,
               IFF(db2_range = sf_range, 'PASS', 'FAIL')
        FROM migration.date_range_comparison
        WHERE table_name = :table_name
    );
END;
$$;
```
</details>

---

## 9. Modèles sémantiques (Snowflake + Power BI)

### Couche sémantique Snowflake

```sql
-- Vues métier (couche sémantique dans Snowflake)
CREATE VIEW semantic.v_ventes_quotidiennes AS
SELECT
    dd.full_date AS date_vente,
    dd.nom_jour,
    dd.nom_mois,
    dd.trimestre,
    dc.nom AS client,
    dc.segment,
    dc.ville,
    dp.nom_produit,
    dp.categorie,
    ft.montant_net AS montant,
    ft.quantite,
    ft.commission
FROM gold.fait_transaction ft
JOIN gold.dim_date dd ON ft.date_key = dd.date_key
JOIN gold.dim_client dc ON ft.sk_client = dc.sk_client AND dc.est_courant = TRUE
JOIN gold.dim_produit dp ON ft.sk_produit = dp.sk_produit;
```

### Modèle sémantique Power BI

```
Power BI se connecte à Snowflake via :
1. Import Mode : données chargées dans Power BI (rapide mais copie)
2. DirectQuery : requêtes en temps réel vers Snowflake (toujours à jour)
3. Composite Model : mix des deux

Bonnes pratiques :
- Utiliser des vues Snowflake comme couche sémantique
- Créer les relations dans Power BI (star schema)
- Mesures DAX pour les KPIs
```

**Mesures DAX essentielles :**
```dax
// Mesure de ventes totales
Total Ventes = SUM(fait_transaction[montant])

// Mesure YTD (Year-to-Date)
Ventes YTD = TOTALYTD(SUM(fait_transaction[montant]), dim_date[full_date])

// Mesure comparaison année précédente
Ventes Année Précédente = CALCULATE(
    SUM(fait_transaction[montant]),
    SAMEPERIODLASTYEAR(dim_date[full_date])
)

// Variation %
Variation % = DIVIDE(
    [Total Ventes] - [Ventes Année Précédente],
    [Ventes Année Précédente],
    0
)

// Moyenne mobile 3 mois
Moy Mobile 3M = AVERAGEX(
    DATESINPERIOD(dim_date[full_date], LASTDATE(dim_date[full_date]), -3, MONTH),
    CALCULATE(SUM(fait_transaction[montant]))
)
```

### Exercices

**Exercice 1** : Concevoir la couche sémantique Snowflake pour un dashboard de performance de portefeuille.

<details>
<summary>Solution</summary>

```sql
CREATE VIEW semantic.v_portfolio_performance AS
SELECT
    dd.full_date,
    dd.nom_mois,
    dd.trimestre,
    dc.nom AS client,
    dc.segment,
    dco.numero_compte,
    dco.type_compte,
    di.ticker,
    di.nom_instrument,
    di.type_instrument,
    di.secteur,
    fp.quantite,
    fp.valeur_marche,
    fp.cout_base,
    fp.valeur_marche - fp.cout_base AS pnl_non_realise,
    ROUND((fp.valeur_marche - fp.cout_base) / NULLIF(fp.cout_base, 0) * 100, 2) AS rendement_pct,
    fp.pnl_jour
FROM gold.fait_position_daily fp
JOIN gold.dim_date dd ON fp.date_key = dd.date_key
JOIN gold.dim_client dc ON fp.sk_client = dc.sk_client AND dc.est_courant
JOIN gold.dim_compte dco ON fp.sk_compte = dco.sk_compte
JOIN gold.dim_instrument di ON fp.sk_instrument = di.sk_instrument;
```
</details>

**Exercice 2** : Écrire les mesures DAX pour un dashboard RH (effectif, taux de rotation, ancienneté moyenne).

<details>
<summary>Solution</summary>

```dax
// Effectif actif
Effectif Actif = COUNTROWS(
    FILTER(dim_employe, dim_employe[est_courant] = TRUE)
)

// Taux de rotation (turnover) sur 12 mois
Taux Rotation = DIVIDE(
    COUNTROWS(
        FILTER(dim_employe,
            dim_employe[date_depart] >= TODAY() - 365
            && dim_employe[date_depart] <= TODAY()
        )
    ),
    [Effectif Actif],
    0
)

// Ancienneté moyenne (en années)
Ancienneté Moyenne = AVERAGEX(
    FILTER(dim_employe, dim_employe[est_courant] = TRUE),
    DATEDIFF(dim_employe[date_embauche], TODAY(), YEAR)
)

// Coût salarial par département
Coût Salarial Dept = SUMX(
    FILTER(dim_employe, dim_employe[est_courant] = TRUE),
    dim_employe[salaire]
)
```
</details>

---

## 10. Exercices de synthèse

### Exercice de synthèse 1 : Conception complète d'un data warehouse (Hard)

**Énoncé** : Morgan Stanley vous demande de concevoir le modèle dimensionnel pour un nouveau data mart "Gestion de patrimoine" qui doit répondre à ces questions :
- Quelle est la performance de chaque portefeuille par période ?
- Quels sont les flux nets (entrées - sorties) par client et par mois ?
- Quel est le taux de rétention des clients par segment ?

Concevoir : les tables de faits, les dimensions, le DDL Snowflake complet.

<details>
<summary>Solution</summary>

```sql
-- DIMENSIONS
CREATE TABLE gold.dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE, jour INT, mois INT, trimestre INT, annee INT,
    nom_jour VARCHAR(10), nom_mois VARCHAR(15),
    est_jour_ouvre BOOLEAN, est_fin_mois BOOLEAN, est_fin_trimestre BOOLEAN
);

CREATE TABLE gold.dim_client (
    sk_client INT AUTOINCREMENT PRIMARY KEY,
    client_id INT, nom VARCHAR(100), segment VARCHAR(20),
    date_relation DATE, gestionnaire VARCHAR(100),
    tranche_age VARCHAR(20), region VARCHAR(50),
    date_debut DATE, date_fin DATE DEFAULT '9999-12-31', est_courant BOOLEAN DEFAULT TRUE
);

CREATE TABLE gold.dim_portefeuille (
    sk_portefeuille INT AUTOINCREMENT PRIMARY KEY,
    portefeuille_id INT, nom VARCHAR(100),
    strategie VARCHAR(50), profil_risque VARCHAR(20),
    devise_base VARCHAR(3), benchmark VARCHAR(50)
);

CREATE TABLE gold.dim_type_flux (
    sk_type_flux INT PRIMARY KEY,
    code_flux VARCHAR(20),     -- 'DEPOT', 'RETRAIT', 'DIVIDENDE', 'FEE'
    categorie VARCHAR(20),      -- 'ENTREE', 'SORTIE'
    description VARCHAR(200)
);

-- FAITS
-- 1. Performance portefeuille (periodic snapshot)
CREATE TABLE gold.fait_performance_portefeuille (
    date_key INT,
    sk_client INT,
    sk_portefeuille INT,
    valeur_marche DECIMAL(18,2),           -- Semi-additif
    cout_base DECIMAL(18,2),               -- Semi-additif
    pnl_jour DECIMAL(18,2),               -- Additif
    pnl_cumule DECIMAL(18,2),             -- Semi-additif
    rendement_jour_pct DECIMAL(8,4),
    rendement_cumule_pct DECIMAL(8,4),
    PRIMARY KEY (date_key, sk_client, sk_portefeuille)
);

-- 2. Flux financiers (transactionnel)
CREATE TABLE gold.fait_flux (
    flux_key BIGINT AUTOINCREMENT,
    date_key INT,
    sk_client INT,
    sk_portefeuille INT,
    sk_type_flux INT,
    montant DECIMAL(18,2),
    devise VARCHAR(3),
    reference VARCHAR(50)
);

-- 3. Rétention client (accumulating snapshot)
CREATE TABLE gold.fait_retention_client (
    sk_client INT PRIMARY KEY,
    date_premiere_relation_key INT,
    date_derniere_activite_key INT,
    date_depart_key INT,                    -- NULL si actif
    aum_premier_mois DECIMAL(18,2),
    aum_actuel DECIMAL(18,2),
    nb_mois_relation INT,
    est_actif BOOLEAN
);

-- VUES SÉMANTIQUES
CREATE VIEW semantic.v_flux_nets_mensuels AS
SELECT
    dd.annee, dd.mois, dd.nom_mois,
    dc.nom AS client, dc.segment,
    SUM(IFF(dtf.categorie = 'ENTREE', ff.montant, 0)) AS total_entrees,
    SUM(IFF(dtf.categorie = 'SORTIE', ff.montant, 0)) AS total_sorties,
    SUM(IFF(dtf.categorie = 'ENTREE', ff.montant, -ff.montant)) AS flux_net
FROM gold.fait_flux ff
JOIN gold.dim_date dd ON ff.date_key = dd.date_key
JOIN gold.dim_client dc ON ff.sk_client = dc.sk_client AND dc.est_courant
JOIN gold.dim_type_flux dtf ON ff.sk_type_flux = dtf.sk_type_flux
GROUP BY dd.annee, dd.mois, dd.nom_mois, dc.nom, dc.segment;
```
</details>

### Exercice de synthèse 2 : Pipeline ETL complet (Hard)

**Énoncé** : Écrire le pipeline Snowflake complet (DDL + streams + tasks) pour :
1. Charger des données JSON depuis S3 (Bronze)
2. Nettoyer et valider (Silver)
3. Alimenter un modèle dimensionnel (Gold)

<details>
<summary>Solution</summary>

```sql
-- BRONZE
CREATE TABLE bronze.raw_orders (
    raw VARIANT,
    _source VARCHAR DEFAULT 'S3_ORDERS',
    _loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

CREATE PIPE bronze.orders_pipe AUTO_INGEST = TRUE AS
COPY INTO bronze.raw_orders (raw)
FROM @s3_orders_stage
FILE_FORMAT = (TYPE = 'JSON' STRIP_OUTER_ARRAY = TRUE);

-- SILVER
CREATE TABLE silver.orders (
    order_id INT, client_id INT, ticker VARCHAR(10),
    type_op VARCHAR(10), quantite DECIMAL(18,4),
    prix DECIMAL(18,6), date_order TIMESTAMP,
    _is_valid BOOLEAN, _error_msg VARCHAR,
    _loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

CREATE STREAM bronze.orders_stream ON TABLE bronze.raw_orders;

CREATE TASK silver.clean_orders
    WAREHOUSE = etl_wh
    SCHEDULE = '5 MINUTE'
    WHEN SYSTEM$STREAM_HAS_DATA('bronze.orders_stream')
AS
INSERT INTO silver.orders
SELECT
    raw:order_id::INT,
    raw:client_id::INT,
    raw:ticker::STRING,
    UPPER(raw:type::STRING),
    raw:quantity::DECIMAL(18,4),
    raw:price::DECIMAL(18,6),
    TRY_TO_TIMESTAMP(raw:timestamp::STRING),
    -- Validation
    raw:order_id IS NOT NULL
    AND raw:client_id IS NOT NULL
    AND TRY_TO_DECIMAL(raw:quantity::STRING) > 0
    AND TRY_TO_TIMESTAMP(raw:timestamp::STRING) IS NOT NULL AS _is_valid,
    CASE
        WHEN raw:order_id IS NULL THEN 'Missing order_id'
        WHEN TRY_TO_DECIMAL(raw:quantity::STRING) <= 0 THEN 'Invalid quantity'
        ELSE NULL
    END,
    CURRENT_TIMESTAMP()
FROM bronze.orders_stream
WHERE METADATA$ACTION = 'INSERT';

-- GOLD
CREATE STREAM silver.orders_stream ON TABLE silver.orders;

CREATE TASK gold.load_fait_transaction
    WAREHOUSE = etl_wh
    AFTER silver.clean_orders
AS
INSERT INTO gold.fait_transaction (date_key, sk_client, sk_instrument, quantite, prix, montant_net, type_operation)
SELECT
    TO_NUMBER(TO_CHAR(s.date_order, 'YYYYMMDD')),
    dc.sk_client,
    di.sk_instrument,
    s.quantite,
    s.prix,
    s.quantite * s.prix,
    s.type_op
FROM silver.orders_stream s
JOIN gold.dim_client dc ON s.client_id = dc.client_id AND dc.est_courant = TRUE
JOIN gold.dim_instrument di ON s.ticker = di.ticker AND di.is_current = TRUE
WHERE s._is_valid = TRUE
AND METADATA$ACTION = 'INSERT';

-- Activer le DAG
ALTER TASK gold.load_fait_transaction RESUME;
ALTER TASK silver.clean_orders RESUME;
```
</details>

### Exercice de synthèse 3 : Questions d'entretien Data Modeling (Hard)

**Question** : Expliquez la différence entre un fait transactionnel, un periodic snapshot et un accumulating snapshot. Donnez un exemple de chaque dans le contexte bancaire Morgan Stanley.

<details>
<summary>Solution</summary>

```
1. FAIT TRANSACTIONNEL
   - Une ligne par événement atomique
   - Le grain est l'événement individuel
   - Mesures additives
   
   Exemple MS : fait_transaction_marche
   - Chaque achat/vente d'instrument est une ligne
   - Grain : une transaction
   - Mesures : quantité, prix, montant, commission
   - On peut SUM(montant) sur toutes les dimensions

2. PERIODIC SNAPSHOT
   - Une ligne par entité par période
   - Photo régulière de l'état
   - Mesures semi-additives (soldes)
   
   Exemple MS : fait_position_quotidienne
   - Une ligne par compte × instrument × jour
   - Grain : position quotidienne
   - Mesures : quantité détenue (semi-additif), valeur marché (semi-additif),
               P&L du jour (additif)
   - ATTENTION : SUM(valeur_marche) n'a de sens QUE pour un jour donné,
                 pas en additionnant les jours

3. ACCUMULATING SNAPSHOT
   - Une ligne par instance de processus
   - Mise à jour à chaque étape franchie
   - Dates jalons multiples
   
   Exemple MS : fait_ouverture_compte
   - Une ligne par demande d'ouverture de compte
   - Colonnes : date_demande, date_kyc, date_approbation, date_activation
   - Mesures : durée entre étapes, montant dépôt initial
   - La ligne est MISE À JOUR quand le processus avance
```
</details>

---

> **Conseils pour le test** :
> - Connaître la différence Star Schema vs Snowflake Schema et quand utiliser chaque
> - Maîtriser SCD Type 1 et Type 2 (implémenter avec MERGE)
> - Comprendre ETL vs ELT dans le contexte Snowflake
> - Savoir concevoir un modèle dimensionnel à partir d'un besoin métier
> - Les questions de gouvernance (masking, row access policies) sont probables pour un poste Morgan Stanley
