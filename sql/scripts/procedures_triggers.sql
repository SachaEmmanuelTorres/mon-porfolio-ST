-- =============================================================
-- Exemples de procedures stockees et triggers
-- Usage: psql -U dataeng -d sql_avance -f /sql_scripts/procedures_triggers.sql
-- =============================================================

-- ---- PROCEDURE : Calculer le CA par region sur une periode ----

CREATE OR REPLACE PROCEDURE sp_ca_par_region(
    p_date_debut DATE,
    p_date_fin DATE
)
LANGUAGE plpgsql AS $$
DECLARE
    rec RECORD;
BEGIN
    FOR rec IN
        SELECT
            region,
            SUM(montant * quantite) AS ca,
            COUNT(*) AS nb_ventes
        FROM ventes
        WHERE date_vente BETWEEN p_date_debut AND p_date_fin
        GROUP BY region
        ORDER BY ca DESC
    LOOP
        RAISE NOTICE 'Region: %, CA: %, Ventes: %', rec.region, rec.ca, rec.nb_ventes;
    END LOOP;
END;
$$;

-- Appel : CALL sp_ca_par_region('2024-01-01', '2024-03-31');

-- ---- FONCTION : Classifier un montant ----

CREATE OR REPLACE FUNCTION fn_classifier_montant(p_montant DECIMAL)
RETURNS VARCHAR
LANGUAGE plpgsql AS $$
BEGIN
    RETURN CASE
        WHEN p_montant >= 10000 THEN 'GROS'
        WHEN p_montant >= 1000 THEN 'MOYEN'
        ELSE 'PETIT'
    END;
END;
$$;

-- Usage : SELECT fn_classifier_montant(5000);

-- ---- TRIGGER : Audit des modifications sur ventes ----

CREATE TABLE IF NOT EXISTS audit_ventes (
    audit_id SERIAL PRIMARY KEY,
    operation VARCHAR(10),
    vente_id INT,
    ancien_montant DECIMAL(10,2),
    nouveau_montant DECIMAL(10,2),
    modifie_par VARCHAR(100),
    modifie_le TIMESTAMP DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION trg_audit_ventes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_ventes (operation, vente_id, ancien_montant, nouveau_montant, modifie_par)
        VALUES ('UPDATE', OLD.id, OLD.montant, NEW.montant, current_user);
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_ventes (operation, vente_id, ancien_montant, nouveau_montant, modifie_par)
        VALUES ('DELETE', OLD.id, OLD.montant, NULL, current_user);
    END IF;
    RETURN COALESCE(NEW, OLD);
END;
$$  LANGUAGE plpgsql;

CREATE TRIGGER trg_ventes_audit
    AFTER UPDATE OR DELETE ON ventes
    FOR EACH ROW
    EXECUTE FUNCTION trg_audit_ventes();
