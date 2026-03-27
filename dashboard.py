import streamlit as st
import requests
import pandas as pd
import re
from datetime import datetime
import os

# --- CONFIGURAÇÕES ---
API_KEY = st.secrets["TRELLO_KEY"]
TOKEN = st.secrets["TRELLO_TOKEN"]

# IDs DAS LISTAS NO TRELLO
LISTA_SERVICOS_ID = '67e4262e8b3b917efd0b6ae1'
LISTA_INFOPRODUTOS_ID = '69af2a85b62772bd7d29463e'

# 🎯 DEFINA AQUI A SUA META MENSAL
META_MENSAL = 1000 

st.set_page_config(page_title="Escalify Hub", layout="wide", page_icon="⚡")

# --- CSS PREMIUM / CYBERPUNK ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

    .main { background-color: #0b0e14; color: #e0e0e0; }
    
    div[data-testid="stMetric"] {
        background: rgba(16, 20, 28, 0.8);
        border: 1px solid #1f2937;
        border-left: 4px solid #00d4ff;
        padding: 20px;
        border-radius: 15px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    div[data-testid="stMetric"]:hover {
        border-color: #00d4ff;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.3);
        transform: translateY(-5px);
    }
    
    .mvp-banner {
        background: linear-gradient(90deg, #001f3f 0%, #00d4ff 100%);
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 212, 255, 0.2);
        margin-bottom: 25px;
        border: 1px solid rgba(255,255,255,0.2);
    }
    .mvp-title { font-size: 16px; color: rgba(255,255,255,0.8); text-transform: uppercase; letter-spacing: 2px; }
    .mvp-name { font-size: 38px; font-weight: 900; color: white; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }

    .tech-header {
        font-family: 'JetBrains Mono', monospace;
        color: #00d4ff;
        text-transform: uppercase;
        border-left: 5px solid #00d4ff;
        padding-left: 15px;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR (LOGO) ---
with st.sidebar:
    if os.path.exists("logo.jpeg"):
        st.image("logo.jpeg", use_container_width=True)
    elif os.path.exists("image_0.png"):
        st.image("image_0.png", use_container_width=True)
    else:
        st.markdown("<h1 style='text-align: center; color: #00d4ff;'>ESCALIFY</h1>", unsafe_allow_html=True)
    
    st.markdown("---")
    mes_selecionado = st.selectbox("📅 PERÍODO", ["Janeiro", "Fevereiro", "Março", "Abril"], index=2)

def buscar_cards(id_lista):
    url = f"https://api.trello.com/1/lists/{id_lista}/cards?key={API_KEY}&token={TOKEN}&members=true&fields=name,dateLastActivity"
    res = requests.get(url)
    return res.json() if res.status_code == 200 else []

# --- PROCESSAMENTO DOS DOIS QUADROS ---
data_serv = buscar_cards(LISTA_SERVICOS_ID)
data_info = buscar_cards(LISTA_INFOPRODUTOS_ID)

mapa_meses = {"Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4}
registos = []

# Motor de Leitura Inteligente
def processar_lista(dados_trello, tipo_trello, lista_final):
    for card in dados_trello:
        dt = datetime.strptime(card['dateLastActivity'], '%Y-%m-%dT%H:%M:%S.%fZ')
        if dt.month != mapa_meses[mes_selecionado]: continue
        
        nome = card['name']
        texto = nome.lower()
        membros = [m['fullName'].lower() for m in card.get('members', [])]
        
        # 1. Identificar Editor
        editor = "Outros"
        if any("suel" in m for m in membros) or "suel" in texto or ".ss" in texto or ".suh" in texto:
            editor = "Suellen Santos"
        elif any("gabriel" in m for m in membros) or "gabriel" in texto or ".gm" in texto:
            editor = "Gabriel Miguel"
        elif any("heitor" in m for m in membros) or "heitor" in texto or ".hl" in texto:
            editor = "Heitor Leão"
            
        if editor != "Outros":
            # 2. Lógica de Contagem por Segmento
            qtd = 0
            if tipo_trello == "Serviços/Criativos":
                match = re.search(r'(\d+)\s*[Aa]n[uú]ncio', nome)
                qtd = int(match.group(1)) if match else 1
            
            elif tipo_trello == "Infoprodutos":
                match_range = re.search(r'[A-Za-z]*\s*(\d+)\s*-\s*[A-Za-z]*\s*(\d+)', nome)
                match_ml_qtd = re.search(r'(\d+)\s*ml', texto)
                match_ml_single = re.search(r'ml\d*', texto)

                if match_range:
                    inicio = int(match_range.group(1))
                    fim = int(match_range.group(2))
                    qtd = (abs(fim - inicio) + 1) * 2
                elif match_ml_qtd:
                    qtd = int(match_ml_qtd.group(1))
                elif match_ml_single:
                    qtd = 1
                else:
                    qtd = 2 

            lista_final.append({"Editor": editor, "Qtd": qtd, "Segmento": tipo_trello, "Projeto": nome})

# Executa o motor
if data_serv: processar_lista(data_serv, "Serviços/Criativos", registos)
if data_info: processar_lista(data_info, "Infoprodutos", registos)

df = pd.DataFrame(registos)

if not df.empty:
    st.markdown(f"<h1 class='tech-header'>PERFORMANCE HUB // {mes_selecionado}</h1>", unsafe_allow_html=True)
    
    # --- BANNER DO MVP ---
    resumo_total = df.groupby('Editor')['Qtd'].sum()
    st.markdown(f"""
    <div class="mvp-banner">
        <div class="mvp-title">👑 MVP DA AGÊNCIA 👑</div>
        <div class="mvp-name">{
