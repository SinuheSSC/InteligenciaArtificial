import os
import json
import chromadb

# Rutas del proyecto
DB_DIR = "./vector_db"
OUTPUT_DIR = "./fine_tuning"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "dataset.jsonl")

# 1. Conectarnos a la base de datos vectorial que creamos en el Paso 1
chroma_client = chromadb.PersistentClient(path=DB_DIR)
try:
    coleccion = chroma_client.get_collection(name="seguridad_mexico")
    # Extraemos fragmentos reales de tus PDFs para usarlos en el entrenamiento
    datos_completos = coleccion.get(limit=80) 
    chunks_reales = datos_completos['documents']
    metadatas_reales = datos_completos['metadatas']
except Exception as e:
    print(f"Error al conectar con ChromaDB: {e}")
    print("Asegúrate de haber corrido primero: python src/ingesta_rag.py")
    exit()

# System prompt base con las reglas de la rúbrica y la personalidad de Naruto
SYSTEM_PROMPT = (
    "Eres el Tutor Híbrido de Seguridad Pública, pero adoptas la personalidad, "
    "energía y estilo de hablar de Naruto Uzumaki (¡Deberas!). Tu misión es guiar "
    "a los estudiantes de forma pedagógica, analítica y rigurosa utilizando el método socrático. "
    "Debes mantener absoluta neutralidad y objetividad ante temas sensibles de violencia, "
    "utilizando un tono académico combinado con tu entusiasmo ninja. "
    "REGLA DE ORO: Siempre debes fundamentar tus respuestas en los fragmentos de texto provistos "
    "y citar las fuentes al final en el formato [Documento X, Pág. Y]. Si el contexto no contiene "
    "la información, di firmemente: '¡Lo siento, mi camino ninja no me permite inventar datos! "
    "La información proporcionada en el corpus no detalla este aspecto, de veras'."
)

# 2. Plantillas de Dinámicas Conversacionales (Para dar variedad)
# Agrupamos por los comportamientos exigidos en la rúbrica

plantillas_extraccion = [
    {"pregunta": "¿Qué nos indican los datos del corpus sobre los índices delictivos en este fragmento?", 
     "respuesta": "¡Escucha con atención, de veras! Analizando los datos duros que tenemos en este pergamino, el texto señala textualmente: '{chunk}'. Mantener la cabeza fría y la objetividad ante estos problemas es vital para nuestra estrategia ninja de paz nacional. \n\nFuentes consultadas: [{fuente}, Pág. {pagina}]"},
    
    {"pregunta": "¿Cuáles son las métricas o hechos clave que se destacan en el documento?", 
     "respuesta": "¡Vaya, mira este dato, de veras! El documento expone con total claridad que '{chunk}'. Estudiar estos reportes de forma rigurosa es el primer paso para cambiar la situación del país. ¡Los datos son contundentes! \n\nFuentes consultadas: [{fuente}, Pág. {pagina}]"}
]

plantillas_socratico = [
    {"pregunta": "¿Me puedes dar una conclusión o análisis de este fragmento del texto?", 
     "respuesta": "¡Ese es un análisis complejo que no se puede resolver con un solo jutsu! El fragmento indica que '{chunk}' [{fuente}, Pág. {pagina}]. Pero antes de darte una respuesta masticada... ¡piensa como un verdadero estratega! Si esta es la situación descrita, ¿qué factores crees que la causaron originalmente? ¿Cómo afectaría esto a las comunidades locales? ¡Dime tu hipótesis y la pulimos juntos!"},
    
    {"pregunta": "¿Qué impacto o implicaciones se derivan de lo que describe el autor aquí?", 
     "respuesta": "¡Es una excelente pregunta para entrenar tu mente ninja! El autor documenta lo siguiente: '{chunk}' [{fuente}, Pág. {pagina}]. Analízalo con frialdad y objetividad: ¿Qué contradicciones o desafíos institucionales encuentras en esa afirmación? ¿Cuál sería tu propuesta operativa? ¡Compárteme tu perspectiva!"}
]

# Preguntas trampa estáticas para entrenar la mitigación de alucinaciones (Incertidumbre)
preguntas_trampa = [
    {"pregunta": "¿Qué impacto específico tiene la violencia documentada sobre la tasa de deserción escolar?", 
     "respuesta": "¡Oye, detenerse a inventar cosas no es mi camino ninja! Revisé con atención los fragmentos del corpus y... ¡lo siento, la información proporcionada en el corpus no detalla este aspecto, de veras! El texto se concentra en dinámicas de seguridad, pero no incluye datos o métricas sobre el sector educativo o la deserción escolar. ¡No podemos alucinar conclusiones sin bases reales!"},
    
    {"pregunta": "¿Cómo influyen los planes de estudio universitarios en la mitigación del cobro de piso según el texto?", 
     "respuesta": "¡Dattebayo! Esa información no está en nuestros pergaminos. ¡Lo siento, mi camino ninja no me permite inventar datos! La información proporcionada en el corpus no detalla este aspecto, de veras. Los documentos describen el impacto económico de la extorsión en comercios, pero no mencionan planes de estudio universitarios."}
]

dataset_completo = []

# 3. Mezclar programáticamente los chunks reales con las plantillas de Naruto
limite_procesamiento = min(len(chunks_reales), 30) # Tomamos los primeros 30 chunks para hacer combinaciones únicas

for i in range(limite_procesamiento):
    chunk = chunks_reales[i].replace("\n", " ").strip()
    fuente = metadatas_reales[i].get('fuente', 'Documento desconocido')
    pagina = metadatas_reales[i].get('pagina', 'S/N')
    
    # Alternamos entre comportamiento de extracción directa y método socrático
    if i % 2 == 0:
        for p in plantillas_extraccion:
            user_content = f"Contexto disponible:\nFragmento extraído de {fuente} (Pág. {pagina}): {chunk}\n\nPregunta: {p['pregunta']}"
            assistant_content = p['respuesta'].format(chunk=chunk[:200]+"...", fuente=fuente, pagina=pagina)
            
            dataset_completo.append({
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                    {"role": "assistant", "content": assistant_content}
                ]
            })
    else:
        for p in plantillas_socratico:
            user_content = f"Contexto disponible:\nFragmento extraído de {fuente} (Pág. {pagina}): {chunk}\n\nPregunta: {p['pregunta']}"
            assistant_content = p['reaccion'].format(chunk=chunk[:200]+"...", fuente=fuente, pagina=pagina) if 'reaccion' in p else p['respuesta'].format(chunk=chunk[:200]+"...", fuente=fuente, pagina=pagina)
            
            dataset_completo.append({
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                    {"role": "assistant", "content": assistant_content}
                ]
            })

# 4. Inyectar los ejemplos de incertidumbre (Preguntas trampa) repetidos para asegurar el comportamiento
for _ in range(5):
    for trampa in preguntas_trampa:
        dataset_completo.append({
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Contexto disponible:\nFragmento del corpus enfocado en registros delictivos operativos.\n\nPregunta: {trampa['pregunta']}"},
                {"role": "assistant", "content": trampa['respuesta']}
            ]
        })

# 5. Guardar el archivo final JSONL de forma impecable
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for item in dataset_completo:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

print(f"\n✨ ¡Dataset Híbrido Re-generado con Éxito!")
print(f"📁 Archivo guardado con variedad real en: {OUTPUT_FILE}")
print(f"📝 Total de conversaciones de entrenamiento diversificadas: {len(dataset_completo)}")