import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 1. CONFIGURACIÓN INICIAL
st.set_page_config(page_title="Simulador r/R - NC", layout="wide")
st.title("📐 Simulador de Relación de Radios y Número de Coordinación")
st.markdown("""
**Teoría:** Esta app visualiza cómo la relación entre el radio del catión (r) y el anión (R) 
determina el número de coordinación (NC) estable en un sólido iónico, asumiendo el modelo de esferas rígidas.
""")

# 2. DEFINICIÓN DE CONSTANTES Y LÍMITES (Reglas de Pauling)
# Límites inferiores para cada NC. Orden: Triangular, Tetraédrico, Octaédrico, Cúbico, Compacto.
LIMITES_NC = [0.155, 0.225, 0.414, 0.732, 1.000]
NC_TIPICOS = [3, 4, 6, 8, 12]
GEOMETRIAS = ["Triangular", "Tetraédrica", "Octaédrica", "Cúbica", "Cuboctaédrica (Compacta)"]

# 3. INTERFAZ DE USUARIO (Sidebar para Controles)
with st.sidebar:
    st.header("⚙️ Controles de los Radios Iónicos")
    st.caption("Ajusta los valores en Ångströms (Å).")
    
    # Radio del catión (r) - Fijo para esta simulación
    radio_cation = st.slider(
        "Radio del Catión (r) [Å]",
        min_value=0.1, max_value=2.0, value=1.0, step=0.01,
        help="Selecciona el radio del catión central. Este valor permanecerá constante."
    )
    
    # Radio del anión (R) - Variable principal
    radio_anion = st.slider(
        "Radio del Anión (R) [Å]",
        min_value=0.1, max_value=2.5, value=1.4, step=0.01,
        help="Varía este control para simular aniones de diferente tamaño. Observa cómo cambia r/R y el NC."
    )

# 4. CÁLCULO PRINCIPAL
relacion_r_R = radio_cation / radio_anion if radio_anion > 0 else 0

# Determinar el NC basado en los límites
nc_predicho = NC_TIPICOS[-1]  # Por defecto, el mayor (12)
geometria_predicha = GEOMETRIAS[-1]

for i, limite in enumerate(LIMITES_NC):
    if relacion_r_R < limite:
        nc_predicho = NC_TIPICOS[i]
        geometria_predicha = GEOMETRIAS[i]
        break

# 5. VISUALIZACIÓN DE RESULTADOS
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Relación r/R", value=f"{relacion_r_R:.3f}")
with col2:
    st.metric(label="Número de Coordinación (NC)", value=nc_predicho)
with col3:
    st.metric(label="Geometría", value=geometria_predicha)

# 6. BARRA DE PROGRESO/INDICADOR VISUAL
st.subheader("📊 Umbrales de Estabilidad para cada NC")
# Crear un DataFrame para los límites
df_limites = pd.DataFrame({
    "NC": NC_TIPICOS,
    "Geometría": GEOMETRIAS,
    "Límite inferior r/R": LIMITES_NC
})

# Mostrar la tabla de referencia
st.dataframe(df_limites, use_container_width=True, hide_index=True)

# Indicador visual de en qué rango se encuentra la relación actual
st.markdown(f"**Posición actual de r/R ({relacion_r_R:.3f}) en la escala:**")
# Crear una barra de progreso conceptual
posicion_relativa = min(relacion_r_R / 1.1, 1.0)  # Normalizar a ~1.1 para visualización
st.progress(posicion_relativa)

# Marcadores para los límites en la barra (usando HTML/CSS simple o texto)
marcadores = " | ".join([f"{limite:.3f} (NC={nc})" for limite, nc in zip(LIMITES_NC, NC_TIPICOS)])
st.caption(f"**Límites:** {marcadores}")

# 7. GRÁFICOS INTERACTIVOS - MODIFICACIÓN PRINCIPAL (2 gráficas)
st.subheader("📈 Relación entre R y r/R")

# Crear dos columnas para las gráficas
col_grafica1, col_grafica2 = st.columns(2)

# Crear un rango de valores de R para el gráfico
R_range = [i/100 for i in range(10, 251)]  # De 0.1 a 2.5 Å
r_R_range = [radio_cation / R if R > 0 else 0 for R in R_range]

# Colores para las regiones de NC
colors = ['#FFDDDD', '#DDEEDD', '#DDDDFF', '#F0E6DD', '#F5DDEC']

# --- GRÁFICA 1: Vista completa (original) ---
with col_grafica1:
    st.markdown("**Vista completa**")
    fig1, ax1 = plt.subplots()
    ax1.plot(R_range, r_R_range, 'b-', linewidth=2, label='r/R')
    ax1.axhline(y=relacion_r_R, color='r', linestyle='--', alpha=0.5, label=f'Valor actual ({relacion_r_R:.2f})')
    ax1.axvline(x=radio_anion, color='g', linestyle='--', alpha=0.5, label=f'R actual ({radio_anion:.2f} Å)')
    
    # Añadir regiones sombreadas para los NC
    for i in range(len(LIMITES_NC)):
        y_min = 0 if i == 0 else LIMITES_NC[i-1]
        y_max = LIMITES_NC[i]
        ax1.axhspan(y_min, y_max, alpha=0.2, color=colors[i], label=f'NC {NC_TIPICOS[i]}')
    
    ax1.set_xlabel('Radio del Anión (R) [Å]')
    ax1.set_ylabel('Relación r/R')
    ax1.set_title(f'Variación de r/R para r = {radio_cation} Å constante')
    ax1.legend(loc='upper right')
    ax1.grid(alpha=0.3)
    st.pyplot(fig1)

# --- GRÁFICA 2: Vista de zoom (0 a 1.1 en eje Y) ---
with col_grafica2:
    st.markdown("**Vista de zoom (r/R: 0 a 1.1)**")
    fig2, ax2 = plt.subplots()
    ax2.plot(R_range, r_R_range, 'b-', linewidth=2, label='r/R')
    ax2.axhline(y=relacion_r_R, color='r', linestyle='--', alpha=0.5, label=f'Valor actual ({relacion_r_R:.2f})')
    ax2.axvline(x=radio_anion, color='g', linestyle='--', alpha=0.5, label=f'R actual ({radio_anion:.2f} Å)')
    
    # Añadir regiones sombreadas para los NC (mismo código)
    for i in range(len(LIMITES_NC)):
        y_min = 0 if i == 0 else LIMITES_NC[i-1]
        y_max = LIMITES_NC[i]
        ax2.axhspan(y_min, y_max, alpha=0.2, color=colors[i], label=f'NC {NC_TIPICOS[i]}')
    
    # CONFIGURACIÓN DEL ZOOM: Establecer límites del eje Y
    ax2.set_ylim(0, 1.1)  # Esta es la línea clave para el zoom
    
    ax2.set_xlabel('Radio del Anión (R) [Å]')
    ax2.set_ylabel('Relación r/R')
    ax2.set_title(f'Zoom: r/R entre 0 y 1.1')
    ax2.legend(loc='upper right')
    ax2.grid(alpha=0.3)
    st.pyplot(fig2)

# 8. INFORMACIÓN CONTEXTUAL Y TEÓRICA
with st.expander("📚 **Explicación Teórica y Consideraciones**"):
    st.markdown("""
    **Fundamento del modelo**
    - Los **límites** mostrados (0.155, 0.225, 0.414, 0.732) son **umbrales geométricos** derivados de asumir iones como esferas rígidas en contacto.
    - Cada límite inferior representa la **relación mínima** `r/R` a la que el catión puede tocar a todos los aniones que lo rodean en esa geometría.
    
    **Interpretación de los resultados**
    - Cuando `r/R` es **menor** que el límite para un NC, el catión es "demasiado pequeño" para esa geometría. Estructuralmente, tenderá a adoptar un NC **menor** (con menos vecinos).
    - Cuando `r/R` está **dentro** de un intervalo, esa geometría es **geométricamente estable** (los iones se tocan sin superponerse).
    - Un `r/R > 1` solo es posible si el catión es **mayor** que el anión (poco común en sólidos iónicos puros).
    
    **Limitaciones importantes del modelo simplificado**
    1.  **Iones no esféricos**: Los iones reales pueden polarizarse (deformarse).
    2.  **Carácter covalente**: El enlace químico puede tener direccionalidad, invalidando la predicción puramente geométrica.
    3.  **Factores energéticos**: La estabilidad real depende de la energía total de red, no solo del contacto geométrico.
    
    **Ejemplo clásico**: Para `r/R ≈ 0.55` (ej. NaCl), la app predice NC=6 (octaédrica), ¡que es correcta!
    """)

# 9. PIE DE PÁGINA - MODIFICACIÓN SOLICITADA
st.caption("App desarrollada con fines académicos por HV Martínez-Tejada. Basado en las reglas de radios de Pauling.")
