**Estudiante:** Sinuhé Sánchez Contreras  

---

## Actividad 1: La Matriz de Atención

Imagina que eres la palabra **COME** y quieres entender qué haces en la oración. Puntúa del 0 al 10 cuánto te “importa” cada palabra para entenderte ($10 = \text{máximo}$).

### Paso 1 — Puntuaciones de Consulta (Query: COME)

| EL | GATO | COME | PESCADO |
| :---: | :---: | :---: | :---: |
| 4 | 8 | 7 | 8 |

### Paso 2 — Normalización Lineal (Mini-Softmax)

| Palabra | Puntuación | Operación ($\div$ Suma) | Porcentaje Estonado ($\approx \%$) |
| :--- | :---: | :---: | :---: |
| **EL** | 4 | $4 \div 27$ | 15% |
| **GATO** | 8 | $8 \div 27$ | 30% |
| **COME** | 7 | $7 \div 27$ | 26% |
| **PESCADO** | 8 | $8 \div 27$ | 30% |
| **Total** | **27** | | **100%** |

### Paso 3 — Interpretación Semántica

* **¿A quién le diste más atención? ¿Tiene sentido para el verbo “come”?** El peso atencional se distribuyó de forma equitativa y con máxima prioridad entre el núcleo del sujeto (**GATO**) y el objeto directo (**PESCADO**). Esta configuración posee total coherencia lingüística, ya que desde la perspectiva del verbo, los componentes críticos para estructurar el contexto de la acción son la entidad ejecutora y el elemento condumio.

* **Si fueras la palabra PESCADO, ¿crees que tu fila de porcentajes sería igual? ¿Por qué sí o por no?** No, la distribución de los coeficientes sufriría una reconfiguración estructural. Bajo el rol del sustantivo objeto, la dependencia inmediata requeriría una vinculación atencional mucho más estrecha hacia la acción rectora (**COME**) para establecer su función sintáctica, mientras que el sujeto original retendría un rol jerárquico secundario pero complementario.

---

## Actividad 2: La Palabra Ambigua (Contextualización)

Análisis del comportamiento semántico del término polisémico **BANCO** bajo entornos adyacentes distintos.

### Escenario A: "FUIMOS AL BANCO DEL RÍO"

* **Suma de puntuaciones vectoriales:** 30

| Palabra | Puntuación | Escalar Relativo | Porcentaje Consolidado |
| :--- | :---: | :---: | :---: |
| **FUIMOS** | 1 | $1 \div 30$ | 3.3% |
| **AL** | 2 | $2 \div 30$ | 6.7% |
| **BANCO** | 10 | $10 \div 30$ | 33.3% |
| **DEL** | 7 | $7 \div 30$ | 23.3% |
| **RÍO** | 10 | $10 \div 30$ | 33.3% |
| **Total** | **30** | | **100%** |

### Escenario B: "FUIMOS AL BANCO A SACAR DINERO"

* **Suma de puntuaciones vectoriales:** 36

| Palabra | Puntuación | Escalar Relativo | Porcentaje Consolidado |
| :--- | :---: | :---: | :---: |
| **FUIMOS** | 1 | $1 \div 36$ | 2.8% |
| **AL** | 2 | $2 \div 36$ | 5.6% |
| **BANCO** | 10 | $10 \div 36$ | 27.8% |
| **A** | 5 | $5 \div 36$ | 13.9% |
| **SACAR** | 8 | $8 \div 36$ | 22.2% |
| **DINERO** | 10 | $10 \div 36$ | 27.8% |
| **Total** | **36** | | **100%** |

### Diagnóstico de Variación Contextual

* **¿En cuál frase BANCO le da más puntos a “RIO” / “DEL”?** En el **Escenario A**, asignando la máxima ponderación a **RÍO**. Este término opera como el anclaje contextual primario que le permite al sistema desambiguar la palabra, determinando que no se refiere a una entidad financiera, sino a un accidente geográfico (borde o ribera).

* **¿En cuál le da más a “DINERO” / “SACAR”?** En el **Escenario B**, focalizándose sólidamente en **DINERO**. La coocurrencia de la secuencia de acciones ligadas al flujo monetario (**SACAR DINERO**) establece de forma unívoca la identidad semántica de la palabra como una institución de crédito.

* **Conclusión operativa (Mecánica Transformer en un máximo de 3 líneas):** Los Transformers procesan el significado de una palabra de manera dinámica en función de la vecindad semántica que la rodea. Así, un mismo token altera su representación vectorial y su relevancia interna según las restricciones de la oración, logrando adaptabilidad contextual adaptativa.

---

## Actividad 3: Máscara Causal (Direccionalidad del Gradiente)

### Matriz de Conectividad Temporal

| Token / Query | EL | GATO | COME | PESCADO |
| :--- | :---: | :---: | :---: | :---: |
| **EL** | | | | |
| **GATO** | ✓ | | | |
| **COME** | ✓ | ✓ | | |
| **PESCADO** | ✓ | ✓ | ✓ | |

* **¿Cuántos $\checkmark$ hay en la fila de la última palabra (PESCADO)?** 3 conexiones activas.
* **¿Cuántos $\checkmark$ hay en la fila de la primera palabra (EL)?** 0 conexiones.

### Análisis Estructural

La distribución triangular inferior conforma la denominada **máscara causal**. Su integración matemática es un requisito estricto en tareas auto-regresivas de generación de lenguaje, ya que prohíbe el acceso de información proveniente de tokens futuros que el sistema aún no ha computado. Al anular algebraicamente estas conexiones, se garantiza que el modelo determine la probabilidad del siguiente elemento basándose exclusivamente en el historial histórico disponible, impidiendo fugas de datos durante la fase de optimización.

---

## Actividad 4: Mecanismo de Atención Múltiple (Multi-Head Attention)

### Configuración de Criterios por Cabeza Atencional

| Cabeza / Head | Dimensión Analítica (Criterio) | MARIA | NO | COMIO | PORQUE | ESTABA | ENFERMA |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **A** | ¿Quién explica la causalidad del evento? | 1 | 2 | 5 | 10 | 8 | 10 |
| **B** | ¿Quién es el agente / sujeto de la acción? | 10 | 2 | 5 | 1 | 1 | 1 |
| **C** | ¿Qué elementos tienen adyacencia al verbo? | 1 | 10 | 5 | 10 | 1 | 1 |

### Distribución de Probabilidades ($Porcentajes \ \mathbf{Softmax}$ por Fila)

| Cabeza | MARIA | NO | COMIO | PORQUE | ESTABA | ENFERMA | Total |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **A** | 2.78% | 5.56% | 13.89% | 27.78% | 22.22% | 27.78% | **100%** |
| **B** | 50.00% | 10.00% | 25.00% | 5.00% | 5.00% | 5.00% | **100%** |
| **C** | 3.57% | 35.71% | 17.86% | 35.71% | 3.57% | 3.57% | **100%** |

### Conclusiones de la Arquitectura

* **¿Las tres filas son iguales?** No. Las distribuciones probabilísticas divergen debido a que cada cabeza de atención opera en un subespacio de proyección ortogonal diferente. Mientras la Cabeza A extrae relaciones lógicas condicionales, la Cabeza B mapea dependencias de rol sintáctico (sujeto) y la Cabeza C atiende a dependencias posicionales inmediatas de la secuencia.

* **¿Qué ventaja tendría ver la frase desde tres criterios y no solo uno?** La integración de múltiples cabezas de atención proporciona representaciones enriquecidas. Al proyectar la secuencia en paralelo bajo diferentes criterios, el sistema previene la pérdida de características globales, logrando consolidar en un único vector de salida la identidad del sujeto, la lógica de la acción y la subordinación causal de forma simultánea.