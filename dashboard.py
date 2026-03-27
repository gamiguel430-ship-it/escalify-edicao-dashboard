import streamlit as st
import requests
import pandas as pd
import re
from datetime import datetime

# --- CONFIGURAÇÕES DO SERVIDOR ---
API_KEY = st.secrets["TRELLO_KEY"]
TOKEN = st.secrets["TRELLO_TOKEN"]

# IDs DAS LISTAS (Mantenha os seus IDs aqui)
LISTA_PERFORMANCE_ID = '67e4262e8b3b917efd0b6ae1'
LISTA_EDICOES_ID = '67e4262e8b3b917efd0b6ae1' # Se for a mesma lista, mantenha o ID igual

st.set_page_config(page_title="Escalify Tech Hub", layout="wide", page_icon="⚡")

# --- ESTILO TECH / DARK MODE ---
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
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    # Aqui você pode colocar o link da sua imagem se ela estiver hospedada online
    st.image("https://raw.githubusercontent.com/streamlit/static-assets/main/images/channels/streamlit-mark-color.png", width=80)
    st.markdown("<h2 style='color:#00d4ff;'>ESCALIFY SYSTEM</h2>", unsafe_allow_html=True)
    mes_selecionado = st.selectbox("📅 PERÍODO", ["Janeiro", "Fevereiro", "Março", "Abril"], index=2)

def buscar_cards(id_lista):
    url = f"https://api.trello.com/1/lists/{id_lista}/cards?key={API_KEY}&token={TOKEN}&members=true&fields=name,dateLastActivity"
    res = requests.get(url)
    return res.json() if res.status_code == 200 else []

# --- PROCESSAMENTO ---
data_perf = buscar_cards(LISTA_PERFORMANCE_ID)
mapa_meses = {"Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4}

if data_perf:
    entregas = []
    for card in data_perf:
        data_card = datetime.strptime(card['dateLastActivity'], '%Y-%m-%dT%H:%M:%S.%fZ')
        if data_card.month != mapa_meses[mes_selecionado]: continue
        
        nome_card = card['name']
        membros = [m['fullName'].lower() for m in card.get('members', [])]
        
        # Identificação de Editores (Radar Suellen Ajustado)
        editor = "Outros"
        if any("suel" in m for m in membros) or "suel" in nome_card.lower():
            editor = "Suellen Santos"
        elif any("gabriel" in m for m in membros) or "gabriel" in nome_card.lower():
            editor = "Gabriel Miguel"
        elif any("heitor" in m for m in membros) or "heitor" in nome_card.lower():
            editor = "Heitor Leao"
            
        if editor != "Outros":
            # Aqui separamos o que é Performance e o que é Edição Escalify pelo nome do card
            tipo = "Edição Escalify" if "escalify" in nome_card.lower() else "Performance"
            
            match_anuncio = re.search(r'(\d+)\s*[Aa]n[uú]ncio', nome_card)
            qtd = int(match_anuncio.group(1)) if match_anuncio else 1
            
            entregas.append({"Editor": editor, "Qtd": qtd, "Tipo": tipo, "Projeto": nome_card})

    df = pd.DataFrame(entregas)

    if not df.empty:
        st.markdown(f"<h1 class='tech-header'>DASHBOARD // {mes_selecionado}</h1>", unsafe_allow_html=True)
        
        # Filtros de Dados
        df_perf = df[df['Tipo'] == "Performance"]
        df_escl = df[df['Tipo'] == "Edição Escalify"]

        # Cards de Métricas
        c1, c2, c3 = st.columns(3)
        c1.metric("📦 PERFORMANCE", f"{df_perf['Qtd'].sum()} vids")
        c2.metric("🎨 EDIDÇÕES ESCALIFY", f"{df_escl['Qtd'].sum()} vids")
        c3.metric("🚀 TOTAL GERAL", f"{df['Qtd'].sum()} vids")

        st.markdown("---")

        # Gráficos
        col_l, col_r = st.columns(2)
        with col_l:
            st.subheader("📊 Ranking Performance")
            st.bar_chart(df_perf.groupby('Editor')['Qtd'].sum(), color="#00d4ff", horizontal=True)
        with col_r:
            st.subheader("🎬 Ranking Edições")
            st.bar_chart(df_escl.groupby('Editor')['Qtd'].sum(), color="#ff007f", horizontal=True)
    else:
        st.info("Aguardando entrada de dados...")
