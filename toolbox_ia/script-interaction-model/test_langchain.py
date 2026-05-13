from langchain_community.llms import HuggingFaceEndpoint
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os

# Lecture du token depuis le fichier sécurisé
with open("token_langchain.md", "r") as f:
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = f.read().strip()

print("--- Test LangChain avec Hugging Face ---")

# Configuration du modèle via l'API Hugging Face
repo_id = "mistralai/Mistral-7B-Instruct-v0.2"

llm = HuggingFaceEndpoint(
    repo_id=repo_id,
    max_length=128,
    temperature=0.5,
)

template = """Question: {question}

Réponse: Donnez une réponse courte et précise en français."""

prompt = PromptTemplate.from_template(template)
llm_chain = prompt | llm

try:
    question = "Quels sont les avantages de l'IA open source ?"
    print(f"Modèle distant : {repo_id}")
    print(f"Question : {question}")
    
    response = llm_chain.invoke({"question": question})
    print("\nRéponse de l'IA :")
    print(response)

except Exception as e:
    print(f"\nErreur : {e}")
    print("Note : L'API Hugging Face peut nécessiter quelques secondes pour charger le modèle.")

# Exemple d'appel local (Ollama)
print("\n--- Note : Utilisation locale ---")
print("Pour utiliser Ollama avec LangChain, utilisez :")
print("from langchain_community.llms import Ollama")
print("llm = Ollama(model='llama3.2', base_url='http://localhost:11434')")
