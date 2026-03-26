import streamlit as st
import requests
import pandas as pd
import re
from datetime import datetime

# --- CONFIGURAÇÕES DO SERVIDOR (Via Secrets) ---
API_KEY = st.secrets["TRELLO_KEY"]
TOKEN = st.secrets["TRELLO_TOKEN"]
LISTA_ID = '67e4262e8b3b917efd0b6ae1'

st.set_page_config(page_title="Escalify Tech Ops", layout="wide", page_icon="⚡")

# --- CSS ESTILO TECH / MOBILE OPTIMIZED ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 212, 255, 0.3);
        padding: 15px;
        border-radius: 12px;
    }
    h1, h2, h3 { color: #00d4ff; font-family: 'Inter', sans-serif; font-weight: 800; }
    .stDataFrame { background-color: #1a1c24; border-radius: 10px; }
    /* Ajuste para telas pequenas */
    @media (max-width: 600px) {
        div[data-testid="stMetricValue"] { font-size: 20px; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🚀 Escalify Hub")
    mes_selecionado = st.selectbox("📅 Selecione o Mês", ["Janeiro", "Fevereiro", "Março", "Abril"], index=2)
    st.divider()
    st.caption("v2.0 - Filtro de Editores Ativo")

def carregar_dados():
    url = f"https://api.trello.com/1/lists/{LISTA_ID}/cards?key={API_KEY}&token={TOKEN}&members=true&fields=name,dateLastActivity"
    res = requests.get(url)
    return res.json() if res.status_code == 200 else []

data = carregar_dados()
mapa_meses = {"Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4}

if data:
    entregas = []
    for card in data:
        # Filtro de Data (Março 2026)
        data_card = datetime.strptime(card['dateLastActivity'], '%Y-%m-%dT%H:%M:%S.%fZ')
        if data_card.month != mapa_meses[mes_selecionado]:
            continue
            
        nome_card = card['name']
        texto_busca = nome_card.lower()
        membros = [m['fullName'].lower() for m in card.get('members', [])]
        
        # Lógica de Quantidade (Ex: "20 Anúncios")
        match_anuncio = re.search(r'(\d+)\s*[Aa]n[uú]ncio', nome_card)
        quantidade = int(match_anuncio.group(1)) if match_anuncio else 1
            
        editor = "Outros"
        
        # --- RADAR DE NOMES CORRIGIDO (Suellen com 2 Ls) ---
        if any("suel" in m for m in membros) or "suel" in texto_busca:
            editor = "Suellen Santos"
        elif any("gabriel" in m for m in membros) or "gabriel" in texto_busca:
            editor = "Gabriel Miguel"
        elif any("heitor" in m for m in membros) or "heitor" in texto_busca:
            editor = "Heitor Leao"
            
        if editor != "Outros":
            entregas.append({
                "Data": data_card.strftime('%d/%m'),
                "Editor": editor, 
                "Qtd": quantidade, 
                "Vídeo": nome_card
            })
    
    df = pd.DataFrame(entregas)
    
    if not df.empty:
        st.title(f"⚡ Performance Escalify - {mes_selecionado}")
        
        # KPIs (Ficam empilhados no Mobile automaticamente)
        c1, c2 = st.columns(2)
        resumo = df.groupby('Editor')['Qtd'].sum().sort_values(ascending=False)
        
        c1.metric("📦 Volume Total", f"{df['Qtd'].sum()} edits")
        c2.metric("🏆 MVP do Mês", resumo.idxmax())

        st.markdown("---")
        
        # Gráfico Neon
        st.subheader("📊 Ranking de Produção")
        st.bar_chart(resumo, color="#00d4ff")

        # Tabela Detalhada
        st.subheader("📋 Log de Atividades")
        st.dataframe(df[["Data", "Editor", "Qtd", "Vídeo"]], use_container_width=True, hide_index=True)
    else:
        st.warning(f"Nenhuma entrega detectada para {mes_selecionado}.")
else:
    st.error("Erro na conexão com o Trello.")
