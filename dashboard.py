import streamlit as st
import requests
import pandas as pd
import re
from datetime import datetime
import os

# --- CONFIGURAÇÕES ---
API_KEY = st.secrets["TRELLO_KEY"]
TOKEN = st.secrets["TRELLO_TOKEN"]

# IDs DAS LISTAS
LISTA_PERFORMANCE_ID = '67e4262e8b3b917efd0b6ae1'
LISTA_EDICOES_ID = '67e4262e8b3b917efd0b6ae1' # Altere se for outra lista

st.set_page_config(page_title="Escalify Hub", layout="wide", page_icon="⚡")

# --- CSS PREMIUM (Inspirado na sua Identidade Visual) ---
st.markdown("""
    <style>
    /* Fundo degradê combinando com a sua logo */
    .stApp {
        background: linear-gradient(135deg, #000814 0%, #001f3f 100%);
        color: #ffffff;
    }
    
    /* Esconder elementos amadores do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Cards de Métricas Premium */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-left: 4px solid #ffffff;
        padding: 20px;
        border-radius: 10px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    
    /* Banner do MVP */
    .mvp-banner {
        background: linear-gradient(90deg, #003366 0%, #00d4ff 100%);
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 212, 255, 0.2);
        margin-bottom: 30px;
        border: 1px solid rgba(255,255,255,0.2);
    }
    .mvp-title { font-size: 18px; color: rgba(255,255,255,0.8); text-transform: uppercase; letter-spacing: 2px; margin-bottom: 5px; }
    .mvp-name { font-size: 42px; font-weight: 900; color: white; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
    .mvp-stats { font-size: 20px; color: white; font-weight: bold; margin-top: 10px; }

    /* Títulos Gerais */
    h1, h2, h3 { color: #ffffff !important; font-family: 'Helvetica Neue', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR (COM SUA LOGO) ---
with st.sidebar:
    # Ele vai procurar a imagem que você vai subir no GitHub
    if os.path.exists("logo.jpeg"):
        st.image("logo.jpeg", use_container_width=True)
    else:
        st.markdown("<h1 style='text-align: center; color: #00d4ff;'>ESCALIFY</h1>", unsafe_allow_html=True)
    
    st.markdown("---")
    mes_selecionado = st.selectbox("📅 PERÍODO", ["Janeiro", "Fevereiro", "Março", "Abril"], index=2)

def buscar_cards(id_lista):
    url = f"https://api.trello.com/1/lists/{id_lista}/cards?key={API_KEY}&token={TOKEN}&members=true&fields=name,dateLastActivity"
    res = requests.get(url)
    return res.json() if res.status_code == 200 else []

# --- PROCESSAMENTO ---
data_trello = buscar_cards(LISTA_PERFORMANCE_ID)
mapa_meses = {"Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4}

if data_trello:
    registos = []
    for card in data_trello:
        dt = datetime.strptime(card['dateLastActivity'], '%Y-%m-%dT%H:%M:%S.%fZ')
        if dt.month != mapa_meses[mes_selecionado]: continue
        
        nome = card['name']
        membros = [m['fullName'].lower() for m in card.get('members', [])]
        
        editor = "Outros"
        if any("suel" in m for m in membros) or "suel" in nome.lower(): editor = "Suellen Santos"
        elif any("gabriel" in m for m in membros) or "gabriel" in nome.lower(): editor = "Gabriel Miguel"
        elif any("heitor" in m for m in membros) or "heitor" in nome.lower(): editor = "Heitor Leão"
            
        if editor != "Outros":
            tipo = "Edição Escalify" if "escalify" in nome.lower() else "Performance"
            match = re.search(r'(\d+)\s*[Aa]n[uú]ncio', nome)
            qtd = int(match.group(1)) if match else 1
            registos.append({"Editor": editor, "Qtd": qtd, "Tipo": tipo, "Projeto": nome})

    df = pd.DataFrame(registos)

    if not df.empty:
        # --- LÓGICA DO MVP ---
        resumo = df.groupby('Editor')['Qtd'].sum()
        mvp_nome = resumo.idxmax()
        mvp_qtd = resumo.max()

        # DESTAQUE DO MVP (BANNER PREMIUM)
        st.markdown(f"""
        <div class="mvp-banner">
            <div class="mvp-title">👑 MVP do Mês 👑</div>
            <div class="mvp-name">{mvp_nome}</div>
            <div class="mvp-stats">🔥 {mvp_qtd} entregas realizadas</div>
        </div>
        """, unsafe_allow_html=True)

        df_perf = df[df['Tipo'] == "Performance"]
        df_escl = df[df['Tipo'] == "Edição Escalify"]

        # --- MÉTRICAS ---
        c1, c2, c3 = st.columns(3)
        c1.metric("📦 VÍDEOS PERFORMANCE", f"{df_perf['Qtd'].sum()}")
        c2.metric("🎨 VÍDEOS ESCALIFY", f"{df_escl['Qtd'].sum()}")
        c3.metric("🚀 TOTAL GERAL", f"{df['Qtd'].sum()}")

        st.markdown("<br>", unsafe_allow_html=True)

        # --- GRÁFICOS ---
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("### 📊 Performance")
            st.bar_chart(df_perf.groupby('Editor')['Qtd'].sum(), color="#ffffff", horizontal=True)
        with col_r:
            st.markdown("### 🎬 Escalify")
            st.bar_chart(df_escl.groupby('Editor')['Qtd'].sum(), color="#00d4ff", horizontal=True)
            
        st.markdown("### 📋 Histórico Recente")
        st.dataframe(df[["Editor", "Tipo", "Qtd", "Projeto"]], use_container_width=True, hide_index=True)
    else:
        st.info("Aguardando dados de produção...")
