import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm

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

# 3. PALETA DE COLORES MEJORADA
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
    
    # MODIFICACIÓN PRINCIPAL: max_value cambiado de 2.5 a 7.0
    radio_anion = st.slider(
        "Radio del Anión (R) [Å]",
        min_value=0.1, max_value=7.0, value=1.4, step=0.01,  # ← LÍNEA MODIFICADA
        help="Varía este control para simular aniones de diferente tamaño. Observa cómo cambia r/R y el NC."
    )

# 5. CÁLCULO PRINCIPAL
relacion_r_R = radio_cation / radio_anion if radio_anion > 0 else 0

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
col_grafica1, col_grafica2 = st.columns(2)

# MODIFICACIÓN SECUNDARIA: Rango extendido para R (hasta 7.0 Å)
R_range = [i/100 for i in range(10, 701)]  # De 0.1 a 7.0 Å (antes 2.5 Å)
r_R_range = [radio_cation / R if R > 0 else 0 for R in R_range]

with col_grafica1:
    st.markdown("**Vista completa**")
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(R_range, r_R_range, 'b-', linewidth=2.5, label='r/R')
    ax1.axhline(y=relacion_r_R, color='r', linestyle='--', alpha=0.7, linewidth=1.5, 
                label=f'Valor actual ({relacion_r_R:.2f})')
    ax1.axvline(x=radio_anion, color='g', linestyle='--', alpha=0.7, linewidth=1.5, 
                label=f'R actual ({radio_anion:.2f} Å)')
    
    for i in range(len(LIMITES_NC)):
        y_min = 0 if i == 0 else LIMITES_NC[i-1]
        y_max = LIMITES_NC[i]
        ax1.axhspan(y_min, y_max, alpha=0.25, color=colors[i], label=f'NC {NC_TIPICOS[i]}')
    
    ax1.set_xlabel('Radio del Anión (R) [Å]', fontsize=12)
    ax1.set_ylabel('Relación r/R', fontsize=12)
    ax1.set_title(f'Variación de r/R para r = {radio_cation} Å constante', fontsize=14, pad=15)
    ax1.legend(loc='upper right', fontsize=9)
    ax1.grid(alpha=0.3)
    st.pyplot(fig1)

with col_grafica2:
    st.markdown("**Vista de zoom (r/R: 0 a 1.1)**")
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    ax2.plot(R_range, r_R_range, 'b-', linewidth=2.5, label='r/R')
    ax2.axhline(y=relacion_r_R, color='r', linestyle='--', alpha=0.7, linewidth=1.5, 
                label=f'Valor actual ({relacion_r_R:.2f})')
    ax2.axvline(x=radio_anion, color='g', linestyle='--', alpha=0.7, linewidth=1.5, 
                label=f'R actual ({radio_anion:.2f} Å)')
    
    for i in range(len(LIMITES_NC)):
        y_min = 0 if i == 0 else LIMITES_NC[i-1]
        y_max = LIMITES_NC[i]
        ax2.axhspan(y_min, y_max, alpha=0.25, color=colors[i], label=f'NC {NC_TIPICOS[i]}')
    
    ax2.set_ylim(0, 1.1)
    
    for limite in LIMITES_NC:
        ax2.axhline(y=limite, color='gray', linestyle=':', alpha=0.4, linewidth=0.8)
    
    ax2.set_xlabel('Radio del Anión (R) [Å]', fontsize=12)
    ax2.set_ylabel('Relación r/R', fontsize=12)
    ax2.set_title('Zoom: r/R entre 0 y 1.1', fontsize=14, pad=15)
    ax2.legend(loc='upper right', fontsize=9)
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

# 10. INFORMACIÓN CONTEXTUAL Y TEÓRICA
with st.expander("📚 **Explicación Teórica y Consideraciones**"):
    st.markdown("""
    **Fundamento del modelo** ...
    """)

# 11. PIE DE PÁGINA
st.caption("App desarrollada con fines académicos por HV Martínez-Tejada. Basado en las reglas de radios de Pauling.")
