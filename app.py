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

# 3. PALETA DE COLORES VIRIDIS (índice 0 → NC=3, 1→ NC=4, 2→ NC=6, 3→ NC=8, 4→ NC=12)
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
    
    st.divider()
    st.header("🔍 Ajustes de zoom vertical (gráfica derecha)")
    y_max_zoom = st.slider(
        "Límite superior del eje Y",
        min_value=0.2, max_value=2.0, value=1.1, step=0.05,
        help="Selecciona el valor máximo del eje Y. Valores más bajos amplían la región inferior."
    )
    y_min_zoom = st.slider(
        "Límite inferior del eje Y",
        min_value=0.0, max_value=0.5, value=0.0, step=0.05,
        help="Selecciona el valor mínimo del eje Y (generalmente 0)."
    )
    if st.button("🔄 Restablecer zoom vertical"):
        y_max_zoom = 1.1
        y_min_zoom = 0.0
        st.rerun()

# 5. CÁLCULO PRINCIPAL
relacion_r_R = radio_cation / radio_anion if radio_anion > 0 else 0

# Determinar el NC basado en los límites (corregido)
nc_predicho = NC_TIPICOS[-1]  # 12
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

col_grafica1, col_grafica2 = st.columns(2)

# Rango completo de R (0.1 a 7.0 Å)
R_range_full = [i/100 for i in range(10, 701)]
r_R_range_full = [radio_cation / R if R > 0 else 0 for R in R_range_full]

# --- GRÁFICA 1: Vista completa (corregida) ---
with col_grafica1:
    st.markdown("**Vista completa – modelo extendido**")
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(R_range_full, r_R_range_full, 'b-', linewidth=2.5, label='r/R')
    ax1.axhline(y=relacion_r_R, color='r', linestyle='--', alpha=0.7, linewidth=1.5,
                label=f'Valor actual ({relacion_r_R:.2f})')
    ax1.axvline(x=radio_anion, color='g', linestyle='--', alpha=0.7, linewidth=1.5,
                label=f'R actual ({radio_anion:.2f} Å)')
    
    # --- CORRECCIÓN: Asignación correcta de intervalos y colores ---
    for i, nc in enumerate(NC_TIPICOS):
        y_min = 0 if i == 0 else LIMITES_NC[i-1]
        y_max = LIMITES_NC[i]
        ax1.axhspan(y_min, y_max, alpha=0.25, color=colors[i], label=f'NC {nc}')
    
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

# --- GRÁFICA 2: Vista de zoom (corregida) ---
with col_grafica2:
    st.markdown("**Vista de zoom – análisis detallado (gráfica principal)**")
    
    # Zoom horizontal alrededor de R actual
    margen = 1.0
    x_min = max(0.1, radio_anion - margen)
    x_max = radio_anion + margen
    
    indices = [i for i, R in enumerate(R_range_full) if x_min <= R <= x_max]
    if len(indices) == 0:
        R_range_zoom = [x_min, x_max]
        r_R_range_zoom = [radio_cation / x_min, radio_cation / x_max]
    else:
        R_range_zoom = [R_range_full[i] for i in indices]
        r_R_range_zoom = [r_R_range_full[i] for i in indices]
    
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    
    # Curva azul
    ax2.plot(R_range_zoom, r_R_range_zoom, 'b-', linewidth=2.5, label='r/R')
    ax2.axhline(y=relacion_r_R, color='r', linestyle='--', alpha=0.7, linewidth=1.5,
                label=f'Valor actual ({relacion_r_R:.2f})')
    ax2.axvline(x=radio_anion, color='g', linestyle='--', alpha=0.7, linewidth=1.5,
                label=f'R actual ({radio_anion:.2f} Å)')
    
    # ------------------------------------------------------------------
    # 🟣 TRANSICIÓN 2D → 3D
    # ------------------------------------------------------------------
    R_transicion = radio_cation / 0.225
    if x_min <= R_transicion <= x_max:
        ax2.axvline(x=R_transicion, color='purple', linestyle='-.', linewidth=1.8, alpha=0.9,
                    label=f'Transición 2D/3D (R={R_transicion:.2f} Å)')
    ax2.axhline(y=0.225, color='purple', linestyle='-.', linewidth=1.8, alpha=0.9,
                label='Límite 2D/3D (r/R = 0.225)')
    
    # ------------------------------------------------------------------
    # 🌫️ REGIÓN 2D (NC=3) - Trama gris (exclusiva)
    # ------------------------------------------------------------------
    ax2.axhspan(0.155, 0.225, alpha=0.4, color='#555555', hatch='///', 
                label='Región 2D (NC=3, planar)')
    if y_max_zoom > 0.19:
        ax2.text(x_min + 0.1, 0.19, '2D', fontsize=11, weight='bold', color='white',
                 bbox=dict(boxstyle='round', facecolor='#555555', alpha=0.8))
    
    # ------------------------------------------------------------------
    # 🌈 REGIONES 3D (NC ≥ 4) - VIRIDIS, cada una con su color correcto
    # ------------------------------------------------------------------
    # NC=4  (0.225 - 0.414) -> colors[1]
    ax2.axhspan(0.225, 0.414, alpha=0.35, color=colors[1], label='NC 4')
    # NC=6  (0.414 - 0.732) -> colors[2]
    ax2.axhspan(0.414, 0.732, alpha=0.35, color=colors[2], label='NC 6')
    # NC=8  (0.732 - 1.000) -> colors[3]
    ax2.axhspan(0.732, 1.000, alpha=0.35, color=colors[3], label='NC 8')
    # NC=12 (≥1.000) - solo se dibuja si y_max_zoom > 1.0
    if y_max_zoom > 1.0:
        ax2.axhspan(1.000, y_max_zoom, alpha=0.35, color=colors[4], label='NC 12')
    
    # Etiqueta "3D" en la región de NC=4 (si es visible)
    if y_max_zoom > 0.30:
        ax2.text(x_min + 0.1, 0.30, '3D', fontsize=11, weight='bold', color='white',
                 bbox=dict(boxstyle='round', facecolor=colors[1], alpha=0.8))
    
    # ------------------------------------------------------------------
    # Líneas divisorias y etiquetas
    # ------------------------------------------------------------------
    # Línea negra en r/R=0.155
    ax2.axhline(y=0.155, color='black', linestyle='-', linewidth=1.0, alpha=0.5)
    # Línea negra en r/R=0.225
    ax2.axhline(y=0.225, color='black', linestyle='-', linewidth=1.0, alpha=0.5)
    
    if y_max_zoom > 0.155:
        ax2.text(x_max - 0.05, 0.155, 'NC=3', fontsize=8, color='black',
                 verticalalignment='bottom', horizontalalignment='right')
    if y_max_zoom > 0.225:
        ax2.text(x_max - 0.05, 0.225, 'NC=4', fontsize=8, color='black',
                 verticalalignment='bottom', horizontalalignment='right')
    
    # Líneas punteadas para los demás límites
    for limite in [0.414, 0.732, 1.000]:
        if limite <= y_max_zoom:
            ax2.axhline(y=limite, color='gray', linestyle=':', alpha=0.4, linewidth=0.8)
    
    # Configuración de ejes
    ax2.set_ylim(y_min_zoom, y_max_zoom)
    ax2.set_xlim(x_min, x_max)
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
            '<div style="background-color: #555555; background-image: repeating-linear-gradient(45deg, rgba(255,255,255,0.2) 0px, rgba(255,255,255,0.2) 5px, transparent 5px, transparent 10px); '
            'padding: 15px; border-radius: 5px; text-align: center; color: white;">'
            '<b>NC = 3</b><br>Triangular (2D)</div>',
            unsafe_allow_html=True
        )
    with col_col2:
        st.markdown(
            f'<div style="background-color: rgba{tuple(int(colors[1][j]*255) for j in range(3))+(0.35,)}; '
            f'padding: 15px; border-radius: 5px; text-align: center; color: white;">'
            f'<b>NC = 4</b><br>Tetraédrica</div>',
            unsafe_allow_html=True
        )
    with col_col3:
        st.markdown(
            f'<div style="background-color: rgba{tuple(int(colors[2][j]*255) for j in range(3))+(0.35,)}; '
            f'padding: 15px; border-radius: 5px; text-align: center; color: white;">'
            f'<b>NC = 6</b><br>Octaédrica</div>',
            unsafe_allow_html=True
        )
    with col_col4:
        st.markdown(
            f'<div style="background-color: rgba{tuple(int(colors[3][j]*255) for j in range(3))+(0.35,)}; '
            f'padding: 15px; border-radius: 5px; text-align: center; color: white;">'
            f'<b>NC = 8</b><br>Cúbica</div>',
            unsafe_allow_html=True
        )
    with col_col5:
        st.markdown(
            f'<div style="background-color: rgba{tuple(int(colors[4][j]*255) for j in range(3))+(0.35,)}; '
            f'padding: 15px; border-radius: 5px; text-align: center; color: white;">'
            f'<b>NC = 12</b><br>Compacta</div>',
            unsafe_allow_html=True
        )
    
    st.markdown("""
    **Explicación de la paleta de colores (vista de zoom):**
    - **Gris con rayas diagonales**: región 2D (NC=3, planar).
    - **Viridis (verde-azul)**: regiones 3D (NC≥4). Cada NC tiene su propio tono, siguiendo una gradación.
    - **Líneas púrpura**: límite \( r/R = 0.225 \) y su correspondiente \( R = r/0.225 \).
    - **Líneas negras sólidas**: divisiones entre NC=3 y NC=4.
    """)

# 10. INFORMACIÓN CONTEXTUAL Y TEÓRICA
with st.expander("📚 **Explicación Teórica y Consideraciones**"):
    st.markdown("""
    **Fundamento del modelo**
    - Los **límites** mostrados (0.155, 0.225, 0.414, 0.732) son **umbrales geométricos** derivados de asumir iones como esferas rígidas en contacto.
    
    **Interpretación de la transición 2D → 3D**
    - El valor **`r/R = 0.225`** es el límite inferior para la coordinación tetraédrica (3D) y el superior para la triangular (2D).
    - Para un catión de radio `r` fijo, el tamaño de anión que produce esta transición es **\( R = r / 0.225 \)**.
    - **¡Corrección aplicada!** Ahora cada NC aparece con su color e intervalo correctos.
    
    **Cómo usar los controles de zoom**
    - Reduce el **límite superior del eje Y** (por ejemplo, a 0.5) para **ampliar la zona de NC=3 y NC=4** y apreciar claramente sus franjas.
    """)

# 11. PIE DE PÁGINA
st.caption("App desarrollada con fines académicos por HV Martínez-Tejada. Basado en las reglas de radios de Pauling.")
