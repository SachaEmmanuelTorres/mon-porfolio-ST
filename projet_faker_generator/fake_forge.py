
import pandas as pd
from faker import Faker
import os

# Initialize the Faker object
fake = Faker()

def generate_fake_dataframe(fields, num_rows):
    """
    Génère des données factices en colonnes et les retourne sous forme de DataFrame pandas.

    Args:
        fields (list): Une liste de chaînes de caractères correspondant aux méthodes du fournisseur Faker.
        num_rows (int): Le nombre de lignes (enregistrements) à générer.

    Returns:
        pandas.DataFrame: Un DataFrame contenant les données factices générées.
    """
    print(f"Génération de {num_rows} lignes de données...")
    
    # Initialiser un dictionnaire pour stocker les données par colonne
    data_columns = {field: [] for field in fields}

    for _ in range(num_rows):
        for field in fields:
            try:
                method_to_call = getattr(fake, field)
                value = method_to_call()
                # Convertir les objets date/datetime en chaînes ISO pour une meilleure compatibilité
                if hasattr(value, 'isoformat'):
                    value = value.isoformat()
                data_columns[field].append(value)
            except AttributeError:
                # Si un fournisseur Faker n'existe pas pour un champ, ajouter None ou une chaîne vide
                # pour maintenir la longueur de la colonne.
                print(f"Avertissement : Le fournisseur Faker pour '{field}' est introuvable. Ajout de None.")
                data_columns[field].append(None)
            except Exception as e:
                print(f"Erreur lors de la génération du champ '{field}': {e}. Ajout de None.")
                data_columns[field].append(None)

    # Créer le DataFrame à partir du dictionnaire de colonnes
    df = pd.DataFrame(data_columns)
    return df

# --- Bloc d'exécution principal ---
if __name__ == "__main__":
    # 1. Lire la liste des champs depuis input_list_columns/fields.txt
    fields_file_path = 'input_list_columns/fields.txt'
    try:
        with open(fields_file_path, 'r', encoding='utf-8') as f:
            desired_fields = [line.strip() for line in f if line.strip()]
        print(f"Champs à générer lus depuis {fields_file_path}: {desired_fields}")
    except FileNotFoundError:
        print(f"Erreur : Le fichier '{fields_file_path}' est introuvable.")
        print("Veuillez créer ce fichier avec un nom de champ par ligne.")
        exit()

    # 2. Demander à l'utilisateur le nombre de lignes à générer
    while True:
        try:
            num_rows_str = input("Combien de lignes de données souhaitez-vous générer ? ")
            num_rows_to_generate = int(num_rows_str)
            if num_rows_to_generate > 0:
                break
            else:
                print("Veuillez entrer un nombre supérieur à zéro.")
        except ValueError:
            print("Entrée invalide. Veuillez entrer un nombre entier.")

    # 3. Générer le DataFrame
    fake_dataframe = generate_fake_dataframe(desired_fields, num_rows_to_generate)

    # 4. Afficher les premières lignes du DataFrame généré
    print("\n--- Aperçu du DataFrame généré ---")
    print(fake_dataframe.head())

    # Optionnel: Sauvegarder le DataFrame dans un fichier CSV pour démonstration
    output_dir = 'Data'
    os.makedirs(output_dir, exist_ok=True)
    output_csv_path = os.path.join(output_dir, 'fake_forge_output.csv')
    fake_dataframe.to_csv(output_csv_path, index=False, encoding='utf-8')
    print(f"\nDataFrame sauvegardé dans {output_csv_path}")
