import streamlit as st
import requests
import pandas as pd
import re
from datetime import datetime
import os

# --- CONFIGURAÇÕES ---
API_KEY = st.secrets["TRELLO_KEY"]
TOKEN = st.secrets["TRELLO_TOKEN"]
LISTA_ID = '67e4262e8b3b917efd0b6ae1'

st.set_page_config(page_title="Escalify Hub", layout="wide", page_icon="⚡")

# --- ESTILO TECH / DARK MODE ---
st.markdown("""
    <style>
    .main { background-color: #0b0e14; color: #e0e0e0; }
    div[data-testid="stMetric"] {
        background: rgba(16, 20, 28, 0.8);
        border: 1px solid #1f2937;
        padding: 15px;
        border-radius: 15px;
    }
    .tech-header {
        font-family: 'JetBrains Mono', monospace;
        color: #00d4ff;
        border-left: 5px solid #00d4ff;
        padding-left: 15px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL (LOGO AUTOMÁTICA) ---
with st.sidebar:
    # O código procura o arquivo direto na pasta do GitHub
    if os.path.exists("image_0.png"):
        st.image("image_0.png", width=180)
    else:
        st.markdown("<h2 style='color:#00d4ff;'>ESCALIFY</h2>", unsafe_allow_html=True)
    
    st.markdown("---")
    mes_selecionado = st.selectbox("📅 PERÍODO", ["Janeiro", "Fevereiro", "Março", "Abril"], index=2)

def carregar_dados():
    url = f"https://api.trello.com/1/lists/{LISTA_ID}/cards?key={API_KEY}&token={TOKEN}&members=true&fields=name,dateLastActivity"
    res = requests.get(url)
    return res.json() if res.status_code == 200 else []

# --- PROCESSAMENTO ---
data_trello = carregar_dados()
mapa_meses = {"Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4}

if data_trello:
    registos = []
    for card in data_trello:
        dt = datetime.strptime(card['dateLastActivity'], '%Y-%m-%dT%H:%M:%S.%fZ')
        if dt.month != mapa_meses[mes_selecionado]: continue
        
        nome = card['name']
        membros = [m['fullName'].lower() for m in card.get('members', [])]
        
        # Identificação Suellen Santos (2 Ls)
        editor = "Outros"
        if any("suel" in m for m in membros) or "suel" in nome.lower():
            editor = "Suellen Santos"
        elif any("gabriel" in m for m in membros) or "gabriel" in nome.lower():
            editor = "Gabriel Miguel"
        elif any("heitor" in m for m in membros) or "heitor" in nome.lower():
            editor = "Heitor Leão"
            
        if editor != "Outros":
            tipo = "Edição Escalify" if "escalify" in nome.lower() else "Performance"
            match = re.search(r'(\d+)\s*[Aa]n[uú]ncio', nome)
            qtd = int(match.group(1)) if match else 1
            registos.append({"Editor": editor, "Qtd": qtd, "Tipo": tipo, "Projeto": nome})

    df = pd.DataFrame(registos)

    if not df.empty:
        st.markdown(f"<h1 class='tech-header'>SYSTEM PERFORMANCE // {mes_selecionado}</h1>", unsafe_allow_html=True)
        
        df_perf = df[df['Tipo'] == "Performance"]
        df_escl = df[df['Tipo'] == "Edição Escalify"]

        c1, c2, c3 = st.columns(3)
        c1.metric("📦 PERFORMANCE", f"{df_perf['Qtd'].sum()} vids")
        c2.metric("🎨 EDIÇÕES ESCALIFY", f"{df_escl['Qtd'].sum()} vids")
        c3.metric("🚀 TOTAL GERAL", f"{df['Qtd'].sum()} vids")

        st.markdown("---")
        col_l, col_r = st.columns(2)
        with col_l:
            st.subheader("📊 Ranking Performance")
            st.bar_chart(df_perf.groupby('Editor')['Qtd'].sum(), color="#00d4ff", horizontal=True)
        with col_r:
            st.subheader("🎬 Ranking Edições")
            st.bar_chart(df_escl.groupby('Editor')['Qtd'].sum(), color="#ff007f", horizontal=True)
            
        st.subheader("📋 Log de Operações")
        st.dataframe(df[["Editor", "Tipo", "Qtd", "Projeto"]], use_container_width=True, hide_index=True)
    else:
        st.info("Aguardando dados de Março...")
