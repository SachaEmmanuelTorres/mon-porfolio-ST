-- =============================================================
-- Import d'un fichier CSV dans une table staging
-- Usage: psql -U dataeng -d etl_warehouse -f /sql_scripts/import_csv.sql
-- =============================================================

-- Import clients
COPY staging.raw_clients (data_source, client_id, nom, email, telephone, adresse, ville, pays, segment, date_inscription)
FROM '/csv_data/exemple_clients.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',', NULL '');

-- Import transactions
COPY staging.raw_transactions (data_source, transaction_id, client_id, produit_id, quantite, montant, date_transaction, canal, statut)
FROM '/csv_data/exemple_transactions.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',', NULL '');

-- Verification
SELECT 'raw_clients' AS table_name, COUNT(*) AS nb_lignes FROM staging.raw_clients
UNION ALL
SELECT 'raw_transactions', COUNT(*) FROM staging.raw_transactions;
