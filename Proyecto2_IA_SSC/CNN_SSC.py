# ============================================================
# ARCHIVO: entrenar_modelo.py
# Usa ImageDataGenerator para no saturar la RAM
# ============================================================

import os
import sys

# Forzar de manera nativa a Windows a mapear las DLLs de Conda
conda_bin_path = r"C:\Users\DELL\anaconda3\envs\cnn_gpu\Library\bin"
if os.path.exists(conda_bin_path):
    os.environ['PATH'] = conda_bin_path + os.path.pathsep + os.environ['PATH']
    if hasattr(os, 'add_dll_directory'):
        os.add_dll_directory(conda_bin_path)

print("Ruta binaria forzada en:", conda_bin_path)

import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Dense, Dropout, Conv2D, MaxPooling2D, Flatten, LeakyReLU
)
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.utils import Sequence
from sklearn.utils.class_weight import compute_class_weight

# ============================================================
# CONFIGURACIÓN GLOBAL
# ============================================================
IMG_ALTO     = 32
IMG_ANCHO    = 32
IMG_SIZE     = (IMG_ALTO, IMG_ANCHO)
INIT_LR      = 5e-4
EPOCHS       = 40
BATCH_SIZE   = 32
RUTA_DATASET = 'E:/Mi_Usuario/Documents/Proyecto2_IA_SSC/dataset'
RUTA_MODELO  = 'E:/Mi_Usuario/Documents/Proyecto2_IA_SSC/sport.h5'
RUTA_CLASES  = 'E:/Mi_Usuario/Documents/Proyecto2_IA_SSC/clases.json'

# ============================================================
# RGBA→RGB — wrapper sobre generador que compone transparencia
# sobre fondo blanco, aprovechando imágenes sin fondo
# ============================================================
class RGBAtoRGBGenerator(Sequence):
    def __init__(self, generator, bg_color=1.0):
        self.generator = generator
        self.bg_color = bg_color
        self.batch_size = generator.batch_size
        self.samples = generator.samples
        self.classes = generator.classes
        self.class_indices = generator.class_indices

    def __len__(self):
        return len(self.generator)

    def __getitem__(self, idx):
        x, y = self.generator[idx]
        if x.shape[-1] == 4:
            rgb = x[..., :3]
            alpha = x[..., 3:]
            # Componer sobre fondo blanco: resultado = rgb * alpha + bg * (1 - alpha)
            x = rgb * alpha + self.bg_color * (1.0 - alpha)
        return x, y

    def on_epoch_end(self):
        self.generator.on_epoch_end()


# ============================================================
# GENERADORES — leen imágenes desde disco en lotes (sin saturar RAM)
# ============================================================
# 80% entrenamiento, 20% validación
train_datagen = ImageDataGenerator(
    rescale=1.0 / 255.0,
    validation_split=0.2,
    rotation_range=15,
    width_shift_range=0.1,
    height_shift_range=0.1,
    horizontal_flip=True,
    fill_mode='nearest'
)

valid_datagen = ImageDataGenerator(rescale=1.0 / 255.0, validation_split=0.2)

train_generator_raw = train_datagen.flow_from_directory(
    RUTA_DATASET,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training',
    shuffle=True,
    interpolation='bilinear',
    color_mode='rgba'
)

valid_generator_raw = valid_datagen.flow_from_directory(
    RUTA_DATASET,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation',
    shuffle=False,
    interpolation='bilinear',
    color_mode='rgba'
)

# Convertir RGBA → RGB componiendo transparencia sobre fondo blanco
train_generator = RGBAtoRGBGenerator(train_generator_raw)
valid_generator = RGBAtoRGBGenerator(valid_generator_raw)

# ============================================================
# GUARDAR CLASES EN JSON (en el orden que detectó el generador)
# ============================================================
# flow_from_directory ordena las carpetas alfabéticamente
deportes  = list(train_generator_raw.class_indices.keys())
nClasses  = len(deportes)

with open(RUTA_CLASES, 'w') as f:
    json.dump(deportes, f)

print("✅ Clases detectadas:", deportes)
print("✅ Total clases     :", nClasses)
print("✅ Imágenes train   :", train_generator_raw.samples)
print("✅ Imágenes valid   :", valid_generator.samples)

# ============================================================
# CLASS WEIGHTS — para balancear clases desbalanceadas
# ============================================================
clases_ids = np.unique(train_generator_raw.classes)
pesos = compute_class_weight('balanced', classes=clases_ids, y=train_generator_raw.classes)
class_weight_dict = dict(enumerate(pesos))
for i, clase in enumerate(deportes):
    print(f"   Peso {clase}: {pesos[i]:.3f}")


# ============================================================
# ARQUITECTURA CNN — 3 bloques Conv, balance capacidad/velocidad
# ============================================================
sport_model = Sequential()

sport_model.add(Conv2D(32, (3, 3), padding='same', input_shape=(IMG_ALTO, IMG_ANCHO, 3)))
sport_model.add(LeakyReLU(alpha=0.1))
sport_model.add(MaxPooling2D((2, 2), padding='same'))
sport_model.add(Dropout(0.25))

sport_model.add(Conv2D(64, (3, 3), padding='same'))
sport_model.add(LeakyReLU(alpha=0.1))
sport_model.add(MaxPooling2D((2, 2), padding='same'))
sport_model.add(Dropout(0.25))

sport_model.add(Conv2D(128, (3, 3), padding='same'))
sport_model.add(LeakyReLU(alpha=0.1))
sport_model.add(Dropout(0.25))

sport_model.add(Flatten())
sport_model.add(Dense(128))
sport_model.add(LeakyReLU(alpha=0.1))
sport_model.add(Dropout(0.5))
sport_model.add(Dense(nClasses, activation='softmax'))

sport_model.summary()

sport_model.compile(
    loss='categorical_crossentropy',
    optimizer=tf.keras.optimizers.Adam(learning_rate=INIT_LR),
    metrics=['accuracy']
)

# ============================================================
# ENTRENAMIENTO
# ============================================================
callbacks = [
    EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=4, min_lr=1e-6, verbose=1)
]

sport_train = sport_model.fit(
    train_generator,
    epochs=EPOCHS,
    validation_data=valid_generator,
    callbacks=callbacks,
    class_weight=class_weight_dict,
    verbose=1
)

sport_model.save(RUTA_MODELO)
print("✅ Modelo guardado en:", RUTA_MODELO)

# ============================================================
# CURVAS DE ENTRENAMIENTO
ep           = range(len(sport_train.history['accuracy']))
accuracy     = sport_train.history['accuracy']
val_accuracy = sport_train.history['val_accuracy']
loss         = sport_train.history['loss']
val_loss     = sport_train.history['val_loss']

plt.figure(figsize=(12, 4))
plt.subplot(121)
plt.plot(ep, accuracy,     'bo', label='Train')
plt.plot(ep, val_accuracy, 'b',  label='Validación')
plt.title('Accuracy')
plt.legend()
plt.subplot(122)
plt.plot(ep, loss,     'ro', label='Train')
plt.plot(ep, val_loss, 'r',  label='Validación')
plt.title('Loss')
plt.legend()
plt.tight_layout()
plt.savefig('training_curves.png', dpi=150)
plt.close()
print("\n✅ Curvas guardadas en training_curves.png")

print("\n✅ Entrenamiento completo. Ahora ejecuta probar_animal.py")