# --- SCRIPT PRINCIPAL ---

# Charger les variables d'environnement du fichier .env
from dotenv import load_dotenv

load_dotenv()

# Imports du projet
from src.obs_twitch import (
    obtenir_jeton_twitch,
    obtenir_id_utilisateur,
    verifier_statut_live,
)
import obsws_python as obs
import time
import src.constants as constants

# --- INITIALISATION ---


# Variable pour suivre l'état
est_en_direct = False
# 1. Obtenir le jeton et l'ID une seule fois au début
jeton_twitch = obtenir_jeton_twitch()
if not jeton_twitch:
    print("Impossible d'obtenir le jeton Twitch. Arrêt du script.")
    exit()

id_utilisateur = obtenir_id_utilisateur(jeton_twitch, constants.NOM_CHAINE_TWITCH)
if not id_utilisateur:
    print("Impossible d'obtenir l'ID de l'utilisateur Twitch. Arrêt du script.")
    exit()

# 2. Se connecter à OBS
try:
    client_obs = obs.ReqClient(
        host=constants.OBS_HOST,
        port=constants.OBS_PORT,
        password=constants.OBS_PASSWORD,
    )
    print("Connecté avec succès à OBS.")
except Exception as e:
    print(f"\n[ERREUR] Impossible de se connecter à OBS : {e}")
    print(
        "Veuillez vérifier que OBS est lancé et que le serveur WebSocket est activé et correctement configuré."
    )
    exit()

# 3. Boucle de surveillance
while True:
    statut_actuel = verifier_statut_live(jeton_twitch, id_utilisateur)

    if statut_actuel and not est_en_direct:
        print("La chaîne est passée EN DIRECT. Démarrage de l'enregistrement...")
        client_obs.start_record()
        est_en_direct = True

    elif not statut_actuel and est_en_direct:
        print("La chaîne est passée HORS LIGNE. Arrêt de l'enregistrement...")
        client_obs.stop_record()
        est_en_direct = False

    else:
        print("Statut inchangé. Prochaine vérification dans 60 secondes.")

    # Attendre avant la prochaine vérification
    time.sleep(60)
