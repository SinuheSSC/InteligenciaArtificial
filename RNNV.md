# Inteligencia Artificial
# Actividad: RNN Básica Vanilla
**Autor de la analogía:** Eduardo Alcaraz  
**Alumno:** Sinuhe Sánchez Contreras  
**Concepto:** El Termómetro de las Emociones

---

## Introducción Matemática
Para resolver estas misiones, utilizaremos la fórmula simplificada de una unidad recurrente (RNN Vanilla), donde el estado actual ($h_t$) depende de la entrada de hoy ($x_t$) y una fracción de la memoria de ayer ($h_{t-1}$).

**Fórmula:** $$h_t = x_t + (w \cdot h_{t-1})$$

*Donde establecemos $w = 0.5$ (50% de retención) según las instrucciones de la actividad.*

---

## Misión 1: El Lunes Increíble (Desvanecimiento)
**Objetivo:** Observar cómo se diluye un impacto emocional fuerte con el paso de los días neutros.

| Día | Entrada ($x_t$) | Operación: $x_t + 0.5(h_{t-1})$ | Estado Final ($h_t$) |
| :--- | :--- | :--- | :--- |
| Día 1 (Lunes) | +10 | $10 + 0.5(0)$ | **10.0** |
| Día 2 | 0 | $0 + 0.5(10)$ | **5.0** |
| Día 3 | 0 | $0 + 0.5(5)$ | **2.5** |
| Día 4 | 0 | $0 + 0.5(2.5)$ | **1.25** |
| **Día 5 (Viernes)** | 0 | $0 + 0.5(1.25)$ | **0.625** |

**Conclusión:** Al llegar al viernes, el estado emocional es de apenas **0.625**. El evento positivo del lunes se ha desvanecido casi por completo debido a la falta de nuevos estímulos.

---

## Misión 2: El Rescate Emocional (Superando el Pasado)
**Objetivo:** Calcular la magnitud necesaria para revertir una memoria negativa acumulada.

1. **Día 1 (Enfermedad):** $h_1 = -6 + 0.5(0) = -6$
2. **Día 2 (Regaño):** $h_2 = -4 + 0.5(-6) = -7$
3. **Día 3 (Rutina):** $h_3 = 0 + 0.5(-7) = -3.5$

**Cálculo para el Día 4:**
Para que el estado final sea positivo ($h_4 > 0$), planteamos la inecuación:
$$x_4 + 0.5(-3.5) > 0$$
$$x_4 - 1.75 > 0$$
$$x_4 > 1.75$$

**Resultado:** El evento del Día 4 debe tener una magnitud **mayor a +1.75** para que el estado de ánimo logre ser positivo.

---

## Misión 3: Constancia vs. El Pico
**Objetivo:** Comparar la retención de información aislada frente a la información constante.

### Escenario A: Un pico el Día 1
* Día 1: +10
* Días 2 al 5: 0
* **Estado Final Día 5:** **0.625**

### Escenario B: Pequeñas alegrías constantes
| Día | Entrada ($x_t$) | Operación | Estado ($h_t$) |
| :--- | :--- | :--- | :--- |
| Día 1 | +3 | $3 + 0$ | 3.0 |
| Día 2 | +3 | $3 + 1.5$ | 4.5 |
| Día 3 | +3 | $3 + 2.25$ | 5.25 |
| Día 4 | +3 | $3 + 2.625$ | 5.625 |
| **Día 5** | +3 | $3 + 2.8125$ | **5.8125** |

### Comparativa Final
* **Estado Final A:** 0.625
* **Estado Final B:** 5.8125

**Análisis:** La Vanilla RNN recuerda mucho mejor la información reciente y constante. Aunque el "pico" inicial del Escenario A fue mucho más alto (+10 vs +3), la constancia del Escenario B permite acumular y mantener un estado mucho más elevado hacia el final de la secuencia.