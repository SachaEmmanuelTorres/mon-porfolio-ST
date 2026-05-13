import os
import subprocess
import sys
import logging
import re

# --- Configuration ---
V2_DIR = "v2"
NOTEBOOK_PATH = os.path.join(V2_DIR, "src", "exercices_SQL.ipynb")
POPULATE_DB_SCRIPT = os.path.join(V2_DIR, "src", "populate_db.py")
EXEMPLE_QUERY_SCRIPT = os.path.join(V2_DIR, "src", "exemple_query_script.py")
LOG_FILE = "main_script_log.log"

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def run_command(command, description=""):
    """Helper function to run shell commands and log output."""
    logger.info(f"Executing: {description} (Command: {' '.join(command)})")
    try:
        # Use shell=True for commands that might need shell features like 'source'
        # However, for python scripts, it's generally safer to pass as list and not use shell=True
        # For this case, we are running python scripts, so shell=False (default) is fine.
        result = subprocess.run(command, capture_output=True, text=True, check=True, cwd=V2_DIR)
        logger.info(f"Command Stdout:\n{result.stdout}")
        if result.stderr:
            logger.warning(f"Command Stderr:\n{result.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {description}")
        logger.error(f"Error Stdout:\n{e.stdout}")
        logger.error(f"Error Stderr:\n{e.stderr}")
        print(f"\n--- ERREUR ---")
        print(f"Une erreur est survenue lors de l'exécution de: {description}")
        print(f"Détails de l'erreur:\n{e.stderr}")
        print(f"Veuillez vérifier le log ({LOG_FILE}) pour plus de détails et corriger le problème.")
        print(f"Assurez-vous que le script '{command[0]}' est exécutable et que les dépendances sont installées.")
        print(f"Relancez l'option 'Utilisation des Scripts Python' après correction.")
        return False
    except FileNotFoundError:
        logger.error(f"Command not found: {command[0]}. Is it in your PATH?")
        print(f"\n--- ERREUR ---")
        print(f"La commande '{command[0]}' n'a pas été trouvée. Assurez-vous qu'elle est installée et dans votre PATH.")
        return False

def launch_notebook_use_case():
    """Launches Jupyter Notebook for interactive use."""
    logger.info("Launching Interactive Notebook use case.")
    print("\n--- Lancement du Notebook Interactif ---")
    print(f"Ouverture de Jupyter Notebook. Naviguez vers '{NOTEBOOK_PATH}' dans votre navigateur.")
    print("\n*** IMPORTANT: Appuyez sur Ctrl+C dans ce terminal pour arrêter Jupyter Notebook une fois terminé. ***\n")

    try:
        # Launch Jupyter from the V2_DIR to ensure relative paths work
        # We need to specify the full path to the notebook relative to cwd=V2_DIR
        subprocess.run(["jupyter", "notebook", os.path.join("src", "exercices_SQL.ipynb")], cwd=V2_DIR)
    except FileNotFoundError:
        logger.error("Jupyter Notebook command not found. Please ensure Jupyter is installed and in your PATH.")
        print("\n--- ERREUR ---")
        print("La commande 'jupyter notebook' n'a pas été trouvée.")
        print("Veuillez installer Jupyter (pip install jupyter) et vous assurer qu'il est dans votre PATH.")
    except KeyboardInterrupt:
        print("\nJupyter Notebook arrêté.")
    logger.info("Interactive Notebook use case finished.")

def script_based_query_use_case():
    """Handles the script-based query use case."""
    logger.info("Launching Script-based Query use case.")
    print("\n--- Utilisation des Scripts Python pour les Requêtes ---")

    # 1. Run populate_db.py
    print("Étape 1: Population de la base de données...")
    if not run_command([sys.executable, os.path.join("src", "populate_db.py")], "populate_db.py"):
        return # Exit if populate_db.py fails

    # 2. Get SQL query from user
    print("\nÉtape 2: Entrez votre requête SQL (terminée par ';').")
    print("Exemple: SELECT name, department FROM employees WHERE department = 'HR';")
    user_query = ""
    while not user_query.strip().endswith(';'):
        user_query = input("Votre requête SQL: ").strip()
        if not user_query.strip().endswith(';'):
            print("La requête doit se terminer par un ';'.")

    # 3. Temporarily modify exemple_query_script.py
    # Read original content
    try:
        with open(EXEMPLE_QUERY_SCRIPT, 'r') as f:
            original_script_content = f.read()
    except FileNotFoundError:
        logger.error(f"Script '{EXEMPLE_QUERY_SCRIPT}' not found.")
        print(f"\n--- ERREUR ---")
        print(f"Le script '{EXEMPLE_QUERY_SCRIPT}' est introuvable. Assurez-vous qu'il existe.")
        return

    # Find and replace the query line using regex
    # This regex pattern is designed to find the 'query = "..."' line in the script.
    # - r'(query\s*=\s*")': This is the first capturing group (\g<1>).
    #   It matches 'query', followed by optional whitespace (\s*),
    #   an equals sign (=), optional whitespace (\s*), and a double quote (").
    #   This ensures we capture the beginning of the assignment.
    # - (.*?): This is the second capturing group (\g<2>).
    #   It matches any character (.), zero or more times (*), non-greedily (?).
    #   This captures the actual SQL query string inside the quotes.
    # - (")': This is the third capturing group (\g<3>).
    #   It matches the closing double quote (").
    pattern = r'(query\s*=\s*")(.*?)(")'
    
    # Escape double quotes in user_query for embedding into a new string literal.
    # This is crucial to prevent SyntaxError in the modified script if the user's query contains quotes.
    escaped_user_query = user_query.replace('"', '\\"')

    # The replacement string reconstructs the line:
    # - \g<1>: The first captured group (e.g., 'query = "').
    # - escaped_user_query: The user's SQL query, with any internal double quotes escaped.
    # - \g<3>: The third captured group (the closing double quote '"').
    # This ensures the 'query = "..."' structure is maintained with the new query.
    replacement = r'\g<1>' + escaped_user_query + r'\g<3>'

    # Perform the replacement, limiting to 1 occurrence to only modify the first 'query =' found.
    modified_script_content, count = re.subn(pattern, replacement, original_script_content, count=1)

    if count == 0:
        logger.error("Could not find 'query = \"...\"' line in exemple_query_script.py for modification.")
        print("\n--- ERREUR ---")
        print("Impossible de modifier la requête dans 'exemple_query_script.py'.")
        print("Veuillez vérifier le format de la ligne 'query = \"...\"' dans le script.")
        return

    # Write modified content back
    try:
        with open(EXEMPLE_QUERY_SCRIPT, 'w') as f:
            f.write(modified_script_content)
        logger.info(f"Successfully updated query in '{EXEMPLE_QUERY_SCRIPT}'.")
    except IOError as e:
        logger.error(f"Failed to write to '{EXEMPLE_QUERY_SCRIPT}': {e}")
        print(f"\n--- ERREUR ---")
        print(f"Impossible d'écrire dans '{EXEMPLE_QUERY_SCRIPT}'. Vérifiez les permissions.")
        return

    # 4. Execute exemple_query_script.py
    print("\nÉtape 3: Exécution de votre requête...")
    if not run_command([sys.executable, os.path.join("src", "exemple_query_script.py")], "exemple_query_script.py"):
        # If execution fails, revert the script to its original content
        try:
            with open(EXEMPLE_QUERY_SCRIPT, 'w') as f:
                f.write(original_script_content)
            logger.info(f"Reverted '{EXEMPLE_QUERY_SCRIPT}' to original content after error.")
        except IOError as e:
            logger.error(f"Failed to revert '{EXEMPLE_QUERY_SCRIPT}': {e}")
            print(f"ATTENTION: Impossible de restaurer '{EXEMPLE_QUERY_SCRIPT}' à son état original.")
        return

    print("\nRequête exécutée avec succès.")
    logger.info("Script-based Query use case finished.")

    # Revert the script to its original content after successful execution
    try:
        with open(EXEMPLE_QUERY_SCRIPT, 'w') as f:
            f.write(original_script_content)
        logger.info(f"Reverted '{EXEMPLE_QUERY_SCRIPT}' to original content after successful execution.")
    except IOError as e:
        logger.error(f"Failed to revert '{EXEMPLE_QUERY_SCRIPT}': {e}")
        print(f"ATTENTION: Impossible de restaurer '{EXEMPLE_QUERY_SCRIPT}' à son état original.")


def main():
    """Main function to present choices to the user."""
    print("--- Lanceur de Projet SQL ---")
    print("Choisissez un cas d'utilisation :")
    print("1. Utilisation Interactive du Notebook")
    print("2. Utilisation des Scripts Python pour les Requêtes")
    print("3. Quitter")

    while True:
        choice = input("Votre choix (1, 2 ou 3): ").strip()
        if choice == '1':
            launch_notebook_use_case()
            break
        elif choice == '2':
            script_based_query_use_case()
            break
        elif choice == '3':
            print("Exiting. Au revoir!")
            break
        else:
            print("Choix invalide. Veuillez entrer 1, 2 ou 3.")

if __name__ == "__main__":
    # Ensure we are in the correct directory for relative paths to v2
    # This script is expected to be at the root, next to the 'v2' directory
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_script_dir)
    
    main()
