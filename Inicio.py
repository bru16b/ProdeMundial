# app.py — Página de Inicio del Prode Mundial 2026

import streamlit as st
import pandas as pd
import datetime

from utils.data_loader import read_partidos, read_participantes, read_pronosticos, read_resultados
from utils.scoring import calcular_ranking
from utils.styles import inject_global_css, render_header, render_metric, render_section_title

st.set_page_config(
    page_title="Prode Mundial 2026",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_global_css()

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚽ Prode Mundial 2026")
    st.markdown("---")
    st.markdown("""
    <div style='color:#8b949e; font-size:0.82rem; line-height:1.6;'>
    Navegá entre las secciones usando el menú de arriba.
    <br><br>
    🏆 Exacto → <strong style='color:#f97316'>3 pts</strong><br>
    🟡 Resultado → <strong style='color:#f97316'>1 pt</strong><br>
    ❌ Error → <strong style='color:#f97316'>0 pts</strong>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(
        "<div style='color:#8b949e; font-size:0.75rem; text-align:center;'>Mundial 2026 · Fase de Grupos</div>",
        unsafe_allow_html=True,
    )

# ── Header ───────────────────────────────────────────────────
render_header("⚽ Prode Mundial 2026", "Fase de Grupos · USA · Canada · México")

# ── Cargar datos ─────────────────────────────────────────────
partidos     = read_partidos()
participantes = read_participantes()
pronosticos  = read_pronosticos()
resultados   = read_resultados()
hoy          = datetime.date.today()

# ── Métricas principales ──────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

n_participantes = len(participantes)
n_partidos_jugados = len(resultados)
n_partidos_total = len(partidos)
n_pronosticos = len(pronosticos)

with col1:
    st.markdown(render_metric(n_participantes, "👥 Participantes"), unsafe_allow_html=True)
with col2:
    st.markdown(render_metric(f"{n_partidos_jugados}/{n_partidos_total}", "📅 Partidos Jugados"), unsafe_allow_html=True)
with col3:
    st.markdown(render_metric(n_pronosticos, "📝 Pronósticos"), unsafe_allow_html=True)
with col4:
    # Promedio de pronósticos por participante
    avg = round(n_pronosticos / n_participantes, 1) if n_participantes > 0 else 0
    st.markdown(render_metric(avg, "📊 Prom. Pronós/Jugador"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Dos columnas principales ──────────────────────────────────
left_col, right_col = st.columns([1.2, 1], gap="large")

# ── TOP 5 RANKING ─────────────────────────────────────────────
with left_col:
    render_section_title("🏆 Top 5 — Ranking")

    ranking = calcular_ranking()

    if ranking.empty:
        st.markdown("""
        <div class="info-box">
            Aún no hay participantes registrados.<br>
            El admin puede agregar jugadores desde el panel de administración.
        </div>
        """, unsafe_allow_html=True)
    else:
        top5 = ranking.head(5)
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        pos_classes = {1: "gold", 2: "silver", 3: "bronze"}

        for pos, row in top5.iterrows():
            medal = medals.get(pos, f"#{pos}")
            pos_class = pos_classes.get(pos, "")
            pts_label = "pt" if row["Puntos"] == 1 else "pts"
            st.markdown(f"""
            <div class="ranking-row">
                <span class="ranking-pos {pos_class}">{medal}</span>
                <span class="ranking-name">{row['Nombre']}</span>
                <span style="color:#8b949e; font-size:0.8rem; margin-right:1rem;">
                    ✅{row['✅ Exactos']} 🟡{row['🟡 Result.']} ❌{row['❌ Errores']}
                </span>
                <span class="ranking-pts">{row['Puntos']} {pts_label}</span>
            </div>
            """, unsafe_allow_html=True)

        if len(ranking) > 5:
            st.markdown(
                f"<div style='color:#8b949e; font-size:0.8rem; text-align:center; margin-top:0.5rem;'>"
                f"… y {len(ranking) - 5} participante(s) más</div>",
                unsafe_allow_html=True,
            )

# ── ÚLTIMOS RESULTADOS ────────────────────────────────────────
with right_col:
    render_section_title("📋 Últimos Resultados")

    if resultados.empty:
        st.markdown("""
        <div class="info-box">
            Todavía no hay resultados cargados.<br>
            El administrador los irá ingresando.
        </div>
        """, unsafe_allow_html=True)
    else:
        ultimos = resultados.merge(partidos[["partido_id", "equipo_local", "equipo_visitante", "grupo", "fecha"]], on="partido_id")
        ultimos = ultimos.sort_values("fecha_carga", ascending=False).head(5)

        for _, r in ultimos.iterrows():
            fecha_str = r["fecha"].strftime("%d/%m") if hasattr(r["fecha"], "strftime") else str(r["fecha"])[:5]
            st.markdown(f"""
            <div class="match-card">
                <div>
                    <div class="teams">{r['equipo_local']} vs {r['equipo_visitante']}</div>
                    <div class="meta">Grupo {r['grupo']} · {fecha_str}</div>
                </div>
                <div class="score">{int(r['goles_local'])}–{int(r['goles_visitante'])}</div>
            </div>
            """, unsafe_allow_html=True)

# ── PRÓXIMO PARTIDO ───────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
render_section_title("⏭️ Próximo Partido")

jugados_ids = set(resultados["partido_id"].tolist()) if not resultados.empty else set()
proximos = partidos[~partidos["partido_id"].isin(jugados_ids)].sort_values("fecha")

if proximos.empty:
    st.info("¡Todos los partidos de la fase de grupos han sido jugados!")
else:
    prox = proximos.iloc[0]
    fecha_str = prox["fecha"].strftime("%A %d de %B de %Y").capitalize()
    col_a, col_b, col_c = st.columns([2, 1, 2])
    with col_a:
        st.markdown(f"""
        <div style='text-align:right;'>
            <div style='font-size:1.8rem; font-weight:800; color:#e6edf3;'>{prox['equipo_local']}</div>
            <div style='color:#8b949e; font-size:0.85rem;'>Local</div>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown(f"""
        <div style='text-align:center; padding:0.5rem;'>
            <div style='font-size:1.4rem; font-weight:800; color:#f97316;'>VS</div>
            <div style='color:#8b949e; font-size:0.75rem; margin-top:0.3rem;'>{prox['hora']}</div>
            <div style='margin-top:0.3rem;'>
                <span class='badge badge-pendiente'>Grupo {prox['grupo']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_c:
        st.markdown(f"""
        <div style='text-align:left;'>
            <div style='font-size:1.8rem; font-weight:800; color:#e6edf3;'>{prox['equipo_visitante']}</div>
            <div style='color:#8b949e; font-size:0.85rem;'>Visitante</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='text-align:center; color:#8b949e; font-size:0.85rem; margin-top:0.5rem;'>
        📍 {prox['estadio']}, {prox['ciudad']} · 🗓️ {fecha_str}
    </div>
    """, unsafe_allow_html=True)
