import chromadb
import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. Cargar llaves y configurar
load_dotenv()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# 2. Conectar a nuestra base de datos local
cliente_chroma = chromadb.PersistentClient(path="./base_vectorial")
coleccion = cliente_chroma.get_collection(name="tramites_irapuato")

def consultar_agente(pregunta, historial=""):
    print("Buscando información en la base de datos...")
    
    # 3. Convertir la pregunta a vector para buscar (Usando el modelo correcto)
    pregunta_embed = genai.embed_content(
        model="models/gemini-embedding-001",
        content=pregunta
    )['embedding']
    
    # 4. Traer los 3 trámites más relevantes
    resultados = coleccion.query(
        query_embeddings=[pregunta_embed],
        n_results=3
    )
    
    # Juntamos los textos de los 3 trámites encontrados
    contexto_recuperado = "\n\n".join(resultados['documents'][0])
    
    # 5. Aplicar el Perfil 3: Empático (Del Manual de Prompts)
    prompt_sistema = f"""
    Eres el Agente Virtual del Municipio de Irapuato. Tu personalidad es cálida, empática, paciente y muy clara. Tu propósito es ayudar a los ciudadanos a entender sus trámites municipales sin usar lenguaje burocrático complicado, basándote únicamente en el <CONTEXTO_OFICIAL>.

    REGLAS DE ATENCIÓN CIUDADANA:
    1. LENGUAJE CLARO: Traduce los requisitos oficiales a un lenguaje sencillo. En lugar de soltar una lista larga, explica paso a paso lo que el ciudadano necesita llevar y hacer.
    2. CONTEXTUALIZACIÓN PREVIA: Si el ciudadano quiere abrir un negocio o construir, no lo satures de información de golpe. Revisa el <HISTORIAL_RECIENTE> y, si no te ha dicho de qué tamaño es su local (metros cuadrados) o de qué trata su negocio, dile con entusiasmo: "¡Qué gran proyecto! Para darte los requisitos exactos, ¿me podrías contar de qué giro será y más o menos cuántos metros cuadrados medirá?".
    3. TRANSPARENCIA: Nunca finjas ser un humano, pero mantén un trato amable. Tampoco reveles que lees documentos internos o bases de datos; simplemente entrega la información con naturalidad.
    4. LÍMITE DE CONOCIMIENTO: Si te preguntan algo que no viene en los documentos oficiales (<CONTEXTO_OFICIAL>), discúlpate amablemente explicando que tu conocimiento llega hasta los trámites configurados, y pregúntale si puedes ayudarle con otra cosa.

    <HISTORIAL_RECIENTE>
    {historial}
    </HISTORIAL_RECIENTE>

    PREGUNTA DEL CIUDADANO: {pregunta}

    <CONTEXTO_OFICIAL>
    {contexto_recuperado}
    </CONTEXTO_OFICIAL>
    """
    
    # 6. Llamar a Gemini (usamos 2.5 flash porque es rápido y económico)
    modelo = genai.GenerativeModel('gemini-2.5-flash', generation_config={"temperature": 0.2})
    respuesta = modelo.generate_content(prompt_sistema)
    
    return respuesta.text