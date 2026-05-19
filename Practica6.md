# Práctica 6 Finalizada
**Estudiante:** Sinuhé Sánchez Contreras

Supón que estás diseñando esta red para procesar secuencias de datos. Si la "novedad pura" ($x_t$) es un vector de entrada con características de dimensión $\mathbb{R}^{20}$ y decides que el "fantasma del pasado" ($h_{t-1}$) requiere una capacidad de memoria representada en un espacio oculto de dimensión $\mathbb{R}^{64}$.

Calcula y justifica matemáticamente:
1. Las dimensiones exactas requeridas para la matriz $W_{hx}$.
2. Las dimensiones exactas requeridas para la matriz recurrente $W_{hh}$.
3. La dimensión final del vector resultante $h_t$.

---

### **1. Dimensiones de $W_{hx}$**
* **Justificación:** Para posibilitar la transformación lineal, el número de columnas de la matriz operadora debe acoplarse formalmente con los componentes del vector de entrada ($20$). Asimismo, para que el vector transformado sea compatible en la adición con el espacio oculto, la cantidad de filas de dicha matriz debe corresponder a la dimensión de la memoria del sistema ($64$).
* **Resultado:** $W_{hx} \in \mathbb{R}^{64 \times 20}$

### **2. Dimensiones de $W_{hh}$**
* **Justificación:** Debido a que el estado oculto previo posee un espacio de dimensión $64$ y requerimos que la salida proyectada mantenga esa misma estructura geométrica de dimensión $64$ para efectuar la suma de estados, la transformación necesita gobernarse por una matriz cuadrada.
* **Resultado:** $W_{hh} \in \mathbb{R}^{64 \times 64}$

### **3. Dimensión final de $h_t$**
* **Justificación:** 
  1. La operación $W_{hx} x_t$ mapea los espacios transformando $(64 \times 20) \times (20 \times 1)$ en un vector de orden $64 \times 1$.
  2. El producto correspondiente a la recurrencia $W_{hh} h_{t-1}$ mapea $(64 \times 64) \times (64 \times 1)$ resultando equivalentemente en un vector de orden $64 \times 1$.
  3. Al consolidar la suma de ambos términos junto al término de sesgo $b$ (cuya naturaleza es igualmente de $64 \times 1$), el espacio vectorial resultante se mantiene en $\mathbb{R}^{64}$.
  4. La aplicación de la función no lineal $\tanh$ opera de manera puntual (elemento a elemento), preservando intacta la morfología y dimensiones del vector.
* **Resultado:** $h_t \in \mathbb{R}^{64}$

---

## 2.3 Actividad 2.3: La Estrofa Perdida (Pensamiento Lateral)

En el poema original, el vector de sesgo (bias) $b$ apenas se menciona como "un pequeño desvío inevitable". Sabiendo que en álgebra lineal el sesgo permite desplazar la función de activación para evitar que pase rígidamente por el origen, **redacta una estrofa corta** (manteniendo el tono literario del acertijo) que describa de manera exclusiva la función y utilidad del parámetro $b$.

> **El Desvío Vital (El Sesgo $b$)**
> Rompo la atadura del origen, soy la sutil desviación,
> la fuerza que altera la simetría y libera la activación.
> Sin memoria previa ni dato entrante, mi rumbo sé trazar,
> dándole un nuevo norte al cero para que el modelo pueda avanzar.

---

## 2.4 Actividad 2.4: El Límite del Muro Curvo (Análisis de Saturación)

El acertijo menciona que el muro curvo ($\tanh$) evita que "nuestra energía explote hacia el infinito".
1. Grafica mentalmente o en papel la función $f(z) = \tanh(z)$ y su derivada $f'(z) = 1 - \tanh^2(z)$.
2. Si los valores de entrada y los pesos crecen descontroladamente y el resultado de la suma lineal es $z = 500$, la salida del muro curvo será casi exactamente $1$. ¿Qué le sucede a la derivada $f'(500)$ en ese punto?
3. Explica brevemente por qué este fenómeno (conocido como saturación) es catastrófico para el aprendizaje de la red.

### 1. Comportamiento de la Función y su Derivada
* **$\tanh(z)$:** Se describe como una curva sigmoidea de transición suave que se aproxima asíntoticamente a $1$ ante valores positivos de $z$ y hacia $-1$ con valores altamente negativos.
* **$f'(z) = 1 - \tanh^2(z)$:** Su comportamiento emula una distribución acampanada con su ápice en el origen ($1$ cuando $z=0$) y decrece exponencialmente hacia $0$ conforme la variable independiente se aleja del centro de la función.

### 2. Evaluación en el Umbral Crítico ($z = 500$)
* **Evaluación de la salida:** El cómputo de $\tanh(500)$ genera un valor tan infinitamente cercano a la unidad que los sistemas informáticos bajo precisión estándar lo consolidan directamente como $1.0$.
* **Evaluación de la derivada:** Sustituyendo formalmente en la ecuación diferencial:
$$f'(500) = 1 - \tanh^2(500)$$
$$f'(500) \approx 1 - (1)^2 = 0$$
En esta región la pendiente de la función se aplana por completo, reduciendo la derivada a un cero algorítmico absoluto.

### 3. Impacto Crítico en la Optimización del Sistema
La actualización de parámetros en arquitecturas neuronales depende por completo del algoritmo de retropropagación (Backpropagation), el cual emplea la Regla de la Cadena para mapear la sensibilidad de los pesos respecto al error. 

La formulación matemática del ajuste de pesos incluye explícitamente el término de la derivada:
$$\Delta W \propto \text{Error} \cdot \mathbf{f'(z)} \cdot \text{Entrada}$$

* **Desvanecimiento de la señal de error:** Al anularse la derivada ($f'(z) \approx 0$), toda la cadena de multiplicaciones colapsa, resultando en un gradiente nulo.
* **Inercia estructural (Neurona muerta):** Los pesos asociados se congelan por completo, impidiendo que el optimizador identifique directrices de mejora al no recibir retroalimentación funcional sobre su desempeño.
* **Afectación temporal (Vanishing Gradient):** En redes recurrentes, este defecto se propaga multiplicativamente en la dimensión del tiempo. Si la información del gradiente se extingue en un paso dado, la influencia de los estados remotos queda incomunicada, inhabilitando la captura de secuencias de largo alcance.

---

## 2.5 Actividad 2.5: El Eco del Castigo (Trazo del Gradiente)

El aprendizaje en una RNN se realiza propagando el error hacia atrás en el tiempo (BPTT). Supón que la red cometió un error en su "respuesta de hoy" ($h_t$). Para corregirlo, la red debe enviar una señal de castigo hacia atrás para ajustar los pesos. Siguiendo la narrativa del acertijo: Describe qué "peajes" y "muros" debe atravesar el error en reversa para llegar desde $h_t$ y poder modificar la percepción del "fantasma del pasado" ($h_{t-1}$). ¿Qué operación matemática del cálculo diferencial representa este viaje en reversa?

### **Respuesta**
El flujo de información en la unidad recurrente integra la entrada actual ($x_t$) con la herencia del estado anterior ($h_{t-1}$) proyectándolos mediante transformaciones matriciales operadas como aduanas numéricas hacia un entorno común (ej. $\mathbb{R}^{64}$). Este espacio es modificado por un sesgo ($b$) que evita la rigidez del origen y posteriormente se somete a la contención del límite curvo impuesto por la función $\tanh$, la cual restringe las magnitudes en un rango cerrado de $[-1, 1]$ para garantizar la estabilidad, dando origen al estado actual ($h_t$). 

Para ejecutar el proceso de corrección, el sistema calcula de forma inversa la influencia del error empleando la Regla de la Cadena mediante Retropropagación a través del Tiempo (BPTT). Esta señal recorre en sentido opuesto las capas multiplicando el error acumulado por la derivada del límite curvo ($\tanh$) y por la transpuesta de las estructuras matriciales. El riesgo matemático imperante radica en que si las magnitudes previas se situaron en zonas extremas, la pendiente se torna plana y el valor de la derivada cae a cero, deteniendo por completo el flujo correctivo e imposibilitando que la experiencia del presente reajuste y optimice la interpretación de la memoria histórica del sistema.

---

## 2.6 Actividad 2.6: Depuración del Oráculo (Inspección de Código NumPy)

A continuación se presenta un intento de programar el oráculo en Python. Sin embargo, el programador junior cometió **un grave error algorítmico y matemático** en la línea 4 que provocará un colapso en la dimensionalidad o un cálculo erróneo.

```python
def paso_rnn_erroneo(x_t, h_prev, W_hx, W_hh, b):
    # Línea con error oculto
    combinacion = (W_hx * x_t) + (W_hh * h_prev) + b
    return np.tanh(combinacion)