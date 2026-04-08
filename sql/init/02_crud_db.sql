-- =============================================================
-- BASE : crud_db — Tables pour exercices CRUD de base
-- =============================================================

\c crud_db;

-- Employes
CREATE TABLE employes (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE,
    departement VARCHAR(50),
    salaire DECIMAL(10,2),
    date_embauche DATE DEFAULT CURRENT_DATE,
    est_actif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Departements
CREATE TABLE departements (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(50) UNIQUE NOT NULL,
    budget DECIMAL(12,2),
    manager_id INT REFERENCES employes(id),
    localisation VARCHAR(100)
);

-- Projets
CREATE TABLE projets (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(150) NOT NULL,
    description TEXT,
    date_debut DATE,
    date_fin DATE,
    statut VARCHAR(20) DEFAULT 'EN_COURS' CHECK (statut IN ('EN_COURS', 'TERMINE', 'ANNULE', 'EN_ATTENTE')),
    budget DECIMAL(12,2)
);

-- Affectations employes-projets (N:N)
CREATE TABLE affectations (
    id SERIAL PRIMARY KEY,
    employe_id INT REFERENCES employes(id) ON DELETE CASCADE,
    projet_id INT REFERENCES projets(id) ON DELETE CASCADE,
    role VARCHAR(50),
    heures_allouees DECIMAL(5,1),
    date_affectation DATE DEFAULT CURRENT_DATE,
    UNIQUE(employe_id, projet_id)
);

-- Donnees initiales
INSERT INTO employes (nom, prenom, email, departement, salaire, date_embauche) VALUES
('Dupont', 'Alice', 'alice.dupont@ms.com', 'Finance', 75000, '2020-01-15'),
('Martin', 'Bob', 'bob.martin@ms.com', 'IT', 82000, '2019-06-01'),
('Bernard', 'Charlie', 'charlie.bernard@ms.com', 'Finance', 68000, '2021-03-20'),
('Petit', 'Diana', 'diana.petit@ms.com', 'IT', 90000, '2018-09-10'),
('Leroy', 'Eve', 'eve.leroy@ms.com', 'RH', 71000, '2020-11-05'),
('Moreau', 'Frank', 'frank.moreau@ms.com', 'IT', 95000, '2017-04-22'),
('Simon', 'Grace', 'grace.simon@ms.com', 'Finance', 78000, '2019-12-01'),
('Laurent', 'Hugo', 'hugo.laurent@ms.com', 'RH', 65000, '2022-02-14'),
('Roux', 'Iris', 'iris.roux@ms.com', 'Marketing', 72000, '2021-07-08'),
('David', 'Jules', 'jules.david@ms.com', 'Marketing', 69000, '2023-01-10');

INSERT INTO departements (nom, budget, localisation) VALUES
('Finance', 500000, 'Paris'),
('IT', 800000, 'Paris'),
('RH', 300000, 'Lyon'),
('Marketing', 400000, 'Paris');

INSERT INTO projets (nom, description, date_debut, date_fin, statut, budget) VALUES
('Migration Cloud', 'Migration des systemes vers AWS', '2024-01-01', '2024-06-30', 'EN_COURS', 250000),
('Dashboard RH', 'Tableau de bord analytique RH', '2024-02-15', '2024-05-15', 'EN_COURS', 80000),
('Refonte API', 'Refonte des APIs REST internes', '2023-09-01', '2024-03-31', 'TERMINE', 150000),
('Campagne Q2', 'Campagne marketing Q2 2024', '2024-04-01', '2024-06-30', 'EN_ATTENTE', 120000);

INSERT INTO affectations (employe_id, projet_id, role, heures_allouees) VALUES
(2, 1, 'Lead Dev', 160),
(4, 1, 'Architecte', 120),
(6, 1, 'DevOps', 80),
(1, 2, 'Analyste', 60),
(5, 2, 'Chef de projet', 100),
(8, 2, 'Support', 40),
(2, 3, 'Developpeur', 140),
(6, 3, 'Lead Dev', 160),
(9, 4, 'Chef de projet', 120),
(10, 4, 'Redacteur', 80);

-- Trigger : mise a jour automatique de updated_at
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_employes_updated
    BEFORE UPDATE ON employes
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();
