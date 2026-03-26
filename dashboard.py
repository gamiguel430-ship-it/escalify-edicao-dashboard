import streamlit as st
import requests
import pandas as pd
import re
from datetime import datetime

# --- CONFIGURAÇÕES DO SERVIDOR ---
API_KEY = st.secrets["TRELLO_KEY"]
TOKEN = st.secrets["TRELLO_TOKEN"]

# IDs DAS LISTAS (Mude o ID_EDICOES para o da sua nova lista)
LISTA_PERFORMANCE_ID = '67e4262e8b3b917efd0b6ae1'
LISTA_EDICOES_ID = 'COLE_AQUI_O_ID_DA_OUTRA_LISTA' 

st.set_page_config(page_title="Escalify Tech Ops", layout="wide", page_icon="⚡")

# --- CSS TECH STYLE ---
st.markdown("""
    <style>
    .main { background-color: #0b0e14; color: #e0e0e0; }
    div[data-testid="stMetric"] {
        background: rgba(16, 20, 28, 0.8);
        border: 1px solid #1f2937;
        padding: 20px;
        border-radius: 15px;
    }
    .tech-header {
        font-family: 'JetBrains Mono', monospace;
        color: #00d4ff;
        border-left: 5px solid #00d4ff;
        padding-left: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

def buscar_cards(id_lista):
    url = f"https://api.trello.com/1/lists/{id_lista}/cards?key={API_KEY}&token={TOKEN}&members=true&fields=name,dateLastActivity"
    res = requests.get(url)
    return res.json() if res.status_code == 200 else []

# --- PROCESSAMENTO DE DADOS ---
mes_atual = datetime.now().month
data_perf = buscar_cards(LISTA_PERFORMANCE_ID)
data_edicoes = buscar_cards(LISTA_EDICOES_ID)

def filtrar_dados(dados_brutos):
    entregas = []
    for card in dados_brutos:
        data_card = datetime.strptime(card['dateLastActivity'], '%Y-%m-%dT%H:%M:%S.%fZ')
        if data_card.month != mes_atual: continue
        
        nome_card = card['name']
        membros = [m['fullName'].lower() for m in card.get('members', [])]
        match_anuncio = re.search(r'(\d+)\s*[Aa]n[uú]ncio', nome_card)
        qtd = int(match_anuncio.group(1)) if match_anuncio else 1
        
        editor = "Outros"
        if any("suel" in m for m in membros) or "suel" in nome_card.lower(): editor = "Suellen Santos"
        elif any("gabriel" in m for m in membros) or "gabriel" in nome_card.lower(): editor = "Gabriel Miguel"
        elif any("heitor" in m for m in membros) or "heitor" in nome_card.lower(): editor = "Heitor Leao"
        
        if editor != "Outros":
            entregas.append({"Editor": editor, "Qtd": qtd, "Projeto": nome_card})
    return pd.DataFrame(entregas)

df_perf = filtrar_dados(data_perf)
df_edicoes = filtrar_dados(data_edicoes)

# --- LAYOUT DASHBOARD ---
st.markdown(f"<h1 class='tech-header'>ESCALIFY HUB // MARÇO</h1>", unsafe_allow_html=True)

# Nova Linha de Métricas
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("📦 PERFORMANCE", f"{df_perf['Qtd'].sum() if not df_perf.empty else 0} vídeos")
with c2:
    st.metric("🎨 EDIDÇÕES ESCALIFY", f"{df_edicoes['Qtd'].sum() if not df_edicoes.empty else 0} itens")
with c3:
    total_geral = (df_perf['Qtd'].sum() if not df_perf.empty else 0) + (df_edicoes['Qtd'].sum() if not df_edicoes.empty else 0)
    st.metric("🚀 TOTAL GERAL", f"{total_geral}")

st.markdown("---")

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 Ranking Performance")
    if not df_perf.empty:
        st.bar_chart(df_perf.groupby('Editor')['Qtd'].sum(), color="#00d4ff", horizontal=True)

with col_right:
    st.subheader("🎬 Ranking Edições")
    if not df_edicoes.empty:
        st.bar_chart(df_edicoes.groupby('Editor')['Qtd'].sum(), color="#ff007f", horizontal=True) # Cor Rosa Choque pra diferenciar
