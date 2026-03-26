import streamlit as st
import requests
import pandas as pd
import re
from datetime import datetime

# --- CONFIGURAÇÕES SEGURAS (Pegando das "Gavetas Escondidas" do Streamlit) ---
API_KEY = st.secrets["TRELLO_KEY"]
TOKEN = st.secrets["TRELLO_TOKEN"]
LISTA_ID = '67e4262e8b3b917efd0b6ae1'

st.set_page_config(page_title="Escalify Performance", layout="wide", page_icon="🎬")

# --- ESTILO ---
st.markdown("""
    <style>
    div[data-testid="stMetricValue"] { font-size: 28px; color: #1E3A8A; }
    h1 { color: #1E3A8A; font-family: 'Helvetica'; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.title("⚙️ Filtros Escalify")
mes_selecionado = st.sidebar.selectbox("Escolha o Mês", ["Janeiro", "Fevereiro", "Março", "Abril", "Maio"], index=2)
filtro_editor = st.sidebar.multiselect("Filtrar Editor", ["Gabriel Miguel", "Suelen Santos", "Heitor Leao"], default=["Gabriel Miguel", "Suelen Santos", "Heitor Leao"])

def carregar_dados():
    url = f"https://api.trello.com/1/lists/{LISTA_ID}/cards?key={API_KEY}&token={TOKEN}&members=true&fields=name,dateLastActivity"
    res = requests.get(url)
    return res.json() if res.status_code == 200 else []

data = carregar_dados()
mapa_meses = {"Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, "Maio": 5}

if data:
    entregas = []
    for card in data:
        data_card = datetime.strptime(card['dateLastActivity'], '%Y-%m-%dT%H:%M:%S.%fZ')
        if data_card.month != mapa_meses[mes_selecionado]:
            continue
            
        nome_card = card['name']
        texto_busca = nome_card.lower()
        membros = [m['fullName'].lower() for m in card.get('members', [])]
        
        match_anuncio = re.search(r'(\d+)\s*[Aa]n[uú]ncio', nome_card)
        quantidade = int(match_anuncio.group(1)) if match_anuncio else 1
            
        editor = "Outros"
        if any("gabriel" in m for m in membros) or "gabriel" in texto_busca:
            editor = "Gabriel Miguel"
        elif any("suelen" in m or "suellen" in m for m in membros) or "suelen" in texto_busca or "suellen" in texto_busca:
            editor = "Suelen Santos"
        elif any("heitor" in m for m in membros) or "heitor" in texto_busca:
            editor = "Heitor Leao"
            
        if editor in filtro_editor:
            entregas.append({
                "Data": data_card.strftime('%d/%m'),
                "Editor": editor, 
                "Qtd": quantidade,
                "Vídeo": nome_card
            })
    
    df = pd.DataFrame(entregas)
    
    if not df.empty:
        st.title(f"🎬 Performance Escalify - {mes_selecionado}")
        c1, c2, c3 = st.columns(3)
        resumo_editor = df.groupby('Editor')['Qtd'].sum()
        
        c1.metric("📦 Total de Entregas", f"{df['Qtd'].sum()} vídeos")
        c2.metric("🏆 Líder do Mês", resumo_editor.idxmax())
        c3.metric("📅 Mês Referência", mes_selecionado)
        
        st.markdown("---")
        st.subheader("📊 Volume de Produção por Editor")
        st.bar_chart(resumo_editor, color="#1E3A8A")
        st.subheader("📋 Detalhamento")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning(f"Nenhuma entrega encontrada para {mes_selecionado}.")
else:
    st.error("Erro ao conectar com o Trello.")
