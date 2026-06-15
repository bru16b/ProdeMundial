# utils/styles.py — Estilos CSS compartidos entre todas las páginas

import streamlit as st


def inject_global_css():
    """Inyecta el CSS global de la aplicación."""
    st.markdown("""
    <style>
    /* ── Fuentes ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Fondo ── */
    [data-testid="stAppViewContainer"] > .main {
        background: linear-gradient(135deg, #0d1117 0%, #0d1117 60%, #1a1f2e 100%);
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: #0d1117;
        border-right: 1px solid #21262d;
    }
    [data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }

    /* ── Encabezado principal ── */
    .prode-header {
        background: linear-gradient(135deg, #1a1f2e 0%, #0d1117 100%);
        border: 1px solid #21262d;
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }
    .prode-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(249,115,22,0.12) 0%, transparent 70%);
        pointer-events: none;
    }
    .prode-header h1 {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #f97316, #fb923c, #fbbf24);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        line-height: 1.2;
    }
    .prode-header p {
        color: #8b949e;
        margin: 0.4rem 0 0;
        font-size: 1rem;
    }

    /* ── Tarjetas métricas ── */
    .metric-card {
        background: #161b22;
        border: 1px solid #21262d;
        border-radius: 12px;
        padding: 1.4rem;
        text-align: center;
        transition: border-color 0.2s, transform 0.2s;
    }
    .metric-card:hover {
        border-color: #f97316;
        transform: translateY(-2px);
    }
    .metric-card .metric-value {
        font-size: 2.4rem;
        font-weight: 800;
        color: #f97316;
        line-height: 1;
    }
    .metric-card .metric-label {
        font-size: 0.8rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 0.3rem;
    }

    /* ── Tarjetas de partido ── */
    .match-card {
        background: #161b22;
        border: 1px solid #21262d;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: border-color 0.2s;
    }
    .match-card:hover {
        border-color: #30363d;
    }
    .match-card .teams {
        font-size: 1rem;
        font-weight: 600;
        color: #e6edf3;
    }
    .match-card .meta {
        font-size: 0.78rem;
        color: #8b949e;
        margin-top: 0.2rem;
    }
    .match-card .score {
        font-size: 1.6rem;
        font-weight: 800;
        color: #f97316;
        min-width: 80px;
        text-align: center;
    }

    /* ── Badges de estado ── */
    .badge {
        display: inline-block;
        padding: 0.2rem 0.7rem;
        border-radius: 99px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.04em;
    }
    .badge-exacto { background: rgba(34,197,94,0.15); color: #22c55e; border: 1px solid rgba(34,197,94,0.3); }
    .badge-resultado { background: rgba(234,179,8,0.15); color: #eab308; border: 1px solid rgba(234,179,8,0.3); }
    .badge-error { background: rgba(239,68,68,0.15); color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }
    .badge-pendiente { background: rgba(99,102,241,0.15); color: #818cf8; border: 1px solid rgba(99,102,241,0.3); }
    .badge-jugado { background: rgba(249,115,22,0.15); color: #f97316; border: 1px solid rgba(249,115,22,0.3); }

    /* ── Sección título ── */
    .section-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #e6edf3;
        border-left: 3px solid #f97316;
        padding-left: 0.75rem;
        margin: 1.5rem 0 1rem;
    }

    /* ── Tabla de ranking ── */
    .ranking-row {
        display: flex;
        align-items: center;
        background: #161b22;
        border: 1px solid #21262d;
        border-radius: 10px;
        padding: 0.8rem 1.2rem;
        margin-bottom: 0.5rem;
        transition: border-color 0.2s;
    }
    .ranking-row:hover { border-color: #30363d; }
    .ranking-pos {
        font-size: 1.1rem;
        font-weight: 800;
        color: #8b949e;
        width: 36px;
        flex-shrink: 0;
    }
    .ranking-pos.gold { color: #fbbf24; }
    .ranking-pos.silver { color: #94a3b8; }
    .ranking-pos.bronze { color: #cd7f32; }
    .ranking-name {
        flex: 1;
        font-size: 0.95rem;
        font-weight: 600;
        color: #e6edf3;
    }
    .ranking-pts {
        font-size: 1.2rem;
        font-weight: 800;
        color: #f97316;
        min-width: 50px;
        text-align: right;
    }

    /* ── Formularios ── */
    .stNumberInput > div > div > input {
        background: #161b22;
        border-color: #30363d;
        color: #e6edf3;
        border-radius: 8px;
    }
    .stSelectbox > div > div {
        background: #161b22;
        border-color: #30363d;
    }

    /* ── Botón primario ── */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(249,115,22,0.3);
    }

    /* ── Divider ── */
    hr { border-color: #21262d !important; }

    /* ── Info box ── */
    .info-box {
        background: rgba(99,102,241,0.08);
        border: 1px solid rgba(99,102,241,0.25);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        color: #a5b4fc;
        font-size: 0.88rem;
    }
    </style>
    """, unsafe_allow_html=True)


def render_header(title: str, subtitle: str = ""):
    """Renderiza el encabezado principal de una página."""
    sub_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(f"""
    <div class="prode-header">
        <h1>{title}</h1>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


def render_metric(value, label: str):
    """Renderiza una tarjeta métrica."""
    return f"""
    <div class="metric-card">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """


def render_section_title(title: str):
    """Renderiza un título de sección con borde naranja."""
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
