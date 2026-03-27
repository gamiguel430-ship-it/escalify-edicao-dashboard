import streamlit as st
import requests
import pandas as pd
import re
from datetime import datetime
import os
import streamlit.components.v1 as components

# --- CONFIGURAÇÕES ---
API_KEY = st.secrets["TRELLO_KEY"]
TOKEN   = st.secrets["TRELLO_TOKEN"]

LISTA_SERVICOS_ID     = '67e4262e8b3b917efd0b6ae1'
LISTA_INFOPRODUTOS_ID = '69af2a85b62772bd7d29463e'
META_MENSAL = 1000

st.set_page_config(page_title="Performance Edição — Escalify", layout="wide", page_icon="⚡")

# ── Auto-refresh 5 min ──
components.html("<script>setTimeout(()=>window.parent.location.reload(),300000)</script>", height=0)

# ══════════════════════════════════════════════
# CSS BASE
# ══════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="block-container"] {
    background-color: #0f0f13 !important;
    font-family: 'Inter', sans-serif !important;
    color: #d4d8e1 !important;
}
[data-testid="stSidebar"] {
    background-color: #13131a !important;
    border-right: 1px solid rgba(0,212,255,0.08) !important;
}
[data-testid="stSidebar"] * { color: #8a9ab5 !important; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="block-container"] {
    padding-top: 20px !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}
h2, h3,
[data-testid="stHeading"] h2,
[data-testid="stHeading"] h3 {
    font-family: 'Inter', sans-serif !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    color: rgba(255,255,255,0.28) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.09em !important;
    border-bottom: 1px solid rgba(255,255,255,0.05) !important;
    padding-bottom: 8px !important;
    margin-top: 24px !important;
    margin-bottom: 12px !important;
}
hr { border-color: rgba(255,255,255,0.06) !important; margin: 6px 0 !important; }
[data-testid="stVegaLiteChart"] {
    background: #16161f !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
    padding: 16px !important;
}
[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(0,212,255,0.15) !important;
    border-radius: 8px !important;
    color: #d4d8e1 !important;
}
[data-testid="stAlert"] {
    background: rgba(0,212,255,0.05) !important;
    border: 1px solid rgba(0,212,255,0.15) !important;
    border-radius: 10px !important;
    color: rgba(0,212,255,0.7) !important;
}
/* remove iframe border */
iframe { border: none !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════
with st.sidebar:
    if os.path.exists("logo.jpeg"):
        st.image("logo.jpeg", use_container_width=True)
    elif os.path.exists("image_0.png"):
        st.image("image_0.png", use_container_width=True)
    else:
        st.markdown("""
        <div style="text-align:center;padding:16px 0 8px">
            <div style="width:52px;height:52px;background:linear-gradient(135deg,#001f3f,#00d4ff);
                        border-radius:12px;display:flex;align-items:center;justify-content:center;
                        font-size:24px;font-weight:700;color:#fff;margin:0 auto;
                        font-family:'JetBrains Mono',monospace;">S</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;padding:6px 0 20px;
                border-bottom:1px solid rgba(0,212,255,0.1);margin-bottom:20px">
        <div style="font-family:'JetBrains Mono',monospace;font-size:16px;font-weight:600;
                    color:#00d4ff;letter-spacing:0.08em">ESCALIFY</div>
        <div style="font-size:10px;color:rgba(0,212,255,0.4);letter-spacing:0.12em;
                    text-transform:uppercase;margin-top:2px">Dashboard de Edição</div>
    </div>
    <div style="font-size:9.5px;font-weight:600;color:rgba(0,212,255,0.4);
                text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px">📅 Período</div>
    """, unsafe_allow_html=True)

    mes_selecionado = st.selectbox(
        "", ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
             "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"],
        index=2, label_visibility="collapsed"
    )


# ══════════════════════════════════════════════
# DADOS TRELLO
# ══════════════════════════════════════════════
def buscar_cards(id_lista):
    url = (f"https://api.trello.com/1/lists/{id_lista}/cards"
           f"?key={API_KEY}&token={TOKEN}&members=true&fields=name,dateLastActivity")
    res = requests.get(url)
    return res.json() if res.status_code == 200 else []

mapa_meses = {m: i+1 for i, m in enumerate([
    "Janeiro","Fevereiro","Março","Abril","Maio","Junho",
    "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"
])}

registos = []

def processar_lista(dados, tipo, lista):
    for card in dados:
        dt = datetime.strptime(card['dateLastActivity'], '%Y-%m-%dT%H:%M:%S.%fZ')
        if dt.month != mapa_meses[mes_selecionado]:
            continue
        nome    = card['name']
        texto   = nome.lower()
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
        if tipo == "Serviços/Criativos":
            m = re.search(r'(\d+)\s*[Aa]n[uú]ncio', nome)
            qtd = int(m.group(1)) if m else 1
        elif tipo == "Infoprodutos":
            mr  = re.search(r'[A-Za-z]*\s*(\d+)\s*-\s*[A-Za-z]*\s*(\d+)', nome)
            mmq = re.search(r'(\d+)\s*ml', texto)
            mms = re.search(r'ml\d*', texto)
            if mr:
                qtd = (abs(int(mr.group(2)) - int(mr.group(1))) + 1) * 2
            elif mmq:
                qtd = int(mmq.group(1))
            elif mms:
                qtd = 1
            else:
                qtd = 2

        lista.append({"Editor": editor, "Qtd": qtd, "Segmento": tipo, "Projeto": nome})

data_serv = buscar_cards(LISTA_SERVICOS_ID)
data_info = buscar_cards(LISTA_INFOPRODUTOS_ID)
if data_serv: processar_lista(data_serv, "Serviços/Criativos", registos)
if data_info: processar_lista(data_info, "Infoprodutos", registos)

df = pd.DataFrame(registos)


# ══════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════
FONT_IMPORT = "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');"
BASE_RESET  = "* { box-sizing:border-box; margin:0; padding:0; font-family:'Inter',sans-serif; }"

def cor_editor(nome, mvp):
    if nome == mvp:
        return "#f59e0b"
    return {"Suellen Santos":"#a78bfa","Gabriel Miguel":"#5dcaa5","Heitor Leão":"#60a5fa"}.get(nome,"#8a9ab5")

def iniciais(nome):
    p = nome.split()
    return (p[0][0]+p[-1][0]).upper() if len(p)>=2 else nome[:2].upper()


# ══════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════
if not df.empty:

    resumo      = df.groupby('Editor')['Qtd'].sum().sort_values(ascending=False)
    mvp_nome    = resumo.idxmax()
    mvp_qtd     = int(resumo.max())
    total_geral = int(df['Qtd'].sum())
    pct         = min(round((total_geral / META_MENSAL) * 100), 100)
    total_serv  = int(df[df['Segmento']=="Serviços/Criativos"]['Qtd'].sum())
    total_info  = int(df[df['Segmento']=="Infoprodutos"]['Qtd'].sum())
    segundo     = int(resumo.iloc[1]) if len(resumo) > 1 else 0
    vantagem    = f"+{round(((mvp_qtd-segundo)/segundo)*100)}% vs 2º" if segundo > 0 else "—"

    # ── CABEÇALHO ──────────────────────────────
    components.html(f"""<style>{FONT_IMPORT}{BASE_RESET}</style>
    <div style="display:flex;align-items:baseline;gap:10px;margin-bottom:4px;">
        <span style="font-size:20px;font-weight:600;color:#f0f4ff;letter-spacing:-0.02em;">
            Performance Edição — Escalify</span>
        <span style="font-family:'JetBrains Mono',monospace;font-size:12px;color:#00d4ff;
                     background:rgba(0,212,255,0.08);border:1px solid rgba(0,212,255,0.18);
                     border-radius:6px;padding:3px 10px;">{mes_selecionado.upper()}</span>
    </div>
    <div style="font-size:11px;color:rgba(255,255,255,0.25);">
        Atualização automática a cada 5 min · Dados via Trello</div>
    """, height=50)

    # ── MVP BANNER ─────────────────────────────
    components.html(f"""<style>{FONT_IMPORT}{BASE_RESET}
    .mvp{{display:flex;align-items:stretch;background:#16161f;
          border:1px solid rgba(255,255,255,0.08);border-radius:14px;overflow:hidden;}}
    .bar{{width:5px;flex-shrink:0;background:linear-gradient(180deg,#f59e0b,#d97706);}}
    .body{{flex:1;display:flex;align-items:center;gap:20px;padding:18px 22px;}}
    .crown{{width:52px;height:52px;border-radius:50%;flex-shrink:0;
            background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.25);
            display:flex;align-items:center;justify-content:center;font-size:24px;}}
    .info{{flex:1;}}
    .eyebrow{{font-size:10px;font-weight:600;color:#f59e0b;text-transform:uppercase;
              letter-spacing:0.1em;margin-bottom:4px;display:flex;align-items:center;gap:7px;}}
    .pill{{font-size:9px;background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.22);
           border-radius:4px;padding:2px 7px;letter-spacing:0.05em;}}
    .mname{{font-size:22px;font-weight:600;color:#f0f4ff;letter-spacing:-0.02em;
            line-height:1.1;margin-bottom:4px;}}
    .msub{{font-size:12px;color:rgba(255,255,255,0.38);}}
    .msub strong{{color:#f0f4ff;font-weight:500;}}
    .divider{{width:1px;background:rgba(255,255,255,0.07);margin:0 4px;align-self:stretch;}}
    .stats{{display:flex;gap:26px;flex-shrink:0;padding-left:24px;}}
    .stat{{text-align:center;}}
    .sval{{font-size:20px;font-weight:600;line-height:1;font-family:'JetBrains Mono',monospace;}}
    .slbl{{font-size:9.5px;color:rgba(255,255,255,0.3);margin-top:3px;
           text-transform:uppercase;letter-spacing:0.06em;}}
    </style>
    <div class="mvp">
      <div class="bar"></div>
      <div class="body">
        <div class="crown">👑</div>
        <div class="info">
          <div class="eyebrow">MVP da Agência
            <span class="pill">{mes_selecionado} 2025</span>
          </div>
          <div class="mname">{mvp_nome}</div>
          <div class="msub">Liderando com <strong>{mvp_qtd} criativos</strong> entregues este mês</div>
        </div>
        <div class="divider"></div>
        <div class="stats">
          <div class="stat">
            <div class="sval" style="color:#5dcaa5">{mvp_qtd}</div>
            <div class="slbl">Entregas</div>
          </div>
          <div class="stat">
            <div class="sval" style="color:#a78bfa">#1</div>
            <div class="slbl">Ranking</div>
          </div>
          <div class="stat">
            <div class="sval" style="color:#f59e0b">{vantagem}</div>
            <div class="slbl">Vantagem</div>
          </div>
        </div>
      </div>
    </div>
    """, height=108)

    # ── META BAR ───────────────────────────────
    components.html(f"""<style>{FONT_IMPORT}{BASE_RESET}
    .meta{{display:flex;align-items:center;gap:14px;background:#16161f;
           border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:13px 20px;}}
    .ml{{font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:500;
         color:rgba(255,255,255,0.45);white-space:nowrap;}}
    .mt{{flex:1;height:7px;background:rgba(255,255,255,0.05);border-radius:4px;overflow:hidden;}}
    .mf{{height:100%;width:{pct}%;background:linear-gradient(90deg,#001f3f,#00d4ff);
         box-shadow:0 0 10px rgba(0,212,255,0.25);border-radius:4px;}}
    .mv{{font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:600;
         color:#00d4ff;white-space:nowrap;}}
    </style>
    <div class="meta">
      <span class="ml">🎯 Meta — {META_MENSAL:,} criativos</span>
      <div class="mt"><div class="mf"></div></div>
      <span class="mv">{total_geral:,} / {META_MENSAL:,} &nbsp;·&nbsp; {pct}%</span>
    </div>
    """, height=62)

    # ── KPI CARDS ──────────────────────────────
    kpis = [
        ("Serviços / Criativos", total_serv,  "#f59e0b", "linear-gradient(90deg,#b07510,#f59e0b)"),
        ("Infoprodutos",          total_info,  "#5dcaa5", "linear-gradient(90deg,#0f9068,#5dcaa5)"),
        ("Total Geral",           total_geral, "#00d4ff", "linear-gradient(90deg,#001f3f,#00d4ff)"),
    ]
    kpi_cards = "".join(f"""
    <div style="background:#16161f;border:1px solid rgba(255,255,255,0.07);
                border-radius:12px;padding:18px 20px;position:relative;overflow:hidden;">
      <div style="position:absolute;top:0;left:0;right:0;height:2px;
                  border-radius:12px 12px 0 0;background:{g};"></div>
      <div style="font-size:10px;font-weight:600;color:rgba(255,255,255,0.3);
                  text-transform:uppercase;letter-spacing:0.07em;margin-bottom:10px;">{l}</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:28px;font-weight:600;
                  line-height:1;margin-bottom:4px;color:{c};">{v:,}</div>
      <div style="font-size:11px;color:rgba(255,255,255,0.25);">criativos</div>
    </div>""" for l, v, c, g in kpis)

    components.html(f"""<style>{FONT_IMPORT}{BASE_RESET}
    .grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;}}
    </style>
    <div class="grid">{kpi_cards}</div>
    """, height=110)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── GRÁFICO ────────────────────────────────
    st.subheader("Ranking Geral Segmentado")
    df_grafico = df.groupby(['Editor','Segmento'])['Qtd'].sum().unstack().fillna(0)
    if not df_grafico.empty:
        st.bar_chart(df_grafico, horizontal=True, color=["#00d4ff","#001f3f"])

    # ── TABELA HTML ────────────────────────────
    st.subheader("Log Completo de Operações")

    seg_pill = {
        "Serviços/Criativos": ("rgba(56,138,221,0.1)",  "#5ba5e8", "rgba(56,138,221,0.18)"),
        "Infoprodutos":        ("rgba(109,93,255,0.1)", "#a78bfa",  "rgba(109,93,255,0.18)"),
    }

    linhas = ""
    for _, row in df.iterrows():
        ed  = row["Editor"]; seg = row["Segmento"]
        qtd = int(row["Qtd"]); proj = row["Projeto"]
        c   = cor_editor(ed, mvp_nome)
        ini = iniciais(ed)
        sbg, scol, sbord = seg_pill.get(seg, ("rgba(255,255,255,0.06)","#aaa","transparent"))
        hl  = "background:rgba(245,158,11,0.03);" if ed == mvp_nome else ""
        ec  = f"color:{c};" if ed == mvp_nome else "color:rgba(255,255,255,0.7);"

        linhas += f"""
        <tr style="{hl}border-bottom:1px solid rgba(255,255,255,0.04);">
          <td style="padding:10px 18px;">
            <div style="display:flex;align-items:center;gap:9px;">
              <div style="width:26px;height:26px;border-radius:50%;flex-shrink:0;
                          background:rgba(0,0,0,0.3);border:1px solid {c}44;
                          display:flex;align-items:center;justify-content:center;
                          font-size:9.5px;font-weight:600;color:{c};">{ini}</div>
              <span style="{ec}font-size:12.5px;">{ed}</span>
            </div>
          </td>
          <td style="padding:10px 18px;">
            <span style="display:inline-flex;align-items:center;padding:2px 9px;border-radius:20px;
                         font-size:10px;font-weight:600;
                         background:{sbg};color:{scol};border:1px solid {sbord};">{seg}</span>
          </td>
          <td style="padding:10px 18px;">
            <span style="display:inline-flex;align-items:center;justify-content:center;
                         min-width:28px;height:20px;background:rgba(255,255,255,0.06);
                         border-radius:4px;font-size:11px;color:rgba(255,255,255,0.6);">{qtd}</span>
          </td>
          <td style="padding:10px 18px;max-width:360px;">
            <span style="display:block;color:rgba(255,255,255,0.5);font-size:11.5px;
                         white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{proj}</span>
          </td>
        </tr>"""

    n   = len(df)
    alt = min(52 + n * 44, 560)

    components.html(f"""<style>{FONT_IMPORT}{BASE_RESET}
    .wrap{{background:#16161f;border:1px solid rgba(255,255,255,0.07);
           border-radius:12px;overflow:hidden;}}
    .head{{display:flex;align-items:center;justify-content:space-between;
           padding:13px 18px;border-bottom:1px solid rgba(255,255,255,0.06);}}
    .htitle{{font-size:12.5px;font-weight:600;color:#e2e2e6;}}
    .search{{background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.09);
             border-radius:6px;padding:5px 12px;color:rgba(255,255,255,0.3);
             font-size:11.5px;width:150px;}}
    .scroll{{overflow-y:auto;max-height:480px;}}
    table{{width:100%;border-collapse:collapse;}}
    thead th{{padding:9px 18px;text-align:left;font-size:10px;font-weight:600;
              color:rgba(0,212,255,0.5);text-transform:uppercase;letter-spacing:0.08em;
              background:rgba(0,212,255,0.04);border-bottom:1px solid rgba(0,212,255,0.08);
              white-space:nowrap;}}
    tbody tr:last-child{{border-bottom:none!important;}}
    tbody tr:hover{{background:rgba(255,255,255,0.02)!important;}}
    </style>
    <div class="wrap">
      <div class="head">
        <span class="htitle">Log de operações · {mes_selecionado}</span>
        <input class="search" placeholder="Buscar projeto..." disabled>
      </div>
      <div class="scroll">
        <table>
          <thead><tr>
            <th>Editor</th><th>Segmento</th><th>Qtd</th><th>Projeto</th>
          </tr></thead>
          <tbody>{linhas}</tbody>
        </table>
      </div>
    </div>
    """, height=alt + 60)

# ── ESTADO VAZIO ───────────────────────────────
else:
    components.html(f"""<style>{FONT_IMPORT}{BASE_RESET}</style>
    <div style="text-align:center;padding:60px 20px;">
      <div style="font-size:36px;margin-bottom:14px;">📭</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:15px;color:rgba(0,212,255,0.6);">
        Aguardando dados de {mes_selecionado}...</div>
      <div style="font-size:11px;color:rgba(255,255,255,0.22);margin-top:8px;">
        Verifique se os cartões no Trello têm a data correta.</div>
    </div>
    """, height=200)
