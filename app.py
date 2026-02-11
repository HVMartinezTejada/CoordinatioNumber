import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

# 1. CONFIGURACIÓN INICIAL
st.set_page_config(page_title="Simulador r/R - NC", layout="wide")
st.title("📐 Simulador de Relación de Radios y Número de Coordinación")
st.markdown("""
**Teoría:** Esta app visualiza cómo la relación entre el radio del catión (r) y el anión (R) 
determina el número de coordinación (NC) estable en un sólido iónico, asumiendo el modelo de esferas rígidas.
""")

# 2. DEFINICIÓN DE CONSTANTES Y LÍMITES (Reglas de Pauling)
LIMITES_NC = [0.155, 0.225, 0.414, 0.732, 1.000]
NC_TIPICOS = [3, 4, 6, 8, 12]
GEOMETRIAS = ["Triangular", "Tetraédrica", "Octaédrica", "Cúbica", "Cuboctaédrica (Compacta)"]

# 3. PALETA DE COLORES MEJORADA (viridis)
colors = [cm.viridis(i / (len(NC_TIPICOS) - 1)) for i in range(len(NC_TIPICOS))]

# 4. INTERFAZ DE USUARIO (Sidebar para Controles)
with st.sidebar:
    st.header("⚙️ Controles de los Radios Iónicos")
    st.caption("Ajusta los valores en Ångströms (Å).")
    
    radio_cation = st.slider(
        "Radio del Catión (r) [Å]",
        min_value=0.1, max_value=2.0, value=1.0, step=0.01,
        help="Selecciona el radio del catión central. Este valor permanecerá constante."
    )
    
    radio_anion = st.slider(
        "Radio del Anión (R) [Å]",
        min_value=0.1, max_value=7.0, value=1.4, step=0.01,
        help="Varía este control para simular aniones de diferente tamaño. Observa cómo cambia r/R y el NC."
    )

# 5. CÁLCULO PRINCIPAL
relacion_r_R = radio_cation / radio_anion if radio_anion > 0 else 0

# Determinar el NC basado en los límites
nc_predicho = NC_TIPICOS[-1]
geometria_predicha = GEOMETRIAS[-1]

for i, limite in enumerate(LIMITES_NC):
    if relacion_r_R < limite:
        nc_predicho = NC_TIPICOS[i]
        geometria_predicha = GEOMETRIAS[i]
        break

# 6. VISUALIZACIÓN DE RESULTADOS
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Relación r/R", value=f"{relacion_r_R:.3f}")
with col2:
    st.metric(label="Número de Coordinación (NC)", value=nc_predicho)
with col3:
    st.metric(label="Geometría", value=geometria_predicha)

# 7. BARRA DE PROGRESO/INDICADOR VISUAL
st.subheader("📊 Umbrales de Estabilidad para cada NC")
df_limites = pd.DataFrame({
    "NC": NC_TIPICOS,
    "Geometría": GEOMETRIAS,
    "Límite inferior r/R": LIMITES_NC
})
st.dataframe(df_limites, use_container_width=True, hide_index=True)

st.markdown(f"**Posición actual de r/R ({relacion_r_R:.3f}) en la escala:**")
posicion_relativa = min(relacion_r_R / 1.1, 1.0)
st.progress(posicion_relativa)

marcadores = " | ".join([f"{limite:.3f} (NC={nc})" for limite, nc in zip(LIMITES_NC, NC_TIPICOS)])
st.caption(f"**Límites:** {marcadores}")

# 8. GRÁFICOS INTERACTIVOS
st.subheader("📈 Relación entre R y r/R")

# Crear dos columnas para las gráficas
col_grafica1, col_grafica2 = st.columns(2)

# Rango completo de R para las gráficas (de 0.1 a 7.0 Å)
R_range_full = [i/100 for i in range(10, 701)]  # 0.1 a 7.0
r_R_range_full = [radio_cation / R if R > 0 else 0 for R in R_range_full]

# --- GRÁFICA 1: Vista completa (rango total de R) ---
with col_grafica1:
    st.markdown("**Vista completa – modelo extendido**")
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(R_range_full, r_R_range_full, 'b-', linewidth=2.5, label='r/R')
    ax1.axhline(y=relacion_r_R, color='r', linestyle='--', alpha=0.7, linewidth=1.5,
                label=f'Valor actual ({relacion_r_R:.2f})')
    ax1.axvline(x=radio_anion, color='g', linestyle='--', alpha=0.7, linewidth=1.5,
                label=f'R actual ({radio_anion:.2f} Å)')
    
    # Añadir regiones sombreadas para los NC (solo hasta r/R = 1.0)
    for i in range(len(LIMITES_NC)):
        y_min = 0 if i == 0 else LIMITES_NC[i-1]
        y_max = LIMITES_NC[i]
        ax1.axhspan(y_min, y_max, alpha=0.25, color=colors[i], label=f'NC {NC_TIPICOS[i]}')
    
    # NOTA SOBRE LA VALIDEZ FÍSICA: se añade texto en la gráfica
    ax1.text(0.98, 0.02,
             "Nota: Esta región (r/R > 1.2) es\nmatemáticamente correcta pero\nfísicamente no aplicable al modelo\nde esferas rígidas.",
             transform=ax1.transAxes,
             fontsize=9,
             verticalalignment='bottom',
             horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    ax1.set_xlabel('Radio del Anión (R) [Å]', fontsize=12)
    ax1.set_ylabel('Relación r/R', fontsize=12)
    ax1.set_title(f'Variación de r/R para r = {radio_cation} Å constante', fontsize=14, pad=15)
    ax1.legend(loc='upper right', fontsize=8)
    ax1.grid(alpha=0.3)
    st.pyplot(fig1)

# --- GRÁFICA 2: Vista de zoom dinámico alrededor de R actual ---
with col_grafica2:
    st.markdown("**Vista de zoom – análisis detallado (gráfica principal)**")
    
    # Definir límites dinámicos para el eje X alrededor de R actual
    margen = 1.0  # margen en Å a cada lado
    x_min = max(0.1, radio_anion - margen)
    x_max = radio_anion + margen
    
    # Filtrar los datos dentro del rango X seleccionado
    indices = [i for i, R in enumerate(R_range_full) if x_min <= R <= x_max]
    if len(indices) == 0:
        # Si no hay datos, usar todo el rango pequeño
        R_range_zoom = [x_min, x_max]
        r_R_range_zoom = [radio_cation / x_min, radio_cation / x_max]
    else:
        R_range_zoom = [R_range_full[i] for i in indices]
        r_R_range_zoom = [r_R_range_full[i] for i in indices]
    
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    ax2.plot(R_range_zoom, r_R_range_zoom, 'b-', linewidth=2.5, label='r/R')
    ax2.axhline(y=relacion_r_R, color='r', linestyle='--', alpha=0.7, linewidth=1.5,
                label=f'Valor actual ({relacion_r_R:.2f})')
    ax2.axvline(x=radio_anion, color='g', linestyle='--', alpha=0.7, linewidth=1.5,
                label=f'R actual ({radio_anion:.2f} Å)')
    
    # Añadir regiones sombreadas para los NC (solo hasta r/R = 1.0)
    for i in range(len(LIMITES_NC)):
        y_min = 0 if i == 0 else LIMITES_NC[i-1]
        y_max = LIMITES_NC[i]
        ax2.axhspan(y_min, y_max, alpha=0.25, color=colors[i], label=f'NC {NC_TIPICOS[i]}')
    
    # Límites del eje Y fijos (zoom vertical)
    ax2.set_ylim(0, 1.1)
    # Límites del eje X dinámicos
    ax2.set_xlim(x_min, x_max)
    
    # Líneas auxiliares en los límites de NC
    for limite in LIMITES_NC:
        ax2.axhline(y=limite, color='gray', linestyle=':', alpha=0.4, linewidth=0.8)
    
    ax2.set_xlabel('Radio del Anión (R) [Å]', fontsize=12)
    ax2.set_ylabel('Relación r/R', fontsize=12)
    ax2.set_title(f'Zoom centrado en R = {radio_anion:.2f} Å', fontsize=14, pad=15)
    ax2.legend(loc='upper right', fontsize=8)
    ax2.grid(alpha=0.3)
    st.pyplot(fig2)

# 9. LEYENDA EXPLICATIVA DE COLORES
with st.expander("🎨 Guía de colores para los Números de Coordinación"):
    col_col1, col_col2, col_col3, col_col4, col_col5 = st.columns(5)
    
    with col_col1:
        st.markdown(
            f'<div style="background-color: rgba{tuple(int(colors[0][j]*255) for j in range(3))+(0.25,)}; '
            f'padding: 15px; border-radius: 5px; text-align: center;">'
            f'<b>NC = 3</b><br>Triangular</div>',
            unsafe_allow_html=True
        )
    with col_col2:
        st.markdown(
            f'<div style="background-color: rgba{tuple(int(colors[1][j]*255) for j in range(3))+(0.25,)}; '
            f'padding: 15px; border-radius: 5px; text-align: center;">'
            f'<b>NC = 4</b><br>Tetraédrica</div>',
            unsafe_allow_html=True
        )
    with col_col3:
        st.markdown(
            f'<div style="background-color: rgba{tuple(int(colors[2][j]*255) for j in range(3))+(0.25,)}; '
            f'padding: 15px; border-radius: 5px; text-align: center;">'
            f'<b>NC = 6</b><br>Octaédrica</div>',
            unsafe_allow_html=True
        )
    with col_col4:
        st.markdown(
            f'<div style="background-color: rgba{tuple(int(colors[3][j]*255) for j in range(3))+(0.25,)}; '
            f'padding: 15px; border-radius: 5px; text-align: center;">'
            f'<b>NC = 8</b><br>Cúbica</div>',
            unsafe_allow_html=True
        )
    with col_col5:
        st.markdown(
            f'<div style="background-color: rgba{tuple(int(colors[4][j]*255) for j in range(3))+(0.25,)}; '
            f'padding: 15px; border-radius: 5px; text-align: center;">'
            f'<b>NC = 12</b><br>Compacta</div>',
            unsafe_allow_html=True
        )
    
    st.markdown("""
    **Explicación de la paleta de colores:**
    - Se utiliza una paleta **viridis** (escala secuencial) que asigna colores más oscuros a números de coordinación bajos y colores más claros a números de coordinación altos.
    - Esta gradación visual ayuda a intuir la progresión del NC a medida que aumenta la relación r/R.
    """)

# 10. INFORMACIÓN CONTEXTUAL Y TEÓRICA
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

# 11. PIE DE PÁGINA
st.caption("App desarrollada con fines académicos por HV Martínez-Tejada. Basado en las reglas de radios de Pauling.")
