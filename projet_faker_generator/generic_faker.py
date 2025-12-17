import json
import os
import pandas as pd
from faker import Faker
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Initialize the Faker object
fake = Faker()

def generate_data_as_dataframe(fields, num_entries):
    """
    Generates fake data and returns it as a pandas DataFrame.
    """
    print(f"Génération de {num_entries} entrées...")
    data = []
    for _ in range(num_entries):
        entry = {}
        for field in fields:
            try:
                method_to_call = getattr(fake, field)
                value = method_to_call()
                # Handle date/datetime objects by converting them to ISO format strings
                if hasattr(value, 'isoformat'):
                    value = value.isoformat()
                entry[field] = value
            except AttributeError:
                print(f"Avertissement : Le fournisseur Faker pour le champ '{field}' est introuvable. Il sera ignoré.")
        data.append(entry)
    return pd.DataFrame(data)

# --- Writer Functions ---

def write_to_json(df, path):
    df.to_json(path, orient='records', indent=4, force_ascii=False)

def write_to_csv(df, path):
    df.to_csv(path, index=False, encoding='utf-8')

def write_to_xlsx(df, path):
    df.to_excel(path, index=False, engine='openpyxl')

def write_to_parquet(df, path):
    try:
        import pyarrow
        df.to_parquet(path, index=False, engine='pyarrow')
    except ImportError:
        print("\nErreur : La bibliothèque 'pyarrow' est requise pour le format Parquet.")
        print("Veuillez l'installer dans votre environnement virtuel avec la commande :")
        print("pip install pyarrow")
        return False
    return True

def write_to_xml(df, path):
    root = ET.Element("data")
    for _, row in df.iterrows():
        record = ET.SubElement(root, "record")
        for field, value in row.items():
            child = ET.SubElement(record, str(field))
            child.text = str(value) if value is not None else ""

    xml_str = ET.tostring(root, 'utf-8')
    reparsed = minidom.parseString(xml_str)
    pretty_xml_str = reparsed.toprettyxml(indent="  ", encoding='utf-8')

    with open(path, "wb") as f:
        f.write(pretty_xml_str)

# --- Main execution block ---
if __name__ == "__main__":
    # 1. Read the desired fields from fields.txt
    try:
        with open('input_list_columns/fields.txt', 'r', encoding='utf-8') as f:
            desired_fields = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("Erreur : Le fichier 'fields.txt' est introuvable.")
        print("Veuillez créer ce fichier avec un nom de champ par ligne.")
        exit()

    # 2. Ask for the output format
    supported_formats = ["json", "csv", "xlsx", "parquet", "xml"]
    while True:
        format_choice = input(f"Choisissez le format de sortie ({', '.join(supported_formats)}): ").lower()
        if format_choice in supported_formats:
            break
        else:
            print(f"Format invalide. Veuillez choisir parmi : {', '.join(supported_formats)}")

    # 3. Ask for the number of entries
    while True:
        try:
            num_entries_str = input("Combien d'entrées souhaitez-vous générer ? ")
            num_entries_to_generate = int(num_entries_str)
            if num_entries_to_generate > 0:
                break
            else:
                print("Veuillez entrer un nombre supérieur à zéro.")
        except ValueError:
            print("Entrée invalide. Veuillez entrer un nombre entier.")

    # 4. Ask for the base output filename
    while True:
        output_filename_base = input("Entrez le nom du fichier de sortie (sans extension): ")
        if output_filename_base:
            break
        else:
            print("Le nom du fichier ne peut pas être vide.")

    # 5. Generate data
    dataframe = generate_data_as_dataframe(desired_fields, num_entries_to_generate)

    # 6. Write to the selected format
    output_dir = 'Data'
    os.makedirs(output_dir, exist_ok=True)
    output_file_path = os.path.join(output_dir, f"{output_filename_base}.{format_choice}")

    writer_functions = {
        'json': write_to_json,
        'csv': write_to_csv,
        'xlsx': write_to_xlsx,
        'parquet': write_to_parquet,
        'xml': write_to_xml,
    }

    print(f"Écriture du fichier {output_file_path}...")
    writer_func = writer_functions.get(format_choice)
    
    if writer_func:
        success = writer_func(dataframe, output_file_path)
        if success is not False: # writer_func returns False on failure
            print(f"\nSuccès ! Les données ont été générées et sauvegardées dans {output_file_path}")
    else:
        # This case should not be reached due to the input validation loop
        print("Erreur : Fonction d'écriture non trouvée pour le format sélectionné.")