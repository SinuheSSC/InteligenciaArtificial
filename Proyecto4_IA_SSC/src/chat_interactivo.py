import os
import chromadb
import ollama

# Conectarnos a la base de datos vectorial local (ChromaDB)
DB_DIR = "./vector_db"
chroma_client = chromadb.PersistentClient(path=DB_DIR)
coleccion = chroma_client.get_collection(name="seguridad_mexico")

print("======================================================================")
print("   🍥 ¡BIENVENIDO AL DOJO DEL TUTOR HÍBRIDO DE SEGURIDAD PÚBLICA! 🍥  ")
print("        Escribe tu pregunta y presiona Enter. (Escribe 'salir' para terminar)       ")
print("======================================================================")

while True:
    # 1. Recibir la pregunta directamente del usuario en la terminal
    pregunta = input("\n👤 Pregunta: ")
    
    if pregunta.lower() == 'salir':
        print("\n¡Entendido! Sigue entrenando duro en tu camino ninja. ¡Adiós, de veras! 🦊")
        break
        
    if not pregunta.strip():
        continue
        
    print("⏳ Buscando en los pergaminos del corpus...")
    
    # ======================================================================
    # FILTRO INTELIGENTE DE METADATOS (OPTIMIZACIÓN RAG)
    # ======================================================================
    # Validamos programáticamente si el estudiante menciona un documento específico
    filtro_metadata = None
    # Recorremos en reversa para proteger los dos dígitos
    for numero in range(22, 0, -1):
        if f"violenciaenmexico{numero}" in pregunta.lower().replace(" ", "") or f"documento {numero}" in pregunta.lower() or f"archivo {numero}" in pregunta.lower():
            filtro_metadata = {"fuente": f"violenciaEnMexico{numero}.pdf"}
            break
    
    # 2. RECUPERACIÓN ROBUSTA: Subimos a 5 fragmentos para no perder información dura
    resultado_vectorial = coleccion.query(
        query_texts=[pregunta],
        n_results=4,
        where=filtro_metadata
    )
    
    chunks_recuperados = resultado_vectorial['documents'][0]
    metadatas_recuperadas = resultado_vectorial['metadatas'][0]
    
    # ======================================================================
    # 3. CONTEXTO RIGUROSO CON ETIQUETAS DE ACCIÓN (EVITA CRUCE DE DATOS)
    # ======================================================================
    contexto_inyectado = ""
    for i, chunk in enumerate(chunks_recuperados):
        fuente = metadatas_recuperadas[i]['fuente']
        pagina = metadatas_recuperadas[i]['pagina']
        chunk_limpio = chunk.replace("\n", " ").strip()
        
        # Etiquetamos rígidamente el inicio y fin de cada documento para el LLM
        contexto_inyectado += f"=== INICIO ARCHIVO: {fuente} (Pág. {pagina}) ===\n"
        contexto_inyectado += f"{chunk_limpio[:850]}\n"
        contexto_inyectado += f"=== FIN ARCHIVO: {fuente} ===\n\n"
    
    # ======================================================================
    # 4. PROMPT DE CONTENCION INGENIERIL (ESTRICTO ANTI-ALUCINACIONES)
    # ======================================================================
    prompt_final = (
        f"SISTEMA DE EXTRACCIÓN ACADÉMICA - DIRECTRIZ INMUTABLE:\n"
        f"1. Responde de forma muy corta y directa la pregunta utilizando UNICAMENTE los datos explícitos del contexto adjunto.\n"
        f"2. Está PROHIBIDO citar autores, libros o años que no aparezcan textualmente en las etiquetas '=== INICIO ARCHIVO' provistas abajo.\n"
        f"3. FORMATO DE CITA OBLIGATORIO: Al terminar tu respuesta, escribe estrictamente el archivo y página real del fragmento utilizado usando la estructura: [NombreDelArchivo.pdf, Pág. X]. No uses texto genérico.\n"
        f"4. Si el dato exacto no está en los bloques, di de inmediato que tu camino ninja no te permite inventar datos.\n\n"
        f"Contexto:\n{contexto_inyectado}\n"
        f"Pregunta: {pregunta}\n\n"
        f"Respuesta concisa de Naruto:"
    )
    
    # 5. Consultar localmente a Ollama de manera segura (Cero cuellos de botella térmicos)
    try:
        response = ollama.chat(
            model='tutor_naruto',
            messages=[{'role': 'user', 'content': prompt_final}]
        )
        
        # 6. Imprimir la respuesta directa en la terminal
        print("\n🦊 Tutor Naruto:")
        print(response['message']['content'])
        print("-" * 70)
        
    except Exception as e:
        print(f"\n❌ ¡Ocurrió un error en la conexión ninja!: {e}")
        print("Asegúrate de que la aplicación de Ollama esté abierta con el icono de la llama cerca del reloj.")