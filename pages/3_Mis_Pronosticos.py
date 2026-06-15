# pages/3_Mis_Pronosticos.py — Ver pronósticos y puntaje del usuario

import streamlit as st

from utils.data_loader import read_partidos, read_participantes, read_pronosticos, read_resultados
from utils.scoring import calcular_puntaje_partido
from utils.styles import inject_global_css, render_header, render_section_title, render_metric
from config import PUNTOS_EXACTO, PUNTOS_RESULTADO

st.set_page_config(
    page_title="Mis Pronósticos · Prode 2026",
    page_icon="🔍",
    layout="wide",
)

inject_global_css()

render_header("🔍 Mis Pronósticos", "Seguí tus aciertos y tu puntaje acumulado")

# ── Datos ─────────────────────────────────────────────────────
partidos      = read_partidos()
participantes = read_participantes()
pronosticos   = read_pronosticos()
resultados    = read_resultados()

if participantes.empty:
    st.markdown("""
    <div class="info-box">
        No hay participantes registrados aún. Pedile al admin que te agregue.
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Selección de usuario ──────────────────────────────────────
nombre_sel = st.selectbox("👤 Seleccioná tu nombre", participantes["nombre"].tolist(), key="mis_pron_user")
participante = participantes[participantes["nombre"] == nombre_sel].iloc[0]
usuario_id   = int(participante["usuario_id"])

st.markdown("---")

# ── Pronósticos del usuario ───────────────────────────────────
if pronosticos.empty:
    user_prons = []
else:
    user_prons = pronosticos[pronosticos["usuario_id"] == usuario_id]

if len(user_prons) == 0:
    st.markdown("""
    <div class="info-box">
        Todavía no cargaste ningún pronóstico.<br>
        Andá a <strong>📝 Cargar Pronóstico</strong> para ingresar tus predicciones.
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Calcular puntajes del usuario ─────────────────────────────
total_pts  = 0
exactos    = 0
result_ok  = 0
errores    = 0
pendientes = 0

filas = []

for _, pron in user_prons.iterrows():
    pid = pron["partido_id"]
    partido_data = partidos[partidos["partido_id"] == pid]
    if partido_data.empty:
        continue

    p = partido_data.iloc[0]
    fecha_str = p["fecha"].strftime("%d/%m")

    # ¿Tiene resultado?
    res_row = None
    if not resultados.empty:
        r = resultados[resultados["partido_id"] == pid]
        if not r.empty:
            res_row = r.iloc[0]

    if res_row is not None:
        pts, tipo = calcular_puntaje_partido(
            pron["goles_local"], pron["goles_visitante"],
            res_row["goles_local"], res_row["goles_visitante"],
        )
        total_pts += pts
        if pts == PUNTOS_EXACTO:
            exactos += 1
        elif pts == PUNTOS_RESULTADO:
            result_ok += 1
        else:
            errores += 1
        resultado_real = f"{int(res_row['goles_local'])}–{int(res_row['goles_visitante'])}"
    else:
        pts  = None
        tipo = "⏳ Pendiente"
        resultado_real = "–"
        pendientes += 1

    filas.append({
        "partido_id": pid,
        "equipo_local": p["equipo_local"],
        "equipo_visitante": p["equipo_visitante"],
        "grupo": p["grupo"],
        "fecha_str": fecha_str,
        "mi_pron": f"{int(pron['goles_local'])}–{int(pron['goles_visitante'])}",
        "resultado_real": resultado_real,
        "pts": pts,
        "tipo": tipo,
    })

# ── Métricas resumen ──────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)
cols = [col1, col2, col3, col4, col5]
datos_metric = [
    (total_pts, "🏆 Puntos Totales"),
    (exactos, "✅ Exactos (3 pts)"),
    (result_ok, "🟡 Resultado (1 pt)"),
    (errores, "❌ Errores (0 pts)"),
    (pendientes, "⏳ Pendientes"),
]
for col, (val, lbl) in zip(cols, datos_metric):
    with col:
        st.markdown(render_metric(val, lbl), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Filtro rápido ─────────────────────────────────────────────
render_section_title(f"📋 Pronósticos de {nombre_sel}")

filtro_estado = st.radio(
    "Filtrar por estado",
    ["Todos", "✅ Exacto", "🟡 Resultado", "❌ Error", "⏳ Pendiente"],
    horizontal=True,
    key="filtro_estado",
)

# ── Tabla de pronósticos ──────────────────────────────────────
badge_map = {
    "✅ Exacto":   ("badge-exacto",    "✅ Exacto"),
    "🟡 Resultado":("badge-resultado", "🟡 Resultado"),
    "❌ Error":    ("badge-error",     "❌ Error"),
    "⏳ Pendiente":("badge-pendiente", "⏳ Pendiente"),
}

filas_mostradas = 0

for f in filas:
    # Aplicar filtro
    if filtro_estado != "Todos" and filtro_estado not in f["tipo"]:
        continue

    tipo_key = f["tipo"]
    badge_class, badge_text = badge_map.get(tipo_key, ("badge-pendiente", tipo_key))
    pts_display = str(f["pts"]) + " pt" if f["pts"] is not None else "–"

    st.markdown(f"""
    <div class="match-card">
        <div style="min-width:220px;">
            <div class="teams">
                {f['equipo_local']} vs {f['equipo_visitante']}
            </div>
            <div class="meta">Grupo {f['grupo']} · {f['fecha_str']}</div>
        </div>
        <div style="display:flex; gap:1.5rem; align-items:center; flex-wrap:wrap;">
            <div style="text-align:center;">
                <div style="font-size:0.72rem; color:#8b949e; text-transform:uppercase; letter-spacing:.05em;">Mi pronós.</div>
                <div style="font-size:1.3rem; font-weight:700; color:#e6edf3;">{f['mi_pron']}</div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:0.72rem; color:#8b949e; text-transform:uppercase; letter-spacing:.05em;">Resultado</div>
                <div style="font-size:1.3rem; font-weight:700; color:#f97316;">{f['resultado_real']}</div>
            </div>
            <div>
                <span class="badge {badge_class}">{badge_text}</span>
            </div>
        </div>
        <div style="font-size:1.1rem; font-weight:700; color:#f97316; min-width:40px; text-align:right;">
            {pts_display}
        </div>
    </div>
    """, unsafe_allow_html=True)
    filas_mostradas += 1

if filas_mostradas == 0:
    st.info("No hay pronósticos para mostrar con este filtro.")
