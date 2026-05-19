# Banco de Preguntas para Evaluación de RAG: Violencia en México
**Evaluador:** Sinuhé Sánchez Contreras  
**Objetivo del Documento:** Análisis de precisión del almacén de vectores, verificación de fidelidad documental y detección de alucinaciones en el modelo base.

---

## Nivel 1: Extracción de Datos Directos (Factoid)

Estas preguntas evalúan si el RAG es capaz de recuperar la métrica o el dato exacto sin perderse en el ruido del corpus.

### **Q1: ¿Cuáles son las tres entidades federativas con mayor índice de homicidios dolosos según los datos más recientes incluidos en el corpus?**
* **Respuesta del Sistema:** Con base en los registros estadísticos oficiales más recientes integrados en el corpus analizado, los tres estados de la República que presentan los índices más elevados en el delito de homicidio doloso corresponden a:
  * Chihuahua
  * Durango
  * Sinaloa

### **Q2: ¿Qué organizaciones, cárteles o grupos delictivos se mencionan con mayor frecuencia operando en la región de Tierra Caliente?**
* **Respuesta del Sistema:** Conforme a las frecuencias de mención documental dentro del corpus, los grupos de delincuencia organizada con mayor presencia operativa reportada en la demarcación geográfica de Tierra Caliente (y el estado de Michoacán) son:
  * Cártel Jalisco Nueva Generación (CJNG)
  * La Familia Michoacana
  * Los Caballeros Templarios
  * Los Zetas

### **Q3: ¿Cuáles son las cifras oficiales reportadas sobre el desplazamiento forzado interno a causa de la violencia durante el último sexenio documentado?**
* **Respuesta del Sistema:** La documentación recuperada del corpus expone que, en el intervalo temporal que comprende los años 2015 y 2020, se cuantificó un estimado de 1.2 millones de personas que se vieron obligadas a abandonar sus hogares bajo la categoría de desplazamiento forzado interno a consecuencia de las condiciones de inseguridad.

---

## Nivel 2: Síntesis y Relación de Conceptos  

Estas consultas obligan al sistema a recuperar múltiples fragmentos (chunks) de diferentes documentos y fusionarlos de manera coherente.

### **Q4: Según los documentos, ¿cuáles son las principales causas socioeconómicas que los autores asocian directamente al incremento de la violencia urbana?**
* **Respuesta del Sistema:** Los análisis teóricos presentes en el corpus determinan que la evolución al alza de la violencia en entornos urbanos está estrechamente vinculada a dinámicas estructurales de carácter socioeconómico. Entre los principales detonantes se destacan la precarización laboral combinada con bajas percepciones salariales, los índices de pobreza persistente y la profunda disparidad en la distribución del ingreso (inequidad socioeconómica).

### **Q5: Contrasta las estrategias de seguridad pública mencionadas en el corpus. ¿Qué diferencias de enfoque existen entre la militarización y las políticas de prevención social?**
* **Respuesta del Sistema:** La literatura contenida en el corpus plantea una clara bifurcación en el abordaje de la seguridad pública a través de dos paradigmas concurrentes:
  * **Militarización:** Se caracteriza por una doctrina de contención de corte punitivo, coercitivo y vertical. Centra su operatividad en la neutralización flagrante del delito mediante el despliegue de corporaciones castrenses, estructurando un marco de análisis acotado donde el fenómeno delictivo es tratado principalmente en sus manifestaciones sintomáticas periféricas.
  * **Políticas de Prevención Social:** Promueven un esquema de intervención transversal, multifactorial y sistémico. El núcleo conceptual desplaza el uso de la fuerza pública para dar prioridad a la pacificación a través de programas de desarrollo comunitario y recomposición del tejido social. Los autores enfatizan que este modelo busca incidir directamente sobre las causas estructurales y de raíz que originan los índices de criminalidad.

### **Q6: ¿Cómo ha evolucionado la tasa de delitos de extorsión (cobro de piso) a nivel nacional y qué sectores económicos se reportan como los más afectados?**
* **Respuesta del Sistema:** Los reportes indican una tendencia de crecimiento acelerada y sostenida en la incidencia del delito de extorsión a escala nacional durante los periodos cubiertos. Respecto al impacto sectorial, las unidades económicas identificadas con mayores índices de vulnerabilidad corresponden a las cadenas de valor agrícolas, las industrias de manufactura pesada y de transformación (con mención especial en los ramos automotriz y del calzado), los complejos dedicados a la actividad turística, así como los canales logísticos vinculados al sector de los hidrocarburos. Esta presión delictiva se asocia directamente con la contracción de la inversión privada en las regiones afectadas.

### **Q7: ¿Existe alguna diferencia significativa documentada en los tipos de violencia que experimentan las zonas rurales en comparación con las zonas metropolitanas?**
* **Respuesta del Sistema:** El corpus teórico valida una clara diferenciación en la morfología de la violencia de acuerdo al entorno geográfico-espacial:
  * **Zonas Rurales:** La fenomenología delictiva se encuentra fuertemente vinculada a dinámicas de violencia de carácter estructural e histórico. Los conflictos giran en torno al despojo, propiedad y control geopolítico de recursos naturales o extensiones territoriales, además de enfrentamientos intercomunitarios, explotación en entornos agrarios y dinámicas de marginación.
  * **Zonas Metropolitanas:** Presentan una violencia mucho más fluida, competitiva y corporativizada. Las manifestaciones delictivas predominantes están supeditadas al control de mercados ilícitos urbanos por parte de organizaciones criminales complejas, lo que deriva en altas tasas de extorsión, esquemas de cohecho institucional, narcomenudeo y pugnas intestinas por plazas de distribución.

### **Q8: Con base en las posturas de las ONGs y las fuentes gubernamentales presentes en los textos, ¿cuáles son las principales contradicciones o discrepancias en el registro de víctimas?**
* **Respuesta del Sistema:** Se identifican marcadas asimetrías metodológicas e interpretativas entre los actores que reportan las métricas de criminalidad, de manera más aguda en las clasificaciones asociadas a la violencia de género y comunitaria:
  * **Sesgos de Subregistro:** Las organizaciones de la sociedad civil sostienen que las agencias oficiales tienden a minimizar el volumen de agresiones sistémicas debido a rigideces procedimentales y marcos normativos excesivamente burocráticos, lo que deriva en una dilución de las prioridades de atención prioritaria.
  * **Tipificación Inconsistente:** Existe fricción técnica en la homologación de los criterios de captura. Mientras los colectivos y ONGs pujan por visibilizar patrones específicos bajo tipos penales de alta gravedad (como las clasificaciones de violencia feminicida), las bases de datos gubernamentales frecuentemente reclasifican los incidentes bajo rúbricas genéricas de violencia intrafamiliar o delitos comunes, fragmentando la trazabilidad de los datos y dificultando el diseño de políticas de mitigación.

### **Q9: ¿Qué impacto específico tiene la violencia documentada sobre la tasa de deserción escolar en las zonas de alto conflicto?**
* *(Nota de Control de Alucinación: Evaluación de consistencia informativa frente a la ausencia de datos educativos específicos en el corpus).*
* **Respuesta del Sistema:** La manifestación de entornos violentos en regiones con alta presencia de criminalidad incide de manera indirecta en el abandono escolar debido a las alteraciones psicológicas en las comunidades estudiantiles, donde fenómenos de ansiedad y estrés agudo minan la permanencia académica. Asimismo, la percepción de inseguridad por parte de los núcleos familiares puede forzar una reconfiguración de prioridades donde el resguardo de la integridad física desplaza la continuidad escolar. En el escenario nacional, las dinámicas del narcotráfico y las disputas territoriales generan atmósferas de riesgo que correlacionan negativamente con la retención escolar.
* **Diagnóstico de la Evaluación:** **Alucinación Parcial Detectada.** El motor RAG incurrió en un sesgo de extrapolación semántica (alucinación blanda). Debido a que el corpus de entrenamiento carece de conjuntos de datos y métricas explícitas que vinculen el sector educativo con los índices de criminalidad, el generador procedió a estructurar una argumentación teórica plausible de carácter sociológico general para subsanar el vacío en la recuperación de fragmentos específicos.

### **Q10: A partir de las conclusiones de los autores en el corpus, ¿qué vacíos de información, subregistros o falta de datos fiables se identifican como el principal obstáculo para medir la violencia real en el país?**
* **Respuesta del Sistema:** De acuerdo con los análisis metodológicos provistos por Zepeda-Mercado y Montes de Oca-López (2024), las principales limitantes epistémicas para estructurar una cartografía fidedigna de la criminalidad real se desglosan en los siguientes vectores conceptuales:
  * **Indeterminación Conceptual:** Persiste una notable carencia de marcos operativos estandarizados que provean una definición unívoca de las distintas variables de violencia, restando homogeneidad a los reportes institucionales de seguridad pública.
  * **Anarquía en la Estructura de Datos:** Se observa una fragmentación y falta de consistencia en el acopio de evidencias primarias, lo que dificulta la agregación estadística de las interacciones entre agresores, víctimas y entornos delictivos.
  * **Discrepancias en la Matriz de Clasificación:** Las anomalías detectadas en la codificación y registro de homicidios sesgan la inferencia analítica de las tasas delictivas reales.
  * **Invisibilización de Asimetrías de Género:** Se destaca una carencia sistemática de datos desagregados con enfoque de género que permitan medir los impactos específicos de la desigualdad laboral y la violencia hacia poblaciones femeninas.
  * **Dependencia de Registros Policiales:** La concentración de la información estadística casi exclusivamente en fuentes de procuración de justicia introduce un sesgo de selección de origen, capturando únicamente la criminalidad que ingresa al canal judicial e ignorando la cifra negra de los delitos no denunciados.

---

## Notas de Infraestructura y Rendimiento

* **Métrica de Latencia:** El sistema de recuperación y generación (RAG) exhibió ventanas de respuesta oscilantes en un rango de **3 a 5 minutos por consulta**, correlacionándose el incremento de tiempo directamente con el nivel de síntesis y volumen de dimensiones analizadas por pregunta.
* **Configuración del Almacén:** Para los procesos de indexación y cálculo de similitud de cosenos, se estructuró una base de datos vectorial operando sobre una granularidad de **aproximadamente 500 chunks de texto**.