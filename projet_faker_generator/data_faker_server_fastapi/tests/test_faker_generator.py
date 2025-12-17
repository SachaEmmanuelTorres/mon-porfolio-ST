import os
import pytest
import pandas as pd
from fastapi.testclient import TestClient
from unittest.mock import patch, mock_open
from pydantic import BaseModel # Import BaseModel

# Import the FastAPI app and the DynamicDataGenerator
from main import app, generated_dataframes, con, regenerate_all_data, INPUT_FIELDS_DIR
from generate_fake_data import DynamicDataGenerator, fake

# Create a TestClient for the FastAPI app
client = TestClient(app)

# Define paths for testing
TEST_INPUT_FIELDS_DIR = "test_input_fields"
TEST_FIELDS_FILE_PATH = os.path.join(TEST_INPUT_FIELDS_DIR, "test_table.txt")
TEST_FIELDS_CONTENT = "id:unique.random_int\nname:name\nemail:email"

@pytest.fixture(scope="module", autouse=True)
def setup_test_environment():
    """
    Setup and teardown for the test environment.
    - Create a temporary input_fields directory.
    - Create a test_table.txt file.
    - Ensure the app starts up and regenerates data.
    """
    # Create a temporary directory for test input fields
    os.makedirs(TEST_INPUT_FIELDS_DIR, exist_ok=True)
    with open(TEST_FIELDS_FILE_PATH, "w") as f:
        f.write(TEST_FIELDS_CONTENT)

    # Patch the INPUT_FIELDS_DIR in main.py to point to our test directory
    # This patch needs to be active for the entire module
    with patch('main.INPUT_FIELDS_DIR', TEST_INPUT_FIELDS_DIR):
        # Run the startup event to generate initial data
        # This needs to be called explicitly for tests as the app doesn't "start" in the same way
        # as when run with uvicorn.
        # We also need to patch os.listdir and os.path.exists for the startup call
        with patch('main.os.listdir', return_value=["test_table.txt"]):
            with patch('main.os.path.exists', return_value=True):
                with patch('builtins.open', mock_open(read_data=TEST_FIELDS_CONTENT)):
                    app.dependency_overrides[regenerate_all_data] = lambda: None # Mock the startup call
                    # Call the startup event directly, as client.get("/") might not trigger it reliably in tests
                    # And the actual regenerate_all_data needs to run with the patches
                    from main import regenerate_all_data as actual_regenerate_all_data
                    pytest.mark.asyncio(actual_regenerate_all_data)()


        yield # Run tests

    # Teardown: Clean up the temporary directory
    os.remove(TEST_FIELDS_FILE_PATH)
    os.rmdir(TEST_INPUT_FIELDS_DIR)
    # Clear generated dataframes and close DuckDB connection
    generated_dataframes.clear()
    con.close()


# --- Tests for DynamicDataGenerator ---

def test_load_fields_config_success():
    """
    Teste le chargement réussi de la configuration des champs.
    """
    generator = DynamicDataGenerator(10, TEST_FIELDS_FILE_PATH)
    config = generator._load_fields_config()
    assert config == {"id": "unique.random_int", "name": "name", "email": "email"}

def test_load_fields_config_file_not_found():
    """
    Teste la gestion de l'erreur si le fichier de configuration est introuvable.
    """
    with pytest.raises(FileNotFoundError, match="Le fichier de configuration des champs est introuvable"):
        DynamicDataGenerator(10, "non_existent_file.txt")._load_fields_config()

def test_create_dynamic_pydantic_model():
    """
    Teste la création dynamique du modèle Pydantic.
    """
    generator = DynamicDataGenerator(10, TEST_FIELDS_FILE_PATH)
    model = generator._create_dynamic_pydantic_model()
    assert issubclass(model, BaseModel)
    assert hasattr(model, "id")
    assert hasattr(model, "name")
    assert hasattr(model, "email")
    assert model.model_fields["id"].annotation == int
    assert model.model_fields["name"].annotation == str
    assert model.model_fields["email"].annotation == str

def test_generate_fake_data():
    """
    Teste la génération de données fictives et la création du DataFrame.
    """
    num_observations = 5
    generator = DynamicDataGenerator(num_observations, TEST_FIELDS_FILE_PATH)
    df = generator.generate_fake_data()

    assert isinstance(df, pd.DataFrame)
    assert len(df) == num_observations
    assert list(df.columns) == ["id", "name", "email"]
    assert df["id"].dtype == "int64" # Pandas infers int64 for unique.random_int
    assert df["name"].dtype == "object" # object for strings
    assert df["email"].dtype == "object"


# --- Tests for FastAPI Endpoints ---

def test_docs_redirect():
    """
    Teste la redirection de la route racine vers /docs.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "swagger-ui" in response.text.lower()

# Removed mock_open_file from signature
@patch('main.os.listdir', return_value=["test_table.txt"])
@patch('main.os.path.exists', return_value=True)
@patch('builtins.open', mock_open(read_data=TEST_FIELDS_CONTENT))
def test_regenerate_all_data_endpoint(mock_exists, mock_listdir):
    """
    Teste l'endpoint de regénération de toutes les données.
    """
    # Ensure the global INPUT_FIELDS_DIR is patched for this test
    with patch('main.INPUT_FIELDS_DIR', TEST_INPUT_FIELDS_DIR):
        response = client.post("/regenerate-all-data")
        assert response.status_code == 200
        assert response.json() == {"message": "Toutes les données ont été regénérées avec succès."}
        assert "test_table" in generated_dataframes
        assert isinstance(generated_dataframes["test_table"], pd.DataFrame)
        # Verify that the table was created in DuckDB
        assert "test_table" in con.execute("SHOW TABLES").fetchdf()["name"].tolist()


def test_get_dynamic_data_success():
    """
    Teste la récupération réussie des données pour une table existante.
    """
    # Ensure data is generated before fetching
    # We need to ensure regenerate_all_data runs with the correct patches
    with patch('main.INPUT_FIELDS_DIR', TEST_INPUT_FIELDS_DIR):
        with patch('main.os.listdir', return_value=["test_table.txt"]):
            with patch('main.os.path.exists', return_value=True):
                with patch('builtins.open', mock_open(read_data=TEST_FIELDS_CONTENT)):
                    from main import regenerate_all_data as actual_regenerate_all_data
                    pytest.mark.asyncio(actual_regenerate_all_data)()


    response = client.get("/data/test_table")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) > 0
    assert "id" in data["items"][0]

def test_get_dynamic_data_not_found():
    """
    Teste la récupération des données pour une table non existante.
    """
    response = client.get("/data/non_existent_table")
    assert response.status_code == 404
    assert response.json() == {"detail": "La table 'non_existent_table' n'existe pas ou n'a pas été générée."}