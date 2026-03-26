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

# --- CSS ESTILO TECH / MOBILE OPTIMIZED ---
st.markdown("""
    <style>
    /* Fundo e Fonte Geral */
    .main { background-color: #0e1117; color: #ffffff; }
    
    /* Estilização dos Cards de Métrica */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    /* Títulos */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        letter-spacing: -1px;
        color: #00d4ff;
    }
    
    /* Ajuste para Mobile (Gráficos) */
    @media (max-width: 640px) {
        .stMetric { margin-bottom: 10px; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR FILTROS ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/8297/8297380.png", width=80)
    st.title("Escalify Control")
    st.markdown("---")
    mes_selecionado = st.selectbox("📅 Período", ["Janeiro", "Fevereiro", "Março", "Abril"], index=2)
    editores_selecionados = st.multiselect("👥 Time", 
                                         ["Gabriel Miguel", "Suelen Santos", "Heitor Leao"], 
                                         default=["Gabriel Miguel", "Suelen Santos", "Heitor Leao"])

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
        match_anuncio = re.search(r'(\d+)\s*[Aa]n[uú]ncio', nome_card)
        quantidade = int(match_anuncio.group(1)) if match_anuncio else 1
            
        editor = "Outros"
        texto_busca = nome_card.lower()
        membros = [m['fullName'].lower() for m in card.get('members', [])]
        
        if any("gabriel" in x for x in membros + [texto_busca]): editor = "Gabriel Miguel"
        elif any(x in ["suelen", "suellen"] for x in membros + [texto_busca]): editor = "Suelen Santos"
        elif any("heitor" in x for x in membros + [texto_busca]): editor = "Heitor Leao"
            
        if editor in editores_selecionados:
            entregas.append({"Data": data_card.strftime('%d/%m'), "Editor": editor, "Qtd": quantidade, "Vídeo": nome_card})
    
    df = pd.DataFrame(entregas)
    
    if not df.empty:
        st.title(f"⚡ Performance {mes_selecionado}")
        
        # --- MÉTRICAS EM LINHA (Fica top no mobile) ---
        c1, c2 = st.columns([1, 1])
        with c1:
            st.metric("📦 Volume Total", f"{df['Qtd'].sum()} edits")
        with c2:
            resumo = df.groupby('Editor')['Qtd'].sum()
            st.metric("🔥 MVP Atual", resumo.idxmax())

        st.markdown("---")

        # --- GRÁFICO PRINCIPAL ---
        st.subheader("📊 Produção por Editor")
        st.bar_chart(resumo, color="#00d4ff")

        # --- TABELA PARA MOBILE ---
        st.subheader("📋 Log de Entregas")
        # No mobile, escondemos colunas menos importantes se necessário
        st.dataframe(df[["Data", "Editor", "Qtd", "Vídeo"]], use_container_width=True, hide_index=True)
        
    else:
        st.warning(f"Sem dados para {mes_selecionado}. Partiu Trello!")
else:
    st.error("Falha na conexão com a API do Trello.")
