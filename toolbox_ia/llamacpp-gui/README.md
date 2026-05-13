# 🏗️ Ajout de modèles à llama.cpp

Pour ajouter un modèle au format GGUF à llama.cpp, consultez sa **carte d'identité** sur Hugging Face pour identifier le dépôt et le fichier GGUF spécifique.

### 🌐 Hugging Face
[Rechercher des modèles GGUF sur Hugging Face](https://huggingface.co/models?library=gguf)

### 💻 Méthodes de lancement

#### Option A : Téléchargement direct (Hugging Face)
Le serveur télécharge et lance le modèle en une commande :
```bash
podman exec -it llamacpp ./build/bin/llama-server \
  --hf-repo <utilisateur>/<depot-gguf> \
  --hf-file <nom_du_fichier>.gguf \
  --host 0.0.0.0 --port 8090
```

#### Option B : Utilisation d'un fichier local
Si le fichier est déjà dans votre volume `/models` :
```bash
podman exec -it llamacpp ./build/bin/llama-server \
  --model /models/<votre_fichier>.gguf \
  --host 0.0.0.0 --port 8090
```

---
*Note : Le volume `/models` est mappé sur votre dossier de stockage local pour persister les téléchargements.*
