**Prérequis du Projet (Ubuntu 24.04)**

**1. Dépendances Système (apt)**

```bash
sudo apt update
sudo apt install python3-venv python3-pip nodejs npm libnss3 libatk1.0-0
```

**2. Environnement Python**

1. Créer l'environnement : `python3 -m venv .env`
2. Activer : `source .env/bin/activate`
3. Installer les paquets : `pip install -r requirements.txt`

**3. Serveurs MCP & Configuration LLM**

**3.0 Configuration du stockage (Optionnel mais recommandé)**
Pour éviter de saturer la racine (`/`), vous pouvez stocker les modèles dans le dossier du projet :
```bash
# S'assurer que le dossier existe et a les bons droits
mkdir -p /media/sacha/datas/3w_quebec_23_avril_2026/models
chmod +x /media/sacha/datas/3w_quebec_23_avril_2026
chmod -R 775 /media/sacha/datas/3w_quebec_23_avril_2026/models

# À exécuter avant de lancer ollama serve ou à ajouter dans votre .bashrc
export OLLAMA_MODELS="/media/sacha/datas/3w_quebec_23_avril_2026/models"
```

**3.1 Installation d'Ollama :**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**3.2 Lancement du serveur :**
Assurez-vous que le serveur utilise le bon dossier de stockage :
```bash
OLLAMA_MODELS="/media/sacha/datas/3w_quebec_23_avril_2026/models" ollama serve
```

**3.3 Téléchargement des modèles :**
```bash
ollama pull phi3:mini          # Réflexion / Planification
ollama pull qwen2.5:3b         # Rédaction / Synthèse
ollama pull mxbai-embed-large  # RAG / Embeddings
```

**4. Serveur MCP Browser**
Le serveur Puppeteer sera installé automatiquement via `npx` lors de la première exécution du script `agent_rag.py`.

**5. État Final des Modèles (Vérification OK)**
- **Planificateur :** `phi3:mini` (2.2 GB) - **Installé**
- **Rédacteur :** `qwen2.5:3b` (1.9 GB) - **Installé**
- **Embeddings (RAG) :** `mxbai-embed-large` (669 MB) - **Installé**
- **Polyvalent :** `llama3.2:latest` (2.0 GB) - **Installé**

**6. Lancement pour la Démo (UQAM 23 Avril)**
Pour garantir que l'agent utilise le bon stockage sur le disque de données :
```bash
export OLLAMA_MODELS="/media/sacha/datas/3w_quebec_23_avril_2026/models"
ollama serve
```
*Note : Gardez ce terminal ouvert pendant l'exécution des scripts `agent_rag.py` ou `agent_rag_v2.py`.*
