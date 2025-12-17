"""
Ce script est dédié à la fonctionnalité principale de génération de données fictives
et ne doit pas être modifié sans une compréhension approfondie de son impact.
"""

import random
import pandas as pd
from faker import Faker
from pydantic import BaseModel, Field, create_model
from typing import Dict, Any, Type

fake = Faker()

class DynamicDataGenerator:
    """
    Générateur de données fictives dynamique basé sur un fichier de configuration des champs.

    Cette classe lit une configuration de champs à partir d'un fichier texte,
    crée dynamiquement un modèle Pydantic et génère des données fictives
    sous forme de DataFrame Pandas en utilisant la bibliothèque Faker.
    """

    def __init__(self, fields_file_path: str):
        """
        Initialise le générateur de données fictives.

        Args:
            fields_file_path (str): Le chemin absolu vers le fichier de configuration des champs.
                                    Chaque ligne du fichier doit être au format 'nom_champ:fournisseur_faker'.
                                    Une ligne '_observations:NOMBRE' peut être incluse pour définir le nombre de lignes.
        """
        self.fields_file_path = fields_file_path
        self.fields_config, self.data_range_observations = self._load_fields_config()
        self.dynamic_model = self._create_dynamic_pydantic_model()

    def _load_fields_config(self) -> (Dict[str, str], int):
        """
        Charge les configurations de champs à partir du fichier spécifié et le nombre d'observations.

        Le format attendu pour chaque ligne est 'nom_champ:fournisseur_faker'.
        Une ligne '_observations:NOMBRE' peut être incluse pour définir le nombre de lignes.
        Par défaut, le nombre d'observations est 1000 si non spécifié.

        Returns:
            (Dict[str, str], int): Un tuple contenant un dictionnaire où les clés sont les noms de champs
                                   et les valeurs sont les chaînes de fournisseurs Faker,
                                   ainsi que le nombre d'observations à générer.

        Raises:
            FileNotFoundError: Si le fichier de configuration des champs est introuvable.
        """
        config = {}
        observations = 1000  # Valeur par défaut
        try:
            with open(self.fields_file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and ':' in line:
                        field_name, value = line.split(':', 1)
                        field_name = field_name.strip()
                        value = value.strip()
                        if field_name == '_observations':
                            try:
                                observations = int(value)
                            except ValueError:
                                print(f"Avertissement: La valeur de _observations '{value}' n'est pas un entier valide. Utilisation de la valeur par défaut (1000).")
                        else:
                            config[field_name] = value
        except FileNotFoundError:
            raise FileNotFoundError(f"Le fichier de configuration des champs est introuvable: {self.fields_file_path}")
        return config, observations

    def _create_dynamic_pydantic_model(self) -> Type[BaseModel]:
        """
        Crée dynamiquement un modèle Pydantic basé sur les configurations de champs chargées.

        Le type de chaque champ est inféré de manière basique à partir du nom du fournisseur Faker.
        Par défaut, les champs sont de type `str`. Si 'int' est présent dans le fournisseur,
        le type est défini comme `int`. Si 'date' ou 'time' est présent, le type reste `str`
        car Faker retourne souvent des chaînes pour ces types.

        Returns:
            Type[BaseModel]: Le modèle Pydantic généré dynamiquement.
        """
        fields = {}
        for field_name, faker_provider in self.fields_config.items():
            # Tentative d'inférer le type basé sur le fournisseur faker, par défaut str
            if 'int' in faker_provider:
                fields[field_name] = (int, Field(...))
            elif 'date' in faker_provider or 'time' in faker_provider:
                fields[field_name] = (str, Field(...)) # Les dates Faker sont souvent des chaînes
            else:
                fields[field_name] = (str, Field(...))

        DynamicModel = create_model("DynamicModel", **fields)
        return DynamicModel

    def generate_fake_data(self) -> pd.DataFrame:
        """
        Génère des données fictives basées sur le modèle dynamique et retourne un DataFrame Pandas.

        Chaque ligne du DataFrame est créée en appelant le fournisseur Faker correspondant
        pour chaque champ défini dans la configuration. Les fournisseurs Faker imbriqués
        (ex: 'unique.random_int') sont gérés.

        Returns:
            pd.DataFrame: Un DataFrame Pandas contenant les données fictives générées.
        """
        import re # Ajout de l'import pour re

        data = []
        for _ in range(self.data_range_observations):
            row = {}
            for field_name, faker_provider_str in self.fields_config.items():
                # Gérer les fournisseurs faker avec arguments comme 'random_element(['a', 'b'])'
                match = re.match(r"(\w+)\((.*)\)", faker_provider_str)
                if match:
                    provider_name = match.group(1)
                    args_str = match.group(2)
                    # Tenter d'évaluer les arguments (ex: "['a', 'b']")
                    try:
                        # Utilisation de eval est potentiellement dangereuse avec des entrées non fiables.
                        # Ici, nous partons du principe que les entrées viennent de fichiers de config contrôlés.
                        args = eval(args_str)
                        if not isinstance(args, (list, tuple)):
                            args = (args,) # S'assurer que c'est un tuple pour *args
                    except Exception:
                        args = (args_str,) # Si l'évaluation échoue, traiter comme une chaîne simple

                    current_provider_func = getattr(fake, provider_name)

                    # Si les arguments évalués sont une liste ou un tuple, on les passe directement à la fonction.
                    # Sinon, on passe l'argument simple tel quel.
                    if isinstance(args, (list, tuple)):
                        row[field_name] = current_provider_func(args)
                    else:
                        row[field_name] = current_provider_func(args)
                else:
                    # Logique existante pour les fournisseurs sans arguments (ex: 'name', 'unique.random_int')
                    provider_parts = faker_provider_str.split('.')
                    current_provider = fake
                    for part in provider_parts:
                        current_provider = getattr(current_provider, part)

                    if callable(current_provider):
                        row[field_name] = current_provider()
                    else:
                        row[field_name] = current_provider # Pour les attributs simples si existants

            data.append(row)

        return pd.DataFrame(data)