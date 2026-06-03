import numpy as np
import os
import pickle
import tensorflow as tf

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
tf.keras.utils.set_random_seed(42)

RUTA_BASE = os.path.dirname(__file__)
RUTA_MODELO = os.path.join(RUTA_BASE, "modelo_rnn.h5")
RUTA_MAPPINGS = os.path.join(RUTA_BASE, "tokenizer_mappings.pkl")
RUTA_DATASET = os.path.join(RUTA_BASE, "dataset_c.txt")
MAX_NUEVOS = 350

with open(RUTA_MAPPINGS, "rb") as f:
    mappings = pickle.load(f)
stoi = mappings["stoi"]
itos = mappings["itos"]
VOCAB_SIZE = mappings["vocab_size"]

modelo = tf.keras.models.load_model(RUTA_MODELO)
block_size = modelo.input_shape[1]

with open(RUTA_DATASET, "r", encoding="utf-8") as f:
    CORPUS = f.read()

SEQ = np.array([stoi[c] for c in CORPUS], dtype=np.int64)

def encode(s):
    return [stoi[c] for c in s]

def decode(ids):
    return "".join(itos[i] for i in ids)

SEP = "=" * 66

# ============================================================
# 1. PREDICCION DEL SIGUIENTE CARACTER (todo el dataset)
# ============================================================
print(f"\n{SEP}")
print("  EVALUACION 1: Prediccion del siguiente caracter")
print("  (ventana deslizante sobre todo el dataset)")
print(f"{SEP}")

top1_aciertos = 0
top3_aciertos = 0
total_preds = 0

for i in range(len(SEQ) - block_size):
    x = SEQ[i : i + block_size].reshape(1, block_size)
    y_real = int(SEQ[i + block_size])
    logits = modelo(x, training=False).numpy()[0, -1, :]
    pred = int(np.argmax(logits))
    top3 = set(np.argpartition(logits, -3)[-3:])

    if pred == y_real:
        top1_aciertos += 1
    if y_real in top3:
        top3_aciertos += 1
    total_preds += 1

pct_top1 = top1_aciertos / total_preds * 100
pct_top3 = top3_aciertos / total_preds * 100

print(f"\n  Predicciones totales: {total_preds:,}")
print(f"  Top-1 accuracy:  {top1_aciertos:>10,} / {total_preds:,}  = {pct_top1:6.2f}%")
print(f"  Top-3 accuracy:  {top3_aciertos:>10,} / {total_preds:,}  = {pct_top3:6.2f}%")
print(f"  Tasa de error:   {total_preds - top1_aciertos:>10,} / {total_preds:,}  = {100 - pct_top1:6.2f}%")

# ============================================================
# 2. COMPLETADO DE FUNCIONES (prompt -> generacion)
# ============================================================
print(f"\n{SEP}")
print("  EVALUACION 2: Completado de funciones (greedy)")
print(f"{SEP}")

rng = np.random.default_rng(42)

def muestrear(logits):
    return int(np.argmax(logits))

def completar(prompt, max_nuevos=MAX_NUEVOS):
    ids = encode(prompt)
    prompt_len = len(ids)
    for _ in range(max_nuevos):
        x = np.array(ids[-block_size:], dtype=np.int64)
        if x.shape[0] < block_size:
            pad = np.full(block_size - x.shape[0], ids[0], dtype=np.int64)
            x = np.concatenate([pad, x])
        x = x.reshape(1, block_size)
        logits = modelo(x, training=False).numpy()[0, -1, :]
        idx = muestrear(logits)
        ids.append(idx)
        if decode(ids[prompt_len:]).endswith("}\n\n"):
            break
    return decode(ids[prompt_len:])

def extraer_funciones(corpus):
    bloques = corpus.strip().split("\n\n")
    funciones = []
    for bloque in bloques:
        if not bloque.startswith("//"):
            continue
        brace_pos = bloque.find("{")
        if brace_pos == -1:
            continue
        if "(" not in bloque[:brace_pos]:
            continue
        prompt = bloque[: brace_pos + 1]
        expected = bloque[brace_pos + 1 :]
        nombre = bloque.split("\n")[0].replace("//", "").strip()
        funciones.append((nombre, prompt, expected))
    return funciones

funciones = extraer_funciones(CORPUS)
print(f"  Funciones encontradas: {len(funciones)}\n")

resultados = []
for nombre, prompt, expected in funciones:
    generado = completar(prompt)

    g = generado.rstrip("\n")
    e = expected.rstrip("\n")

    min_len = min(len(g), len(e))
    max_len = max(len(g), len(e))
    coinciden = sum(1 for i in range(min_len) if g[i] == e[i])
    char_pct = (coinciden / max_len * 100) if max_len > 0 else 0
    exacto = g == e

    resultados.append(
        (nombre, exacto, char_pct, coinciden, max_len, prompt, expected, generado)
    )

    marca = "✓" if exacto else "✗"
    print(f"  [{marca}] {nombre:30s}  {char_pct:5.1f}% coincidencia "
          f"({coinciden:>3}/{max_len:<3} chars)")

exactos = sum(1 for r in resultados if r[1])
total = len(resultados)
promedio_char = float(np.mean([r[2] for r in resultados]))

print(f"\n{SEP}")
print("  RESUMEN DE EVALUACION")
print(f"{SEP}")
print(f"  Coincidencias exactas:           {exactos:>2}/{total:<2}  = {exactos / total * 100:6.2f}%")
print(f"  Funciones con errores:           {total - exactos:>2}/{total:<2}  = {(total - exactos) / total * 100:6.2f}%")
print(f"  Coincidencia de chars (promedio):          {promedio_char:6.2f}%")

print(f"\n{SEP}")
print("  DETALLE: funciones con errores (max 8)")
print(f"{SEP}")

errores = [r for r in resultados if not r[1]]
for nombre, _, char_pct, _, _, prompt, expected, generado in errores[:8]:
    print(f"\n  << {nombre} >>  (coincidencia: {char_pct:.1f}%)")
    print(f"  Prompt:  {repr(prompt[:80])}")
    print(f"  Esperado:{expected[:150]}")
    print(f"  Generado:{generado[:150]}")

print(f"\n{SEP}")
print("  FUNCIONES CORRECTAS")
print(f"{SEP}")
for nombre, exacto, char_pct, _, _, _, _, _ in resultados:
    if exacto:
        print(f"  ✓ {nombre}")
