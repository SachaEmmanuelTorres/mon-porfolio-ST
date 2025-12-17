# Importer les bibliothèques pour les requêtes HTTP et le client OBS WebSocket
import requests

from . import constants


# --- FONCTIONS ---
def obtenir_jeton_twitch():
    """
    Fait une requête POST à l'API de Twitch pour obtenir un jeton d'accès d'application.
    """
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": constants.TWITCH_CLIENT_ID,
        "client_secret": constants.TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials",
    }
    try:
        response = requests.post(url, params=params)
        response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP (4xx ou 5xx)
        data = response.json()
        access_token = data.get("access_token")
        if access_token:
            print("Jeton d'accès Twitch obtenu avec succès.")
            return access_token
        print("Erreur: 'access_token' non trouvé dans la réponse de l'API Twitch.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Une erreur est survenue lors de la requête vers l'API Twitch : {e}")
        return None


def obtenir_id_utilisateur(jeton, nom_utilisateur):
    """
    Fait une requête GET à l'API de Twitch pour obtenir l'ID d'un utilisateur.
    """
    url = "https://api.twitch.tv/helix/users"
    headers = {
        "Authorization": f"Bearer {jeton}",
        "Client-ID": constants.TWITCH_CLIENT_ID,
    }
    params = {"login": nom_utilisateur}
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        users = data.get("data")
        if users and len(users) > 0:
            user_id = users[0].get("id")
            if user_id:
                print(
                    f"ID utilisateur pour '{nom_utilisateur}' obtenu avec succès : {user_id}"
                )
                return user_id
            print(
                f"Erreur: 'id' non trouvé pour l'utilisateur '{nom_utilisateur}' dans la réponse de l'API Twitch."
            )
            return None
        print(f"Erreur: Aucun utilisateur trouvé pour '{nom_utilisateur}'.")
        return None
    except requests.exceptions.RequestException as e:
        print(
            f"Une erreur est survenue lors de la requête vers l'API Twitch pour obtenir l'ID utilisateur : {e}"
        )
        return None


def verifier_statut_live(jeton, id_utilisateur):
    """
    Vérifie le statut en direct d'une chaîne Twitch.
    """
    url = "https://api.twitch.tv/helix/streams"
    headers = {
        "Authorization": f"Bearer {jeton}",
        "Client-ID": constants.TWITCH_CLIENT_ID,
    }
    params = {"user_id": id_utilisateur}
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        streams = data.get("data")
        if streams and len(streams) > 0:
            print(f"La chaîne est EN DIRECT. Titre: {streams[0].get('title')}")
            return True
        print("La chaîne est HORS LIGNE.")
        return False
    except requests.exceptions.RequestException as e:
        print(
            f"Une erreur est survenue lors de la requête vers l'API Twitch pour vérifier le statut live : {e}"
        )
