from huggingface_hub import InferenceClient
import os

# Pour utiliser l'API, vous pouvez définir votre jeton dans un fichier .env
# ou directement ici pour le test (non recommandé en production)
# HF_TOKEN = "votre_token_ici"
HF_TOKEN = os.getenv("HF_TOKEN")

client = InferenceClient(api_key=HF_TOKEN)

print("--- Test Hugging Face Inference API ---")

# Exemple avec un modèle de texte
model_id = "meta-llama/Llama-3.2-3B-Instruct"

try:
    messages = [{"role": "user", "content": "Quelle est la particularité du Québec ?"}]
    
    completion = client.chat.completions.create(
        model=model_id, 
        messages=messages, 
        max_tokens=500
    )

    print(f"Modèle : {model_id}")
    print("Réponse :", completion.choices[0].message.content)

except Exception as e:
    print(f"Erreur lors de l'appel à l'API : {e}")
    print("Note : Assurez-vous d'avoir défini la variable d'environnement HF_TOKEN.")
