import os
import fitz  # PyMuPDF: Extractor de PDF ultra rápido
import torch
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb

# ==========================================
# DIAGNÓSTICO DE HARDWARE
# ==========================================
# Verificamos si PyTorch tiene acceso a los núcleos CUDA de tu Quadro M2000M
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"\n🚀 CONFIGURACIÓN: Usando {device.upper()} para aceleración por hardware.")

# Rutas del proyecto
DATASET_DIR = "./dataset"
DB_DIR = "./vector_db"

# ==========================================
# 1. CARGA DEL MODELO DE EMBEDDINGS
# ==========================================
# Usamos 'all-MiniLM-L6-v2'. Es un modelo ligero pero sumamente preciso,
# ideal para los 4GB de VRAM de tu tarjeta gráfica.
print("🧠 Cargando modelo de embeddings en la GPU...")
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device=device)

# ==========================================
# 2. EXTRACCIÓN DE TEXTO (Lectura de PDFs)
# ==========================================
def extraer_texto_pdfs(carpeta):
    documentos = []
    # Validar que la carpeta exista
    if not os.path.exists(carpeta):
        raise FileNotFoundError(f"No se encontró la carpeta: {carpeta}")
        
    for archivo in os.listdir(carpeta):
        if archivo.endswith(".pdf"):
            ruta_completa = os.path.join(carpeta, archivo)
            print(f"📄 Leyendo: {archivo}")
            
            # Abrir el PDF de forma eficiente
            doc = fitz.open(ruta_completa)
            for num_pag, pagina in enumerate(doc):
                texto = pagina.get_text()
                # Solo guardamos páginas que tengan texto real (filtramos imágenes o vacías)
                if texto.strip(): 
                    documentos.append({
                        "texto": texto,
                        "metadata": {"fuente": archivo, "pagina": num_pag + 1}
                    })
    return documentos

print("\n📥 Iniciando extracción de textos...")
textos_puros = extraer_texto_pdfs(DATASET_DIR)
print(f"✅ Extracción completada. Total de páginas procesadas: {len(textos_puros)}")

# ==========================================
# 3. SEGMENTACIÓN DE TEXTO (Chunking)
# ==========================================
# Dividimos el texto en trozos de 800 caracteres. Un traslape (overlap) de 150
# caracteres garantiza que los conceptos que queden a la mitad de un corte no pierdan sentido.
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,       # Bloques más grandes para capturar párrafos enteros
    chunk_overlap=200,     # Traslape de 200 caracteres para asegurar la continuidad histórica
    separators=["\n\n", "\n", " ", ""]
)

chunks_finales = []
metadatas_finales = []
ids_finales = []

contador = 0
for doc in textos_puros:
    fragmentos = text_splitter.split_text(doc["texto"])
    for f in fragmentos:
        chunks_finales.append(f)
        metadatas_finales.append(doc["metadata"])
        ids_finales.append(f"id_{contador}")
        contador += 1

print(f"✂️ Texto segmentado estratégicamente en {len(chunks_finales)} fragmentos.")

# ==========================================
# 4. VECTORIZACIÓN E INDEXACIÓN EN CHROMADB
# ==========================================
print("\n💾 Inicializando Base de Datos Vectorial (ChromaDB)...")
chroma_client = chromadb.PersistentClient(path=DB_DIR)

# Si la colección ya existía de pruebas anteriores, la borramos para iniciar limpios
try:
    chroma_client.delete_collection(name="seguridad_mexico")
except:
    pass

coleccion = chroma_client.create_collection(name="seguridad_mexico")

print("⚡ Generando embeddings en tu Quadro M2000M y guardando en base de datos...")

# Procesamos por lotes (Batching) para optimizar el flujo de datos hacia la GPU
BATCH_SIZE = 64
for i in range(0, len(chunks_finales), BATCH_SIZE):
    batch_chunks = chunks_finales[i:i+BATCH_SIZE]
    batch_metadatas = metadatas_finales[i:i+BATCH_SIZE]
    batch_ids = ids_finales[i:i+BATCH_SIZE]
    
    # La GPU calcula las coordenadas vectoriales de este lote de texto
    vectores = embedding_model.encode(batch_chunks, show_progress_bar=False).tolist()
    
    # Insertamos los datos en la BD indexada
    coleccion.add(
        embeddings=vectores,
        documents=batch_chunks,
        metadatas=batch_metadatas,
        ids=batch_ids
    )

print("\n🎉 ¡Paso 1 Completado con éxito! Tu base de datos vectorial está lista en './vector_db'.")