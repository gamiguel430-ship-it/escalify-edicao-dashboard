import streamlit as st
import requests
import pandas as pd
import re
from datetime import datetime
import os
import streamlit.components.v1 as components

# --- CONFIGURAÇÕES ---
API_KEY = st.secrets["TRELLO_KEY"]
TOKEN = st.secrets["TRELLO_TOKEN"]

# IDs DAS LISTAS NO TRELLO
LISTA_SERVICOS_ID = '67e4262e8b3b917efd0b6ae1'
LISTA_INFOPRODUTOS_ID = '69af2a85b62772bd7d29463e'

# 🎯 META MENSAL
META_MENSAL = 1000

st.set_page_config(page_title="Performance Edição — Escalify", layout="wide", page_icon="⚡")

# --- AUTO-REFRESH (5 minutos) ---
components.html(
    """
    <script>
    setTimeout(function(){
        window.parent.location.reload();
    }, 300000);
    </script>
    """,
    height=0
)

# ─────────────────────────────────────────────
# CSS — ESCALIFY DESIGN SYSTEM
# Paleta: fundo #0b0e14 · superfície #10141c
# Ciano Escalify: #00d4ff · Azul escuro: #001f3f
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── BASE ── */
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: #0b0e14 !important;
    color: #d4d8e1;
    font-family: 'Inter', sans-serif;
}
[data-testid="stSidebar"] {
    background-color: #0d1017 !important;
    border-right: 1px solid rgba(0, 212, 255, 0.08) !important;
}
[data-testid="stSidebar"] * { color: #8a9ab5 !important; }

/* Oculta rodapé e menu do Streamlit */
#MainMenu, footer, header { visibility: hidden; }

/* ── SIDEBAR HEADER ── */
.sidebar-brand {
    text-align: center;
    padding: 8px 0 20px;
    border-bottom: 1px solid rgba(0, 212, 255, 0.1);
    margin-bottom: 20px;
}
.sidebar-brand-name {
    font-family: 'JetBrains Mono', monospace;
    font-size: 18px;
    font-weight: 600;
    color: #00d4ff !important;
    letter-spacing: 0.08em;
    margin-top: 10px;
}
.sidebar-brand-sub {
    font-size: 10px;
    color: rgba(0, 212, 255, 0.45) !important;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 2px;
}

/* ── FILTRO PERÍODO ── */
.period-label {
    font-size: 9.5px !important;
    font-weight: 600;
    color: rgba(0, 212, 255, 0.45) !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 4px;
}

/* ── TÍTULO DA PÁGINA ── */
.page-header {
    display: flex;
    align-items: baseline;
    gap: 12px;
    margin-bottom: 6px;
}
.page-title {
    font-family: 'Inter', sans-serif;
    font-size: 22px;
    font-weight: 600;
    color: #f0f4ff;
    letter-spacing: -0.02em;
    margin: 0;
}
.page-month {
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    color: #00d4ff;
    background: rgba(0, 212, 255, 0.08);
    border: 1px solid rgba(0, 212, 255, 0.18);
    border-radius: 6px;
    padding: 3px 10px;
}
.page-sub {
    font-size: 12px;
    color: rgba(255,255,255,0.28);
    margin-bottom: 22px;
    margin-top: 4px;
}

/* ── MVP BANNER ── */
.mvp-banner {
    display: flex;
    align-items: center;
    gap: 0;
    background: #10141c;
    border: 1px solid rgba(0, 212, 255, 0.12);
    border-radius: 14px;
    overflow: hidden;
    margin-bottom: 16px;
}
.mvp-accent-bar {
    width: 5px;
    align-self: stretch;
    background: linear-gradient(180deg, #00d4ff 0%, #001f3f 100%);
    flex-shrink: 0;
}
.mvp-body {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 18px 22px;
}
.mvp-crown-wrap {
    width: 52px;
    height: 52px;
    border-radius: 50%;
    background: rgba(0, 212, 255, 0.08);
    border: 1px solid rgba(0, 212, 255, 0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    flex-shrink: 0;
}
.mvp-info { flex: 1; }
.mvp-eyebrow {
    font-size: 10px;
    font-weight: 600;
    color: #00d4ff;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.mvp-eyebrow-badge {
    font-size: 9px;
    background: rgba(0, 212, 255, 0.1);
    border: 1px solid rgba(0, 212, 255, 0.2);
    border-radius: 4px;
    padding: 2px 7px;
    letter-spacing: 0.06em;
}
.mvp-name {
    font-size: 24px;
    font-weight: 600;
    color: #f0f4ff;
    letter-spacing: -0.02em;
    line-height: 1;
    margin-bottom: 4px;
}
.mvp-sub {
    font-size: 12px;
    color: rgba(255,255,255,0.38);
}
.mvp-sub strong { color: #f0f4ff; font-weight: 500; }
.mvp-stats {
    display: flex;
    gap: 28px;
    flex-shrink: 0;
    border-left: 1px solid rgba(255,255,255,0.06);
    padding-left: 28px;
}
.mvp-stat { text-align: center; }
.mvp-stat-val {
    font-size: 20px;
    font-weight: 600;
    line-height: 1;
    font-family: 'JetBrains Mono', monospace;
}
.mvp-stat-lbl {
    font-size: 10px;
    color: rgba(255,255,255,0.3);
    margin-top: 3px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* ── META BAR ── */
.meta-wrap {
    background: #10141c;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 14px 20px;
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 18px;
}
.meta-label {
    font-size: 12px;
    font-weight: 500;
    color: rgba(255,255,255,0.45);
    white-space: nowrap;
    font-family: 'JetBrains Mono', monospace;
}
.meta-track {
    flex: 1;
    height: 7px;
    background: rgba(255,255,255,0.05);
    border-radius: 4px;
    overflow: hidden;
}
.meta-fill {
    height: 100%;
    border-radius: 4px;
    background: linear-gradient(90deg, #001f3f 0%, #00d4ff 100%);
    box-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
}
.meta-val {
    font-size: 12px;
    font-weight: 600;
    color: #00d4ff;
    white-space: nowrap;
    font-family: 'JetBrains Mono', monospace;
}

/* ── KPI CARDS ── */
div[data-testid="stMetric"] {
    background: #10141c !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-top: 2px solid #00d4ff !important;
    border-radius: 12px !important;
    padding: 18px 20px !important;
    box-shadow: none !important;
    transition: border-color 0.2s, box-shadow 0.2s;
}
div[data-testid="stMetric"]:hover {
    border-color: rgba(0, 212, 255, 0.35) !important;
    box-shadow: 0 0 18px rgba(0, 212, 255, 0.1) !important;
    transform: none !important;
}
div[data-testid="stMetric"] label {
    font-size: 10px !important;
    font-weight: 600 !important;
    color: rgba(0, 212, 255, 0.55) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    font-family: 'Inter', sans-serif !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-size: 26px !important;
    font-weight: 600 !important;
    color: #f0f4ff !important;
    font-family: 'JetBrains Mono', monospace !important;
    letter-spacing: -0.02em !important;
}
div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
    font-size: 11px !important;
}

/* ── SECTION TITLES ── */
h2, h3,
[data-testid="stHeading"] h2,
[data-testid="stHeading"] h3 {
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    color: rgba(255,255,255,0.5) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    margin-top: 24px !important;
    margin-bottom: 12px !important;
    padding-bottom: 8px !important;
    border-bottom: 1px solid rgba(255,255,255,0.06) !important;
}

/* ── GRÁFICO DE BARRAS ── */
[data-testid="stVegaLiteChart"] {
    background: #10141c !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
    padding: 16px !important;
}

/* ── DATAFRAME / TABLE ── */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    background: #10141c !important;
}
[data-testid="stDataFrame"] table {
    background: #10141c !important;
}
[data-testid="stDataFrame"] thead th {
    background: rgba(0, 212, 255, 0.05) !important;
    color: rgba(0, 212, 255, 0.6) !important;
    font-size: 10px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    border-bottom: 1px solid rgba(0, 212, 255, 0.1) !important;
}
[data-testid="stDataFrame"] tbody tr:hover td {
    background: rgba(0, 212, 255, 0.03) !important;
}
[data-testid="stDataFrame"] td {
    color: rgba(255,255,255,0.6) !important;
    font-size: 12.5px !important;
    border-bottom: 1px solid rgba(255,255,255,0.04) !important;
}

/* ── SELECTBOX ── */
[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(0, 212, 255, 0.15) !important;
    border-radius: 8px !important;
    color: #d4d8e1 !important;
    font-size: 13px !important;
}

/* ── SEPARADOR ── */
hr { border-color: rgba(255,255,255,0.06) !important; margin: 20px 0 !important; }

/* ── INFO BOX ── */
[data-testid="stAlert"] {
    background: rgba(0, 212, 255, 0.05) !important;
    border: 1px solid rgba(0, 212, 255, 0.15) !important;
    border-radius: 10px !important;
    color: rgba(0, 212, 255, 0.7) !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    # Logo da empresa
    if os.path.exists("logo.jpeg"):
        st.image("logo.jpeg", use_container_width=True)
    elif os.path.exists("image_0.png"):
        st.image("image_0.png", use_container_width=True)
    else:
        st.markdown("""
        <div style="text-align:center; padding: 20px 0 10px;">
            <div style="width:60px; height:60px; background:linear-gradient(135deg,#001f3f,#00d4ff);
                        border-radius:14px; display:flex; align-items:center; justify-content:center;
                        font-size:28px; font-weight:700; color:#fff; margin:0 auto; font-family:'JetBrains Mono',monospace;">
                S
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-name">ESCALIFY</div>
        <div class="sidebar-brand-sub">Dashboard de Edição</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="period-label">📅 Período</div>', unsafe_allow_html=True)
    mes_selecionado = st.selectbox(
        "",
        ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
         "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"],
        index=2,
        label_visibility="collapsed"
    )


# ─────────────────────────────────────────────
# FUNÇÕES DE DADOS
# ─────────────────────────────────────────────
def buscar_cards(id_lista):
    url = (f"https://api.trello.com/1/lists/{id_lista}/cards"
           f"?key={API_KEY}&token={TOKEN}&members=true&fields=name,dateLastActivity")
    res = requests.get(url)
    return res.json() if res.status_code == 200 else []


mapa_meses = {
    "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
    "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
    "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12,
}

registos = []


def processar_lista(dados_trello, tipo_trello, lista_final):
    for card in dados_trello:
        dt = datetime.strptime(card['dateLastActivity'], '%Y-%m-%dT%H:%M:%S.%fZ')
        if dt.month != mapa_meses[mes_selecionado]:
            continue

        nome = card['name']
        texto = nome.lower()
        membros = [m['fullName'].lower() for m in card.get('members', [])]

        editor = "Outros"
        if any("suel" in m for m in membros) or "suel" in texto or ".ss" in texto or ".suh" in texto:
            editor = "Suellen Santos"
        elif any("gabriel" in m for m in membros) or "gabriel" in texto or ".gm" in texto:
            editor = "Gabriel Miguel"
        elif any("heitor" in m for m in membros) or "heitor" in texto or ".hl" in texto:
            editor = "Heitor Leão"

        if editor == "Outros":
            continue

        qtd = 0
        if tipo_trello == "Serviços/Criativos":
            match = re.search(r'(\d+)\s*[Aa]n[uú]ncio', nome)
            qtd = int(match.group(1)) if match else 1

        elif tipo_trello == "Infoprodutos":
            match_range  = re.search(r'[A-Za-z]*\s*(\d+)\s*-\s*[A-Za-z]*\s*(\d+)', nome)
            match_ml_qtd = re.search(r'(\d+)\s*ml', texto)
            match_ml_single = re.search(r'ml\d*', texto)

            if match_range:
                inicio = int(match_range.group(1))
                fim    = int(match_range.group(2))
                qtd    = (abs(fim - inicio) + 1) * 2
            elif match_ml_qtd:
                qtd = int(match_ml_qtd.group(1))
            elif match_ml_single:
                qtd = 1
            else:
                qtd = 2

        lista_final.append({"Editor": editor, "Qtd": qtd, "Segmento": tipo_trello, "Projeto": nome})


# ─────────────────────────────────────────────
# BUSCAR DADOS
# ─────────────────────────────────────────────
data_serv = buscar_cards(LISTA_SERVICOS_ID)
data_info = buscar_cards(LISTA_INFOPRODUTOS_ID)

if data_serv:
    processar_lista(data_serv, "Serviços/Criativos", registos)
if data_info:
    processar_lista(data_info, "Infoprodutos", registos)

df = pd.DataFrame(registos)


# ─────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────
if not df.empty:

    # ── Cabeçalho ──
    st.markdown(f"""
    <div class="page-header">
        <span class="page-title">Performance Edição — Escalify</span>
        <span class="page-month">{mes_selecionado.upper()}</span>
    </div>
    <div class="page-sub">Atualização automática a cada 5 min · Dados via Trello</div>
    """, unsafe_allow_html=True)

    # ── MVP Banner ──
    resumo_total = df.groupby('Editor')['Qtd'].sum()
    mvp_nome     = resumo_total.idxmax()
    mvp_qtd      = int(resumo_total.max())
    mvp_rank     = "#1"
    mvp_delta    = "+18%"  # pode calcular dinamicamente se tiver dados históricos

    # Variação percentual vs 2º colocado
    sorted_vals = resumo_total.sort_values(ascending=False)
    if len(sorted_vals) > 1:
        segundo = int(sorted_vals.iloc[1])
        diff_pct = round(((mvp_qtd - segundo) / segundo) * 100) if segundo > 0 else 0
        mvp_delta = f"+{diff_pct}% vs 2º"

    st.markdown(f"""
    <div class="mvp-banner">
        <div class="mvp-accent-bar"></div>
        <div class="mvp-body">
            <div class="mvp-crown-wrap">👑</div>
            <div class="mvp-info">
                <div class="mvp-eyebrow">
                    MVP da Agência
                    <span class="mvp-eyebrow-badge">{mes_selecionado} 2025</span>
                </div>
                <div class="mvp-name">{mvp_nome}</div>
                <div class="mvp-sub">Liderando com <strong>{mvp_qtd} criativos</strong> entregues este mês</div>
            </div>
            <div class="mvp-stats">
                <div class="mvp-stat">
                    <div class="mvp-stat-val" style="color:#00d4ff">{mvp_qtd}</div>
                    <div class="mvp-stat-lbl">Entregas</div>
                </div>
                <div class="mvp-stat">
                    <div class="mvp-stat-val" style="color:#a78bfa">{mvp_rank}</div>
                    <div class="mvp-stat-lbl">Ranking</div>
                </div>
                <div class="mvp-stat">
                    <div class="mvp-stat-val" style="color:#34d399">{mvp_delta}</div>
                    <div class="mvp-stat-lbl">Vantagem</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Barra de Meta ──
    total_geral   = int(df['Qtd'].sum())
    progresso_pct = min(round((total_geral / META_MENSAL) * 100), 100)

    st.markdown(f"""
    <div class="meta-wrap">
        <span class="meta-label">🎯 Meta — {META_MENSAL:,} criativos</span>
        <div class="meta-track">
            <div class="meta-fill" style="width:{progresso_pct}%"></div>
        </div>
        <span class="meta-val">{total_geral:,} / {META_MENSAL:,} &nbsp;·&nbsp; {progresso_pct}%</span>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI Cards ──
    df_serv = df[df['Segmento'] == "Serviços/Criativos"]
    df_info = df[df['Segmento'] == "Infoprodutos"]

    c1, c2, c3 = st.columns(3)
    c1.metric("📦 Serviços / Criativos", f"{int(df_serv['Qtd'].sum()):,}")
    c2.metric("🎥 Infoprodutos",          f"{int(df_info['Qtd'].sum()):,}")
    c3.metric("🚀 Total Geral",           f"{total_geral:,}")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Gráfico: Ranking por Editor ──
    st.subheader("Ranking Geral Segmentado")
    df_grafico = df.groupby(['Editor', 'Segmento'])['Qtd'].sum().unstack().fillna(0)
    if not df_grafico.empty:
        st.bar_chart(df_grafico, horizontal=True, color=["#00d4ff", "#001f3f"])

    # ── Tabela: Log Completo ──
    st.subheader("Log Completo de Operações")
    st.dataframe(
        df[["Editor", "Segmento", "Qtd", "Projeto"]],
        use_container_width=True,
        hide_index=True,
    )

else:
    st.markdown(f"""
    <div style="text-align:center; padding: 60px 20px;">
        <div style="font-size:32px; margin-bottom:12px;">📭</div>
        <div style="font-size:16px; color:rgba(0,212,255,0.6); font-family:'JetBrains Mono',monospace;">
            Aguardando dados de {mes_selecionado}...
        </div>
        <div style="font-size:12px; color:rgba(255,255,255,0.25); margin-top:8px;">
            Verifique se os cartões no Trello têm a data correta.
        </div>
    </div>
    """, unsafe_allow_html=True)
