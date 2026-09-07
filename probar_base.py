import chromadb
import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. Cargar las llaves
load_dotenv()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

print("🔍 Conectando con la base de datos local...")

# 2. Conectar a ChromaDB
cliente_chroma = chromadb.PersistentClient(path="./base_vectorial")
coleccion = cliente_chroma.get_collection(name="tramites_irapuato")

print(f"✅ Hay {coleccion.count()} trámites guardados en total.\n")

# 3. La pregunta de prueba
pregunta_prueba = "Quiero abrir un local comercial para vender comida"
print(f"🤔 Buscando trámites relacionados con: '{pregunta_prueba}'\n")

# 4. Convertir la pregunta a vector usando el MISMO modelo
pregunta_embed = genai.embed_content(
    model="models/gemini-embedding-001",
    content=pregunta_prueba
)['embedding']

# 5. Buscar en la base de datos los 3 más cercanos
resultados = coleccion.query(
    query_embeddings=[pregunta_embed],
    n_results=3
)

# 6. Mostrar los resultados
print("🏆 LOS 3 TRÁMITES MÁS RELEVANTES ENCONTRADOS SON:")
print("-" * 50)
for i in range(len(resultados['ids'][0])):
    nombre_tramite = resultados['metadatas'][0][i]['nombre']
    dependencia = resultados['metadatas'][0][i]['dependencia']
    print(f"{i+1}. {nombre_tramite}")
    print(f"   Dependencia: {dependencia}")
    print("-" * 50)