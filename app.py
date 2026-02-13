import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import json

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
# 3. DEFINICIÓN DE VÉRTICES NORMALIZADOS (distancia = 1)
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
            v[(i+1) % 3] = s2
            VERTICES_NC12.append(v[:])
VERTICES_NC12 = [[v[0]/2**0.5, v[1]/2**0.5, v[2]/2**0.5] for v in VERTICES_NC12]

# ============================================================
# 4. INTERFAZ DE USUARIO (Sidebar)
# ============================================================
with st.sidebar:
    st.header("⚙️ Controles de los Radios Iónicos")
    st.caption("Ajusta los valores en Ångströms (Å).")

    radio_cation = st.slider(
        "Radio del Catión (r) [Å]",
        min_value=0.1, max_value=2.0, value=1.0, step=0.01,
        help="Selecciona el radio del catión central."
    )

    radio_anion = st.slider(
        "Radio del Anión (R) [Å]",
        min_value=0.1, max_value=7.0, value=1.4, step=0.01,
        help="Varía este control para simular aniones de diferente tamaño."
    )

    st.divider()
    st.header("🔍 Ajustes de zoom vertical (gráfica derecha)")
    y_max_zoom = st.slider("Límite superior del eje Y", 0.2, 2.0, 1.1, 0.05)
    y_min_zoom = st.slider("Límite inferior del eje Y", 0.0, 0.5, 0.0, 0.05)
    if st.button("🔄 Restablecer zoom vertical"):
        y_max_zoom = 1.1
        y_min_zoom = 0.0
        st.rerun()

# ============================================================
# 5. CÁLCULO PRINCIPAL
# ============================================================
relacion_r_R = radio_cation / radio_anion if radio_anion > 0 else 0

nc_predicho = NC_TIPICOS[-1]
geometria_predicha = GEOMETRIAS[-1]

for i, limite in enumerate(LIMITES_NC):
    if relacion_r_R < limite:
        nc_predicho = NC_TIPICOS[i]
        geometria_predicha = GEOMETRIAS[i]
        break

# ============================================================
# 6. VISUALIZACIÓN DE RESULTADOS (métricas)
# ============================================================
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Relación r/R", f"{relacion_r_R:.3f}")
with col2:
    st.metric("Número de Coordinación (NC)", nc_predicho)
with col3:
    st.metric("Geometría", geometria_predicha)

# ============================================================
# 7. TABLA DE LÍMITES
# ============================================================
st.subheader("📊 Umbrales de Estabilidad para cada NC")
df_limites = pd.DataFrame({"NC": NC_TIPICOS, "Geometría": GEOMETRIAS, "Límite inferior r/R": LIMITES_NC})
st.dataframe(df_limites, width="stretch", hide_index=True)

st.markdown(f"**Posición actual de r/R ({relacion_r_R:.3f}) en la escala:**")
posicion_relativa = min(relacion_r_R / 1.1, 1.0)
st.progress(posicion_relativa)

marcadores = " | ".join([f"{limite:.3f} (NC={nc})" for limite, nc in zip(LIMITES_NC, NC_TIPICOS)])
st.caption(f"**Límites:** {marcadores}")

# ============================================================
# 8. GRÁFICOS (dos columnas)
# ============================================================
st.subheader("📈 Relación entre R y r/R")
col_grafica1, col_grafica2 = st.columns(2)

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

    ax1.set_xlabel('Radio del Anión (R) [Å]')
    ax1.set_ylabel('Relación r/R')
    ax1.set_title(f'Variación de r/R para r = {radio_cation} Å constante')
    ax1.legend(loc='upper right', fontsize=8)
    ax1.grid(alpha=0.3)
    st.pyplot(fig1)

# --- GRÁFICA 2: Zoom didáctico con franjas + transición 2D/3D + etiquetas internas (auto-evitan curva) ---
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

    # Transición 2D/3D: r/R=0.225 y R=r/0.225
    R_transicion = radio_cation / 0.225
    if x_min <= R_transicion <= x_max:
        ax2.axvline(x=R_transicion, color='purple', linestyle='-.', linewidth=1.8, alpha=0.9,
                    label=f'Transición 2D/3D (R={R_transicion:.2f} Å)')
    ax2.axhline(y=0.225, color='purple', linestyle='-.', linewidth=1.8, alpha=0.9,
                label='Límite 2D/3D (r/R = 0.225)')

    # Franjas didácticas
    ax2.axhspan(0.155, 0.225, alpha=0.40, color='#555555', hatch='///',
                label='Región 2D (NC=3, planar)')
    ax2.axhspan(0.225, 0.414, alpha=0.35, color=colors[1], label='NC 4')
    ax2.axhspan(0.414, 0.732, alpha=0.35, color=colors[2], label='NC 6')
    ax2.axhspan(0.732, 1.000, alpha=0.35, color=colors[3], label='NC 8')
    if y_max_zoom > 1.0:
        ax2.axhspan(1.000, y_max_zoom, alpha=0.35, color=colors[4], label='NC 12')

    # Líneas auxiliares
    ax2.axhline(y=0.155, color='black', linestyle='-', linewidth=1.0, alpha=0.5)
    ax2.axhline(y=0.225, color='black', linestyle='-', linewidth=1.0, alpha=0.5)
    for limite in [0.414, 0.732, 1.000]:
        if limite <= y_max_zoom:
            ax2.axhline(y=limite, color='gray', linestyle=':', alpha=0.4, linewidth=0.8)

    # Etiquetas 2D / 3D
    if y_min_zoom <= 0.19 <= y_max_zoom:
        ax2.text(
            x_min + 0.10, 0.19, '2D', fontsize=11, weight='bold', color='white',
            bbox=dict(boxstyle='round', facecolor='#555555', alpha=0.85, edgecolor='none')
        )
    if y_min_zoom <= 0.30 <= y_max_zoom:
        ax2.text(
            x_min + 0.10, 0.30, '3D', fontsize=11, weight='bold', color='white',
            bbox=dict(boxstyle='round', facecolor=colors[1], alpha=0.85, edgecolor='none')
        )

    # ✅ Quitar rótulos redundantes sobre las líneas (NC=3 y NC=4 en el borde derecho)
    # (antes estaban aquí, ya NO los ponemos)

    # ======================================================
    # ✅ Etiquetas dentro de franjas con % + auto-desplazamiento
    # ======================================================
    x_candidates = [0.12, 0.55, 0.82]  # fracciones del ancho: izquierda, medio, derecha
    y_tol = max(0.03, 0.04 * (y_max_zoom - y_min_zoom))  # tolerancia: evita tapar curva en zoom apretado

    def _curve_y(x: float) -> float:
        # curva azul: r/R = r / R
        return (radio_cation / x) if x > 0 else 999.0

    def _pick_x_away_from_curve(y_target: float) -> float:
        # elige el primer x candidato donde la curva quede "lejos" de y_target
        for frac in x_candidates:
            x = x_min + frac * (x_max - x_min)
            if abs(_curve_y(x) - y_target) > y_tol:
                return x
        # fallback: aléjate del punto de intersección (si cae en el rango)
        x_at = (radio_cation / y_target) if y_target > 0 else (x_min + x_max) / 2
        x_left = x_min + x_candidates[0] * (x_max - x_min)
        x_right = x_min + x_candidates[-1] * (x_max - x_min)
        return x_right if abs(x_right - x_at) > abs(x_left - x_at) else x_left

    def _label_in_band(y_low, y_high, text, facecolor):
        y_mid = 0.5 * (y_low + y_high)
        if not (y_min_zoom <= y_mid <= y_max_zoom):
            return

        x = _pick_x_away_from_curve(y_mid)
        y = y_mid

        # Si aun así cae muy cerca de la curva, desplaza un poco dentro de la franja (sin salir)
        yc = _curve_y(x)
        if abs(y - yc) <= y_tol:
            band_h = (y_high - y_low)
            shift = 0.18 * band_h
            # mover alejándose de la curva
            if yc >= y:
                y = max(y_low + 0.12 * band_h, y - shift)
            else:
                y = min(y_high - 0.12 * band_h, y + shift)

        ax2.text(
            x, y, text,
            fontsize=10, weight='bold', color='white',
            bbox=dict(boxstyle='round', facecolor=facecolor, alpha=0.85, edgecolor='none')
        )

    # Porcentajes (según tu tabla: rango relevante 0.155–1.000; excluye NC=12)
    _label_in_band(0.155, 0.225, "NC=3 (8.3%)", "#555555")
    _label_in_band(0.225, 0.414, "NC=4 (22.4%)", colors[1])
    _label_in_band(0.414, 0.732, "NC=6 (37.6%)", colors[2])
    _label_in_band(0.732, 1.000, "NC=8 (31.7%)", colors[3])
    if y_max_zoom > 1.0:
        _label_in_band(1.000, y_max_zoom, "NC=12", colors[4])

    ax2.set_ylim(y_min_zoom, y_max_zoom)
    ax2.set_xlim(x_min, x_max)
    ax2.set_xlabel('Radio del Anión (R) [Å]')
    ax2.set_ylabel('Relación r/R')
    ax2.set_title(f'Zoom centrado en R = {radio_anion:.2f} Å')
    ax2.legend(loc='upper right', fontsize=8)
    ax2.grid(alpha=0.3)
    st.pyplot(fig2)

# ============================================================
# 10. VISUALIZACIONES 3D — Embedding directo (SIN py3Dmol)
# ============================================================
st.subheader("🧊 Geometrías de coordinación en 3D")
st.markdown("""
Aquí se muestra **por defecto** la geometría correspondiente al **NC predicho** (según tus radios *r* y *R*).  
Si quieres, puedes **explorar** (elegir NC) o **comparar todas** (modo didáctico).
""")

_vertices_por_nc = {3: VERTICES_NC3, 4: VERTICES_NC4, 6: VERTICES_NC6, 8: VERTICES_NC8, 12: VERTICES_NC12}

def _xyz_from_vertices(nc: int, vertices_norm, R: float, r: float) -> tuple[str, list]:
    dist = R + r
    vertices = [[v[0]*dist, v[1]*dist, v[2]*dist] for v in vertices_norm]

    n_atoms = nc + 1
    lines = [str(n_atoms), f"NC={nc} ionic coordination (Na center, Cl ligands)"]
    lines.append("Na 0.00000 0.00000 0.00000")
    for (x, y, z) in vertices:
        lines.append(f"Cl {x:.5f} {y:.5f} {z:.5f}")
    return "\n".join(lines), vertices

def _make_3dmol_embed_html(nc: int, R: float, r: float, etiqueta: str, ancho=560, alto=560) -> str:
    vertices_norm = _vertices_por_nc[nc]
    xyz, vertices = _xyz_from_vertices(nc, vertices_norm, R, r)

    verts_js = json.dumps(vertices)
    enlaces = vertices[:6] if nc == 12 else vertices
    enlaces_js = json.dumps(enlaces)

    etiqueta_html = (etiqueta.replace("\\n", "<br>").replace("\n", "<br>").replace('"', "&quot;"))
    max_z = max([p[2] for p in vertices] + [0.0])
    label_z = max_z + 2.2

    html = f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <script src="https://3Dmol.org/build/3Dmol-min.js"></script>
  <script src="https://3Dmol.org/build/3Dmol.ui-min.js"></script>
  <style>
    body {{ margin: 0; padding: 0; background: transparent; }}
    #viewer {{ width: {ancho}px; height: {alto}px; position: relative; }}
  </style>
</head>
<body>

<pre id="moldata" style="display:none;">{xyz}</pre>

<div id="viewer"
     class="viewer_3Dmoljs"
     data-element="moldata"
     data-type="xyz"
     data-backgroundcolor="#ffffff"
     data-ui="true"
     data-callback="onViewerCreated">
</div>

<script>
function onViewerCreated(viewer) {{
  const R = {R};
  const r = {r};
  const verts = {verts_js};
  const bonds = {enlaces_js};

  function addAxesLike(viewer, L) {{
    viewer.addCylinder({{start:{{x:0,y:0,z:0}}, end:{{x:L,y:0,z:0}}, radius:0.03, color:"red"}});
    viewer.addCylinder({{start:{{x:0,y:0,z:0}}, end:{{x:0,y:L,z:0}}, radius:0.03, color:"green"}});
    viewer.addCylinder({{start:{{x:0,y:0,z:0}}, end:{{x:0,y:0,z:L}}, radius:0.03, color:"blue"}});
  }}

  function draw() {{
    try {{
      if (viewer.removeAllShapes) viewer.removeAllShapes();
      if (viewer.removeAllLabels) viewer.removeAllLabels();

      if (viewer.setStyle) {{
        viewer.setStyle({{}}, {{sphere: {{scale: 1.0}}}});
        viewer.setStyle({{elem:"Cl"}}, {{sphere: {{scale: 1.0, color:"red", opacity:0.80}}}});
        viewer.setStyle({{elem:"Na"}}, {{sphere: {{scale: 1.0, color:"blue", opacity:1.00}}}});
      }}

      addAxesLike(viewer, 1.2);

      verts.forEach(v => {{
        viewer.addSphere({{
          center: {{x: v[0], y: v[1], z: v[2]}},
          radius: R,
          color: "red",
          alpha: 0.80
        }});
      }});

      viewer.addSphere({{
        center: {{x: 0, y: 0, z: 0}},
        radius: r,
        color: "blue",
        alpha: 1.00
      }});

      bonds.forEach(v => {{
        viewer.addCylinder({{
          start: {{x:0, y:0, z:0}},
          end: {{x:v[0], y:v[1], z:v[2]}},
          radius: 0.05,
          color: "gray"
        }});
      }});

      viewer.addLabel("{etiqueta_html}", {{
        position: {{x: 0, y: 0, z: {label_z}}},
        fontSize: 16,
        fontColor: "black",
        backgroundColor: "white",
        backgroundOpacity: 0.85,
        inFront: true
      }});

      if (viewer.zoomTo) viewer.zoomTo();
      if (viewer.render) viewer.render();

      setTimeout(() => {{
        if (viewer.resize) viewer.resize();
        if (viewer.render) viewer.render();
      }}, 50);

      console.log("✅ draw() OK: spheres should be visible");
    }} catch (e) {{
      console.error("❌ draw() error:", e);
      try {{
        console.log("viewer keys:", Object.keys(viewer));
        console.log("typeof addSphere:", typeof viewer.addSphere);
        console.log("typeof addCylinder:", typeof viewer.addCylinder);
      }} catch (_) {{}}
    }}
  }}

  let tries = 0;
  const timer = setInterval(() => {{
    tries++;
    try {{
      const m = viewer.getModel ? viewer.getModel() : null;
      const ok = (m && m.selectedAtoms && m.selectedAtoms({{}}).length > 0);
      if (ok || tries > 120) {{
        clearInterval(timer);
        draw();
      }}
    }} catch (e) {{
      if (tries > 120) {{
        clearInterval(timer);
        draw();
      }}
    }}
  }}, 25);
}}
</script>

</body>
</html>
"""
    return html

modo = st.radio(
    "Modo de visualización",
    options=[
        "Mostrar solo la estructura predicha (según r/R)",
        "Explorar (elegir NC manualmente)",
        "Comparar todas (3×2)"
    ],
    index=0,
    horizontal=True
)

if modo == "Explorar (elegir NC manualmente)":
    nc_elegido = st.selectbox("Selecciona un NC para explorar", NC_TIPICOS, index=NC_TIPICOS.index(nc_predicho))
else:
    nc_elegido = nc_predicho

visores = {nc: "" for nc in NC_TIPICOS}

if modo == "Comparar todas (3×2)":
    R_ANION_FIJO = 1.0
    r_R_representativo = {3: 0.19, 4: 0.30, 6: 0.50, 8: 0.80, 12: 0.90}

    for nc in NC_TIPICOS:
        idx = NC_TIPICOS.index(nc)
        if nc == 3:
            intervalo = "0.155–0.225"
        elif nc == 12:
            intervalo = ">0.732"
        else:
            intervalo = f"{LIMITES_NC[idx-1]:.3f}–{LIMITES_NC[idx]:.3f}"

        etiqueta = f"NC = {nc}\\n{GEOMETRIAS[idx]}\\nr/R: {intervalo}"
        r_rep = r_R_representativo[nc] * R_ANION_FIJO

        visores[nc] = _make_3dmol_embed_html(nc, R_ANION_FIJO, r_rep, etiqueta, ancho=450, alto=450)

    st.success("Modo comparar activado: se renderizan todas las geometrías (3×2).")

else:
    idx = NC_TIPICOS.index(nc_elegido)
    etiqueta = (
        f"NC = {nc_elegido}\\n"
        f"{GEOMETRIAS[idx]}\\n"
        f"r = {radio_cation:.2f} Å\\n"
        f"R = {radio_anion:.2f} Å\\n"
        f"r/R = {relacion_r_R:.3f}"
    )

    visores[nc_elegido] = _make_3dmol_embed_html(nc_elegido, radio_anion, radio_cation, etiqueta, ancho=560, alto=560)

    if nc_elegido == nc_predicho:
        st.markdown('<div style="border: 3px solid gold; padding: 8px; border-radius: 12px;">', unsafe_allow_html=True)

    st.markdown(f"### ✅ Geometría mostrada: **NC = {nc_elegido}** · *{GEOMETRIAS[idx]}*")
    st.components.v1.html(visores[nc_elegido], height=580)

    if nc_elegido == nc_predicho:
        st.markdown("</div>", unsafe_allow_html=True)

    st.caption("Ahora NO usamos viewer.addAxes; los ejes se dibujan con cilindros. Si algo falla, mira la consola del iframe para debug.")

# ============================================================
# 11. DISPOSICIÓN EN CUADRÍCULA 3x2 (solo en modo comparar)
# ============================================================
if modo == "Comparar todas (3×2)":
    st.subheader("🧩 Cuadrícula 3×2 (comparación didáctica)")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**NC = 3**  ·  *Triangular*")
        st.components.v1.html(visores[3], height=450)
    with col2:
        st.markdown("**NC = 4**  ·  *Tetraédrica*")
        st.components.v1.html(visores[4], height=450)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**NC = 6**  ·  *Octaédrica*")
        st.components.v1.html(visores[6], height=450)
    with col2:
        st.markdown("**NC = 8**  ·  *Cúbica*")
        st.components.v1.html(visores[8], height=450)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**NC = 12**  ·  *Cuboctaédrica (Compacta)*")
        st.components.v1.html(visores[12], height=450)
    with col2:
        st.markdown("""
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; height: 450px; display: flex; flex-direction: column; justify-content: center;">
            <h4 style="text-align: center;">📘 Información</h4>
            <p style="text-align: center;">
            <span style="color:blue;">● Catión (central)</span><br>
            <span style="color:red;">● Aniones (coordinados)</span><br><br>
            Esta cuadrícula solo aparece en “Comparar” para evitar saturación visual.
            </p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.caption("La cuadrícula completa se muestra solo si eliges **“Comparar todas (3×2)”**.")

# ============================================================
# 12. PIE DE PÁGINA
# ============================================================
st.caption("App desarrollada con fines académicos por HV Martínez-Tejada. Basado en las reglas de radios de Pauling. Visualizaciones 3D con 3Dmol.js (embedding directo).")
