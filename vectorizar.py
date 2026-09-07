import pandas as pd
import chromadb
import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. Cargar nuestra llave secreta
load_dotenv()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

print("🚀 Iniciando la lectura del archivo CSV...")

# 2. Crear la base de datos local en tu Mac
# Esto creará una carpeta llamada "base_vectorial" junto a tus archivos
cliente_chroma = chromadb.PersistentClient(path="./base_vectorial")

# Borramos la base si ya existía para empezar limpios
try:
    cliente_chroma.delete_collection(name="tramites_irapuato")
except:
    pass

coleccion = cliente_chroma.create_collection(name="tramites_irapuato")

# 3. Leer el CSV que nos compartió el equipo
df = pd.read_csv('Base tramites septiembre 26.csv')

# 4. Procesar fila por fila
for indice, fila in df.iterrows():
    # Juntamos los datos más importantes en un solo bloque de texto
    texto_tramite = f"TRÁMITE: {fila['tramite_nombre']}\n" \
                    f"DEPENDENCIA: {fila['dependencia_responsable']}\n" \
                    f"DESCRIPCIÓN: {fila['tramite_descripcion']}\n" \
                    f"REQUISITOS: {fila['requisitos']}\n" \
                    f"COSTO: {fila['costos']}\n" \
                    f"TIEMPO DE RESPUESTA: {fila['tiempo_respuesta']}\n" \
                    f"UBICACIÓN: {fila['ubicaciones']}"
    
    # 5. Generar el Embedding (con el modelo correcto)
    respuesta_embedding = genai.embed_content(
        model="models/gemini-embedding-001",
        content=texto_tramite
    )
    vector = respuesta_embedding['embedding']
    
    # 6. Guardar todo en ChromaDB
    coleccion.add(
        embeddings=[vector],
        documents=[texto_tramite],
        metadatas=[{"nombre": fila['tramite_nombre'], "dependencia": fila['dependencia_responsable']}],
        ids=[str(fila['id'])]
    )
    print(f"✅ Guardado: {fila['tramite_nombre']}")

print("🎉 ¡Vectorización terminada con éxito!")