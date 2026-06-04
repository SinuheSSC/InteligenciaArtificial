import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración de estilo estético para los gráficos
sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 10, 'figure.titlesize': 12})

# =====================================================================
# 1. GENERACIÓN DE LA SERIE TEMPORAL BASE (SEÑAL SINTÉTICA LIMPIA)
# =====================================================================

np.random.seed(42)

# Muestreo temporal por minuto
vector_tiempo = pd.date_range(start='2026-04-15', periods=500, freq='min')

# Modelado de la señal: Tendencia lineal + Componente sinusoidal + Ruido gaussiano
componente_tendencia = np.linspace(10, 50, 500)
componente_oscilatoria = np.sin(np.linspace(0, 20, 500)) * 5
ruido_blanco = np.random.normal(0, 2, 500)

lecturas_sensor = componente_tendencia + componente_oscilatoria + ruido_blanco

# Construcción e indexación del DataFrame principal
df_telemetria = pd.DataFrame({'Lectura': lecturas_sensor}, index=vector_tiempo)
df_telemetria.index.name = 'Timestamp'

# --- Inspección Gráfica Inicial ---
fig, axes = plt.subplots(1, 2, figsize=(15, 4.5))

# Gráfico de línea temporal (Señal cruda)
axes[0].plot(df_telemetria.index, df_telemetria['Lectura'], color='#1f77b4', linewidth=1.5)
axes[0].set_title("Comportamiento Temporal de la Señal Base")
axes[0].set_xlabel("Línea de Tiempo")
axes[0].set_ylabel("Magnitud / Amplitud")

# Distribución estadística de la densidad
sns.histplot(df_telemetria['Lectura'], kde=True, bins=30, color='#1f77b4', ax=axes[1])
axes[1].set_title("Distribución de Frecuencias (Señal Limpia)")
axes[1].set_xlabel("Rangos de Lectura")
axes[1].set_ylabel("Frecuencia Absoluta")

plt.tight_layout()
plt.show()

print("=== Resumen Estadístico: Fase de Control ===")
print(df_telemetria.describe())
print("-" * 50)


# =====================================================================
# 2. INYECCIÓN CONTROLADA DE ANOMALÍAS E INTERFERENCIAS
# =====================================================================

# Anomalía Tipo A: Evento de Transitorio Crítico (Outliers por pico de voltaje)
df_telemetria.iloc[100:105, 0] = 120.0

# Anomalía Tipo B: Deriva / Congelamiento de Señal (Fallo en sensor / Flatline)
df_telemetria.iloc[250:300, 0] = 30.0

# Anomalía Tipo C: Pérdida de Paquetes de Datos (Apagón de enlace / NaNs)
df_telemetria.iloc[400:420, 0] = np.nan


# =====================================================================
# 3. ANÁLISIS EXPLORATORIO DE DATOS (EDA) SOBRE SEÑAL DEGRADADA
# =====================================================================

# --- Diagnóstico Temporal de Anomalías ---
plt.figure(figsize=(12, 5.5))
plt.plot(df_telemetria.index, df_telemetria['Lectura'], color='#e377c2', linewidth=1.2, label='Señal Degradada')

# Delimitación y etiquetado de zonas críticas de interferencia
plt.axvspan(df_telemetria.index[100], df_telemetria.index[105], color='#ff7f0e', alpha=0.3, label='Zona A: Outliers Estructurales')
plt.axvspan(df_telemetria.index[250], df_telemetria.index[300], color='#bcbd22', alpha=0.2, label='Zona B: Estancamiento (Flatline)')
plt.axvspan(df_telemetria.index[400], df_telemetria.index[420], color='#7f7f7f', alpha=0.25, label='Zona C: Vacíos de Conexión (NaN)')

plt.title("Mapeo y Detección de Anomalías e Inconsistencias en Telemetría")
plt.xlabel("Registro Temporal (HH:MM)")
plt.ylabel("Magnitud del Sensor")
plt.legend(loc='upper left')
plt.grid(True, linestyle=':', alpha=0.6)
plt.tight_layout()
plt.show()

# --- Análisis del Impacto en la Distribución ---
plt.figure(figsize=(7, 4.5))
sns.histplot(df_telemetria['Lectura'].dropna(), kde=True, color='#d62728', bins=35)
plt.title("Deformación de la Densidad por Efecto de Anomalías")
plt.xlabel("Escala de Medición")
plt.ylabel("Frecuencia")
plt.tight_layout()
plt.show()


# =====================================================================
# 4. DIAGNÓSTICO ESTADÍSTICO DE CALIDAD DE DATOS
# =====================================================================

print("=== Perfil de Métricas Estadísticas con Datos Corruptos ===")
print(df_telemetria.describe())
print("\n" + "="*40)
print("Auditoría de Integridad: Conteo de Registros Nulos (NaN)")
print(f"Total de vacíos detectados: {df_telemetria.isnull().sum().values[0]}")
print("="*40)