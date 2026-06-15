# pages/4_Admin.py — Panel de administración (solo admin)

import streamlit as st
import datetime
import io

from utils.auth import check_admin_password
from utils.data_loader import (
    read_partidos, read_participantes, read_pronosticos,
    read_resultados, save_resultado, add_participante, delete_participante,
)
from utils.scoring import calcular_ranking, calcular_puntaje_partido
from utils.styles import inject_global_css, render_header, render_section_title, render_metric

st.set_page_config(
    page_title="Admin · Prode 2026",
    page_icon="🔐",
    layout="wide",
)

inject_global_css()

render_header("🔐 Panel de Administración", "Acceso exclusivo para el administrador del prode")

# ── Login ─────────────────────────────────────────────────────
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if not st.session_state.admin_logged_in:
    st.markdown("<br>", unsafe_allow_html=True)
    col_login, _ = st.columns([1, 2])
    with col_login:
        st.markdown("""
        <div style="background:#161b22; border:1px solid #21262d; border-radius:14px; padding:2rem;">
            <h3 style="color:#e6edf3; margin-bottom:1rem;">🔑 Ingresá la contraseña</h3>
        """, unsafe_allow_html=True)

        password = st.text_input("Contraseña de admin", type="password", key="admin_pwd_input")
        login_btn = st.button("Entrar", type="primary", use_container_width=True)

        if login_btn:
            if check_admin_password(password):
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta.")

        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ── Panel admin (usuario autenticado) ─────────────────────────
col_logout, _ = st.columns([1, 4])
with col_logout:
    if st.button("🚪 Cerrar sesión", key="logout_btn"):
        st.session_state.admin_logged_in = False
        st.rerun()

st.success("✅ Sesión de administrador activa.")
st.markdown("---")

# ── Tabs principales ──────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📥 Cargar Resultado",
    "👥 Gestionar Participantes",
    "🏆 Ranking Completo",
    "📊 Pronósticos por Partido",
    "⚠️ Resetear Datos",
])

# ── Tab 1: Cargar resultado ───────────────────────────────────
with tab1:
    render_section_title("📥 Cargar Resultado Real")

    partidos   = read_partidos()
    resultados = read_resultados()

    jugados_ids = set(resultados["partido_id"].tolist()) if not resultados.empty else set()

    # Admin ve TODOS los partidos, sin filtro de fecha
    todos_partidos = partidos.sort_values(["fecha", "hora"])

    opciones = {
        f"{r['equipo_local']} vs {r['equipo_visitante']}  [Grupo {r['grupo']}] ({r['fecha'].strftime('%d/%m')})"
        + (" ✅" if r["partido_id"] in jugados_ids else " ⏳"): r["partido_id"]
        for _, r in todos_partidos.iterrows()
    }

    partido_sel_label = st.selectbox("Seleccioná el partido", list(opciones.keys()), key="admin_partido_sel")
    partido_id_sel    = opciones[partido_sel_label]

    partido_data = partidos[partidos["partido_id"] == partido_id_sel].iloc[0]

    # Valores por defecto (si ya tiene resultado)
    gl_default, gv_default = 0, 0
    if partido_id_sel in jugados_ids:
        res = resultados[resultados["partido_id"] == partido_id_sel].iloc[0]
        gl_default = int(res["goles_local"])
        gv_default = int(res["goles_visitante"])
        st.markdown(
            f"<span class='badge badge-jugado'>Ya cargado: {gl_default}–{gv_default}</span>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    col_r1, col_r2, col_r3 = st.columns([2, 1, 2])
    with col_r1:
        st.markdown(
            f"<div style='text-align:right; font-weight:700; font-size:1.1rem; color:#e6edf3; padding-top:0.5rem;'>{partido_data['equipo_local']}</div>",
            unsafe_allow_html=True,
        )
        gl_real = st.number_input("Goles local", min_value=0, max_value=20, value=gl_default, key="admin_gl")
    with col_r2:
        st.markdown("<div style='text-align:center; padding-top:1.8rem; font-size:1.4rem; color:#8b949e;'>–</div>", unsafe_allow_html=True)
    with col_r3:
        st.markdown(
            f"<div style='font-weight:700; font-size:1.1rem; color:#e6edf3; padding-top:0.5rem;'>{partido_data['equipo_visitante']}</div>",
            unsafe_allow_html=True,
        )
        gv_real = st.number_input("Goles visitante", min_value=0, max_value=20, value=gv_default, key="admin_gv")

    if st.button("💾 Guardar Resultado", type="primary", key="admin_save_resultado"):
        save_resultado(partido_id_sel, gl_real, gv_real)
        st.success(
            f"✅ Resultado guardado: **{partido_data['equipo_local']} {gl_real}–{gv_real} {partido_data['equipo_visitante']}**"
        )
        st.rerun()

# ── Tab 2: Gestionar participantes ───────────────────────────
with tab2:
    render_section_title("👥 Gestionar Participantes")

    participantes = read_participantes()

    # Agregar nuevo
    with st.expander("➕ Agregar nuevo participante", expanded=False):
        with st.form("form_add_participante"):
            nuevo_nombre = st.text_input("Nombre completo", key="nuevo_nombre")
            submitted_add = st.form_submit_button("Agregar", type="primary")

            if submitted_add:
                if not nuevo_nombre.strip():
                    st.error("❌ Ingresá un nombre.")
                else:
                    ok, msg = add_participante(nuevo_nombre, "")
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    st.markdown("<br>", unsafe_allow_html=True)

    if participantes.empty:
        st.markdown("""
        <div class="info-box">No hay participantes registrados aún.</div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"**{len(participantes)} participante(s) registrados:**")
        for _, p in participantes.iterrows():
            col_p1, col_p2, col_p3 = st.columns([4, 3, 1])
            with col_p1:
                st.markdown(f"**{p['nombre']}**")
            with col_p2:
                fecha_reg = str(p.get("fecha_registro", ""))[:10]
                st.markdown(f"<span style='color:#8b949e; font-size:0.8rem;'>Reg. {fecha_reg}</span>", unsafe_allow_html=True)
            with col_p3:
                if st.button("🗑️", key=f"del_{p['usuario_id']}", help=f"Eliminar {p['nombre']}"):
                    delete_participante(int(p["usuario_id"]))
                    st.success(f"🗑️ {p['nombre']} eliminado.")
                    st.rerun()

# ── Tab 3: Ranking completo ───────────────────────────────────
with tab3:
    render_section_title("🏆 Ranking Completo")

    ranking = calcular_ranking()

    if ranking.empty:
        st.info("Sin datos de ranking aún.")
    else:
        # ── Botones de exportación ─────────────────────────────
        col_exp1, col_exp2, _ = st.columns([1, 1, 3])

        # Export CSV
        ranking_export = ranking.reset_index()[["Pos", "Nombre", "Puntos", "✅ Exactos", "🟡 Result.", "❌ Errores", "Pronós."]]
        csv_data = ranking_export.to_csv(index=False, encoding="utf-8-sig")
        with col_exp1:
            st.download_button(
                label="📥 Exportar CSV",
                data=csv_data,
                file_name="ranking_prode_2026.csv",
                mime="text/csv",
                use_container_width=True,
            )

        # Export Excel
        buffer = io.BytesIO()
        with __import__('contextlib').suppress(Exception):
            import openpyxl  # noqa: F401 — check availability
            ranking_export.to_excel(buffer, index=False, sheet_name="Ranking")
            buffer.seek(0)
            with col_exp2:
                st.download_button(
                    label="📊 Exportar Excel",
                    data=buffer,
                    file_name="ranking_prode_2026.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)

        medals = {1: "🥇", 2: "🥈", 3: "🥉"}

        for pos, row in ranking.iterrows():
            medal = medals.get(pos, f"#{pos}")
            st.markdown(f"""
            <div class="ranking-row">
                <span class="ranking-pos {'gold' if pos==1 else 'silver' if pos==2 else 'bronze' if pos==3 else ''}">{medal}</span>
                <span class="ranking-name">{row['Nombre']}</span>
                <span style="color:#8b949e; font-size:0.82rem; margin-right:1rem;">
                    ✅{row['✅ Exactos']} &nbsp;🟡{row['🟡 Result.']} &nbsp;❌{row['❌ Errores']} &nbsp;📝{row['Pronós.']}
                </span>
                <span class="ranking-pts">{row['Puntos']} pts</span>
            </div>
            """, unsafe_allow_html=True)

# ── Tab 4: Pronósticos por partido ───────────────────────────
with tab4:
    render_section_title("📊 Pronósticos por Partido")

    partidos_tab4   = read_partidos()
    pronosticos_tab4 = read_pronosticos()
    resultados_tab4  = read_resultados()
    participantes_tab4 = read_participantes()

    jugados_ids_tab4 = set(resultados_tab4["partido_id"].tolist()) if not resultados_tab4.empty else set()

    # Solo partidos con al menos un pronóstico
    if pronosticos_tab4.empty:
        st.info("No hay pronósticos cargados aún.")
    else:
        pids_con_pron = pronosticos_tab4["partido_id"].unique()
        partidos_con_pron = partidos_tab4[partidos_tab4["partido_id"].isin(pids_con_pron)].sort_values("fecha")

        opciones_tab4 = {
            f"[Grupo {r['grupo']}] {r['equipo_local']} vs {r['equipo_visitante']} ({r['fecha'].strftime('%d/%m')})"
            + (" ✅" if r["partido_id"] in jugados_ids_tab4 else " ⏳"): r["partido_id"]
            for _, r in partidos_con_pron.iterrows()
        }

        partido_t4_label = st.selectbox("Seleccioná un partido", list(opciones_tab4.keys()), key="tab4_partido")
        partido_t4_id    = opciones_tab4[partido_t4_label]
        partido_t4_data  = partidos_tab4[partidos_tab4["partido_id"] == partido_t4_id].iloc[0]

        # Resultado real del partido
        res_t4 = None
        if partido_t4_id in jugados_ids_tab4:
            res_t4 = resultados_tab4[resultados_tab4["partido_id"] == partido_t4_id].iloc[0]
            st.markdown(
                f"<div class='info-box'>🏆 Resultado real: <strong>{int(res_t4['goles_local'])}–{int(res_t4['goles_visitante'])}</strong></div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown("<div class='info-box'>⏳ Este partido aún no tiene resultado cargado.</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        prons_t4 = pronosticos_tab4[pronosticos_tab4["partido_id"] == partido_t4_id]

        for _, pron in prons_t4.iterrows():
            part = participantes_tab4[participantes_tab4["usuario_id"] == pron["usuario_id"]]
            nombre_jugador = part.iloc[0]["nombre"] if not part.empty else f"ID {pron['usuario_id']}"

            if res_t4 is not None:
                pts, tipo = calcular_puntaje_partido(
                    pron["goles_local"], pron["goles_visitante"],
                    res_t4["goles_local"], res_t4["goles_visitante"],
                )
                badge_map_t4 = {
                    "✅ Exacto":    "badge-exacto",
                    "🟡 Resultado": "badge-resultado",
                    "❌ Error":     "badge-error",
                }
                badge_cls = badge_map_t4.get(tipo, "badge-pendiente")
                pts_display = f"{pts} pts"
            else:
                tipo = "⏳ Pendiente"
                badge_cls = "badge-pendiente"
                pts_display = "–"

            st.markdown(f"""
            <div class="match-card">
                <div style="flex:1;">
                    <div style="font-weight:600; color:#e6edf3;">{nombre_jugador}</div>
                </div>
                <div style="font-size:1.3rem; font-weight:700; color:#e6edf3; margin: 0 1rem;">
                    {int(pron['goles_local'])}–{int(pron['goles_visitante'])}
                </div>
                <span class="badge {badge_cls}">{tipo}</span>
                <div style="font-size:1rem; font-weight:700; color:#f97316; min-width:50px; text-align:right;">
                    {pts_display}
                </div>
            </div>
            """, unsafe_allow_html=True)

# ── Tab 5: Resetear datos ─────────────────────────────────────
with tab5:
    render_section_title("⚠️ Resetear Datos del Prode")

    st.markdown("""
    <div style="background:rgba(239,68,68,0.08); border:1px solid rgba(239,68,68,0.3);
                border-radius:12px; padding:1.2rem 1.5rem; margin-bottom:1.5rem;">
        <div style="color:#f87171; font-weight:700; font-size:1rem; margin-bottom:0.4rem;">🚨 Zona de peligro</div>
        <div style="color:#fca5a5; font-size:0.88rem; line-height:1.6;">
            Esta acción <strong>elimina permanentemente</strong> todos los datos de:
            <ul style="margin:0.4rem 0 0; padding-left:1.2rem;">
                <li>👥 Participantes registrados</li>
                <li>📝 Pronósticos cargados</li>
                <li>✅ Resultados ingresados</li>
            </ul>
            El fixture de partidos <strong>no se borra</strong>.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Inicializar estado de confirmación
    if "confirm_reset" not in st.session_state:
        st.session_state.confirm_reset = False

    if not st.session_state.confirm_reset:
        col_btn, _ = st.columns([1, 3])
        with col_btn:
            if st.button("🗑️ Formatear todos los datos", type="primary",
                         use_container_width=True, key="btn_reset_step1"):
                st.session_state.confirm_reset = True
                st.rerun()
    else:
        st.markdown("""
        <div style="background:rgba(239,68,68,0.12); border:1px solid rgba(239,68,68,0.5);
                    border-radius:10px; padding:1rem 1.4rem; margin-bottom:1rem;">
            <div style="color:#f87171; font-weight:700;">⚠️ ¿Estás seguro? Esta acción no se puede deshacer.</div>
        </div>
        """, unsafe_allow_html=True)

        col_confirm, col_cancel, _ = st.columns([1, 1, 2])

        with col_confirm:
            if st.button("✅ Sí, borrar todo", type="primary",
                         use_container_width=True, key="btn_reset_confirm"):
                import os
                from config import DATA_DIR

                # Resetear participantes
                with open(os.path.join(DATA_DIR, "participantes.csv"), "w", encoding="utf-8") as f:
                    f.write("usuario_id,nombre,email,fecha_registro\n")

                # Resetear pronósticos
                with open(os.path.join(DATA_DIR, "pronosticos.csv"), "w", encoding="utf-8") as f:
                    f.write("pronostico_id,usuario_id,partido_id,goles_local,goles_visitante,fecha_carga\n")

                # Resetear resultados
                with open(os.path.join(DATA_DIR, "resultados.csv"), "w", encoding="utf-8") as f:
                    f.write("partido_id,goles_local,goles_visitante,fecha_carga\n")

                st.session_state.confirm_reset = False
                st.success("✅ Datos reseteados correctamente. Podés empezar de cero.")
                st.balloons()
                st.rerun()

        with col_cancel:
            if st.button("❌ Cancelar", use_container_width=True, key="btn_reset_cancel"):
                st.session_state.confirm_reset = False
                st.rerun()
