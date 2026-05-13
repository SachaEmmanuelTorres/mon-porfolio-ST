-- =============================================================
-- Export d'une table ou requete vers un fichier CSV
-- Usage: psql -U dataeng -d etl_warehouse -f /sql_scripts/export_csv.sql
-- =============================================================

-- Export dimension clients
COPY dwh.dim_client
TO '/csv_data/export_dim_client.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',');

-- Export avec requete personnalisee
COPY (
    SELECT
        f.transaction_id,
        c.nom AS client,
        p.nom AS produit,
        f.quantite,
        f.montant,
        d.full_date AS date_transaction
    FROM dwh.fait_transactions f
    JOIN dwh.dim_client c ON f.client_key = c.client_key
    JOIN dwh.dim_produit p ON f.produit_key = p.produit_key
    JOIN dwh.dim_date d ON f.date_key = d.date_key
    WHERE c.est_courant = TRUE
    ORDER BY d.full_date DESC
    LIMIT 100
) TO '/csv_data/export_top_transactions.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',');
