import ollama
from openai import OpenAI

# 1. Test avec Ollama
print("--- Test Ollama ---")
try:
    response = ollama.chat(model='llama3.2', messages=[
        {'role': 'user', 'content': 'Bonjour, es-tu prêt ?'},
    ])
    print("Ollama:", response['message']['content'])
except Exception as e:
    print("Ollama non disponible ou modèle manquant.")

# 2. Test avec Llama.cpp (API compatible OpenAI)
print("\n--- Test Llama.cpp ---")
client = OpenAI(base_url="http://localhost:8090/v1", api_key="sk-no-key-required")

try:
    completion = client.chat.completions.create(
      model="qwen2.5-3b-instruct",
      messages=[
        {"role": "user", "content": "Quelle est la capitale du Québec ?"}
      ]
    )
    print("Llama.cpp:", completion.choices[0].message.content)
except Exception as e:
    print("Llama.cpp non disponible.")
