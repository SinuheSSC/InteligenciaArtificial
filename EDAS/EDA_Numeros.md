# Análisis Exploratorio de Datos (EDA): Diagnóstico Estructural y Distribución Espacial para la Clasificación de Dígitos Manuscritos ($1$, $2$ y $3$)

**Estudiante:** Sinuhé Sánchez Contreras  
**Objetivo Metodológico:** Auditar y perfilar un subconjunto de tensores bidimensionales que representan caracteres numéricos manuscritos, restringiendo el espacio de hipótesis a tres clases específicas para garantizar la calidad de los datos previa a la optimización de un clasificador estadístico.

---

## 1. Naturaleza y Delimitación del Problema

Este análisis aborda el procesamiento de un corpus de imágenes rasterizadas que contienen representaciones gráficas de los dígitos de la base decimal. Para este diseño experimental, el espacio de clases se reduce de forma controlada a un esquema de clasificación supervisada multiclase compuesto por tres categorías excluyentes:

$$\mathcal{Y} = \{1, 2, 3\}$$

El objetivo principal del EDA es mapear la topología de las intensidades de los píxeles, identificar la varianza en los estilos de trazo y asegurar la separabilidad de las fronteras de decisión antes de entrenar un modelo predictivo.

---

## 2. Especificación y Arquitectura del Dataset

El conjunto de datos se descompone en un espacio de características de alta dimensionalidad y un vector de etiquetas discretas:

### Espacio de Características / Variables de Entrada ($\mathbf{X}$)
Cada muestra consiste en una matriz de proyección bidimensional de orden $28 \times 28$. Al aplanar el tensor para su procesamiento en clasificadores lineales o densos, se genera un vector de características continuas en $\mathbb{R}^{74}$ debido a la resolución espacial:

$$28 \times 28 = 784 \quad \text{características}$$

| Descriptor en Vector | Dimensión Teórica | Tipo de Magnitud | Descripción Operacional |
| :--- | :--- | :--- | :--- |
| `pixel_1` a `pixel_784` | $\mathbb{R}^{784}$ | Escalar Discretizado | Intensidad luminosa de cada celda de la rejilla. Rango nativo en escala de grises de $0$ (ausencia de trazo / fondo) a $255$ (saturación máxima del canal / trazo). |

### Espacio de Etiquetas / Variables de Salida ($y$)
El espacio objetivo asigna una variable categórica codificada numéricamente para cada muestra del sistema:

| Valor Entero ($y$) | Clase Semántica | Condición Topológica Esperada |
| :---: | :--- | :--- |
| **`1`** | Dígito Uno | Densidad de píxeles concentrada en un eje vertical o diagonal simple. |
| **`2`** | Dígito Dos | Transición de curvatura superior con desaceleración horizontal en la base. |
| **`3`** | Dígito Tres | Distribución bimodal de curvas reflexivas simétricas respecto al eje horizontal. |

---

## 3. Caracterización Estructural y Extracción de Patrones Visuales

El análisis geométrico de las matrices de intensidad permite predecir los niveles de activación de los componentes en las capas ocultas:

### Perfil Morfológico del Dígito 1
* **Distribución Espacial:** Exhibe la menor entropía del dataset debido a su simplicidad lineal.
* **Métrica de Activación:** Registra un volumen reducido de píxeles activos (valores $> 0$), concentrándose en una franja vertical central con inclinaciones marginales de entre $5^\circ$ y $15^\circ$.

### Perfil Morfológico del Dígito 2
* **Distribución Espacial:** Presenta una estructura combinada. La sección superior activa un arco continuo que transiciona hacia un vector diagonal con dirección al vértice inferior izquierdo.
* **Métrica de Activación:** Densidad lineal fuertemente marcada en la base horizontal del tensor, generando un patrón característico en las últimas filas de la matriz.

### Perfil Morfológico del Dígito 3
* **Distribución Espacial:** Formado por una secuencia de dos arcos abiertos orientados hacia el margen izquierdo.
* **Métrica de Activación:** Se observa un vacío o baja intensidad en el centro geométrico izquierdo de la imagen, mientras que los cuadrantes superior e inferior derecho muestran una alta concentración de píxeles activos.

---

## 4. Auditoría de Balanceo y Simetría del Ecosistema de Clases

Para evitar sesgos algorítmicos durante la fase de optimización, es indispensable validar que la distribución de frecuencias marginales sea uniforme entre las categorías:

$$P(y=1) \approx P(y=2) \approx P(y=3)$$

Un desbalance crítico en las clases provocaría que el optimizador minimice la función de costo especializándose en la clase mayoritaria. Esto afectaría la capacidad de generalización del clasificador en las clases con menor representación en el dataset.

---

## 5. Matriz de Fricciones y Ruido Topológico (Inconsistencias)

Durante la fase de exploración se identifican cinco factores de riesgo que introducen variabilidad no lineal en el espacio de características:

| Factor de Riesgo | Manifestación en la Matriz | Impacto en el Modelo |
| :--- | :--- | :--- |
| **Solapamiento Morfológico** | Similitud estructural entre las curvas superiores del $2$ y el $3$. | Confusión en las fronteras de decisión de clasificadores lineales. |
| **Degradación de Contraste** | Transiciones borrosas o valores intermedios en los bordes del trazo. | Reduce la nitidez de las características y diluye los gradientes espaciales. |
| **Varianza Estilística** | Variaciones individuales en el grosor, inclinación y florituras del trazo. | Exige una mayor capacidad de generalización en las capas ocultas. |
| **Descentrado del Tensor** | Desplazamiento del centro de masa del dígito respecto al origen $(14, 14)$. | Altera los índices de los píxeles activos, afectando a modelos sin invariancia espacial. |
| **Ruido de Captura** | Artefactos o activaciones aisladas en píxeles periféricos del fondo. | Introduce información irrelevante y componentes de alta frecuencia innecesarios. |

---

## 6. Pipeline de Preprocesamiento de Datos

Con base en las inconsistencias detectadas, se establece un flujo de normalización previo al entrenamiento de los modelos:

1. **Auditoría de Integridad:** Depuración de muestras con inconsistencias entre la matriz visual y su etiqueta asociada.
2. **Normalización del Espacio de Estados:** Transformación lineal de las intensidades para escalar los tensores desde su rango nativo $[0, 255]$ hacia un intervalo acotado de flotantes:
$$X_{\text{norm}} = \frac{X}{255.0} \in [0.0, 1.0]$$
3. **Centrado por Momento Estático:** Ajuste del centro de gravedad de los píxeles activos para estabilizar la posición de los trazos.
4. **Segmentación de Control Cruzado:** División aleatoria del corpus en subconjuntos independientes de entrenamiento (*train*) y prueba (*test*) para garantizar una evaluación objetiva del rendimiento.

---

## 7. Modelos de Clasificación Evaluados

La naturaleza dimensional del problema permite la implementación de diversas familias de algoritmos:

* **Modelos de Distancia de Instancias (KNN):** Útiles para establecer una línea base, aunque su costo computacional escala de forma lineal con el tamaño del dataset.
* **Separadores de Margen Máximo (SVM):** Eficientes en espacios de alta dimensionalidad mediante el uso de funciones kernel para resolver la no linealidad.
* **Modelos Ensamblados (Random Forest):** Robustos ante variaciones menores, aunque propensos a perder la correlación espacial de los píxeles vecinos al aplanar la matriz.
* **Redes Neuronales Convolucionales (CNN):** Representan la opción óptima para este tipo de tareas. Mediante el uso de filtros locales de convolución y operaciones de submuestreo (*pooling*), las CNN logran extraer características complejas conservando la invariancia a la rotación y el desplazamiento de los dígitos.

---

## 8. Conclusiones del Diagnóstico Exploratorio

El análisis exploratorio confirma que el dígito $1$ presenta la menor complejidad estructural, lo que facilitará su separación en las primeras etapas de entrenamiento debido a su perfil lineal característico. Por el contrario, los dígitos $2$ y $3$ comparten subespacios de características comunes en sus zonas curvas, consolidando la principal zona de fricción del dataset. 

La implementación de la normalización a escala $[0.0, 1.0]$ y el uso de arquitecturas convolucionales permitirán capturar estas sutiles diferencias geométricas. Esto mitigará el impacto de los diferentes estilos de escritura y optimizará la precisión general del sistema de clasificación.