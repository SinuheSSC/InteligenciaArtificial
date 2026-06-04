**Estudiante:** Sinuhé Sánchez Contreras  

## Actividad 6 — Matriz de Atención Completa

Análisis de conectividad del corpus oracional: **"LA NIÑA PEQUEÑA COME FRUTA"**

### Paso 1 — Puntuaciones de Consulta Raw (Matriz de Afinidad)

Para cada token de consulta (Query, eje vertical), se asigna una puntuación escalar de correlación hacia los tokens de clave (Key, eje horizontal) en un rango de 0 a 10.

| Desde (Query) $\downarrow$ / Hacia (Key) $\rightarrow$ | LA | NIÑA | PEQUEÑA | COME | FRUTA |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **LA** | 3 | 10 | 6 | 1 | 1 |
| **NIÑA** | 7 | 10 | 9 | 8 | 3 |
| **PEQUEÑA** | 4 | 10 | 8 | 2 | 1 |
| **COME** | 2 | 10 | 4 | 10 | 10 |
| **FRUTA** | 1 | 5 | 1 | 10 | 10 |

### Paso 2 — Normalización por Renglón (Softmax Estocástico)

Se calcula la sumatoria por renglón ($\sum x$) para transformar las magnitudes escalares en coeficientes probabilísticos independientes.

| Desde $\downarrow$ / Hacia $\rightarrow$ | $\sum \text{Fila}$ | LA | NIÑA | PEQUEÑA | COME | FRUTA | Total |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **LA** | **21** | 14.3% | 47.6% | 28.6% | 4.8% | 4.8% | $\approx 100\%$ |
| **NIÑA** | **37** | 18.9% | 27.0% | 24.3% | 21.6% | 8.1% | $\approx 100\%$ |
| **PEQUEÑA** | **25** | 16.0% | 40.0% | 32.0% | 8.0% | 4.0% | $100\%$ |
| **COME** | **36** | 5.6% | 27.8% | 11.1% | 27.8% | 27.8% | $\approx 100\%$ |
| **FRUTA** | **27** | 3.7% | 18.5% | 3.7% | 37.0% | 37.0% | $\approx 100\%$ |

### Paso 3 — Mapeo de Activaciones Críticas (Zonas de Máxima Densidad)

Identificación de los picos de activación probabilística por cada vector latente.

| Desde $\downarrow$ / Hacia $\rightarrow$ | LA | NIÑA | PEQUEÑA | COME | FRUTA |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **LA** | 14.3% | 🔴 **47.6%** | 28.6% | 4.8% | 4.8% |
| **NIÑA** | 18.9% | 🔴 **27.0%** | 24.3% | 21.6% | 8.1% |
| **PEQUEÑA** | 16.0% | 🔴 **40.0%** | 32.0% | 8.0% | 4.0% |
| **COME** | 5.6% | 🔴 **27.8%** | 11.1% | 🔴 **27.8%** | 🔴 **27.8%** |
| **FRUTA** | 3.7% | 18.5% | 3.7% | 🔴 **37.0%** | 🔴 **37.0%** |

* **Diagnóstico Morfológico:** El mapa de calor resultante evidencia una geometría de activación asimétrica que responde a dependencias sintácticas funcionales. Los modificadores directos (**LA**, **PEQUEÑA**) concentran su masa de probabilidad sobre el núcleo del sujeto (**NIÑA**). El núcleo del predicado (**COME**) ramifica su atención bidireccionalmente hacia el agente y el objeto, mientras que el argumento acusativo (**FRUTA**) se ancla fuertemente a la acción que lo transita.

---

### Preguntas de Análisis Metódico

#### **1. Grado de simetría estructural entre las filas de COME y FRUTA**
Existe una correlación semántica innegable dado que ambos tokens se co-determinan a través de la relación verbo-objeto; no obstante, exhiben disparidades en sus vectores latentes:

| Token Evaluado | Rol Sintáctico | Perfil de Distribución de Carga Atencional |
| :--- | :--- | :--- |
| **COME** | Núcleo Verbal | **Multimodal:** Distribuye la atención de forma balanceada entre el sujeto (**NIÑA**) y el objeto (**FRUTA**) para parametrizar por completo las condiciones de la acción. |
| **FRUTA** | Objeto Directo | **Focalizado:** Subordina su peso atencional de forma masiva hacia el verbo (**COME**), puesto que la acción es el único componente que define su presencia en la secuencia. |

#### **2. Análisis de entropía en el token NIÑA (Distribución Uniforme)**
La fila correspondiente a **NIÑA** destaca por presentar una dispersión de pesos con la menor entropía del sistema (atención distribuida de manera más homogénea). 

Esto ocurre debido a su rol jerárquico como **nodo central de la oración**. Al ser el sujeto activo, entabla conexiones semánticas directas con el determinante que lo define (**LA**), el adjetivo que lo restringe (**PEQUEÑA**) y la acción que ejecuta (**COME**), requiriendo un balance de atención múltiple para integrar todas sus dimensiones descriptivas.

#### **3. Complejidad Espacial del Mecanismo Atencional**
Bajo una secuencia extendida a $N = 100$ tokens, las dimensiones de la matriz de atención escalar corresponderían a $100 \times 100$, consolidando un total de **10,000 celdas operacionales**.

| Longitud del Input ($N$) | Dimensión Cuadrática ($N^2$) | Impacto en la Memoria del Sistema |
| :---: | :---: | :--- |
| 5 tokens | 25 celdas | Carga computacional insignificante. |
| 10 tokens | 100 celdas | Escalamiento controlado. |
| 100 tokens | 10,000 celdas | Requerimiento de bloques de memoria dedicados. |
| 1,000 tokens | 1,000,000 celdas | Alta demanda de hardware. Cuello de botella en GPU. |

* **Conclusión de Complejidad:** A diferencia de las arquitecturas recurrentes cuyo costo computacional escala de forma lineal ($O(N)$), los Transformers operan bajo una complejidad espacial y temporal de orden cuadrático ($O(N^2)$). Debido a que cada elemento de la secuencia debe calcular de forma obligatoria un producto escalar contra todos los componentes del contexto, el volumen de memoria requerida se expande exponencialmente ante secuencias masivas de texto.

---

## Actividad 7 — Mecánica de Softmax en Subespacios Vectoriales

Formulación matemática del operador de normalización exponencial:

$$p_i = \frac{e^{s_i}}{\sum_{j} e^{s_j}}$$

### Paso 1 — Proyección a Escala Exponencial (Aproximación Numérica)

Dados los logits de activación: $\mathbf{s} = [\text{NIÑA}: 3.0, \ \text{PEQUEÑA}: 0.5, \ \text{COME}: 0.2, \ \text{FRUTA}: 1.0]$

* $e^{3.0} \approx 20.09$
* $e^{0.5} \approx 1.65$
* $e^{0.2} \approx 1.22$
* $e^{1.0} \approx 2.72$
* **Sumatoria de Exponenciales ($\sum e^{s_j}$):** $20.09 + 1.65 + 1.22 + 2.72 = \mathbf{25.68}$

### Paso 2 — Cálculo de la Distribución Probabilística Final

| Componente | Logit ($s_i$) | Valor Exponencial ($e^{s_i}$) | Operación de Normalización | Porcentaje Normalizado |
| :--- | :---: | :---: | :---: | :---: |
| **NIÑA** | 3.0 | 20.09 | $20.09 \div 25.68$ | **78%** |
| **PEQUEÑA** | 0.5 | 1.65 | $1.65 \div 25.68$ | **6%** |
| **COME** | 0.2 | 1.22 | $1.22 \div 25.68$ | **5%** |
| **FRUTA** | 1.0 | 2.72 | $2.72 \div 25.68$ | **11%** |
| **Total** | | **25.68** | | **100%** |

### Paso 3 — Análisis e Interpretación de Resultados

* **Efecto de Amplificación Gradiente:** Se evidencia que, si bien en el vector original de logits el valor de **NIÑA** ($3.0$) era solo tres veces superior al de **FRUTA** ($1.0$), tras la transformación del Softmax la distancia se amplifica exponencialmente, otorgando a **NIÑA** el 78% del peso absoluto y diluyendo los componentes restantes. 
* **Justificación de la Escala $\frac{1}{\sqrt{d_k}}$:** Si los valores de entrada crecen desproporcionadamente, el operador Softmax entra en zonas de saturación donde los gradientes se desvanecen. Para mitigar este comportamiento, la arquitectura Transformer introduce el factor de escala $\frac{1}{\sqrt{d_k}}$ (raíz cuadrada de la dimensión de las llaves), conteniendo las magnitudes de las puntuaciones de atención previas a la capa exponencial.

* **Insuficiencia del Reparto Proporcional Lineal (Sin Exponencial):** La simple normalización por división ($\frac{s_i}{\sum s_j}$) resulta ineficaz por dos limitaciones críticas:
  1. No cuenta con la propiedad de **amplificar diferencias latentes**, lo que causaría que el modelo disperse su atención de forma ambigua entre elementos competitivos (ej. otorgando un sobreestimado 21% a **FRUTA** en lugar de priorizar el 78% de **NIÑA**).
  2. Es matemáticamente inestable ante la presencia de logits con signo negativo (frecuentes tras transformaciones lineales afines), pudiendo generar denominadores nulos o asignaciones probabilísticas inválidas menores a cero. La función exponencial garantiza que todas las salidas pertenezcan estrictamente al dominio real positivo $(0, 1]$.

---

## Actividad 8 — Combinación Lineal de Vectores de Valor (Values)

### Paso 1 — Intermediación de Pesos Atencionales a Notación Decimal

| Componente | Vector de Valor ($V$) | Peso Atencional ($\%$) | Coeficiente Decimal ($\alpha$) |
| :--- | :---: | :---: | :---: |
| **LA** | $(1, 1)$ | 5% | 0.05 |
| **NIÑA** | $(4, 5)$ | 35% | 0.35 |
| **PEQUEÑA** | $(3, 4)$ | 10% | 0.10 |
| **COME** | $(5, 1)$ | 10% | 0.10 |
| **FRUTA** | $(6, 3)$ | 40% | 0.40 |

### Paso 2 — Ecuación de Combinación Escalar ($\alpha_i \cdot V_i$)

* $\text{LA} \rightarrow 0.05 \cdot (1, 1) = (0.05, 0.05)$
* $\text{NIÑA} \rightarrow 0.35 \cdot (4, 5) = (1.40, 1.75)$
* $\text{PEQUEÑA} \rightarrow 0.10 \cdot (3, 4) = (0.30, 0.40)$
* $\text{COME} \rightarrow 0.10 \cdot (5, 1) = (0.50, 0.10)$
* $\text{FRUTA} \rightarrow 0.40 \cdot (6, 3) = (2.40, 1.20)$

### Paso 3 — Agregación e Intersección del Vector Salida ($\sum \alpha_i V_i$)

* Componente $X$: $0.05 + 1.40 + 0.30 + 0.50 + 2.40 = \mathbf{4.65}$
* Componente $Y$: $0.05 + 1.75 + 0.40 + 0.10 + 1.20 = \mathbf{3.50}$

$$\text{Vector Resultante de Atención (Context Vector)} = (4.65, \ 3.50)$$

### Análisis Espacial (Desplazamiento de la Representación)

Si calculamos el vector de desplazamiento relativo tomando como pivote la coordenada inicial del token **COME** $(5, 1)$, se obtiene un gradiente posicional de $(-0.35, \ 2.50)$. Al evaluar la distancia euclidiana frente a los demás nodos, se demuestra un cambio de posición geoespacial:

$$\text{Distancia a FRUTA}(6, 3) \approx 1.44 \quad \Big| \quad \text{Distancia a NIÑA}(4, 5) \approx 1.64 \quad \Big| \quad \text{Distancia a COME}(5, 1) \approx 2.52$$

* **Conclusión de la Operación:** La representación semántica de **COME** abandona su definición abstracta aislada para reubicarse geométricamente en las proximidades vectoriales de **FRUTA** y **NIÑA**. Esto demuestra empíricamente cómo el mecanismo de atención altera los embeddings base, forzando a que el token absorba el contexto dinámico que lo rodea.

---

## Actividad 9 — Enmascaramiento por Relleno (Padding Mask)

Estructura de minilote en procesamiento paralelo:
* **Secuencia 1 (Con Padding):** `[EL, GATO, COME, PAD, PAD]` (Longitud efectiva: 3)
* **Secuencia 2 (Limpia):** `[LA, NIÑA, PEQUEÑA, COME, FRUTA]` (Longitud efectiva: 5)

### Paso 1 — Matriz de Restricción Booleana para Secuencia 1 ($5 \times 5$)

Las posiciones de relleno lógico se marcan con la bandera $\mathbf{P}$ (Masked / Celda Anulada).

| Desde $\downarrow$ / Hacia $\rightarrow$ | EL | GATO | COME | PAD | PAD |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **EL** | | | | $\mathbf{P}$ | $\mathbf{P}$ |
| **GATO** | | | | $\mathbf{P}$ | $\mathbf{P}$ |
| **COME** | | | | $\mathbf{P}$ | $\mathbf{P}$ |
| **PAD** | $\mathbf{P}$ | $\mathbf{P}$ | $\mathbf{P}$ | $\mathbf{P}$ | $\mathbf{P}$ |
| **PAD** | $\mathbf{P}$ | $\mathbf{P}$ | $\mathbf{P}$ | $\mathbf{P}$ | $\mathbf{P}$ |

### Análisis Técnico del Enmascaramiento

El objetivo de la máscara de padding es neutralizar la influencia de los tokens de control artificiales (`PAD`) añadidos para estandarizar las dimensiones de los tensores. Al interceptar la matriz antes de la función Softmax, a las celdas marcadas con $\mathbf{P}$ se les asigna un valor analítico extremo de $-\infty$. Esto provoca que, al aplicar la base exponencial, su coeficiente de atención se reduzca a un **cero absoluto** (representado formalmente con las exclusiones $\mathbf{\times}$), evitando de este modo que el modelo distorsione sus gradientes con datos nulos y aprenda correlaciones artificiales o ruido estructural. El lote 2 queda exento de estas restricciones severas debido a que posee un aprovechamiento completo de su longitud de secuencia.

---

## Actividad 10 — Mecánica de Atención Cruzada (Cross-Attention)

Simulación de traducción automática (Arquitectura Encoder-Decoder).

### Paso 1 — Estructura de la Matriz Inter-Lenguaje ($3 \times 3$)

El Decoder genera el token de salida número 3 fijando la atención sobre los estados ocultos calculados por el Encoder en el idioma origen.

| Desde Decoder (EN) $\downarrow$ / Hacia Encoder (ES) $\rightarrow$ | YO | QUIERO | CAFÉ |
| :--- | :---: | :---: | :---: |
| **I** | | | |
| **WANT** | | | |
| **Token 3 (Target: COFFEE)** | 1 | 3 | **10** |

### Paso 2 — Normalización Probabilística de la Consulta

* **Sumatoria de Logits de Entrada:** $1 + 3 + 10 = \mathbf{14}$

$$\text{Peso sobre CAFÉ} = \frac{10}{14} \approx \mathbf{71.4\%} \quad \Big| \quad \text{Peso sobre QUIERO} = \frac{3}{14} \approx \mathbf{21.4\%} \quad \Big| \quad \text{Peso sobre YO} = \frac{1}{14} \approx \mathbf{7.1\%}$$

* **Diferenciación Arquitectónica Clave:**
  * **Self-Attention (Auto-atención):** Modula las relaciones internas de una misma frase compartiendo el mismo espacio de representación lingüística. Las matrices $Q$, $K$ y $V$ provienen de la misma fuente.
  * **Cross-Attention (Atención cruzada):** Actúa como un puente de alineación entre dos dominios de información independientes. Las consultas ($Q$) son generadas de forma nativa por el bloque del Decoder (idioma destino), mientras que las llaves ($K$) y valores ($V$) se derivan directamente del espacio semántico codificado por el Encoder (idioma origen).

---

## Actividad 11 — Modelado de Lenguaje Enmascarado (MLM / BERT Style)

Análisis de la secuencia truncada: **"EL GATO `[MASK]` PESCADO"**

### Paso 1 — Evaluación Teórica de Compatibilidad de Vocabulario

| Candidato ($w_i$) | Viabilidad Sintáctica / Semántica | Diagnóstico de Ajuste de Contexto |
| :--- | :---: | :--- |
| **COME** | **Alta** | Óptima correlación. Satisface la estructura sujeto-verbo-objeto. |
| **DUERME** | **Nula** | Incompatibilidad de selección. Un verbo intransitivo no admite objeto directo físico. |
| **VERDE** | **Nula** | Ruptura de estructura sintáctica. Un adjetivo no puede actuar como núcleo de la predicación. |
| **RÁPIDO** | **Nula** | Ruptura de jerarquía. Un adverbio requiere un núcleo verbal para modificar. |

### Paso 2 — Simulación de Puntuación y Distribución Softmax

* Sumatoria de afinidades asignadas: $10 + 2 + 1 + 1 = \mathbf{14}$

[COME]    ██████████████████████████████ 71.4%
[DUERME]  ██████ 14.3%
[VERDE]   ███ 7.1%
[RÁPIDO]  ███ 7.1%


* **El Criterio Bidireccional de BERT:** Los modelos autoregresivos clásicos (como la familia GPT) sufren de una restricción causal izquierda-derecha que les impide leer tokens posteriores. En contraste, arquitecturas tipo BERT rompen esta limitación mediante el entrenamiento bidireccional. Al ocultar un token intermedio, el sistema calcula de forma simultánea el contexto izquierdo (`EL GATO`) y el contexto derecho (`PESCADO`). Esta inspección de doble flanco proporciona las restricciones semánticas necesarias para determinar de manera unívoca que el elemento faltante debe ser obligatoriamente un verbo de acción transitiva enfocado al consumo de alimentos.

---

## Actividad 12 — Procesamiento en Redes Profundas (Multi-Layer Refinement)

### Evolución de los Atributos Latentes en la Capa 2

Tras el procesamiento en la Capa 1, los tokens base han modificado sus coordenadas iniciales, cargándose de información contextual. Al ejecutarse la segunda ronda de atención focalizada en el token **FRUTA**, el sistema ya no procesa palabras crudas aisladas, sino perfiles híbridos enriquecidos.

[Representación en Capa 1] ──> [Segunda Ronda de Atención] ──> [Perfil Semántico Capa 2]
Desde: FRUTA
Hacia: COME (Peso Máximo: 10)
NIÑA (Peso Secundario: 7)


En este nivel de profundidad, la matriz de atención de la Capa 2 detecta que **COME** contiene información integrada sobre quién ejecuta la acción. En consecuencia, cuando **FRUTA** atiende al verbo, indirectamente está asimilando la semántica de la totalidad del evento (Verbo + Sujeto). Este mecanismo de refinamiento jerárquico permite a las capas superiores de los Transformers consolidar conceptos abstractos de alta complejidad.

---

## Actividad 13 — Análisis Comparativo: RNN vs. Transformer

### Topología de Red sobre un Grafo de 5 Nodos: `[A] ── [B] ── [C] ── [D] ── [E]`

Modo Recurrente (RNN):
[A] ──> [B] ──> [C] ──> [D] ──> [E]  (Procesamiento secuencial paso a paso)

Modo Atención (Transformer):
[E] ──────────────────────────> [A]  (Conexión directa en un solo salto)


### Tabla Comparativa de Complejidad de Conectividad

| Métrica Estructural | Arquitectura Recurrente (RNN) | Redes de Atención (Transformer) |
| :--- | :--- | :--- |
| **Saltos Operacionales ($A \rightarrow E$)** | $4 \text{ pasos secuenciales}$ | **$1 \text{ paso directo}$** |
| **Escalamiento con $N=100$ tokens** | $100 \text{ pasos de estado}$ | $10,000 \text{ interacciones matriciales}$ |
| **Mecánica de Procesamiento** | Secuencial (Iterativa por paso) | Paralela (Simultánea en bloques) |
| **Retención de Largo Alcance** | Degradación por gradiente desvanecido. | **Inmune a la distancia física.** |

* **Justificación de la Transición Tecnológica:** Las redes recurrentes procesan la información de manera estrictamente lineal, lo que genera un cuello de botella temporal y provoca la pérdida paulatina de información debido al desvanecimiento del gradiente a lo largo del tiempo. Los Transformers resuelven este problema al eliminar la dependencia del orden secuencial físico: la distancia de comunicación entre cualquier par de palabras, por más distantes que se encuentren en el texto, se reduce a un solo salto directo ($O(1)$). A pesar de demandar una mayor cantidad de memoria debido a la naturaleza cuadrática de sus matrices de atención, su capacidad para entrenarse en paralelo y capturar dependencias de largo alcance los convierte en la opción estándar para tareas complejas de procesamiento de lenguaje.

---

## Actividad 14 — Mitigación de Saturación mediante Escalamiento ($\sqrt{d_k}$)

Evaluación del comportamiento del operador Softmax con una dimensión de llave fijada en $d_k = 4$, donde el factor estabilizador es $\sqrt{d_k} = \sqrt{4} = 2$.

### Caso A: Vector de Logits Sin Escalar ($\mathbf{s} = [8, \ 2, \ 2, \ 2]$)

* **Valores Exponenciales:** $[e^8 \approx 2980.96, \ e^2 \approx 7.39, \ e^2 \approx 7.39, \ e^2 \approx 7.39]$
* **Suma total:** $2980.96 + 7.39 + 7.39 + 7.39 = \mathbf{3003.13}$

$$\text{Probabilidad del Ganador} = \frac{2980.96}{3003.13} \approx \mathbf{99.26\%} \quad \Big| \quad \text{Probabilidad de los demás} \approx \mathbf{0.25\%}$$

### Caso B: Vector de Logits Escalado ($\mathbf{s}_{\text{scaled}} = [4, \ 1, \ 1, \ 1]$)

* **Valores Exponenciales:** $[e^4 \approx 54.60, \ e^1 \approx 2.72, \ e^1 \approx 2.72, \ e^1 \approx 2.72]$
* **Suma total:** $54.60 + 2.72 + 2.72 + 2.72 = \mathbf{62.76}$

$$\text{Probabilidad del Ganador} = \frac{54.60}{62.76} \approx \mathbf{87.00\%} \quad \Big| \quad \text{Probabilidad de los demás} \approx \mathbf{4.33\%}$$

### Conclusión Matemática del Escalamiento

| Muestra Evaluada | Distribución de Probabilidad Resultante | Estado del Gradiente |
| :--- | :--- | :--- |
| **Sin Escalar** | $[\mathbf{99.26\%}, \ 0.25\%, \ 0.25\%, \ 0.25\%]$ | **Saturado:** Gradiente nulo para optimización. |
| **Con Escalar ($\sqrt{d_k}$)** | $[\mathbf{87.00\%}, \ 4.33\%, \ 4.33\%, \ 4.33\%]$ | **Estable:** Permite la retropropagación. |

El análisis numérico demuestra que el proceso de escalado no altera la jerarquía de los elementos (el token dominante conserva el liderazgo), pero evita que la distribución de probabilidad colapse en una función delta que concentre el 99% de la atención en un solo nodo. Al reducir las magnitudes internas mediante el factor $\sqrt{d_k}$, se mantiene la suavidad de la función Softmax, permitiendo que el resto de los tokens de la secuencia aporten información al contexto y garantizando un flujo constante de gradientes durante la fase de entrenamiento de la red.