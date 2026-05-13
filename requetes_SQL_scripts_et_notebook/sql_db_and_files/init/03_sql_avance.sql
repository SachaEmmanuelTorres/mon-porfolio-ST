-- =============================================================
-- BASE : sql_avance — Tables pour Window Functions, CTE, etc.
-- =============================================================

\c sql_avance;

-- ---- VENTES (window functions, agregation) ----

CREATE TABLE ventes (
    id SERIAL PRIMARY KEY,
    produit VARCHAR(100),
    region VARCHAR(50),
    vendeur VARCHAR(100),
    montant DECIMAL(10,2),
    quantite INT,
    date_vente DATE
);

INSERT INTO ventes (produit, region, vendeur, montant, quantite, date_vente) VALUES
('Laptop Pro', 'Nord', 'Alice', 1200.00, 2, '2024-01-05'),
('Laptop Pro', 'Sud', 'Bob', 1200.00, 1, '2024-01-08'),
('Serveur X1', 'Nord', 'Alice', 5000.00, 1, '2024-01-10'),
('Ecran 27"', 'Est', 'Charlie', 450.00, 5, '2024-01-12'),
('Laptop Pro', 'Nord', 'Alice', 1200.00, 3, '2024-01-15'),
('Serveur X1', 'Sud', 'Diana', 5000.00, 2, '2024-01-18'),
('Ecran 27"', 'Nord', 'Bob', 450.00, 4, '2024-01-20'),
('Laptop Pro', 'Est', 'Charlie', 1200.00, 2, '2024-01-22'),
('Serveur X1', 'Nord', 'Alice', 5000.00, 1, '2024-01-25'),
('Ecran 27"', 'Sud', 'Bob', 450.00, 6, '2024-01-28'),
('Laptop Pro', 'Nord', 'Diana', 1200.00, 1, '2024-02-01'),
('Serveur X1', 'Est', 'Charlie', 5000.00, 1, '2024-02-05'),
('Ecran 27"', 'Nord', 'Alice', 450.00, 3, '2024-02-08'),
('Laptop Pro', 'Sud', 'Bob', 1200.00, 2, '2024-02-10'),
('Serveur X1', 'Nord', 'Diana', 5000.00, 1, '2024-02-15'),
('Ecran 27"', 'Est', 'Alice', 450.00, 2, '2024-02-18'),
('Laptop Pro', 'Nord', 'Charlie', 1200.00, 4, '2024-02-20'),
('Serveur X1', 'Sud', 'Bob', 5000.00, 1, '2024-02-25'),
('Ecran 27"', 'Nord', 'Diana', 450.00, 5, '2024-02-28'),
('Laptop Pro', 'Est', 'Alice', 1200.00, 1, '2024-03-01');

-- ---- HIERARCHIE (CTE recursive) ----

CREATE TABLE organisation (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100),
    poste VARCHAR(100),
    manager_id INT REFERENCES organisation(id),
    salaire DECIMAL(10,2)
);

INSERT INTO organisation (nom, poste, manager_id, salaire) VALUES
('PDG', 'Directeur General', NULL, 200000),
('VP Finance', 'Vice-President', 1, 150000),
('VP Tech', 'Vice-President', 1, 155000),
('VP RH', 'Vice-President', 1, 140000),
('Dir Compta', 'Directeur', 2, 110000),
('Dir Tresorerie', 'Directeur', 2, 105000),
('Dir Dev', 'Directeur', 3, 120000),
('Dir Infra', 'Directeur', 3, 115000),
('Dir Recrutement', 'Directeur', 4, 100000),
('Comptable 1', 'Analyste', 5, 65000),
('Comptable 2', 'Analyste', 5, 62000),
('Tresorier 1', 'Analyste', 6, 70000),
('Dev Senior 1', 'Senior', 7, 85000),
('Dev Senior 2', 'Senior', 7, 82000),
('Dev Junior', 'Junior', 7, 55000),
('SysAdmin', 'Senior', 8, 78000),
('Recruteur 1', 'Analyste', 9, 60000),
('Recruteur 2', 'Analyste', 9, 58000);

-- ---- CONNEXIONS (Gaps & Islands) ----

CREATE TABLE connexions (
    id SERIAL PRIMARY KEY,
    user_id INT,
    date_connexion DATE
);

INSERT INTO connexions (user_id, date_connexion) VALUES
(1, '2024-01-01'), (1, '2024-01-02'), (1, '2024-01-03'),
(1, '2024-01-06'), (1, '2024-01-07'),
(1, '2024-01-10'), (1, '2024-01-11'), (1, '2024-01-12'), (1, '2024-01-13'),
(2, '2024-01-01'), (2, '2024-01-02'),
(2, '2024-01-05'), (2, '2024-01-06'), (2, '2024-01-07'), (2, '2024-01-08'),
(2, '2024-01-15'), (2, '2024-01-16'),
(3, '2024-01-03'), (3, '2024-01-04'), (3, '2024-01-05'), (3, '2024-01-06'), (3, '2024-01-07');

-- ---- TRANSACTIONS (Top-N, agregation) ----

CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100),
    segment VARCHAR(30),
    region VARCHAR(50),
    date_inscription DATE
);

CREATE TABLE comptes (
    id SERIAL PRIMARY KEY,
    client_id INT REFERENCES clients(id),
    type_compte VARCHAR(30),
    date_ouverture DATE,
    statut VARCHAR(20) DEFAULT 'ACTIF'
);

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    compte_id INT REFERENCES comptes(id),
    montant DECIMAL(12,2),
    type_transaction VARCHAR(20),
    date_transaction TIMESTAMP
);

INSERT INTO clients (nom, segment, region, date_inscription) VALUES
('Entreprise Alpha', 'Premium', 'IDF', '2020-01-10'),
('Societe Beta', 'Standard', 'IDF', '2021-05-22'),
('Corp Gamma', 'Premium', 'Lyon', '2019-08-15'),
('PME Delta', 'Standard', 'Marseille', '2022-03-01'),
('Groupe Epsilon', 'VIP', 'IDF', '2018-11-30');

INSERT INTO comptes (client_id, type_compte, date_ouverture, statut) VALUES
(1, 'Courant', '2020-01-15', 'ACTIF'),
(1, 'Epargne', '2020-06-01', 'ACTIF'),
(2, 'Courant', '2021-06-01', 'ACTIF'),
(3, 'Courant', '2019-09-01', 'ACTIF'),
(3, 'Titre', '2020-01-10', 'ACTIF'),
(3, 'Epargne', '2020-01-10', 'FERME'),
(4, 'Courant', '2022-03-15', 'ACTIF'),
(5, 'Courant', '2018-12-01', 'ACTIF'),
(5, 'Titre', '2019-01-15', 'ACTIF'),
(5, 'Epargne', '2019-01-15', 'ACTIF');

INSERT INTO transactions (compte_id, montant, type_transaction, date_transaction)
SELECT
    (random() * 9 + 1)::INT,
    round((random() * 50000 - 10000)::numeric, 2),
    (ARRAY['CREDIT', 'DEBIT', 'VIREMENT', 'PRELEVEMENT'])[floor(random() * 4 + 1)::INT],
    '2024-01-01'::timestamp + (random() * 90)::INT * INTERVAL '1 day' + (random() * 86400)::INT * INTERVAL '1 second'
FROM generate_series(1, 500);

-- ---- VENTES MENSUELLES (PIVOT) ----

CREATE TABLE ventes_mensuelles (
    id SERIAL PRIMARY KEY,
    produit VARCHAR(100),
    mois VARCHAR(10),
    montant DECIMAL(10,2)
);

INSERT INTO ventes_mensuelles (produit, mois, montant) VALUES
('Laptop', 'Jan', 15000), ('Laptop', 'Fev', 18000), ('Laptop', 'Mar', 22000),
('Serveur', 'Jan', 45000), ('Serveur', 'Fev', 38000), ('Serveur', 'Mar', 52000),
('Ecran', 'Jan', 8000), ('Ecran', 'Fev', 9500), ('Ecran', 'Mar', 11000),
('Clavier', 'Jan', 2000), ('Clavier', 'Fev', 2500), ('Clavier', 'Mar', 3000);

-- ---- PROCEDURE STOCKEE : calcul de statistiques ----

CREATE OR REPLACE PROCEDURE calc_stats_vendeur(p_vendeur VARCHAR)
LANGUAGE plpgsql AS $$
DECLARE
    v_total DECIMAL;
    v_nb INT;
    v_moy DECIMAL;
BEGIN
    SELECT SUM(montant * quantite), COUNT(*), AVG(montant * quantite)
    INTO v_total, v_nb, v_moy
    FROM ventes
    WHERE vendeur = p_vendeur;

    RAISE NOTICE 'Vendeur: %, Total: %, Nb ventes: %, Moyenne: %',
        p_vendeur, v_total, v_nb, v_moy;
END;
$$;

-- ---- VUES utiles ----

CREATE VIEW v_ventes_resume AS
SELECT
    region,
    produit,
    COUNT(*) AS nb_ventes,
    SUM(montant * quantite) AS ca_total,
    AVG(montant * quantite) AS ca_moyen,
    MIN(date_vente) AS premiere_vente,
    MAX(date_vente) AS derniere_vente
FROM ventes
GROUP BY region, produit;
