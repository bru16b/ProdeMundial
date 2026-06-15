# pages/5_Ranking.py — Vista pública del ranking (sin login)

import streamlit as st
import datetime

from utils.data_loader import read_participantes, read_pronosticos, read_resultados, read_partidos
from utils.scoring import calcular_ranking
from utils.styles import inject_global_css, render_header, render_section_title, render_metric

st.set_page_config(
    page_title="Ranking · Prode 2026",
    page_icon="🏆",
    layout="wide",
)

inject_global_css()

render_header("🏆 Ranking del Prode", "Posiciones en tiempo real · Mundial 2026")

# ── Datos ─────────────────────────────────────────────────────
ranking       = calcular_ranking()
participantes = read_participantes()
pronosticos   = read_pronosticos()
resultados    = read_resultados()
partidos      = read_partidos()

# ── Métricas superiores ───────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

n_part     = len(participantes)
n_jugados  = len(resultados)
n_total    = len(partidos)
n_prons    = len(pronosticos)

with col1:
    st.markdown(render_metric(n_part, "👥 Participantes"), unsafe_allow_html=True)
with col2:
    st.markdown(render_metric(f"{n_jugados}/{n_total}", "⚽ Partidos con resultado"), unsafe_allow_html=True)
with col3:
    st.markdown(render_metric(n_prons, "📝 Pronósticos totales"), unsafe_allow_html=True)
with col4:
    # Actualización
    now_str = datetime.datetime.now().strftime("%H:%M hs")
    st.markdown(render_metric(now_str, "🕐 Actualizado"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Ranking completo ──────────────────────────────────────────
if ranking.empty:
    st.markdown("""
    <div class="info-box">
        Todavía no hay participantes registrados.<br>
        El ranking aparecerá aquí ni bien se carguen datos.
    </div>
    """, unsafe_allow_html=True)
    st.stop()

render_section_title("📊 Tabla de Posiciones")

medals   = {1: "🥇", 2: "🥈", 3: "🥉"}
pos_class = {1: "gold", 2: "silver", 3: "bronze"}

# ── Header de la tabla ─────────────────────────────────────────
st.markdown("""
<div style="display:flex; align-items:center; padding:0.4rem 1.2rem;
            color:#8b949e; font-size:0.75rem; text-transform:uppercase; letter-spacing:.08em;">
    <span style="width:36px;"></span>
    <span style="flex:1;">Jugador</span>
    <span style="min-width:60px; text-align:center;">✅ Exactos</span>
    <span style="min-width:60px; text-align:center;">🟡 Result.</span>
    <span style="min-width:60px; text-align:center;">❌ Errores</span>
    <span style="min-width:60px; text-align:center;">📝 Pronós.</span>
    <span style="min-width:70px; text-align:right;">Puntos</span>
</div>
""", unsafe_allow_html=True)

for pos, row in ranking.iterrows():
    medal     = medals.get(pos, str(pos))
    cls       = pos_class.get(pos, "")
    pts_label = "pt" if row["Puntos"] == 1 else "pts"

    # Barra de progreso visual (relativa al máximo)
    max_pts = ranking["Puntos"].max()
    pct     = (row["Puntos"] / max_pts * 100) if max_pts > 0 else 0

    st.markdown(f"""
    <div class="ranking-row" style="flex-direction:column; align-items:stretch; padding:0.75rem 1.2rem;">
        <div style="display:flex; align-items:center;">
            <span class="ranking-pos {cls}">{medal}</span>
            <span class="ranking-name" style="flex:1;">{row['Nombre']}</span>
            <span style="min-width:60px; text-align:center; color:#22c55e; font-weight:600;">{row['✅ Exactos']}</span>
            <span style="min-width:60px; text-align:center; color:#eab308; font-weight:600;">{row['🟡 Result.']}</span>
            <span style="min-width:60px; text-align:center; color:#ef4444; font-weight:600;">{row['❌ Errores']}</span>
            <span style="min-width:60px; text-align:center; color:#8b949e;">{row['Pronós.']}</span>
            <span class="ranking-pts" style="min-width:70px;">{row['Puntos']} {pts_label}</span>
        </div>
        <div style="margin-top:0.4rem; background:#21262d; border-radius:99px; height:4px; overflow:hidden;">
            <div style="width:{pct:.1f}%; background:linear-gradient(90deg,#f97316,#fbbf24);
                        height:100%; border-radius:99px; transition:width 0.3s;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Podio visual (top 3) ──────────────────────────────────────
if len(ranking) >= 2:
    render_section_title("🎖️ Podio")

    top3 = ranking.head(3)
    podio_cols = st.columns(3)

    podio_info = {1: ("🥇", "#fbbf24", "1.4rem"), 2: ("🥈", "#94a3b8", "1.1rem"), 3: ("🥉", "#cd7f32", "1rem")}

    orden = [2, 1, 3] if len(ranking) >= 3 else [2, 1]  # 2do - 1ro - 3ro visual

    for col_idx, pos in enumerate(orden):
        if pos not in top3.index:
            continue
        row = top3.loc[pos]
        emoji, color, font_size = podio_info[pos]
        altura = "160px" if pos == 1 else "120px" if pos == 2 else "90px"

        with podio_cols[col_idx]:
            st.markdown(f"""
            <div style="text-align:center; padding:1.2rem 0.5rem;">
                <div style="font-size:2.5rem;">{emoji}</div>
                <div style="font-size:{font_size}; font-weight:800; color:#e6edf3;
                            margin:0.3rem 0 0.2rem;">{row['Nombre']}</div>
                <div style="font-size:1.6rem; font-weight:900; color:{color};">{row['Puntos']} pts</div>
                <div style="font-size:0.78rem; color:#8b949e; margin-top:0.3rem;">
                    ✅{row['✅ Exactos']} &nbsp; 🟡{row['🟡 Result.']} &nbsp; ❌{row['❌ Errores']}
                </div>
                <div style="background:{color}; height:4px; border-radius:99px; margin-top:0.8rem; opacity:0.5;"></div>
                <div style="background:#161b22; border:2px solid {color}33; border-radius:10px;
                            height:{altura}; margin-top:-2px;"></div>
            </div>
            """, unsafe_allow_html=True)

# ── Última actualización ──────────────────────────────────────
st.markdown("""
<div style="text-align:center; color:#8b949e; font-size:0.78rem; margin-top:1rem;">
    🔄 El ranking se actualiza automáticamente cada vez que el admin carga un resultado
</div>
""", unsafe_allow_html=True)
