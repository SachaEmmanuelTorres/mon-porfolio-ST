"""
Flask application for SQL exercises against PostgreSQL.
Provides: SQL editor, database explorer, CSV import/export, exercise panel.
"""

import csv
import io
import json
import os
import traceback

import psycopg2
import psycopg2.extras
from flask import Flask, jsonify, render_template, request, Response

app = Flask(__name__)

# ---------- connection config ----------
DB_HOST = os.environ.get("DB_HOST", "postgres")
DB_PORT = int(os.environ.get("DB_PORT", "5432"))
DB_USER = os.environ.get("DB_USER", "dataeng")
DB_PASS = os.environ.get("DB_PASS", "dataeng2024")
DATABASES = ["crud_db", "sql_avance", "etl_warehouse"]


def get_conn(dbname: str):
    """Return a new psycopg2 connection to *dbname*."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        dbname=dbname,
    )


# ===================== pages =====================

@app.route("/")
def index():
    return render_template("index.html")


# ===================== API =====================

@app.route("/api/databases")
def list_databases():
    return jsonify(DATABASES)


@app.route("/api/explore/<dbname>")
def explore(dbname: str):
    """Return schemas -> tables -> columns tree for *dbname*."""
    if dbname not in DATABASES:
        return jsonify({"error": "Unknown database"}), 400

    sql = """
    SELECT
        c.table_schema,
        c.table_name,
        c.column_name,
        c.data_type,
        c.is_nullable,
        c.column_default,
        c.ordinal_position
    FROM information_schema.columns c
    JOIN information_schema.tables t
      ON c.table_schema = t.table_schema AND c.table_name = t.table_name
    WHERE t.table_type IN ('BASE TABLE', 'VIEW')
      AND c.table_schema NOT IN ('pg_catalog', 'information_schema')
    ORDER BY c.table_schema, c.table_name, c.ordinal_position;
    """
    try:
        conn = get_conn(dbname)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    # Build nested structure: {schema: {table: [columns]}}
    tree: dict = {}
    for r in rows:
        schema = r["table_schema"]
        table = r["table_name"]
        col = {
            "name": r["column_name"],
            "type": r["data_type"],
            "nullable": r["is_nullable"],
            "default": r["column_default"],
        }
        tree.setdefault(schema, {}).setdefault(table, []).append(col)

    return jsonify(tree)


@app.route("/api/query", methods=["POST"])
def run_query():
    """Execute a SQL query and return columns + rows."""
    body = request.get_json(force=True)
    dbname = body.get("database", "crud_db")
    sql = body.get("sql", "").strip()

    if dbname not in DATABASES:
        return jsonify({"error": "Unknown database"}), 400
    if not sql:
        return jsonify({"error": "Empty query"}), 400

    try:
        conn = get_conn(dbname)
        conn.autocommit = False
        cur = conn.cursor()
        cur.execute(sql)

        # Check if the query returns rows
        if cur.description:
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            # Convert to serialisable types
            clean_rows = []
            for row in rows:
                clean_rows.append(
                    [str(v) if v is not None and not isinstance(v, (int, float, bool)) else v for v in row]
                )
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({
                "columns": columns,
                "rows": clean_rows,
                "rowcount": len(clean_rows),
            })
        else:
            rowcount = cur.rowcount
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({
                "columns": [],
                "rows": [],
                "rowcount": rowcount,
                "message": f"Query executed successfully. {rowcount} row(s) affected.",
            })
    except Exception as exc:
        try:
            conn.rollback()
            conn.close()
        except Exception:
            pass
        return jsonify({"error": str(exc), "traceback": traceback.format_exc()}), 400


@app.route("/api/export_csv", methods=["POST"])
def export_csv():
    """Run the query and return results as a downloadable CSV."""
    body = request.get_json(force=True)
    dbname = body.get("database", "crud_db")
    sql = body.get("sql", "").strip()

    if dbname not in DATABASES:
        return jsonify({"error": "Unknown database"}), 400
    if not sql:
        return jsonify({"error": "Empty query"}), 400

    try:
        conn = get_conn(dbname)
        cur = conn.cursor()
        cur.execute(sql)
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(columns)
    for row in rows:
        writer.writerow(row)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=query_result.csv"},
    )


@app.route("/api/import_csv", methods=["POST"])
def import_csv():
    """Upload a CSV and create/insert into a table."""
    dbname = request.form.get("database", "crud_db")
    table_name = request.form.get("table_name", "").strip()
    mode = request.form.get("mode", "create")  # 'create' or 'append'
    schema_name = request.form.get("schema", "public")

    if dbname not in DATABASES:
        return jsonify({"error": "Unknown database"}), 400
    if not table_name:
        return jsonify({"error": "table_name is required"}), 400

    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    try:
        stream = io.StringIO(file.stream.read().decode("utf-8-sig"))
        reader = csv.reader(stream)
        headers = next(reader)
        all_rows = list(reader)
    except Exception as exc:
        return jsonify({"error": f"Failed to parse CSV: {exc}"}), 400

    fq_table = f"{schema_name}.{table_name}"

    try:
        conn = get_conn(dbname)
        cur = conn.cursor()

        if mode == "create":
            # Infer types (basic: everything TEXT)
            col_defs = ", ".join(f'"{h}" TEXT' for h in headers)
            cur.execute(f'DROP TABLE IF EXISTS {fq_table};')
            cur.execute(f'CREATE TABLE {fq_table} ({col_defs});')

        # Insert rows
        placeholders = ", ".join(["%s"] * len(headers))
        col_names = ", ".join(f'"{h}"' for h in headers)
        insert_sql = f"INSERT INTO {fq_table} ({col_names}) VALUES ({placeholders})"

        for row in all_rows:
            if len(row) == len(headers):
                cur.execute(insert_sql, row)

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": f"Imported {len(all_rows)} rows into {fq_table}."})
    except Exception as exc:
        try:
            conn.rollback()
            conn.close()
        except Exception:
            pass
        return jsonify({"error": str(exc)}), 400


@app.route("/api/tables/<dbname>")
def list_tables(dbname: str):
    """List tables for CSV import target autocomplete."""
    if dbname not in DATABASES:
        return jsonify({"error": "Unknown database"}), 400
    try:
        conn = get_conn(dbname)
        cur = conn.cursor()
        cur.execute("""
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_type = 'BASE TABLE'
              AND table_schema NOT IN ('pg_catalog', 'information_schema')
            ORDER BY table_schema, table_name;
        """)
        tables = [{"schema": r[0], "table": r[1]} for r in cur.fetchall()]
        cur.close()
        conn.close()
        return jsonify(tables)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


# ===================== Exercises =====================

EXERCISES = [
    # PARTIE A -- SQL de base (crud_db)
    {
        "id": "A1",
        "db": "crud_db",
        "title": "SELECT, WHERE, ORDER BY",
        "description": "Afficher le nom, prenom et salaire des employes du departement 'IT', tries par salaire decroissant.",
        "hint": "SELECT nom, prenom, salaire FROM employes WHERE ... ORDER BY ...;",
    },
    {
        "id": "A2",
        "db": "crud_db",
        "title": "INSERT, UPDATE, DELETE",
        "description": "1) Inserer un nouvel employe : 'Nguyen', 'Kim', departement 'IT', salaire 88000\n2) Augmenter de 5% le salaire de tous les employes du departement 'RH'\n3) Supprimer les employes inactifs (est_actif = FALSE)",
        "hint": "INSERT INTO ... VALUES (...); UPDATE ... SET salaire = salaire * 1.05 WHERE ...; DELETE FROM ... WHERE ...;",
    },
    {
        "id": "A3",
        "db": "crud_db",
        "title": "JOIN (INNER, LEFT, RIGHT, FULL)",
        "description": "1) Lister tous les employes avec le nom de leur(s) projet(s) (meme ceux sans projet)\n2) Trouver les projets qui n'ont aucun employe affecte\n3) Afficher chaque employe avec son nombre de projets et le total d'heures allouees",
        "hint": "LEFT JOIN affectations ... LEFT JOIN projets ...",
    },
    {
        "id": "A4",
        "db": "crud_db",
        "title": "GROUP BY, HAVING",
        "description": "1) Nombre d'employes et salaire moyen par departement\n2) Departements ayant un salaire moyen superieur a 75000\n3) Pour chaque projet, le nombre d'employes affectes et le total d'heures, uniquement pour les projets avec plus de 2 personnes",
        "hint": "GROUP BY departement HAVING AVG(salaire) > 75000",
    },
    {
        "id": "A5",
        "db": "crud_db",
        "title": "Sous-requetes",
        "description": "1) Employes dont le salaire est superieur a la moyenne de leur departement\n2) Departement(s) ayant le plus grand nombre d'employes\n3) Employes travaillant sur tous les projets EN_COURS",
        "hint": "WHERE e.salaire > (SELECT AVG(e2.salaire) FROM employes e2 WHERE ...)",
    },

    # PARTIE B -- SQL Avance (sql_avance)
    {
        "id": "B1",
        "db": "sql_avance",
        "title": "Window Functions -- Classement",
        "description": "Pour chaque vendeur, afficher :\n- Le montant total de ses ventes\n- Son rang global par CA (RANK)\n- Son rang dans sa region (DENSE_RANK)\n- Le quartile dans lequel il se trouve (NTILE(4))",
        "hint": "RANK() OVER (ORDER BY ...), DENSE_RANK() OVER (PARTITION BY region ORDER BY ...)",
    },
    {
        "id": "B2",
        "db": "sql_avance",
        "title": "Window Functions -- Cumul et moyenne mobile",
        "description": "Pour chaque region, afficher par date de vente :\n- Le montant de la vente\n- Le cumul du montant\n- La moyenne mobile sur 3 ventes\n- Le montant de la vente precedente (LAG)\n- La variation en % par rapport a la vente precedente",
        "hint": "SUM(...) OVER (PARTITION BY region ORDER BY date_vente ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)",
    },
    {
        "id": "B3",
        "db": "sql_avance",
        "title": "CTE Recursive -- Hierarchie",
        "description": "A partir de la table organisation, afficher la hierarchie complete :\n- Nom, poste, niveau hierarchique (0 pour le PDG)\n- Le chemin complet (ex: PDG > VP Tech > Dir Dev > Dev Senior 1)\n- Le salaire cumule de chaque sous-arbre",
        "hint": "WITH RECURSIVE hierarchie AS (SELECT ... WHERE manager_id IS NULL UNION ALL SELECT ... JOIN hierarchie ...)",
    },
    {
        "id": "B4",
        "db": "sql_avance",
        "title": "Gaps and Islands",
        "description": "A partir de la table connexions, identifier pour chaque utilisateur les series de jours consecutifs de connexion.\nAfficher : user_id, date debut, date fin, nombre de jours consecutifs.",
        "hint": "date_connexion - ROW_NUMBER() OVER (...) = constante pour un groupe consecutif",
    },
    {
        "id": "B5",
        "db": "sql_avance",
        "title": "Top-N par groupe",
        "description": "Afficher les 3 plus grosses transactions par compte, avec :\n- Le rang de la transaction dans le compte\n- Le % du montant par rapport au total du compte\n- Le cumul des montants pour ces top 3",
        "hint": "ROW_NUMBER() OVER (PARTITION BY compte_id ORDER BY ABS(montant) DESC) AS rang",
    },
    {
        "id": "B6",
        "db": "sql_avance",
        "title": "PIVOT avec CASE WHEN",
        "description": "A partir de ventes_mensuelles, creer un tableau croise : une ligne par produit, une colonne par mois (Jan, Fev, Mar) avec le montant, et une colonne Total.",
        "hint": "SUM(CASE WHEN mois = 'Jan' THEN montant ELSE 0 END) AS jan",
    },
    {
        "id": "B7",
        "db": "sql_avance",
        "title": "Requete complexe multi-tables",
        "description": "Ecrire UNE seule requete retournant pour chaque client :\n- Son nom et segment\n- Le nombre de comptes actifs\n- Le montant total des transactions du dernier mois de donnees\n- Son rang par montant total dans son segment\n- Uniquement les clients dans le top 5 de leur segment",
        "hint": "CTE + Window functions + multi-JOIN",
    },
    {
        "id": "B8",
        "db": "sql_avance",
        "title": "Procedures stockees et Triggers",
        "description": "1) Creer une procedure sp_augmentation(p_departement, p_pourcentage) qui augmente le salaire de tous les employes d'un departement\n2) Creer un trigger qui empeche la suppression d'un employe ayant des affectations actives\n3) Creer une vue materialisee du CA par region et par mois",
        "hint": "CREATE OR REPLACE PROCEDURE ... LANGUAGE plpgsql AS $$ ... $$;",
    },
    {
        "id": "B9",
        "db": "etl_warehouse",
        "title": "ETL en SQL -- MERGE / Upsert (SCD Type 2)",
        "description": "Ecrire un MERGE qui synchronise staging.raw_clients vers dwh.dim_client en SCD Type 2 :\n- Mettre a jour (fermer l'ancienne ligne + inserer la nouvelle) si ville ou segment a change\n- Inserer les nouveaux clients",
        "hint": "UPDATE ... SET date_fin = ..., est_courant = FALSE ... ; INSERT INTO ... SELECT ... WHERE NOT EXISTS (...);",
    },
    {
        "id": "B10",
        "db": "sql_avance",
        "title": "Analyse avancee -- Requete financiere",
        "description": "Ecrire une requete qui calcule pour chaque compte :\n- Le solde courant (cumul des credits - debits)\n- La transaction la plus recente\n- Le nombre de jours sans transaction\n- La moyenne mobile du montant sur les 5 dernieres transactions\n- Si le compte est en 'alerte' (plus de 3 debits consecutifs)",
        "hint": "Combiner CTEs, window functions (LAG, SUM OVER), gaps-and-islands",
    },
]


@app.route("/api/exercises")
def get_exercises():
    return jsonify(EXERCISES)


# ===================== run =====================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
