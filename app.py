import streamlit as st
import pandas as pd
import requests
import io

st.set_page_config(page_title="Leilões Caixa PR", layout="wide", page_icon="🏢")

st.title("🏢 Monitor de Oportunidades - Leilões Caixa PR")
st.caption("Buscando e filtrando os dados direto da Caixa Econômica")

# Função que tenta baixar direto da Caixa furando o bloqueio de segurança
@st.cache_data(ttl=3600) # Atualiza a cada 1 hora se alguém acessar
def baixar_e_tratar_dados():
    url = "https://venda-imoveis.caixa.gov.br/listaweb/Lista_imoveis_PR.csv"
    
    # Headers e cookies para simular um navegador comum e evitar o bloqueio da Caixa
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://venda-imoveis.caixa.gov.br/sistema/download-lista.asp"
    }
    
    try:
        # Tenta baixar o arquivo simulando o clique do usuário
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        # Lê o CSV pulando os metadados iniciais da Caixa
        # Usa io.BytesIO para ler o conteúdo direto da memória sem salvar arquivo físico
        df = pd.read_csv(io.BytesIO(response.content), skiprows=2, sep=';', encoding='latin-1')
        
        # Limpa os nomes das colunas de espaços extras
        df.columns = df.columns.str.strip()
        
        # Tratamento dos preços de formato brasileiro para número
        df['Preço'] = df['Preço'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)
        df['Valor de avaliação'] = df['Valor de avaliação'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)
        df['Desconto (%)'] = ((df['Valor de avaliação'] - df['Preço']) / df['Valor de avaliação'] * 100).round(1)
        
        return df
    except Exception as e:
        # Caso a Caixa mude algo ou bloqueie o IP temporariamente, tenta ler o arquivo local de backup
        try:
            df = pd.read_csv("imoveis_pr_limpo.csv", sep=';', encoding='utf-8')
            return df
        except:
            st.error(f"Erro ao conectar com o site da Caixa: {e}")
            return pd.DataFrame()

df = baixar_e_tratar_dados()

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
    st.warning("Aguardando liberação de conexão com o servidor da Caixa econômica.")
