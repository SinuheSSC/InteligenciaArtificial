# ============================================================
# ARCHIVO 2: probar_animal.py
# Carga el modelo entrenado y predice imagenes externas
# ============================================================

import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Dense, Dropout, Conv2D, MaxPooling2D, Flatten, LeakyReLU
)
from PIL import Image
import json
import glob
import os

# ============================================================
# CONFIGURACION -- debe coincidir con entrenar_modelo.py
# ============================================================
IMG_SIZE    = (32, 32)
RUTA_MODELO = 'E:/Mi_Usuario/Documents/Proyecto2_IA_SSC/sport.h5'
RUTA_CLASES = 'E:/Mi_Usuario/Documents/Proyecto2_IA_SSC/clases.json'


# ============================================================
# RE-CONSTRUIR ARQUITECTURA (misma que CNN_SSC.py)
# Cargamos solo los pesos, evitando la deserializacion de Lambda
# ============================================================

def construir_modelo(n_classes):
    model = Sequential()

    model.add(Conv2D(32, (3, 3), padding='same', input_shape=(32, 32, 3)))
    model.add(LeakyReLU(alpha=0.1))
    model.add(MaxPooling2D((2, 2), padding='same'))
    model.add(Dropout(0.25))

    model.add(Conv2D(64, (3, 3), padding='same'))
    model.add(LeakyReLU(alpha=0.1))
    model.add(MaxPooling2D((2, 2), padding='same'))
    model.add(Dropout(0.25))

    model.add(Conv2D(128, (3, 3), padding='same'))
    model.add(LeakyReLU(alpha=0.1))
    model.add(Dropout(0.25))

    model.add(Flatten())
    model.add(Dense(128))
    model.add(LeakyReLU(alpha=0.1))
    model.add(Dropout(0.5))
    model.add(Dense(n_classes, activation='softmax'))

    return model


# ============================================================
# CARGAR MODELO Y CLASES
# ============================================================

with open(RUTA_CLASES, 'r') as f:
    deportes = json.load(f)
n_classes = len(deportes)
print("[OK] Clases cargadas:", deportes)

print("Cargando modelo...")
sport_model = construir_modelo(n_classes)
sport_model.load_weights(RUTA_MODELO)
print("[OK] Modelo cargado. Input:", sport_model.input_shape)


# ============================================================
# CARGA DE IMAGENES con manejo de transparencia
# ============================================================
def cargar_imagen_rgb(ruta, target_size=None):
    """Carga cualquier imagen (RGB, RGBA, P con transparencia) como RGB,
    componiendo las areas transparentes sobre fondo blanco."""
    img = Image.open(ruta)
    if img.mode == 'P':
        if 'transparency' in img.info:
            img = img.convert('RGBA')
        else:
            img = img.convert('RGB')
    elif img.mode in ('RGBA', 'LA', 'PA'):
        img = img.convert('RGBA')
    else:
        img = img.convert('RGB')
    if target_size:
        img = img.resize(target_size, Image.BILINEAR)
    arr = np.array(img).astype('float32')
    if arr.ndim == 3 and arr.shape[-1] == 4:
        rgb = arr[..., :3]
        alpha = arr[..., 3:] / 255.0
        arr = rgb * alpha + 255.0 * (1.0 - alpha)
        arr = np.round(arr).clip(0, 255).astype('float32')
    return arr


def load_img_rgb(ruta, target_size=IMG_SIZE):
    """Reemplazo de keras load_img que maneja transparencia correctamente."""
    arr = cargar_imagen_rgb(ruta, target_size)
    return arr / 255.0


# ============================================================
# FUNCIONES DE PREDICCION
# ============================================================
def predecir_animal(ruta_imagen, modelo, clases, img_size=IMG_SIZE):
    imagen = load_img_rgb(ruta_imagen, target_size=img_size)
    imagen = np.expand_dims(imagen, axis=0)
    probs  = modelo.predict(imagen, verbose=0)[0]
    idx    = np.argmax(probs)
    return clases[idx], probs[idx] * 100, probs


def mostrar_prediccion(ruta_imagen):
    nombre, confianza, probs = predecir_animal(ruta_imagen, sport_model, deportes)
    imagen = cargar_imagen_rgb(ruta_imagen) / 255.0

    fig, axes = plt.subplots(1, 2, figsize=(13, 4))
    color = 'green' if confianza >= 65 else 'darkorange'
    axes[0].imshow(imagen)
    axes[0].set_title(f"Prediccion: {nombre.upper()}\nConfianza: {confianza:.1f}%",
                      fontsize=14, fontweight='bold', color=color)
    axes[0].axis('off')

    colores = ['#2ecc71' if c == nombre else '#3498db' for c in deportes]
    barras  = axes[1].barh(deportes, probs * 100, color=colores,
                           edgecolor='white', height=0.55)
    for barra, prob in zip(barras, probs):
        axes[1].text(barra.get_width() + 0.8,
                     barra.get_y() + barra.get_height() / 2,
                     f'{prob*100:.1f}%', va='center', fontsize=10)
    axes[1].set_xlabel('Probabilidad (%)')
    axes[1].set_title('Distribucion de Probabilidades')
    axes[1].set_xlim(0, 120)
    axes[1].spines[['top', 'right']].set_visible(False)
    plt.suptitle(f'Archivo: {ruta_imagen}', fontsize=9, color='gray')
    plt.tight_layout()
    salida = f'prediccion_{os.path.splitext(os.path.basename(ruta_imagen))[0]}.png'
    plt.savefig(salida, dpi=150)
    plt.close()
    print(f"[OK] Prediccion guardada en: {salida}")


def predecir_consola(ruta_imagen):
    nombre, confianza, probs = predecir_animal(ruta_imagen, sport_model, deportes)
    print("=" * 45)
    print(f"  Imagen     : {ruta_imagen}")
    print(f"  Prediccion : {nombre.upper()}")
    print(f"  Confianza  : {confianza:.2f}%")
    print("-" * 45)
    for clase, prob in zip(deportes, probs):
        barra    = '#' * int(prob * 25)
        marcador = ' <--' if clase == nombre else ''
        print(f"  {clase:<12} {prob*100:6.2f}%  {barra}{marcador}")
    print("=" * 45)


# ============================================================
# GRAD-CAM -- diagnostico de que mira el modelo
# ============================================================
def encontrar_ultima_conv(modelo):
    for capa in reversed(modelo.layers):
        if isinstance(capa, tf.keras.layers.Conv2D):
            return capa.name
    return None


def gradcam(modelo, img_array, layer_name):
    grad_model = tf.keras.models.Model(
        inputs=modelo.inputs,
        outputs=[modelo.get_layer(layer_name).output, modelo.output]
    )
    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_array)
        class_idx = tf.argmax(predictions[0])
        loss = predictions[:, class_idx]

    grads = tape.gradient(loss, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(1, 2))
    conv_outputs = conv_outputs[0]
    heatmap = tf.reduce_sum(tf.multiply(pooled_grads, conv_outputs), axis=-1)
    heatmap = tf.maximum(heatmap, 0)
    heatmap /= tf.reduce_max(heatmap) + tf.keras.backend.epsilon()
    return heatmap.numpy()


def mostrar_gradcam(ruta_imagen, modelo, clases, img_size=IMG_SIZE):
    img_array = load_img_rgb(ruta_imagen, target_size=img_size)
    img_batch = np.expand_dims(img_array, axis=0)

    nombre, confianza, probs = predecir_animal(ruta_imagen, modelo, clases)
    layer_name = encontrar_ultima_conv(modelo)
    if layer_name is None:
        print("No se encontro capa Conv2D")
        return

    heatmap = gradcam(modelo, img_batch, layer_name)
    heatmap = np.maximum(heatmap, 0)
    heatmap = np.clip(heatmap, 0, 1)

    import cv2
    heatmap_resized = cv2.resize(heatmap, img_size)
    heatmap_colored = cv2.applyColorMap(
        np.uint8(255 * heatmap_resized), cv2.COLORMAP_JET
    )
    heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)

    overlay = (0.5 * img_array + 0.5 * heatmap_colored.astype('float32') / 255.0)
    overlay = np.clip(overlay, 0, 1)

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    color = 'green' if confianza >= 65 else 'darkorange'
    axes[0].imshow(img_array)
    axes[0].set_title(f"Original: {nombre.upper()} ({confianza:.1f}%)",
                      fontsize=13, fontweight='bold', color=color)
    axes[0].axis('off')

    axes[1].imshow(overlay)
    axes[1].set_title("Grad-CAM (ultima conv)", fontsize=13, fontweight='bold')
    axes[1].axis('off')

    colores = ['#2ecc71' if c == nombre else '#3498db' for c in clases]
    axes[2].barh(clases, probs * 100, color=colores, edgecolor='white', height=0.55)
    for barra, prob in zip(axes[2].patches, probs):
        axes[2].text(barra.get_width() + 0.8,
                     barra.get_y() + barra.get_height() / 2,
                     f'{prob*100:.1f}%', va='center', fontsize=10)
    axes[2].set_xlabel('Probabilidad (%)')
    axes[2].set_title('Distribucion')
    axes[2].set_xlim(0, 120)
    axes[2].spines[['top', 'right']].set_visible(False)

    plt.suptitle(f'Archivo: {ruta_imagen}', fontsize=9, color='gray')
    plt.tight_layout()
    salida = f'gradcam_{os.path.splitext(os.path.basename(ruta_imagen))[0]}.png'
    plt.savefig(salida, dpi=150)
    plt.close()
    print(f"[OK] GradCAM guardada en: {salida}")


# ============================================================
# ► PRUEBA TODAS LAS IMAGENES DE LA CARPETA test/
# ============================================================
RUTA_TEST = 'test/'
extensiones = ('*.png', '*.jpg', '*.jpeg', '*.bmp', '*.tiff')

imagenes = []
for ext in extensiones:
    imagenes.extend(glob.glob(os.path.join(RUTA_TEST, ext)))

if not imagenes:
    print(f"[!] No se encontraron imagenes en '{RUTA_TEST}'")
else:
    print(f"[OK] Se encontraron {len(imagenes)} imagen(es) en '{RUTA_TEST}':\n")
    for ruta in sorted(imagenes):
        mostrar_prediccion(ruta)
        #mostrar_gradcam(ruta, sport_model, deportes)
        #predecir_consola(ruta)
