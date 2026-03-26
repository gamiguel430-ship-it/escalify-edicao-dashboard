import streamlit as st
import requests
import pandas as pd
import re
from datetime import datetime

# --- CONFIGURAÇÕES DO SERVIDOR ---
API_KEY = st.secrets["TRELLO_KEY"]
TOKEN = st.secrets["TRELLO_TOKEN"]
LISTA_ID = '67e4262e8b3b917efd0b6ae1'

st.set_page_config(page_title="Escalify Tech Ops", layout="wide", page_icon="⚡")

# --- CSS AVANÇADO (GLOW & TECH) ---
st.markdown("""
    <style>
    /* Importando fonte Tech */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

    .main { background-color: #0b0e14; color: #e0e0e0; }
    
    /* Card de Métrica com Efeito Glow */
    div[data-testid="stMetric"] {
        background: rgba(16, 20, 28, 0.8);
        border: 1px solid #1f2937;
        padding: 25px;
        border-radius: 20px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    div[data-testid="stMetric"]:hover {
        border-color: #00d4ff;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.3);
        transform: translateY(-5px);
    }

    /* Estilo do Título Principal */
    .tech-header {
        font-family: 'JetBrains Mono', monospace;
        color: #00d4ff;
        text-transform: uppercase;
        letter-spacing: 3px;
        border-left: 5px solid #00d4ff;
        padding-left: 15px;
        margin-bottom: 30px;
    }

    /* Tabelas e Dataframes */
    .stDataFrame {
        border: 1px solid #1f2937;
        border-radius: 15px;
    }
    
    /* Esconder menus desnecessários */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:#00d4ff;'>SYSTEM CONTROL</h2>", unsafe_allow_html=True)
    mes_selecionado = st.selectbox("📅 SELECIONE O MÊS", ["Janeiro", "Fevereiro", "Março", "Abril"], index=2)
    st.markdown("---")
    st.caption("ESCALIFY v3.0 - MONITORING ACTIVE")

def carregar_dados():
    url = f"https://api.trello.com/1/lists/{LISTA_ID}/cards?key={API_KEY}&token={TOKEN}&members=true&fields=name,dateLastActivity"
    res = requests.get(url)
    return res.json() if res.status_code == 200 else []

data = carregar_dados()
mapa_meses = {"Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4}

if data:
    entregas = []
    for card in data:
        data_card = datetime.strptime(card['dateLastActivity'], '%Y-%m-%dT%H:%M:%S.%fZ')
        if data_card.month != mapa_meses[mes_selecionado]:
            continue
            
        nome_card = card['name']
        texto_busca = nome_card.lower()
        membros = [m['fullName'].lower() for m in card.get('members', [])]
        
        # Regex para quantidade
        match_anuncio = re.search(r'(\d+)\s*[Aa]n[uú]ncio', nome_card)
        quantidade = int(match_anuncio.group(1)) if match_anuncio else 1
            
        editor = "Outros"
        if any("suel" in m for m in membros) or "suel" in texto_busca:
            editor = "Suellen Santos"
        elif any("gabriel" in m for m in membros) or "gabriel" in texto_busca:
            editor = "Gabriel Miguel"
        elif any("heitor" in m for m in membros) or "heitor" in texto_busca:
            editor = "Heitor Leao"
            
        if editor != "Outros":
            entregas.append({
                "DATA": data_card.strftime('%d/%m'),
                "EDITOR": editor, 
                "QTD": quantidade, 
                "PROJETO": nome_card
            })
    
    df = pd.DataFrame(entregas)
    
    if not df.empty:
        st.markdown(f"<h1 class='tech-header'>PERFORMANCE HUB // {mes_selecionado}</h1>", unsafe_allow_html=True)
        
        # Grid de Métricas
        c1, c2, c3 = st.columns(3)
        resumo = df.groupby('EDITOR')['QTD'].sum().sort_values(ascending=False)
        
        c1.metric("📦 TOTAL EDITS", f"{df['QTD'].sum()}")
        c2.metric("🏆 TOP EDITOR", resumo.idxmax())
        c3.metric("🔥 MÉDIA/DIA", f"{round(df['QTD'].sum()/30, 1)}")

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Layout de duas colunas para Gráfico e Lista
        col_grafico, col_lista = st.columns([1, 1.2])
        
        with col_grafico:
            st.subheader("📊 RANKING DE PRODUÇÃO")
            # Gráfico de barras horizontais para melhor leitura no mobile
            st.bar_chart(resumo, color="#00d4ff", horizontal=True)

        with col_lista:
            st.subheader("📋 RECENT LOGS")
            st.dataframe(df, use_container_width=True, hide_index=True)
            
    else:
        st.info(f"Aguardando transmissões de dados para {mes_selecionado}...")
else:
    st.error("Conexão interrompida com o servidor Trello.")
