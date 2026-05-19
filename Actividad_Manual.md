# Actividad Manual: Entender Transformers sin Computadora
# Sinuhe Sanchez Contreras
# Inteligencia Artificial

**Objetivo:** Experimentar la idea central del Transformer (*cada palabra decide a cuáles otras presta atención*) usando solo papel, lápiz y una calculadora (o porcentajes a ojo).  
**Nivel:** Principiantes. No se requiere programación ni álgebra lineal.  
**Materiales:** Hojas de esta actividad (una por alumno o pareja), lápiz, calculadora (opcional).

---

## Resumen de Conceptos Reforzados

| Concepto | Actividad donde aparece |
| :--- | :--- |
| Atención como “reparto de importancia” | Actividad 1 y 2 |
| El contexto cambia el significado | Actividad 2 |
| Máscara causal (no ver el futuro) | Actividad 3 |
| Varias “cabezas” / varios criterios | Actividad 4 |
| Leer todo vs. escribir paso a paso | Actividad 5 |

---

## Hoja para Alumnos — Actividad 1: La matriz de atención

### Enunciado
Frase corta (4 palabras):  
`EL` — `GATO` — `COME` — `PESCADO`

Imagina que eres la palabra **COME** y quieres entender qué haces en la oración. Puntúa del 0 al 10 cuánto te “importa” cada palabra para entenderte (10 = muchísimo).

| Desde... | EL | GATO | COME | PESCADO |
| :--- | :---: | :---: | :---: | :---: |
| **COME** → | 2 | 9 | 1 | 8 |

*(Nota: Esta es una propuesta lógica. El GATO realiza la acción y el PESCADO es el objeto comido, por lo que reciben la mayor puntuación. A sí misma se da un valor mínimo).*

### Paso 2 — Convertir a porcentajes (mini-softmax)
* **Suma tus cuatro puntuaciones:** `2 + 9 + 1 + 8 = 20`
* **Cálculo:** Divide cada puntuación entre la suma y multiplica por 100.

| Palabra | Puntuación | ÷ Suma | × 100 ≈ % |
| :--- | :---: | :---: | :---: |
| **EL** | 2 | $2 \div 20 = 0.10$ | **10 %** |
| **GATO** | 9 | $9 \div 20 = 0.45$ | **45 %** |
| **COME** | 1 | $1 \div 20 = 0.05$ | **5 %** |
| **PESCADO** | 8 | $8 \div 20 = 0.40$ | **40 %** |
| **Total** | **20** | | **100 %** |

### Paso 3 — Interpretación
* **¿A quién le diste más atención? ¿Tiene sentido para el verbo “come”?** > Le di más atención a **GATO** (45%) y a **PESCADO** (40%). Sí tiene total sentido, porque para entender el significado del verbo "comer" en una oración, es indispensable saber *quién* come y *qué* es lo que come.

### Pregunta de cierre
* **Si fueras la palabra PESCADO, ¿crees que tu fila de porcentajes sería igual? ¿Por qué sí o por no?** > **No sería igual.** Cada palabra busca un contexto diferente. Para el *PESCADO*, la palabra más importante sería *COME* (para saber qué acción recae sobre él), mientras que *GATO* o *EL* tendrían menor relevancia directa en su propia estructura.

---

## Hoja para Alumnos — Actividad 2: La palabra ambigua (dos contextos)

### Enunciado
La palabra **BANCO** aparece en dos frases. Completen la fila de BANCO (puntuación 0–10 y luego porcentajes aproximados) en cada caso.

#### Frase A: `FUIMOS` — `AL` — `BANCO` — `DEL` — `RIO`
* **Puntuaciones:** FUIMOS (1), AL (1), BANCO (1), DEL (7), RIO (10) $\rightarrow$ *Suma = 20*

| Palabra | FUIMOS | AL | BANCO | DEL | RIO | Total |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **% Ojo** | 5% | 5% | 5% | 35% | 50% | **100%** |

#### Frase B: `FUIMOS` — `AL` — `BANCO` — `A` — `SACAR` — `DINERO`
* **Puntuaciones:** FUIMOS (1), AL (1), BANCO (1), A (1), SACAR (8), DINERO (10) $\rightarrow$ *Suma = 22*

| Palabra | FUIMOS | AL | BANCO | A | SACAR | DINERO | Total |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **% Ojo** | 4% | 4% | 4% | 4% | 36% | 48% | **100%** |

### Preguntas
1. **¿En cuál frase BANCO le da más puntos a “RIO” / “DEL”?** > En la Frase A.
2. **¿En cuál le da más a “DINERO” / “SACAR”?** > En la Frase B.
3. **Explica con tus palabras cómo esto imita a un Transformer (máx. 3 líneas):** > Los Transformers no usan significados fijos. La palabra BANCO cambia su sentido matemático (financiero o geográfico) según la atención que presta a sus palabras vecinas en el contexto.

---

## Hoja para Alumnos — Actividad 3: Máscara causal (no hacer trampa)

### Situación
Un modelo que escribe la frase palabra por palabra (como ChatGPT) no puede ver palabras del futuro al generar la actual.
* **Orden de generación:** `1º EL` → `2º GATO` → `3º COME` → `4º PESCADO`

### Instrucción
Cuadrícula 4×4 (filas = palabra que “pregunta”, columnas = palabra a la que mira).  
* `✓` = SÍ se permite mirar.  
* `✗` = NO se permite mirar (futuro).

| ¿Quién mira? ↓ | 1º EL | 2º GATO | 3º COME | 4º PESCADO |
| :--- | :---: | :---: | :---: | :---: |
| **1º EL** | ✓ | ✗ | ✗ | ✗ |
| **2º GATO** | ✓ | ✓ | ✗ | ✗ |
| **3º COME** | ✓ | ✓ | ✓ | ✗ |
| **4º PESCADO** | ✓ | ✓ | ✓ | ✓ |

### Preguntas
1. **¿Cuántos ✓ hay en la fila de la última palabra (PESCADO)?** > Hay 4 ✓.
2. **¿Cuántos ✓ hay en la fila de la primera palabra (EL)?** > Hay 1 ✓.
3. **La forma de ✓ que queda (triángulo abajo) se llama máscara causal. ¿Por qué creen que es necesaria para escribir texto?** > Es necesaria porque durante el entrenamiento, si el modelo pudiera "ver el futuro", haría trampa copiando la palabra siguiente en lugar de aprender a predecir el lenguaje de forma lógica y natural.

---

## Hoja para Alumnos — Actividad 4: Varias cabezas (varios criterios)

### En equipo
Frase de análisis:  
`MARIA` — `NO` — `COMIO` — `PORQUE` — `ESTABA` — `ENFERMA`

Cada persona del equipo actúa como una **cabeza de atención distinta** y puntúa la fila de **COMIO** (0–10) bajo su propio criterio:

| Persona | Criterio (solo para COMIO) | MARIA | NO | COMIO | PORQUE | ESTABA | ENFERMA |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Cabeza A** | ¿Quién explica el porqué? (Causa) | 0 | 0 | 1 | 8 | 6 | 10 |
| **Cabeza B** | ¿Quién es el sujeto de la acción? | 10 | 1 | 1 | 0 | 0 | 0 |
| **Cabeza C** | ¿Quién está junto al verbo? (Vecinos) | 0 | 10 | 0 | 10 | 0 | 0 |

### Después de puntuar
1. **Comparen: ¿las tres filas son iguales?** > No, son completamente diferentes porque cada una busca un patrón distinto.
2. **En un Transformer real, esas “vistas” se juntan. ¿Qué ventaja tendría ver la frase desde tres criterios y no solo uno?** > Permite procesar el texto en paralelo analizando múltiples dimensiones a la vez: la lógica/causalidad (Cabeza A), la estructura sintáctica (Cabeza B) y la gramática inmediata (Cabeza C). Al unirlas, el modelo comprende el contexto real.

---

## Hoja para Alumnos — Actividad 5: Encoder vs Decoder (role-play)

### Respuestas para el Debrief (Discusión en grupo)

1. **¿Qué fue más fácil: leer todo (encoder) o escribir de a poco (decoder)?** > Leer todo (Encoder) es más sencillo porque cuentas con toda la información disponible simultáneamente. Escribir paso a paso (Decoder) genera incertidumbre ya que se avanza a ciegas, prediciendo elemento por elemento.
2. **¿En qué momento el decoder “necesitó” mirar atrás?** > Cada vez que finalizaba una palabra. Necesitaba voltear al pasado para recordar qué había escrito antes y qué instrucciones le dio el Encoder, manteniendo así la coherencia.
3. **¿Cómo se relaciona esto con traducir o con un chatbot?** > En un traductor, el **Encoder** lee el texto completo en el idioma origen (ej. Inglés) y extrae sus conceptos. El **Decoder** toma esas ideas y empieza a generar el texto en el idioma destino (ej. Español) palabra por palabra, usando la atención para "mirar" qué parte del origen está traduciendo exactamente.

---

## Actividad extra: Tokenizar a mano

### Enunciado
Los modelos no siempre cortan en palabras completas. Partan en “tokens” (pedazos útiles de caracteres y raíces):

* **inteligencia** $\rightarrow$ `intel` - `igencia` *(o `inteligencia` completa si es de alta frecuencia)*
* **programación** $\rightarrow$ `program` - `ación`
* **des-apro-bado** $\rightarrow$ `des` - `apro` - `bado`
* **Transform** $\rightarrow$ `Trans` - `form`