import os
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay

import tensorflow as tf
from tensorflow.keras import layers, models, optimizers, callbacks
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# =====================================================================
# 0. CONFIGURACIÓN DEL ENTORNO DE DESARROLLO
# =====================================================================
DIRECTORIO_DATASET = Path("./dataset")
RUTA_SALIDA_MODELO = Path("./modelo_animales_transfer.keras")

DIMENSION_IMAGEN = (224, 224)
FORMA_ENTRADA = (224, 224, 3)
TAMAÑO_LOTE = 16

# Parámetros del optimizador y ciclos de entrenamiento
EPOCAS_CABEZA = 15
EPOCAS_FINE_TUNING = 25
LEARNING_RATE_INICIAL = 1e-3
LEARNING_RATE_FINO = 1e-5

FORMATOS_VALIDOS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff"}

# =====================================================================
# 1. CARGA PIPELINE DE DATOS EN MEMORIA
# =====================================================================
tensores_imagenes = []
etiquetas_clases = []
nombres_categorias = []

print(f"Iniciando escaneo de directorios en: {DIRECTORIO_DATASET}\n")

# Escaneo estructurado del árbol de carpetas
directorios_validos = sorted([d for d in DIRECTORIO_DATASET.iterdir() if d.is_dir()])

for idx, ruta_carpeta in enumerate(directorios_validos):
    nombres_categorias.append(ruta_carpeta.name)
    contador_local = 0
    
    for archivo in ruta_carpeta.iterdir():
        if archivo.suffix.lower() not in FORMATOS_VALIDOS:
            continue
            
        # Pipeline interno de procesamiento de imágenes con TF
        contenido_binario = tf.io.read_file(str(archivo))
        imagen_decodificada = tf.image.decode_jpeg(contenido_binario, channels=3)
        imagen_escalada = tf.image.resize(imagen_decodificada, DIMENSION_IMAGEN)
        
        tensores_imagenes.append(imagen_escalada.numpy().astype(np.uint8))
        etiquetas_clases.append(idx)
        contador_local += 1
        
    print(f"  [{idx}] {ruta_carpeta.name}: {contador_local} muestras indexadas.")

total_clases = len(nombres_categorias)
print(f"\n✅ Carga completada: {len(tensores_imagenes)} imágenes | {total_clases} categorías.")

# =====================================================================
# 2. PROCESAMIENTO Y DIVISIÓN ESTRATIFICADA
# =====================================================================
# Escalamiento al rango simétrico [-1, 1] requerido por MobileNetV2
X_datos = preprocess_input(np.array(tensores_imagenes, dtype=np.float32))
y_datos = np.array(etiquetas_clases)

# Primer split: Aislamiento del conjunto de pruebas final (15%)
X_entrena, X_test, y_entrena, y_test = train_test_split(
    X_datos, y_datos, test_size=0.15, stratify=y_datos, random_state=42
)

# Segundo split: Separación del conjunto de entrenamiento y validación cruzada
X_entrena, X_val, y_entrena, y_val = train_test_split(
    X_entrena, y_entrena, test_size=0.15, stratify=y_entrena, random_state=42
)

print(f"Distribución Final -> Train: {X_entrena.shape[0]} | Val: {X_val.shape[0]} | Test: {X_test.shape[0]}")

# Conversión de las matrices categóricas a codificación One-Hot
y_entrena_oh = to_categorical(y_entrena, total_clases)
y_val_oh = to_categorical(y_val, total_clases)
y_test_oh = to_categorical(y_test, total_clases)

# =====================================================================
# 3. CONFIGURACIÓN DEL MOTOR DE DATA AUGMENTATION
# =====================================================================
generador_imagenes = ImageDataGenerator(
    rotation_range=30,
    width_shift_range=0.15,
    height_shift_range=0.15,
    zoom_range=0.2,
    shear_range=10,
    brightness_range=[0.7, 1.3],
    horizontal_flip=True,
    vertical_flip=False,
    fill_mode='reflect'
)
generador_imagenes.fit(X_entrena)

# =====================================================================
# 4. CONSTRUCCIÓN DE LA ARQUITECTURA DE RED NEURONAL
# =====================================================================
# Extractor base preentrenado en ImageNet (excluyendo la cabeza densa original)
modelo_base_convolucional = MobileNetV2(
    input_shape=FORMA_ENTRADA,
    include_top=False,
    weights='imagenet'
)

# --- FASE 1: Congelamiento estructural de la base ---
modelo_base_convolucional.trainable = False

entradas_red = tf.keras.Input(shape=FORMA_ENTRADA)
bloque_features = modelo_base_convolucional(entradas_red, training=False)
reduccion_espacial = layers.GlobalAveragePooling2D()(bloque_features)
capa_densa_intermedia = layers.Dense(128, activation='relu')(reduccion_espacial)
regularizacion_dropout = layers.Dropout(0.4)(capa_densa_intermedia)
salidas_probabilisticas = layers.Dense(total_clases, activation='softmax')(regularizacion_dropout)

red_neuronal_transfer = models.Model(inputs=entradas_red, outputs=salidas_probabilisticas)
red_neuronal_transfer.summary()

# Monitores de estabilidad para la Fase 1
politica_parada_fase1 = [
    callbacks.EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True, verbose=1),
    callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, verbose=1)
]

print("\n🚀 FASE 1: Optimizando la cabeza de clasificación adaptativa...\n")
red_neuronal_transfer.compile(
    optimizer=optimizers.Adam(learning_rate=LEARNING_RATE_INICIAL),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

historial_fase1 = red_neuronal_transfer.fit(
    generador_imagenes.flow(X_entrena, y_entrena_oh, batch_size=TAMAÑO_LOTE),
    epochs=EPOCAS_CABEZA,
    validation_data=(X_val, y_val_oh),
    callbacks=politica_parada_fase1,
    verbose=1
)

# --- FASE 2: Descongelamiento y Ajuste Fino (Fine-Tuning) ---
print("\n🟠 FASE 2: Liberando bloques superiores para Fine-Tuning...\n")
modelo_base_convolucional.trainable = True

# Conservar congeladas todas las capas excepto los últimos 30 bloques convolucionales
for capa in modelo_base_convolucional.layers[:-30]:
    capa.trainable = False

# Recompilación obligatoria con tasa de aprendizaje atenuada
red_neuronal_transfer.compile(
    optimizer=optimizers.Adam(learning_rate=LEARNING_RATE_FINO),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

politica_parada_fase2 = [
    callbacks.EarlyStopping(monitor='val_loss', patience=8, restore_best_weights=True, verbose=1),
    callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=4, verbose=1)
]

historial_fase2 = red_neuronal_transfer.fit(
    generador_imagenes.flow(X_entrena, y_entrena_oh, batch_size=TAMAÑO_LOTE),
    epochs=EPOCAS_FINE_TUNING,
    validation_data=(X_val, y_val_oh),
    callbacks=politica_parada_fase2,
    verbose=1
)

# Exportación del modelo optimizado a disco
red_neuronal_transfer.save(str(RUTA_SALIDA_MODELO))
print(f"\n💾 Modelo binario consolidado en: {RUTA_SALIDA_MODELO}")

# =====================================================================
# 5. DIAGNÓSTICO METROLÓGICO DEL CLASIFICADOR
# =====================================================================
costo_test, precision_test = red_neuronal_transfer.evaluate(X_test, y_test_oh, verbose=0)
print(f"\n🎯 Rendimiento en Test (Accuracy) : {precision_test:.4f}")
print(f"📉 Pérdida en Test (Loss)        : {costo_test:.4f}")

distribuciones_predichas = red_neuronal_transfer.predict(X_test)
clases_predichas = np.argmax(distribuciones_predichas, axis=1)

print("\n=== REPORTE FORMAL DE CLASIFICACIÓN ===")
print(classification_report(y_test, clases_predichas, target_names=nombres_categorias))

# =====================================================================
# 6. ENTORNO GRÁFICO DE CONVERGENCIA
# =====================================================================
def consolidar_metricas(h1, h2, clave_metrica):
    return h1.history[clave_metrica] + h2.history[clave_metrica]

eje_temporal_epochs = range(len(consolidar_metricas(historial_fase1, historial_fase2, 'accuracy')))
frontera_fases = len(historial_fase1.history['accuracy'])

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Mapeo de curvas de precisión y costo
for ax, metrica, titulo in zip(axes, ['accuracy', 'loss'], ['Precisión (Accuracy)', 'Costo (Loss)']):
    valores_entrenamiento = consolidar_metricas(historial_fase1, historial_fase2, metrica)
    valores_validacion = consolidar_metricas(historial_fase1, historial_fase2, f'val_{metrica}')
    
    ax.plot(eje_temporal_epochs, valores_entrenamiento, label='Muestreo Entrenamiento', color='teal')
    ax.plot(eje_temporal_epochs, valores_validacion, label='Muestreo Validación', color='darkorange')
    ax.axvline(x=frontera_fases - 1, color='crimson', linestyle='--', label='Inflexión Fine-Tuning')
    ax.set_title(f'Evolución de {titulo}')
    ax.set_xlabel('Ciclos (Epochs)')
    ax.set_ylabel(titulo.split()[0])
    ax.legend()

plt.tight_layout()
plt.savefig("./curvas_entrenamiento.png", dpi=150)
plt.show()

# Construcción de la matriz de confusión
matriz_confusion_datos = confusion_matrix(y_test, clases_predichas)
grafico_cm = ConfusionMatrixDisplay(confusion_matrix=matriz_confusion_datos, display_labels=nombres_categorias)
grafico_cm.plot(xticks_rotation=45, cmap='GnBu')
plt.title("Matriz de Confusión Estructural")
plt.tight_layout()
plt.savefig("./confusion_matrix.png", dpi=150)
plt.show()

# =====================================================================
# 7. EXTRACCIÓN DE RESULTADOS Y VERIFICACIÓN VISUAL
# =====================================================================
# Desnormalización inversa del rango [-1, 1] al espacio entero de visualización RGB [0, 1]
X_test_renderizable = np.clip((X_test + 1.0) / 2.0, 0.0, 1.0)

def desplegar_muestras_predichas(indices_muestras, titulo_ventana):
    if len(indices_muestras) == 0:
        print(f"(No se registran ocurrencias para la condición: {titulo_ventana})")
        return
        
    plt.figure(figsize=(10, 10))
    plt.suptitle(titulo_ventana, fontsize=12, weight='bold')
    
    for posicion, idx in enumerate(indices_muestras[:9]):
        plt.subplot(3, 3, posicion + 1)
        plt.imshow(X_test_renderizable[idx])
        
        id_predicho = nombres_categorias[clases_predichas[idx]]
        id_esperado = nombres_categorias[y_test[idx]]
        
        color_etiqueta = 'darkgreen' if id_predicho == id_esperado else 'darkred'
        plt.title(f"Pred: {id_predicho}\nReal: {id_esperado}", color=color_etiqueta, fontsize=9)
        plt.axis('off')
        
    plt.tight_layout()
    plt.show()

muestras_correctas = np.where(clases_predichas == y_test)[0]
muestras_incorrectas = np.where(clases_predichas != y_test)[0]

print(f"\nAuditoría Visual -> Aciertos detectados: {len(muestras_correctas)}")
print(f"Auditoría Visual -> Fallos detectados: {len(muestras_incorrectas)}")

desplegar_muestras_predichas(muestras_correctas, "Muestras: Predicciones Correctas")
desplegar_muestras_predichas(muestras_incorrectas, "Muestras: Predicciones Erróneas")