# Análisis Exploratorio de Datos (EDA): Mapeo de Telemetría de Disparo y Comportamiento Neuronal

**Estudiante:** Sinuhé Sánchez Contreras  
**Repositorio / Script Base:** `juego_pygame_mlp1.py`  
**Objetivo Metodológico:** Analizar la estructura de los datos recolectados por el entorno interactivo en Pygame antes de alimentar el clasificador basado en una red neuronal Perceptrón Multicapa (MLP), evaluando la física del entorno, la consistencia de las clases y los costos de memoria del dataset.

---

## 1. Descripción del Problema y Mecánica del Entorno

El script implementa un entorno interactivo en dos dimensiones donde un agente (jugador) debe mitigar colisiones contra un proyectil (bala) disparado desde una nave nodriza. Para evadir la colisión con éxito, el sistema captura variables físicas continuas en tiempo real y requiere mapearlas a una de tres respuestas motrices discretas (clases de salida).

### Flujo de Simulación y Toma de Acciones
1. **Detección Espacial:** La bala se genera en el extremo derecho de la pantalla con una velocidad horizontal negativa aleatoria.
2. **Segmentación de Alturas:** El proyectil es asignado aleatoriamente a uno de tres carriles físicos continuos.
3. **Mapeo de Respuestas Excluyentes:** * Si la trayectoria intersecta las extremidades inferiores del agente (**Carril Bajo**), la única acción evasiva válida es ejecutar un vector de fuerza vertical hacia arriba (**Saltar**).
   * Si el proyectil compromete el torso (**Carril Medio**), la física del juego exige reducir el volumen del cuadro de colisión a la mitad (**Agacharse**).
   * Si el proyectil viaja sobre la corona del agente (**Carril Alto**), la inercia es la opción óptima (**Quedarse quieto / Nada**).

---

## 2. Objetivo del Análisis Exploratorio (EDA)

El propósito fundamental de este EDA es auditar la calidad, distribución y separabilidad lineal de los datos recopilados durante la fase manual. Este análisis previo garantiza:
* Verificar que las variables cinemáticas (`velocidad_bala`, `distancia`, `bala_y`) tengan suficiente poder predictivo para delimitar las fronteras de decisión del modelo.
* Validar que el mecanismo de agregación temporal por "buckets" (moda estadística por distancias) refleje fielmente las intenciones de evasión del usuario sin introducir ruido o retrasos (*lags*) en el dataset.

---

## 3. Estructura y Perfil del Dataset

El sistema captura la telemetría del entorno cuadro por cuadro (*frame-by-frame*) durante la ejecución del bucle interactivo. Los datos extraídos se estructuran de la siguiente manera:

### Espacio de Características / Variables de Entrada ($X$)

| Parámetro Teórico | Variable en Código | Naturaleza Matemática | Descripción Operacional |
| :--- | :--- | :--- | :--- |
| **Velocidad de la Bala** | `velocidad_bala` | Escalar Continuo ($\mathbb{R}$) | Velocidad de aproximación horizontal del proyectil. Rango dinámico escalado entre -12 y -6 píxeles por frame. |
| **Distancia Relativa** | `distancia` | Escalar Continuo ($\mathbb{R}^+$) | Distancia euclidiana en el eje X entre el borde del agente y la coordenada actual del proyectil. |
| **Posición Vertical Relativa** | `bala_y_rel` | Escalar Continuo ($\mathbb{R}$) | Altura calculada mediante la diferencia formal respecto al plano del suelo del entorno (`ground_y - bala.y`). |

### Espacio de Etiquetas / Variables de Salida ($y$)

La variable objetivo se encuentra codificada de forma categórica discreta mediante un mapeo entero de tres clases posibles:

| Valor Entero ($y$) | Etiqueta en Script | Acción Semántica | Condición Física de Éxito |
| :---: | :--- | :--- | :--- |
| **`0`** | `CARRIL_ALTO` | Nada / Quieto | El proyectil sobrevuela al agente (`bala.y` en cota superior). |
| **`1`** | `CARRIL_BAJO` | Saltar | Modificación temporal de la coordenada `jugador.y` mediante parábola de gravedad. |
| **`2`** | `CARRIL_MEDIO` | Agacharse | Reducción instantánea de la altura del cuadro de colisión a $h/2$. |

---

## 4. Análisis Geométrico de los Carriles y Fronteras de Decisión

La altura relativa de la bala (`bala_y_rel`) es el descriptor de mayor peso lineal para la segregación de clases, ya que mapea directamente la geometría de los carriles calculados por el método `_y_para_carril`.

[Carril Alto]   ─── Envolvente Superior (h_jugador + 8px) ───> Acción: 0 (Nada)
[Carril Medio]  ─── Mitad del Torso (h_normal // 2)      ───> Acción: 2 (Agacharse)
[Carril Bajo]   ─── Nivel del Suelo (Sustracción de h)   ───> Acción: 1 (Saltar)
====================== LINEA DEL SUELO (ground_y) ======================


Esta separación geométrica estricta implica que, en condiciones ideales, el espacio de características con respecto a `bala_y_rel` es altamente separable. No obstante, las variables `distancia` y `velocidad_bala` introducen la dimensión temporal: si la velocidad es máxima y la distancia es mínima, el tiempo de cómputo del modelo o de reacción del humano puede retrasar la transición de la etiqueta, generando zonas de solapamiento en las fronteras de clasificación.

---

## 5. Análisis de Distribución Espacio-Temporal: El Impacto de la Velocidad

La velocidad del proyectil afecta drásticamente la tasa de recolección de muestras. Al operar el bucle a una frecuencia fija de **45 Hz** (`reloj.tick(45)`), la velocidad dicta el tamaño del dataset de forma indirecta:

* **Proyectiles de Baja Velocidad (-6 px/frame):** El proyectil permanece más tiempo suspendido en el espacio de juego, permitiendo al método `registrar_decision_manual` capturar un mayor volumen de muestras continuas por cada disparo.
* **Proyectiles de Alta Velocidad (-12 px/frame):** Reducen a la mitad las ventanas temporales de muestreo, compactando las observaciones en el eje de la distancia y exigiendo una mayor velocidad de respuesta por parte del usuario.

---

## 6. Auditoría de Calidad y Sesgos en los Datos (Análisis de Inconsistencias)

Durante la inspección de la telemetría grabada en el manual, se identifican tres fenómenos críticos que alteran la distribución normal del dataset:

### 1. El Fenómeno del Historial de Transición (*Lag* Humano)
Cuando el jugador decide presionar la tecla `ESPACIO` o `FLECHA ABAJO`, el proyectil ya ha recorrido una distancia determinada. Esto significa que para un mismo carril (por ejemplo, Carril Bajo), existirán registros donde el agente estaba en el suelo (`accion: 0`) a distancias lejanas, y registros con la acción activa (`accion: 1` o `2`) a distancias cercanas. El modelo de aprendizaje profundo debe aprender a identificar este umbral exacto de distancia crítica de activación.

### 2. Desbalanceo Crítico de Clases por Inercia
Si el jugador decide realizar una sesión de entrenamiento estática (sin presionar ningún comando de control), el sistema registrará de forma masiva muestras con la etiqueta `0` (Nada). Al intentar ejecutar el método `entrenar_modelo()`, el módulo `sklearn` activará la salvaguarda de **Clase Única** (`self.clase_unica`), generando un modelo trivial que perderá la capacidad predictiva generalizada del clasificador neuronal.

### 3. Discretización por Modas (*Timeline Buckets*)
El script implementa una técnica de suavizado de datos mediante la agrupación en contenedores de distancia (`BUCKET_SIZE = 20`). Al aplicar una función de moda estadística (`Counter(acciones).most_common(1)`), se eliminan de forma deliberada las fluctuaciones menores del operador humano (peticiones erróneas o retrasos accidentales). Este proceso actúa como un filtro de paso bajo que regulariza el ruido antes de mapear la trayectoria en el modo automático.

---

## 7. Análisis de la Gráfica y Visualización del Espacio de Características

El script integra soporte directo para la proyección de gráficos en entornos bidimensionales y tridimensionales mediante `matplotlib`, lo que permite un diagnóstico visual inmediato del estado del dataset.

### Inspección en el Espacio 2D (`distancia` vs. `velocidad_bala`)
Al invocar `graficar_datos_2d`, se mapea la distribución de las maniobras de evasión ignorando temporalmente la altura. Esto permite evaluar si el usuario altera su distancia de reacción en función de la velocidad de la bala. En un dataset sano, se observa un desplazamiento de los cúmulos de color (rojo y verde) hacia la derecha cuando la velocidad es mayor, reflejando que el usuario reacciona antes ante amenazas más rápidas.

### Proyección del Gradiente Temporal en 3D (`distancia` vs. `velocidad_bala` vs. `Tiempo`)
El método `graficar_datos_3d` sustituye la cota de altura por un eje Z sintético basado en el índice cronológico de las muestras. Esta representación gráfica permite:
* Evaluar el desgaste o la fatiga del usuario a lo largo de la sesión de juego.
* Monitorear la evolución temporal de los criterios de evasión.
* Identificar visualmente la densidad de muestras recolectadas, asegurando que se cumpla con el umbral mínimo de diseño fijado en **$N \ge 80$ observaciones** previo a la optimización del perceptrón.

---

## 8. Conclusión del Diagnóstico

El entorno propuesto reduce un problema cinemático continuo a una tarea de **clasificación supervisada multiclase**. La variable de cota vertical `bala_y_rel` establece de forma lineal la acción básica, mientras que el binomio integrado por la velocidad y la distancia define la ventana crítica de activación. 

El uso del suavizado por bloques (*buckets*) de 20 píxeles ayuda a mitigar las inconsistencias en el tiempo de reacción del usuario. Esto estabiliza las predicciones de la red neuronal y permite que el Perceptrón Multicapa (MLM) configure fronteras de decisión robustas cuando el juego pasa al modo automatizado.