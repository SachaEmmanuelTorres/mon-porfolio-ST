# IA Locale, Open Source et Agents RAG (version 2)

### Bâtir une infrastructure souveraine avec Podman


### Le choix de l'écosystème

**Le choix du LLM :** ⇒ Hugging Face : [https://huggingface.co/](https://huggingface.co/)

Approche structurée :

- **Modèles optimisés pour le code :** Granite 3.0 3B (Instruct) et Qwen 2.5 3B (Instruct).

- **Format :** Utilisation systématique du format GGUF.

**Le choix des outils :**

- **Llama.cpp :** Serveur backend haute performance.

- **Ollama :** Gestionnaire de modèles local simplifié.

- **OpenCode-GUI :** Environnement de développement conteneurisé.

- **OpenRouter-Proxy :** Hub central pour l'orchestration.


### 🏗️ Architecture : La Force du Volume Partagé

- **Un seul dossier `/models`** pour tous les services.

- **Interopérabilité** : Ollama (modèles simples) + Llama.cpp (GGUF avancés).

- **Persistance** : Logs, Données et Entraînement isolés.


### Agents & RAG :

- **RAG (Retrieval Augmented Generation) :** Système basé sur Marimo pour interroger dynamiquement vos connaissances locales.

- **Interfaces graphiques :** Open-WebUI (Port 3000).


### 🛠️ Automatisation et Interaction

- **`add\_model.sh`** : Un pont interactif entre Hugging Face et votre stack locale.

- **Écosystème Python (uv)** :

  - Scripts d'interaction rapides.

  - Intégration LangChain & Pydantic-AI.


### MCP (Model Context Protocol)

**Définition :** Standard pour exposer des outils et données aux modèles de manière sécurisée.

**Exemple d'outil MCP :**

```
def check\_disk\_usage():  
    import shutil  
    total, used, free = shutil.disk\_usage("/")  
    return \{"total": total, "used": used, "free": free\}  
  
from mcp.server import Server  
from mcp.types import Tool, Schema  
  
server = Server()  
@server.tool(  
    Tool(  
        name="check\_disk",  
        description="Returns disk usage stats",  
        input\_schema=Schema(type="object", properties=\{\}),  
        output\_schema=Schema(  
            type="object",  
            properties=\{  
                "total": \{"type": "number"\},  
                "used": \{"type": "number"\},  
                "free": \{"type": "number"\}  
            \}  
        )  
    )  
)  
def check\_disk\_tool(\_args):  
    return check\_disk\_usage()  
  
server.run()
```


### 🚀 Démo : Du modèle à l'interaction

1. **Démarrage** : `podman-compose up -d`

2. **Installation** : `./add\_model.sh`

3. **Inférence** : `uv run test\_ai.py`


### 🌐 Conclusion

- **Souveraineté Totale** : 100% Hors-ligne si nécessaire.

- **Contrôle des coûts** : Pas de facturation au token.

**Merci de votre attention !** *Accès stack : http://localhost:8080*

