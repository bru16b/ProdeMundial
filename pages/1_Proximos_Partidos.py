# pages/1_Proximos_Partidos.py — Próximos partidos del Mundial 2026

import streamlit as st
import datetime

from utils.data_loader import read_partidos, read_resultados, read_pronosticos, read_participantes
from utils.styles import inject_global_css, render_header, render_section_title
from config import GRUPOS

st.set_page_config(
    page_title="Próximos Partidos · Prode 2026",
    page_icon="📅",
    layout="wide",
)

inject_global_css()

render_header("📅 Próximos Partidos", "Fixture completo de la fase de grupos — Mundial 2026")

# ── Cargar datos ──────────────────────────────────────────────
partidos    = read_partidos()
resultados  = read_resultados()
participantes = read_participantes()
pronosticos = read_pronosticos()
hoy         = datetime.date.today()

jugados_ids = set(resultados["partido_id"].tolist()) if not resultados.empty else set()

# ── Filtros ───────────────────────────────────────────────────
col_f1, col_f2, col_f3 = st.columns([1, 1, 2])

with col_f1:
    vista = st.selectbox(
        "📂 Ver",
        ["Próximos", "Jugados", "Todos"],
        key="filtro_vista",
    )

with col_f2:
    grupos_opciones = ["Todos los grupos"] + [f"Grupo {g}" for g in GRUPOS]
    filtro_grupo = st.selectbox("🔠 Grupo", grupos_opciones, key="filtro_grupo")

with col_f3:
    # Selector de participante para ver si ya pronosticó
    nombres = ["— Sin filtrar —"]
    if not participantes.empty:
        nombres += participantes["nombre"].tolist()
    jugador_sel = st.selectbox("👤 Ver mis pronósticos", nombres, key="filtro_jugador")

st.markdown("<br>", unsafe_allow_html=True)

# ── Aplicar filtros ───────────────────────────────────────────
df = partidos.copy()

if vista == "Próximos":
    df = df[~df["partido_id"].isin(jugados_ids)]
elif vista == "Jugados":
    df = df[df["partido_id"].isin(jugados_ids)]

if filtro_grupo != "Todos los grupos":
    grupo_letra = filtro_grupo.replace("Grupo ", "")
    df = df[df["grupo"] == grupo_letra]

df = df.sort_values(["fecha", "hora"]).reset_index(drop=True)

# Obtener ID del jugador seleccionado
usuario_id_sel = None
if jugador_sel != "— Sin filtrar —" and not participantes.empty:
    match = participantes[participantes["nombre"] == jugador_sel]
    if not match.empty:
        usuario_id_sel = match.iloc[0]["usuario_id"]

# ── Resumen de filtro ─────────────────────────────────────────
total_filtrado = len(df)
st.markdown(
    f"<div style='color:#8b949e; font-size:0.85rem; margin-bottom:1rem;'>"
    f"Mostrando <strong style='color:#f97316'>{total_filtrado}</strong> partido(s)"
    f"</div>",
    unsafe_allow_html=True,
)

if df.empty:
    st.info("No hay partidos para mostrar con los filtros seleccionados.")
    st.stop()

# ── Agrupar por fecha ─────────────────────────────────────────
for fecha, grupo_df in df.groupby("fecha"):
    fecha_str = fecha.strftime("%A %d de %B de %Y").capitalize()
    render_section_title(f"🗓️ {fecha_str}")

    for _, partido in grupo_df.iterrows():
        pid = partido["partido_id"]
        es_jugado = pid in jugados_ids

        # Resultado real (si existe)
        resultado_str = ""
        if es_jugado and not resultados.empty:
            res = resultados[resultados["partido_id"] == pid]
            if not res.empty:
                r = res.iloc[0]
                resultado_str = f"{int(r['goles_local'])}–{int(r['goles_visitante'])}"

        # Pronóstico del jugador seleccionado
        pron_str = ""
        pron_badge = ""
        if usuario_id_sel is not None and not pronosticos.empty:
            p = pronosticos[
                (pronosticos["usuario_id"] == usuario_id_sel) &
                (pronosticos["partido_id"] == pid)
            ]
            if not p.empty:
                pr = p.iloc[0]
                pron_str = f"{int(pr['goles_local'])}–{int(pr['goles_visitante'])}"
                pron_badge = "<span class='badge badge-pendiente'>Mi pronóstico</span>"
            else:
                pron_badge = "<span class='badge badge-error'>Sin pronóstico</span>"

        # Badge de estado
        if es_jugado:
            estado_badge = f"<span class='badge badge-jugado'>Jugado {resultado_str}</span>"
        else:
            estado_badge = "<span class='badge badge-pendiente'>Pendiente</span>"

        pron_str_html = f"<span style='color:#8b949e; font-size:0.82rem;'>Mi pronós: <strong>{pron_str}</strong></span>" if pron_str else ""

        html_card = f"""
        <div class="match-card">
            <div style="min-width:220px;">
                <div class="teams">{partido['equipo_local']} <span style='color:#8b949e'>vs</span> {partido['equipo_visitante']}</div>
                <div class="meta">Grupo {partido['grupo']} · {partido['hora']} hs · {partido['estadio']}, {partido['ciudad']}</div>
            </div>
            <div style="display:flex; gap:0.5rem; align-items:center; flex-wrap:wrap;">
                {estado_badge}
                {pron_badge}
                {pron_str_html}
            </div>
        </div>
        """
        st.html(html_card)

