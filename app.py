import streamlit as st
import pandas as pd

st.set_page_config(page_title="Leilões Caixa PR", layout="wide", page_icon="🏢")

st.title("🏢 Monitor de Oportunidades - Leilões Caixa PR")

try:
    # Lê a planilha exatamente do jeito que ela vem da Caixa (pulando as duas linhas de texto iniciais)
    df = pd.read_csv("imoveis_pr_limpo.csv", skiprows=2, sep=';', encoding='latin-1')
    
    # Remove espaços em branco que a Caixa joga nos nomes das colunas
    df.columns = df.columns.str.strip()
    
    # Mostra a planilha bruta na tela com os filtros padrão do próprio Streamlit
    st.dataframe(df, use_container_width=True)

except FileNotFoundError:
    st.warning("Aguardando o arquivo 'imoveis_pr_limpo.csv' ser adicionado ao repositório.")
