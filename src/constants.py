import os

# --- CONFIGURATION (chargée depuis l'environnement) ---
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
NOM_CHAINE_TWITCH = os.getenv("NOM_CHAINE_TWITCH")
OBS_HOST = os.getenv("OBS_HOST")
OBS_PORT = int(os.getenv("OBS_PORT"))
OBS_PASSWORD = os.getenv("OBS_PASSWORD")
NOM_SCENE_OBS = os.getenv("NOM_SCENE_OBS")
