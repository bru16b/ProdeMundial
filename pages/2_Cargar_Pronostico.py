# pages/2_Cargar_Pronostico.py — Formulario de pronóstico para usuarios

import streamlit as st
import datetime

from utils.data_loader import (
    read_partidos, read_participantes, read_pronosticos,
    read_resultados, save_pronostico,
)
from utils.styles import inject_global_css, render_header, render_section_title

st.set_page_config(
    page_title="Cargar Pronóstico · Prode 2026",
    page_icon="📝",
    layout="wide",
)

inject_global_css()

render_header("📝 Cargar Pronóstico", "Ingresá tu pronóstico antes de que empiece el partido")

# ── Datos ─────────────────────────────────────────────────────
partidos      = read_partidos()
participantes = read_participantes()
pronosticos   = read_pronosticos()
resultados    = read_resultados()
hoy           = datetime.date.today()

jugados_ids = set(resultados["partido_id"].tolist()) if not resultados.empty else set()

# ── Selección de participante ─────────────────────────────────
if participantes.empty:
    st.markdown("""
    <div class="info-box">
        ⚠️ Todavía no hay participantes registrados.<br>
        Pedile al administrador que te agregue al sistema.
    </div>
    """, unsafe_allow_html=True)
    st.stop()

st.markdown("### 👤 ¿Quién sos?")
nombres = participantes["nombre"].tolist()
nombre_sel = st.selectbox("Seleccioná tu nombre", nombres, key="nombre_sel")

participante = participantes[participantes["nombre"] == nombre_sel].iloc[0]
usuario_id   = int(participante["usuario_id"])

st.markdown("---")

# ── Partidos disponibles para pronosticar ─────────────────────────────
# Disponible = partido SIN resultado cargado aún (sin límite de fecha)
disponibles = partidos[
    ~partidos["partido_id"].isin(jugados_ids)
].sort_values(["fecha", "hora"])

# También mostrar partidos futuros aunque ya estén pronosticados (para editar)
render_section_title("📋 Partidos disponibles para pronosticar")

if disponibles.empty:
    st.info("No hay partidos disponibles para pronosticar en este momento.")
    st.stop()

# ── Estadísticas del usuario ──────────────────────────────────
user_prons = pronosticos[pronosticos["usuario_id"] == usuario_id] if not pronosticos.empty else []
n_user_prons = len(user_prons) if hasattr(user_prons, '__len__') else 0
n_disponibles = len(disponibles)

col_s1, col_s2 = st.columns(2)
with col_s1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{n_disponibles}</div>
        <div class="metric-label">Partidos para pronosticar</div>
    </div>
    """, unsafe_allow_html=True)
with col_s2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{n_user_prons}</div>
        <div class="metric-label">Tus pronósticos cargados</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Formulario de pronósticos ──────────────────────────────────
with st.form("form_pronosticos", clear_on_submit=False):
    st.markdown(f"**Pronósticos para {nombre_sel}** — completá los que quieras y guardá al final.")
    st.markdown("<br>", unsafe_allow_html=True)

    inputs = {}  # partido_id → (col_local, col_visitante)

    for _, partido in disponibles.iterrows():
        pid = partido["partido_id"]
        fecha_str = partido["fecha"].strftime("%d/%m")

        # Ver si ya tiene pronóstico
        pron_existente = None
        if not pronosticos.empty:
            p = pronosticos[
                (pronosticos["usuario_id"] == usuario_id) &
                (pronosticos["partido_id"] == pid)
            ]
            if not p.empty:
                pron_existente = p.iloc[0]

        # Header del partido
        ya_pron_badge = (
            "<span class='badge badge-pendiente' style='margin-left:0.5rem;'>Ya pronosticado ✏️</span>"
            if pron_existente is not None else ""
        )
        st.markdown(f"""
        <div style="
            background:#161b22; border:1px solid #21262d; border-radius:10px;
            padding:0.8rem 1.2rem; margin-bottom:0.3rem;
        ">
            <span style='font-weight:600; color:#e6edf3;'>
                {partido['equipo_local']} vs {partido['equipo_visitante']}
            </span>
            <span style='color:#8b949e; font-size:0.8rem; margin-left:0.5rem;'>
                Grupo {partido['grupo']} · {fecha_str} {partido['hora']} hs
            </span>
            {ya_pron_badge}
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([2, 1, 2])

        default_local    = int(pron_existente["goles_local"])    if pron_existente is not None else 0
        default_visitante = int(pron_existente["goles_visitante"]) if pron_existente is not None else 0

        with col1:
            gl = st.number_input(
                f"{partido['equipo_local']}",
                min_value=0, max_value=20,
                value=default_local,
                key=f"gl_{pid}",
                label_visibility="visible",
            )
        with col2:
            st.markdown(
                "<div style='text-align:center; padding-top:1.8rem; font-size:1.2rem; color:#8b949e;'>–</div>",
                unsafe_allow_html=True,
            )
        with col3:
            gv = st.number_input(
                f"{partido['equipo_visitante']}",
                min_value=0, max_value=20,
                value=default_visitante,
                key=f"gv_{pid}",
                label_visibility="visible",
            )

        inputs[pid] = (gl, gv)
        st.markdown("<br>", unsafe_allow_html=True)

    submitted = st.form_submit_button("💾 Guardar pronósticos", use_container_width=True, type="primary")

    if submitted:
        guardados = 0
        for pid, (gl, gv) in inputs.items():
            save_pronostico(usuario_id, pid, gl, gv)
            guardados += 1
        st.success(f"✅ ¡{guardados} pronóstico(s) guardados para **{nombre_sel}**!")
        st.balloons()
