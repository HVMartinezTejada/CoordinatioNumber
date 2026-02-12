import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import py3Dmol

# ============================================================
# 1. CONFIGURACIÓN INICIAL
# ============================================================
st.set_page_config(page_title="Simulador r/R - NC", layout="wide")
st.title("📐 Simulador de Relación de Radios y Número de Coordinación")
st.markdown("""
**Teoría:** Esta app visualiza cómo la relación entre el radio del catión (r) y el anión (R) 
determina el número de coordinación (NC) estable en un sólido iónico, asumiendo el modelo de esferas rígidas.
""")

# ============================================================
# 2. DEFINICIÓN DE CONSTANTES Y LÍMITES
# ============================================================
LIMITES_NC = [0.155, 0.225, 0.414, 0.732, 1.000]
NC_TIPICOS = [3, 4, 6, 8, 12]
GEOMETRIAS = ["Triangular", "Tetraédrica", "Octaédrica", "Cúbica", "Cuboctaédrica (Compacta)"]

# Paleta de colores Viridis
colors = [cm.viridis(i / (len(NC_TIPICOS) - 1)) for i in range(len(NC_TIPICOS))]

# ============================================================
# 3. FUNCIONES PARA VISUALIZACIONES 3D (MEJORADAS)
# ============================================================
def generar_visor(nc, vertices_norm, radio_anion, radio_cation, texto_etiqueta,
                  ancho=450, alto=450):
    """
    Crea un visor py3Dmol independiente con la geometría de coordinación.
    - vertices_norm: coordenadas normalizadas (distancia 1 desde el centro).
    - radio_anion, radio_cation: radios de las esferas.
    - texto_etiqueta: texto flotante (NC, geometría, intervalo r/R).
    - ancho, alto: dimensiones del visor en píxeles.
    """
    # Escalar posiciones para que las esferas sean tangentes
    distancia_centro = radio_anion + radio_cation
    vertices = [[v * distancia_centro for v in pos] for pos in vertices_norm]
    
    view = py3Dmol.view(width=ancho, height=alto)
    
    # ---- Aniones (rojo, semitransparente) ----
    for v in vertices:
        view.addSphere({
            'center': {'x': v[0], 'y': v[1], 'z': v[2]},
            'radius': radio_anion,
            'color': 'red',
            'alpha': 0.8,
            'wireframe': False
        })
    
    # ---- Catión central (azul) ----
    view.addSphere({
        'center': {'x': 0, 'y': 0, 'z': 0},
        'radius': radio_cation,
        'color': 'blue',
        'alpha': 1.0,
        'wireframe': False
    })
    
    # ---- Enlaces (cilindros grises) - solo algunos en NC=12 para no saturar ----
    enlaces_mostrar = vertices[:6] if nc == 12 else vertices
    for v in enlaces_mostrar:
        view.addCylinder({
            'start': {'x': 0, 'y': 0, 'z': 0},
            'end': {'x': v[0], 'y': v[1], 'z': v[2]},
            'radius': 0.05,
            'color': 'gray'
        })
    
    # ---- Etiqueta flotante con información ----
    max_z = max([p[2] for p in vertices] + [0])
    view.addLabel(texto_etiqueta, {
        'position': {'x': 0, 'y': 0, 'z': max_z + 2.2},
        'fontSize': 16,
        'fontColor': 'black',
        'backgroundColor': 'white',
        'backgroundOpacity': 0.8,
        'inFront': True
    })
    
    # ---- Ajuste de cámara para encuadre perfecto ----
    view.setView({
        'fov': 35,
        'position': [0, 0, distancia_centro * 3.5],
        'up': [0, 1, 0]
    })
    view.zoomTo()
    return view

# ============================================================
# 4. DEFINICIÓN DE VÉRTICES NORMALIZADOS (distancia = 1)
# ============================================================
VERTICES_NC3 = [
    [1.0, 0.0, 0.0],
    [-0.5, np.sqrt(3)/2, 0.0],
    [-0.5, -np.sqrt(3)/2, 0.0]
]

VERTICES_NC4 = [
    [1, 1, 1],
    [1, -1, -1],
    [-1, 1, -1],
    [-1, -1, 1]
]
VERTICES_NC4 = [[v[0]/3**0.5, v[1]/3**0.5, v[2]/3**0.5] for v in VERTICES_NC4]

VERTICES_NC6 = [
    [1, 0, 0], [-1, 0, 0],
    [0, 1, 0], [0, -1, 0],
    [0, 0, 1], [0, 0, -1]
]

VERTICES_NC8 = [
    [1, 1, 1], [1, 1, -1], [1, -1, 1], [1, -1, -1],
    [-1, 1, 1], [-1, 1, -1], [-1, -1, 1], [-1, -1, -1]
]
VERTICES_NC8 = [[v[0]/3**0.5, v[1]/3**0.5, v[2]/3**0.5] for v in VERTICES_NC8]

VERTICES_NC12 = []
for i in range(3):
    for s1 in [-1, 1]:
        for s2 in [-1, 1]:
            v = [0, 0, 0]
            v[i] = s1
            v[(i+1)%3] = s2
            VERTICES_NC12.append(v[:])
VERTICES_NC12 = [[v[0]/2**0.5, v[1]/2**0.5, v[2]/2**0.5] for v in VERTICES_NC12]

# ============================================================
# 5. INTERFAZ DE USUARIO (Sidebar)
# ============================================================
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

# ============================================================
# 6. CÁLCULO PRINCIPAL
# ============================================================
relacion_r_R = radio_cation / radio_anion if radio_anion > 0 else 0

nc_predicho = NC_TIPICOS[-1]  # 12
geometria_predicha = GEOMETRIAS[-1]

for i, limite in enumerate(LIMITES_NC):
    if relacion_r_R < limite:
        nc_predicho = NC_TIPICOS[i]
        geometria_predicha = GEOMETRIAS[i]
        break

# ============================================================
# 7. VISUALIZACIÓN DE RESULTADOS (métricas)
# ============================================================
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Relación r/R", value=f"{relacion_r_R:.3f}")
with col2:
    st.metric(label="Número de Coordinación (NC)", value=nc_predicho)
with col3:
    st.metric(label="Geometría", value=geometria_predicha)

# ============================================================
# 8. BARRA DE PROGRESO Y TABLA DE LÍMITES
# ============================================================
st.subheader("📊 Umbrales de Estabilidad para cada NC")
df_limites = pd.DataFrame({
    "NC": NC_TIPICOS,
    "Geometría": GEOMETRIAS,
    "Límite inferior r/R": LIMITES_NC
})
st.dataframe(df_limites, width="stretch", hide_index=True)

st.markdown(f"**Posición actual de r/R ({relacion_r_R:.3f}) en la escala:**")
posicion_relativa = min(relacion_r_R / 1.1, 1.0)
st.progress(posicion_relativa)

marcadores = " | ".join([f"{limite:.3f} (NC={nc})" for limite, nc in zip(LIMITES_NC, NC_TIPICOS)])
st.caption(f"**Límites:** {marcadores}")

# ============================================================
# 9. GRÁFICOS INTERACTIVOS (dos columnas)
# ============================================================
st.subheader("📈 Relación entre R y r/R")

col_grafica1, col_grafica2 = st.columns(2)

# Rango completo de R (0.1 a 7.0 Å)
R_range_full = [i/100 for i in range(10, 701)]
r_R_range_full = [radio_cation / R if R > 0 else 0 for R in R_range_full]

# --- GRÁFICA 1: Vista completa ---
with col_grafica1:
    st.markdown("**Vista completa – modelo extendido**")
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(R_range_full, r_R_range_full, 'b-', linewidth=2.5, label='r/R')
    ax1.axhline(y=relacion_r_R, color='r', linestyle='--', alpha=0.7, linewidth=1.5,
                label=f'Valor actual ({relacion_r_R:.2f})')
    ax1.axvline(x=radio_anion, color='g', linestyle='--', alpha=0.7, linewidth=1.5,
                label=f'R actual ({radio_anion:.2f} Å)')
    
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

# --- GRÁFICA 2: Vista de zoom dinámico ---
with col_grafica2:
    st.markdown("**Vista de zoom – análisis detallado (gráfica principal)**")
    
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
    ax2.plot(R_range_zoom, r_R_range_zoom, 'b-', linewidth=2.5, label='r/R')
    ax2.axhline(y=relacion_r_R, color='r', linestyle='--', alpha=0.7, linewidth=1.5,
                label=f'Valor actual ({relacion_r_R:.2f})')
    ax2.axvline(x=radio_anion, color='g', linestyle='--', alpha=0.7, linewidth=1.5,
                label=f'R actual ({radio_anion:.2f} Å)')
    
    # Transición 2D/3D
    R_transicion = radio_cation / 0.225
    if x_min <= R_transicion <= x_max:
        ax2.axvline(x=R_transicion, color='purple', linestyle='-.', linewidth=1.8, alpha=0.9,
                    label=f'Transición 2D/3D (R={R_transicion:.2f} Å)')
    ax2.axhline(y=0.225, color='purple', linestyle='-.', linewidth=1.8, alpha=0.9,
                label='Límite 2D/3D (r/R = 0.225)')
    
    # Región 2D (NC=3) - trama gris
    ax2.axhspan(0.155, 0.225, alpha=0.4, color='#555555', hatch='///',
                label='Región 2D (NC=3, planar)')
    if y_max_zoom > 0.19:
        ax2.text(x_min + 0.1, 0.19, '2D', fontsize=11, weight='bold', color='white',
                 bbox=dict(boxstyle='round', facecolor='#555555', alpha=0.8))
    
    # Regiones 3D (NC≥4) - viridis
    ax2.axhspan(0.225, 0.414, alpha=0.35, color=colors[1], label='NC 4')
    ax2.axhspan(0.414, 0.732, alpha=0.35, color=colors[2], label='NC 6')
    ax2.axhspan(0.732, 1.000, alpha=0.35, color=colors[3], label='NC 8')
    if y_max_zoom > 1.0:
        ax2.axhspan(1.000, y_max_zoom, alpha=0.35, color=colors[4], label='NC 12')
    
    if y_max_zoom > 0.30:
        ax2.text(x_min + 0.1, 0.30, '3D', fontsize=11, weight='bold', color='white',
                 bbox=dict(boxstyle='round', facecolor=colors[1], alpha=0.8))
    
    # Líneas divisorias NC=3 / NC=4
    ax2.axhline(y=0.155, color='black', linestyle='-', linewidth=1.0, alpha=0.5)
    ax2.axhline(y=0.225, color='black', linestyle='-', linewidth=1.0, alpha=0.5)
    
    if y_max_zoom > 0.155:
        ax2.text(x_max - 0.05, 0.155, 'NC=3', fontsize=8, color='black',
                 verticalalignment='bottom', horizontalalignment='right')
    if y_max_zoom > 0.225:
        ax2.text(x_max - 0.05, 0.225, 'NC=4', fontsize=8, color='black',
                 verticalalignment='bottom', horizontalalignment='right')
    
    for limite in [0.414, 0.732, 1.000]:
        if limite <= y_max_zoom:
            ax2.axhline(y=limite, color='gray', linestyle=':', alpha=0.4, linewidth=0.8)
    
    ax2.set_ylim(y_min_zoom, y_max_zoom)
    ax2.set_xlim(x_min, x_max)
    ax2.set_xlabel('Radio del Anión (R) [Å]', fontsize=12)
    ax2.set_ylabel('Relación r/R', fontsize=12)
    ax2.set_title(f'Zoom centrado en R = {radio_anion:.2f} Å', fontsize=14, pad=15)
    ax2.legend(loc='upper right', fontsize=8)
    ax2.grid(alpha=0.3)
    st.pyplot(fig2)

# ============================================================
# 10. VISUALIZACIONES 3D - ORGANIZACIÓN EN CUADRÍCULA 3x2
# ============================================================
# st.markdown("### 🧪 Visor de prueba (NC=6)")
# st.markdown(visores[6], height=450)

st.subheader("🧊 Geometrías de coordinación en 3D")
st.markdown("""
Cada visor muestra un poliedro de coordinación con **aniones rojos** y **catión azul central**.  
Los tamaños relativos corresponden a los valores típicos de r/R dentro de cada intervalo.  
Puedes rotar, desplazar y hacer zoom con el mouse.
""")

# Parámetros fijos para las visualizaciones (anión = 1.0 Å)
R_ANION_FIJO = 1.0

# Valores representativos de r/R dentro de cada intervalo
r_R_representativo = {
    3: 0.19,
    4: 0.19,
    6: 0.30,
    8: 0.60,
    12: 0.80
}

# Generar los visores para cada NC
visores = {}
for nc in NC_TIPICOS:
    r_cat = r_R_representativo[nc] * R_ANION_FIJO
    idx = NC_TIPICOS.index(nc)
    
    # Texto del intervalo
    if nc == 3:
        intervalo = "0.155–0.225"
    elif nc == 12:
        intervalo = ">0.732"
    else:
        intervalo = f"{LIMITES_NC[idx-1]:.3f}–{LIMITES_NC[idx]:.3f}"
    
    etiqueta = f"NC = {nc}\n{GEOMETRIAS[idx]}\nr/R: {intervalo}"
    
    # Selección de vértices
    if nc == 3:
        vertices = VERTICES_NC3
    elif nc == 4:
        vertices = VERTICES_NC4
    elif nc == 6:
        vertices = VERTICES_NC6
    elif nc == 8:
        vertices = VERTICES_NC8
    elif nc == 12:
        vertices = VERTICES_NC12
    
    visor = generar_visor(nc, vertices, R_ANION_FIJO, r_cat, etiqueta,
                          ancho=450, alto=450)
    visores[nc] = visor._make_html()   # <--- ¡IMPORTANTE!

# ---- DISPOSICIÓN EN CUADRÍCULA 3 FILAS x 2 COLUMNAS ----

# Fila 1: NC = 3 y NC = 4
col1, col2 = st.columns(2)
with col1:
    if 3 == nc_predicho:
        st.markdown('<div style="border: 3px solid gold; padding: 5px; border-radius: 10px;">', unsafe_allow_html=True)
    st.markdown("**NC = 3**  ·  *Triangular*")
    st.markdown(visores[6], unsafe_allow_html=True)
    if 3 == nc_predicho:
        st.markdown('</div>', unsafe_allow_html=True)

with col2:
    if 4 == nc_predicho:
        st.markdown('<div style="border: 3px solid gold; padding: 5px; border-radius: 10px;">', unsafe_allow_html=True)
    st.markdown("**NC = 4**  ·  *Tetraédrica*")
    st.markdown(visores[4], unsafe_allow_html=True)
    if 4 == nc_predicho:
        st.markdown('</div>', unsafe_allow_html=True)

# Fila 2: NC = 6 y NC = 8
col1, col2 = st.columns(2)
with col1:
    if 6 == nc_predicho:
        st.markdown('<div style="border: 3px solid gold; padding: 5px; border-radius: 10px;">', unsafe_allow_html=True)
    st.markdown("**NC = 6**  ·  *Octaédrica*")
    st.markdown(visores[6], unsafe_allow_html=True)
    if 6 == nc_predicho:
        st.markdown('</div>', unsafe_allow_html=True)

with col2:
    if 8 == nc_predicho:
        st.markdown('<div style="border: 3px solid gold; padding: 5px; border-radius: 10px;">', unsafe_allow_html=True)
    st.markdown("**NC = 8**  ·  *Cúbica*")
    st.markdown(visores[8], height=450)
    if 8 == nc_predicho:
        st.markdown('</div>', unsafe_allow_html=True)

# Fila 3: NC = 12 y Leyenda
col1, col2 = st.columns(2)
with col1:
    if 12 == nc_predicho:
        st.markdown('<div style="border: 3px solid gold; padding: 5px; border-radius: 10px;">', unsafe_allow_html=True)
    st.markdown("**NC = 12**  ·  *Cuboctaédrica (Compacta)*")
    st.markdown(visores[12], unsafe_allow_html=True)
    if 12 == nc_predicho:
        st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; height: 450px; display: flex; flex-direction: column; justify-content: center;">
        <h4 style="text-align: center;">📘 Información</h4>
        <p style="text-align: center;">
        <span style="color:blue;">● Catión (central)</span><br>
        <span style="color:red;">● Aniones (coordinados)</span><br><br>
        <strong>Radios fijos para visualización:</strong><br>
        Anión (R) = 1.0 Å<br>
        Catión (r) = r/R × 1.0 Å<br>
        (valores representativos del intervalo)<br><br>
        <em>El visor NC=12 muestra solo 6 enlaces<br>para no saturar la escena.</em>
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# 11. LEYENDA DE COLORES Y EXPLICACIÓN TEÓRICA
# ============================================================
with st.expander("🎨 Guía de colores y explicación teórica"):
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
            f'<b>NC = 12</b><br>Cuboctaédrica</div>',
            unsafe_allow_html=True
        )
    
    st.markdown("""
    **Interpretación de la transición 2D → 3D**
    - El valor r"**\( R = r / 0.225 \)**" es el límite inferior para la coordinación tetraédrica (3D) y el superior para la triangular (2D).
    - Para un catión de radio `r` fijo, el tamaño de anión que produce esta transición es **\( R = r / 0.225 \)**.
    - En la gráfica de zoom, puedes **ajustar el límite superior del eje Y** para ampliar la región inferior y observar con claridad las franjas de NC=3 y NC=4.
    
    **Visualizaciones 3D**
    - Las esferas **rojas** representan los aniones.
    - La esfera **azul** central es el catión.
    - Las barras grises indican las direcciones de enlace (solo algunas en NC=12 para no saturar).
    - Puedes **rotar, desplazar y hacer zoom** sobre cada modelo con el mouse.
    """)

# ============================================================
# 12. PIE DE PÁGINA
# ============================================================
st.caption("App desarrollada con fines académicos por HV Martínez-Tejada. Basado en las reglas de radios de Pauling. Visualizaciones 3D con Py3Dmol.")










