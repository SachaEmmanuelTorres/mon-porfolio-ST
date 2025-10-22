import sqlite3
import os

from loguru import logger
import constants as ct

# initialisation du fichier log
logger.add(
    "execution_queries.log", 
    format="{time} {level} {message}", 
    level="DEBUG", rotation="10 MB"
        )
work_env = os.getcwd()

logger.info(f"📁 Répertoire de travail : {work_env}")
# le repertoire de travail s'affiche maintenant dans le logger.info



# Connexion à la base de données
conn = sqlite3.connect(ct.DB_NAME)
cursor = conn.cursor()

# Exemples de codes python de requetes :

# Voir les scripts SQLite de requetes
# sur les base de donnees SQLite explo.db
# contenue dans le repertoire SQL_queries_scripts

# ceci est un exemple de requete SQL
# remplacer la requete par celle de votre choix

query = "SELECT * FROM products WHERE price > 50;"

# Exécution de la requête
cursor.execute(query)
rows = cursor.fetchall()

# Affichage des resultats
print("Résultats de la requête :")
for row in rows:
    logger.info(row)

# Fermeture de la connexion a la base de donnees
cursor.close()
conn.close()

logger.info("✅ Connexion fermée.")
