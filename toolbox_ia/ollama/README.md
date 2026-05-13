# 🦙 Ajout de modèles à Ollama

Pour ajouter un modèle à Ollama, vous devez d'abord consulter sa **carte d'identité** (Model Card) sur Hugging Face pour vérifier ses spécifications et son nom exact.

### 🌐 Hugging Face
[Rechercher des modèles sur Hugging Face](https://huggingface.co/models)

### 💻 Méthodes d'ajout

#### Option A : Téléchargement depuis le Hub officiel
Si le modèle est disponible sur [ollama.com/library](https://ollama.com/library) :
```bash
podman exec -it ollama ollama pull <nom_du_modele>
```

#### Option B : Importation d'un fichier GGUF local
Si vous avez un fichier `.gguf` dans votre dossier `/models` :

1. Créez un fichier `Modelfile` :
   ```bash
   echo "FROM /root/.ollama/models/<votre_fichier>.gguf" > Modelfile
   ```
2. Importez le modèle dans Ollama :
   ```bash
   podman exec -it ollama ollama create <nom_choisi> -f /root/.ollama/models/Modelfile
   ```
