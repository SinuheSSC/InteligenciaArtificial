import os
import re
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, LeakyReLU
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# ==========================================
# 1. CONFIGURACIÓN DE RUTAS Y CARGA DE DATOS
# ==========================================

# Ruta local del dataset ajustada al entorno de desarrollo
RUTA_DATASET = r"C:\Users\Sinuhe\Proyectos\IA\dataset"

lista_imagenes = []
rutas_directorios = []
conteo_por_subdir = []
ultimo_directorio = ""
contador_temporal = 0

print(f"Iniciando escaneo de imágenes en: {RUTA_DATASET}")

for raiz, subdirs, archivos in os.walk(RUTA_DATASET):
    for archivo in archivos:
        # Validación de extensiones válidas de imágenes mediante Regex
        if re.search(r"\.(jpg|jpeg|png|bmp|tiff)$", archivo, re.IGNORECASE):
            contador_temporal += 1
            ruta_completa = os.path.join(raiz, archivo)
            
            # Lectura de la matriz de la imagen
            matriz_imagen = plt.imread(ruta_completa)
            
            # Conservar únicamente imágenes con canales de color válidos (RGB)
            if len(matriz_imagen.shape) == 3:
                lista_imagenes.append(matriz_imagen)
                
            if ultimo_directorio != raiz:
                ultimo_directorio = raiz
                rutas_directorios.append(raiz)
                conteo_por_subdir.append(contador_temporal)
                contador_temporal = 0

# Ajuste y sincronización de los contadores de directorios
conteo_por_subdir.append(contador_temporal)
conteo_por_subdir = conteo_por_subdir[1:]
if len(conteo_por_subdir) > 0:
    conteo_por_subdir[0] += 1

print(f"Total de categorías encontradas: {len(rutas_directorios)}")
print(f"Distribución de imágenes por carpeta: {conteo_por_subdir}")
print(f"Volumen total de imágenes procesadas: {sum(conteo_por_subdir)}")

# ==========================================
# 2. PROCESAMIENTO DE ETIQUETAS Y CLASES
# ==========================================

etiquetas = []
id_clase = 0
for cantidad in conteo_por_subdir:
    for _ in range(cantidad):
        etiquetas.append(id_clase)
    id_clase += 1
print(f"Total de etiquetas numéricas asignadas: {len(etiquetas)}")

# Extracción de nombres de clases a partir del nombre del directorio
clases_deportes = []
for idx, dir_path in enumerate(rutas_directorios):
    nombre_categoria = dir_path.split(os.sep)[-1]
    print(f"Categoría [{idx}]: {nombre_categoria}")
    clases_deportes.append(nombre_categoria)

# Conversión a estructuras nativas de NumPy
X_datos = np.array(lista_imagenes, dtype=np.uint8)
y_etiquetas = np.array(etiquetas)

valores_unicos = np.unique(y_etiquetas)
num_clases = len(valores_unicos)
print(f"Número total de salidas de la red: {num_clases}")
print(f"Mapeo de clases del sistema: {valores_unicos}")

# Split inicial: Separación del conjunto global en Entrenamiento y Prueba
x_entrena, x_test, y_entrena, y_test = train_test_split(X_datos, y_etiquetas, test_size=0.2, random_state=42)
print(f"Dimensiones de entrenamiento: X={x_entrena.shape}, Y={y_entrena.shape}")
print(f"Dimensiones de test: X={x_test.shape}, Y={y_test.shape}")

# Visualización inicial de muestras del Dataset
plt.figure(figsize=[10, 5])
plt.subplot(121)
plt.imshow(x_entrena[0])
plt.title(f"Muestra Entrena - Clase: {y_entrena[0]}")

plt.subplot(122)
plt.imshow(x_test[0])
plt.title(f"Muestra Test - Clase: {y_test[0]}")
plt.show()

# Normalización de tensores en el rango [0, 1]
x_entrena = x_entrena.astype("float32") / 255.0
x_test = x_test.astype("float32") / 255.0

# Conversión de vectores de enteros a codificación One-Hot
y_entrena_one_hot = to_categorical(y_entrena, num_classes=num_clases)
y_test_one_hot = to_categorical(y_test, num_classes=num_clases)

# Validación cruzada: Creación del set de validación interna
x_entrena, x_val, y_entrena_oh, y_val_oh = train_test_split(
    x_entrena, y_entrena_one_hot, test_size=0.2, random_state=48
)
print(f"Set final - Entrenamiento: {x_entrena.shape}, Validación: {x_val.shape}")

# ==========================================
# 3. ARQUITECTURA DE LA RED NEURONAL (CNN)
# ==========================================

LR_INICIAL = 1e-4
CICLOS_EPOCHS = 40
TAMAÑO_LOTE = 128

# Construcción secuencial del modelo convolucional
modelo_cnn = Sequential([
    # Primera capa Convolucional + Extracción de características primarias
    Conv2D(64, kernel_size=(5, 5), activation="linear", padding="same", input_shape=(28, 21, 3)),
    LeakyReLU(alpha=0.1),
    MaxPooling2D((2, 2), padding="same"),
    Dropout(0.5),
    
    # Segunda capa Convolucional + Reducción de dimensionalidad
    Conv2D(64, kernel_size=(3, 3), padding="same"),
    LeakyReLU(alpha=0.1),
    MaxPooling2D((2, 2), padding="same"),
    
    # Aplanado de tensores y capas densas de clasificación
    Flatten(),
    Dense(64, activation="linear"),
    LeakyReLU(alpha=0.1),
    Dropout(0.5),
    Dense(num_clases, activation="softmax")
])

modelo_cnn.summary()

# Configuración del proceso de optimización del modelo
modelo_cnn.compile(
    loss=keras.losses.categorical_crossentropy,
    optimizer=tf.keras.optimizers.Adam(learning_rate=LR_INICIAL),
    metrics=["accuracy"]
)

# Ejecución del entrenamiento de la red
historial_entrenamiento = modelo_cnn.fit(
    x_entrena, y_entrena_oh,
    batch_size=TAMAÑO_LOTE,
    epochs=CICLOS_EPOCHS,
    verbose=1,
    validation_data=(x_val, y_val_oh)
)

# Almacenamiento del modelo en disco
ruta_guardado = r"C:\Users\Sinuhe\Proyectos\IA\modelos\clasificador_deportes.keras"
os.makedirs(os.path.dirname(ruta_guardado), exist_ok=True)
modelo_cnn.save(ruta_guardado)
print(f"Modelo exportado exitosamente en: {ruta_guardado}")

# ==========================================
# 4. EVALUACIÓN Y DIAGNÓSTICO METROLÓGICO
# ==========================================

evaluacion_test = modelo_cnn.evaluate(x_test, y_test_one_hot, verbose=1)
print(f"\nPérdida en el conjunto de prueba (Test Loss): {evaluacion_test[0]:.4f}")
print(f"Precisión en el conjunto de prueba (Test Accuracy): {evaluacion_test[1]:.4f}")

# Gráficas de rendimiento del entrenamiento
acc = historial_entrenamiento.history["accuracy"]
val_acc = historial_entrenamiento.history["val_accuracy"]
loss = historial_entrenamiento.history["loss"]
val_loss = historial_entrenamiento.history["val_loss"]
vector_epochs = range(len(acc))

plt.figure(figsize=(12, 5))

# Curvas de precisión
plt.subplot(121)
plt.plot(vector_epochs, acc, "bo-", label="Precisión Entrenamiento")
plt.plot(vector_epochs, val_acc, "b-", label="Precisión Validación")
plt.title("Evolución de la Precisión (Accuracy)")
plt.xlabel("Epochs")
plt.ylabel("Accuracy")
plt.legend()

# Curvas de función de costo
plt.subplot(122)
plt.plot(vector_epochs, loss, "ro-", label="Pérdida Entrenamiento")
plt.plot(vector_epochs, val_loss, "r-", label="Pérdida Validación")
plt.title("Evolución de la Pérdida (Loss)")
plt.xlabel("Epochs")
plt.ylabel("Loss")
plt.legend()
plt.show()

# Predicciones e inspección visual de resultados
probabilidades_predichas = modelo_cnn.predict(x_test)
clases_predichas = np.argmax(probabilidades_predichas, axis=1)

# Filtrado de índices correctos e incorrectos
indices_correctos = np.where(clases_predichas == y_test)[0]
indices_incorrectos = np.where(clases_predichas != y_test)[0]

# Despliegue de predicciones acertadas
print(f"\nVisualizando clasificaciones correctas (Total: {len(indices_correctos)})...")
plt.figure(figsize=(9, 9))
for idx, muestra in enumerate(indices_correctos[:9]):
    plt.subplot(3, 3, idx + 1)
    plt.imshow(x_test[muestra])
    etiqueta_pred = clases_deportes[clases_predichas[muestra]]
    etiqueta_real = clases_deportes[y_test[muestra]]
    plt.title(f"Pred: {etiqueta_pred}\nReal: {etiqueta_real}", fontsize=9)
    plt.axis("off")
plt.tight_layout()
plt.show()

# Despliegue de predicciones erróneas
print(f"Visualizando clasificaciones incorrectas (Total: {len(indices_incorrectos)})...")
plt.figure(figsize=(9, 9))
for idx, muestra in enumerate(indices_incorrectos[:9]):
    plt.subplot(3, 3, idx + 1)
    plt.imshow(x_test[muestra])
    etiqueta_pred = clases_deportes[clases_predichas[muestra]]
    etiqueta_real = clases_deportes[y_test[muestra]]
    plt.title(f"Pred: {etiqueta_pred}\nReal: {etiqueta_real}", fontsize=9, color="red")
    plt.axis("off")
plt.tight_layout()
plt.show()

# Reporte formal de métricas estadísticas de clasificación
nombres_clases_reporte = [f"Clase {i}" for i in range(num_clases)]
print("\n=== REPORTE FORMAL DE CLASIFICACIÓN ===")
print(classification_report(y_test, clases_predichas, target_names=nombres_clases_reporte))