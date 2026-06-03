import time
import chromadb
import ollama

# Conectarnos a la base de datos vectorial que creamos en el Paso 1
DB_DIR = "./vector_db"
chroma_client = chromadb.PersistentClient(path=DB_DIR)
coleccion = chroma_client.get_collection(name="seguridad_mexico")

# Banco de preguntas oficial de la actividad
banco_preguntas = [
    # Nivel 1: Extracción Directa
    "¿Cuáles son las tres entidades federativas con mayor índice de homicidios dolosos según los datos más recientes incluidos en el corpus?",
    "¿Qué organizaciones, cárteles o grupos delictivos se mencionan con mayor frecuencia operando en la región de Tierra Caliente?",
    "¿Cuáles son las cifras oficiales reportadas sobre el desplazamiento forzado interno a causa de la violencia durante el último sexenio documentado?",
    
    # Nivel 2: Síntesis
    "Según los documentos, ¿cuáles son las principales causas socioeconómicas que los autores asocian directamente al incremento de la violencia urbana?",
    "Contrasta las estrategias de seguridad pública mencionadas en el corpus. ¿Qué diferencias de enfoque existen entre la militarización y las políticas de prevención social?",
    "¿Cómo ha evolucionado la tasa de delitos de extorsión (cobro de piso) a nivel nacional and qué sectores económicos se reportan como los más afectados?",
    "¿Existe alguna diferencia significativa documentada en los tipos de violencia que experimentan las zonas rurales en comparación con las zonas metropolitanas?",
    
    # Nivel 3: Razonamiento Analítico y Límites (Preguntas trampa)
    "Con base en las posturas de las ONGs y las fuentes gubernamentales presentes en los textos, ¿cuáles son las principales contradicciones o discrepancias en el registro de víctimas?",
    "¿Qué impacto específico tiene la violencia documentada sobre la tasa de deserción escolar en las zonas de alto conflicto?",
    "A partir de las conclusiones de los autores en el corpus, ¿qué vacíos de información, subregistros o falta de datos fiables se identifican como el principal obstacle para medir la violencia real en el país?"
]

print("⚡ INICIANDO BANCO DE PRUEBAS DEL TUTOR HÍBRIDO (RAG + FINE-TUNING) ⚡\n")

# Iterar sobre cada pregunta del banco
for idx, pregunta in enumerate(banco_preguntas, 1):
    print("="*80)
    print(f"Pregunta Q{idx}: {pregunta}")
    print("="*80)
    
    # 1. Medir tiempo de la Recuperación RAG
    inicio_rag = time.time()
    
    # Mantenemos el Top-K = 6 para garantizar la certeza en la búsqueda de datos exactos
    resultado_vectorial = coleccion.query(
        query_texts=[pregunta],
        n_results=6
    )
    
    chunks_recuperados = resultado_vectorial['documents'][0]
    metadatas_recuperadas = resultado_vectorial['metadatas'][0]
    fin_rag = time.time()
    
    # Construir el contexto optimizado para no saturar la GPU
    contexto_inyectado = ""
    print("\n[CHUNKS RECUPERADOS DE LOS PDFS]:")
    for i, chunk in enumerate(chunks_recuperados):
        fuente = metadatas_recuperadas[i]['fuente']
        pagina = metadatas_recuperadas[i]['pagina']
        print(f" -> Fragmento {i+1} de {fuente} (Pág. {pagina}): {chunk[:80].strip()}...")
        
        # Limpiamos los molestos saltos de línea del PDF y limitamos el tamaño
        chunk_limpio = chunk.replace("\n", " ").strip()
        contexto_inyectado += f"Fragmento extraído de {fuente} (Pág. {pagina}): {chunk_limpio[:450]}\n\n"
    
    # 2. Enviar los datos combinados al modelo a través de Ollama y medir la latencia de generación
    inicio_llm = time.time()
    
    # Forzamos una instrucción de concisión al prompt final para limitar tokens redundantes
    prompt_final = f"Contexto breve para análisis:\n{contexto_inyectado}\nEstudiante pregunta: {pregunta}\nResponde de forma concisa:"
    
    response = ollama.chat(
        model='tutor_naruto',
        messages=[{'role': 'user', 'content': prompt_final}]
    )
    
    fin_llm = time.time()
    
    # Calcular métricas de tiempo exigidas en las notas de evaluación
    latencia_rag = fin_rag - inicio_rag
    latencia_llm = fin_llm - inicio_llm
    latencia_total = latencia_rag + latencia_llm
    
    print("\n[RESPUESTA DEL TUTOR NINJA]:")
    print(response['message']['content'])
    
    print(f"\n⏱️ METRICAS DE LATENCIA:")
    print(f" 🔹 Tiempo de consulta RAG: {latencia_rag:.4f} segundos")
    print(f" 🔹 Tiempo de respuesta LLM: {latencia_llm:.4f} segundos")
    print(f" 🔸 Tiempo Total del Pipeline: {latencia_total:.4f} segundos\n")