-- =============================================================
-- BASE : etl_warehouse — Tables pour exercices ETL / Data Modeling
-- =============================================================

\c etl_warehouse;

-- ==================== ZONE STAGING (raw) ====================

CREATE SCHEMA staging;

CREATE TABLE staging.raw_clients (
    raw_id SERIAL PRIMARY KEY,
    data_source VARCHAR(50),
    client_id VARCHAR(50),
    nom VARCHAR(200),
    email VARCHAR(200),
    telephone VARCHAR(50),
    adresse TEXT,
    ville VARCHAR(100),
    pays VARCHAR(50),
    segment VARCHAR(50),
    date_inscription VARCHAR(50),  -- VARCHAR volontairement (donnees sales)
    loaded_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE staging.raw_produits (
    raw_id SERIAL PRIMARY KEY,
    data_source VARCHAR(50),
    produit_id VARCHAR(50),
    nom VARCHAR(200),
    categorie VARCHAR(100),
    sous_categorie VARCHAR(100),
    prix_unitaire VARCHAR(50),  -- VARCHAR pour donnees sales
    loaded_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE staging.raw_transactions (
    raw_id SERIAL PRIMARY KEY,
    data_source VARCHAR(50),
    transaction_id VARCHAR(50),
    client_id VARCHAR(50),
    produit_id VARCHAR(50),
    quantite VARCHAR(20),
    montant VARCHAR(50),
    date_transaction VARCHAR(50),
    canal VARCHAR(50),
    statut VARCHAR(30),
    loaded_at TIMESTAMP DEFAULT NOW()
);

-- ==================== ZONE DWH (modele etoile) ====================

CREATE SCHEMA dwh;

-- Dimension Date
CREATE TABLE dwh.dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE UNIQUE NOT NULL,
    jour INT,
    mois INT,
    trimestre INT,
    annee INT,
    nom_jour VARCHAR(10),
    nom_mois VARCHAR(15),
    est_jour_ouvre BOOLEAN,
    est_fin_mois BOOLEAN,
    semaine_iso INT
);

-- Remplir dim_date sur 3 ans
INSERT INTO dwh.dim_date
SELECT
    TO_CHAR(d, 'YYYYMMDD')::INT AS date_key,
    d AS full_date,
    EXTRACT(DAY FROM d)::INT,
    EXTRACT(MONTH FROM d)::INT,
    EXTRACT(QUARTER FROM d)::INT,
    EXTRACT(YEAR FROM d)::INT,
    TO_CHAR(d, 'Dy'),
    TO_CHAR(d, 'Mon'),
    EXTRACT(DOW FROM d) NOT IN (0, 6),
    d = (DATE_TRUNC('month', d) + INTERVAL '1 month - 1 day')::DATE,
    EXTRACT(WEEK FROM d)::INT
FROM generate_series('2022-01-01'::date, '2025-12-31'::date, '1 day') AS d;

-- Dimension Client (SCD Type 2)
CREATE TABLE dwh.dim_client (
    client_key SERIAL PRIMARY KEY,
    client_id VARCHAR(50) NOT NULL,
    nom VARCHAR(200),
    email VARCHAR(200),
    ville VARCHAR(100),
    pays VARCHAR(50),
    segment VARCHAR(50),
    date_debut DATE NOT NULL,
    date_fin DATE DEFAULT '9999-12-31',
    est_courant BOOLEAN DEFAULT TRUE
);

-- Dimension Produit
CREATE TABLE dwh.dim_produit (
    produit_key SERIAL PRIMARY KEY,
    produit_id VARCHAR(50) NOT NULL,
    nom VARCHAR(200),
    categorie VARCHAR(100),
    sous_categorie VARCHAR(100),
    prix_unitaire DECIMAL(10,2)
);

-- Junk Dimension (flags)
CREATE TABLE dwh.dim_indicateurs (
    indicateur_key SERIAL PRIMARY KEY,
    canal VARCHAR(50),
    statut VARCHAR(30),
    est_gros_montant BOOLEAN,
    est_weekend BOOLEAN
);

-- Table de faits
CREATE TABLE dwh.fait_transactions (
    transaction_key SERIAL PRIMARY KEY,
    date_key INT REFERENCES dwh.dim_date(date_key),
    client_key INT REFERENCES dwh.dim_client(client_key),
    produit_key INT REFERENCES dwh.dim_produit(produit_key),
    indicateur_key INT REFERENCES dwh.dim_indicateurs(indicateur_key),
    transaction_id VARCHAR(50),
    quantite INT,
    montant DECIMAL(12,2),
    prix_unitaire DECIMAL(10,2)
);

-- Donnees de demo pour dimensions
INSERT INTO dwh.dim_client (client_id, nom, email, ville, pays, segment, date_debut) VALUES
('C001', 'Entreprise Alpha', 'contact@alpha.fr', 'Paris', 'France', 'Premium', '2022-01-01'),
('C002', 'Societe Beta', 'info@beta.fr', 'Lyon', 'France', 'Standard', '2022-01-01'),
('C003', 'Corp Gamma', 'hello@gamma.fr', 'Marseille', 'France', 'Premium', '2022-01-01'),
('C004', 'PME Delta', 'contact@delta.fr', 'Lille', 'France', 'Standard', '2022-03-15'),
('C005', 'Groupe Epsilon', 'info@epsilon.fr', 'Paris', 'France', 'VIP', '2022-01-01');

INSERT INTO dwh.dim_produit (produit_id, nom, categorie, sous_categorie, prix_unitaire) VALUES
('P001', 'Laptop Pro 15', 'Informatique', 'Ordinateurs', 1200.00),
('P002', 'Serveur Rack X1', 'Informatique', 'Serveurs', 5000.00),
('P003', 'Ecran 27" 4K', 'Informatique', 'Peripheriques', 450.00),
('P004', 'Licence Office', 'Logiciel', 'Bureautique', 150.00),
('P005', 'Licence Securite', 'Logiciel', 'Securite', 300.00);

INSERT INTO dwh.dim_indicateurs (canal, statut, est_gros_montant, est_weekend) VALUES
('Web', 'VALIDE', FALSE, FALSE),
('Web', 'VALIDE', TRUE, FALSE),
('Magasin', 'VALIDE', FALSE, FALSE),
('Magasin', 'VALIDE', TRUE, FALSE),
('Web', 'ANNULE', FALSE, FALSE),
('Telephone', 'VALIDE', FALSE, TRUE),
('Telephone', 'VALIDE', TRUE, TRUE);

-- Generer des faits
INSERT INTO dwh.fait_transactions (date_key, client_key, produit_key, indicateur_key, transaction_id, quantite, montant, prix_unitaire)
SELECT
    TO_CHAR('2024-01-01'::date + (random() * 89)::INT, 'YYYYMMDD')::INT,
    (random() * 4 + 1)::INT,
    (random() * 4 + 1)::INT,
    (random() * 6 + 1)::INT,
    'TXN-' || LPAD(s::TEXT, 6, '0'),
    (random() * 10 + 1)::INT,
    round((random() * 20000)::numeric, 2),
    round((random() * 5000)::numeric, 2)
FROM generate_series(1, 1000) AS s;

-- ==================== PROCEDURE : SCD Type 2 ====================

CREATE OR REPLACE PROCEDURE dwh.upsert_client_scd2(
    p_client_id VARCHAR,
    p_nom VARCHAR,
    p_email VARCHAR,
    p_ville VARCHAR,
    p_pays VARCHAR,
    p_segment VARCHAR,
    p_date_effet DATE
)
LANGUAGE plpgsql AS $$
BEGIN
    -- Fermer la ligne courante si un attribut a change
    UPDATE dwh.dim_client
    SET date_fin = p_date_effet - INTERVAL '1 day',
        est_courant = FALSE
    WHERE client_id = p_client_id
      AND est_courant = TRUE
      AND (nom IS DISTINCT FROM p_nom
           OR ville IS DISTINCT FROM p_ville
           OR segment IS DISTINCT FROM p_segment);

    -- Inserer la nouvelle version si une maj a eu lieu ou si nouveau client
    IF NOT EXISTS (
        SELECT 1 FROM dwh.dim_client
        WHERE client_id = p_client_id AND est_courant = TRUE
    ) THEN
        INSERT INTO dwh.dim_client (client_id, nom, email, ville, pays, segment, date_debut)
        VALUES (p_client_id, p_nom, p_email, p_ville, p_pays, p_segment, p_date_effet);
    END IF;
END;
$$;
