import streamlit as st
import pandas as pd

st.set_page_config(page_title="Leilões Caixa PR", layout="wide", page_icon="🏢")

st.title("🏢 Monitor de Oportunidades - Leilões Caixa PR")
st.caption("Acesse e filtre os imóveis de leilão de qualquer lugar")

# Carrega o arquivo localmente do seu repositório
@st.cache_data
def carregar_dados():
    try:
        # Lendo o arquivo limpo que estará no repositório
        df = pd.read_csv("imoveis_pr_limpo.csv", sep=';', encoding='utf-8')
        
        # Tratamento básico de preços para garantir que os filtros funcionem
        df['Preço'] = df['Preço'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)
        df['Valor de avaliação'] = df['Valor de avaliação'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)
        df['Desconto (%)'] = ((df['Valor de avaliação'] - df['Preço']) / df['Valor de avaliação'] * 100).round(1)
        return df
    except FileNotFoundError:
        return pd.DataFrame()

df = carregar_dados()

if not df.empty:
    # --- BARRA LATERAL DE FILTROS ---
    st.sidebar.header("Filtros de Busca")
    
    cidades = sorted(df['Cidade'].unique())
    cidade_selecionada = st.sidebar.selectbox("Selecione a Cidade", cidades)
    
    df_cidade = df[df['Cidade'] == cidade_selecionada]
    
    bairros = sorted(df_cidade['Bairro'].unique())
    bairro_selecionado = st.sidebar.multiselect("Selecione os Bairros (Vazio para todos)", bairros)
    
    if bairro_selecionado:
        df_filtrado = df_cidade[df_cidade['Bairro'].isin(bairro_selecionado)]
    else:
        df_filtrado = df_cidade

    # --- PAINEL PRINCIPAL ---
    st.metric("Oportunidades Encontradas na Região", len(df_filtrado))
    
    df_visualizacao = df_filtrado[[
        'Cidade', 'Bairro', 'Preço', 'Valor de avaliação', 'Desconto (%)', 'Modalidade de venda', 'Link de acesso'
    ]].copy().sort_values(by='Desconto (%)', ascending=False)
    
    st.dataframe(
        df_visualizacao,
        column_config={
            "Preço": st.column_config.NumberColumn("Valor de Venda", format="R$ %.2f"),
            "Valor de avaliação": st.column_config.NumberColumn("Avaliação", format="R$ %.2f"),
            "Link de acesso": st.column_config.LinkColumn("Link da Caixa", display_text="Ver Imóvel")
        },
        hide_index=True,
        use_container_width=True
    )
else:
    st.warning("Nenhum dado encontrado. Adicione o arquivo 'imoveis_pr_limpo.csv' no seu repositório do GitHub.")
