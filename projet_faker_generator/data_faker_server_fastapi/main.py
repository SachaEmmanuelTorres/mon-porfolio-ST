import os
import duckdb
from fastapi import FastAPI, Query, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html # Keep this import for default docs
from fastapi.responses import RedirectResponse, HTMLResponse, StreamingResponse # Added StreamingResponse
from fastapi_pagination import Page, add_pagination, paginate
from generate_fake_data import DynamicDataGenerator
from typing import TypeVar, Dict, Any
from fastapi_pagination.customization import CustomizedPage, UseParamsFields
import io # Added io import

T = TypeVar("T")

CustomPage = CustomizedPage[
    Page[T],
    UseParamsFields(size=Query(100, ge=1, le=100)),
]

app = FastAPI(
    title="Fake Data DB API", # Updated title
    description="API pour générer et servir des données fictives pour l'entraînement de bases de données et d'APIs.", # Updated description
    version="1.0",
    docs_url="/docs", # Set docs_url here
)

# Define the path for the DuckDB database file
DUCKDB_DB_PATH = "fake_data_db.duckdb"

# Delete the DuckDB file at startup for a fresh database
if os.path.exists(DUCKDB_DB_PATH):
    os.remove(DUCKDB_DB_PATH)

# Initialise la connexion DuckDB à un fichier persistant
con = duckdb.connect(database=DUCKDB_DB_PATH, read_only=False)

# Variable globale pour stocker les DataFrames générés (utilisé pour la pagination)
generated_dataframes: Dict[str, Any] = {}

# Global constant for the input fields directory
INPUT_FIELDS_DIR = os.path.join(os.path.dirname(__file__), "input_fields")


@app.get("/")
async def docs_redirect():
    """
    Redirige la requête racine vers la documentation Swagger UI.
    """
    return RedirectResponse(url="/docs")


@app.get("/regenerate-ui", response_class=HTMLResponse, tags=["UI"])
async def regenerate_ui():
    """
    Affiche une page HTML avec un bouton pour régénérer toutes les données.
    """
    with open("regenerate_button.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


# Removed the overridden_swagger function entirely. FastAPI will now serve its default Swagger UI at /docs.


@app.post("/regenerate-all-data", tags=["Gestion des données"])
async def regenerate_all_data():
    """
    **Regénère toutes les données fictives pour toutes les tables définies dans le répertoire `input_fields/`.**

    Parcourt tous les fichiers `.txt` dans `input_fields/`, utilise chaque fichier
    pour générer un DataFrame de données fictives, puis crée ou remplace une table
    correspondante dans la base de données DuckDB.

    Returns:
        Dict[str, str]: Un message de succès.

    Raises:
        HTTPException: Si le répertoire `input_fields` est introuvable ou si une erreur
                       survient lors de la génération des données pour une table.
    """
    global generated_dataframes
    generated_dataframes.clear() # Efface les données existantes

    if not os.path.exists(INPUT_FIELDS_DIR):
        raise HTTPException(status_code=404, detail="Le répertoire 'input_fields' est introuvable.")

    for filename in os.listdir(INPUT_FIELDS_DIR):
        if filename.endswith(".txt"):
            table_name = filename.replace(".txt", "")
            fields_file_path = os.path.join(INPUT_FIELDS_DIR, filename)
            
            try:
                generator = DynamicDataGenerator(fields_file_path=fields_file_path)
                df = generator.generate_fake_data()
                generated_dataframes[table_name] = df
                
                # Crée ou remplace la table dans DuckDB
                con.execute(f"DROP TABLE IF EXISTS {table_name}")
                con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df")
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Erreur lors de la génération des données pour la table {table_name}: {str(e)}")
    
    return {"message": "Toutes les données ont été regénérées avec succès."}

@app.on_event("startup")
async def startup_event():
    """
    Événement de démarrage de l'application.
    Appelle `regenerate_all_data` pour générer les données initiales au lancement du serveur.
    """
    await regenerate_all_data() # Génère les données au démarrage

@app.get("/data/{table_name}", tags=["Accès aux données"])
async def get_dynamic_data(table_name: str) -> CustomPage[Dict[str, Any]]:
    """
    **Récupère les données fictives générées pour une table spécifique.**

    Les données sont récupérées depuis la base de données DuckDB
    et sont paginées pour une meilleure gestion des grands ensembles de données.

    Args:
        table_name (str): Le nom de la table dont les données doivent être récupérées.
                          Ce nom correspond au nom du fichier `.txt` (sans l'extension)
                          dans le répertoire `input_fields/`.

    Returns:
        CustomPage[Dict[str, Any]]: Une page de données paginées pour la table spécifiée.

    Raises:
        HTTPException: Si la table spécifiée n'existe pas ou n'a pas été générée.
    """
    if table_name not in generated_dataframes:
        raise HTTPException(status_code=404, detail=f"La table '{table_name}' n'existe pas ou n'a pas été générée.")
    
    # Récupère les données de DuckDB
    df = con.execute(f"SELECT * FROM {table_name}").fetchdf()
    
    # Convertit le DataFrame en liste de dictionnaires pour la pagination
    data_list = df.to_dict(orient="records")
    return paginate(data_list)

@app.get("/export-csv/{table_name}", tags=["Accès aux données"])
async def export_table_to_csv(table_name: str):
    """
    **Exporte les données d'une table spécifique au format CSV.**

    Args:
        table_name (str): Le nom de la table à exporter.

    Returns:
        StreamingResponse: Un fichier CSV téléchargeable.

    Raises:
        HTTPException: Si la table spécifiée n'existe pas ou n'a pas été générée.
    """
    if table_name not in generated_dataframes:
        raise HTTPException(status_code=404, detail=f"La table '{table_name}' n'existe pas ou n'a pas été générée.")

    try:
        df = con.execute(f"SELECT * FROM {table_name}").fetchdf()
        # Utiliser StringIO pour écrire le CSV en mémoire
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        return StreamingResponse(
            iter([csv_buffer.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={table_name}.csv"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'exportation de la table {table_name} en CSV: {str(e)}")

add_pagination(app)
