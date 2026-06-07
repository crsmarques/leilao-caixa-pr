import streamlit as st
import pandas as pd
import requests
import io

st.set_page_config(page_title="Leilões Caixa PR", layout="wide", page_icon="🏢")

st.title("🏢 Monitor de Oportunidades - Leilões Caixa PR")
st.caption("Buscando e filtrando os dados direto da Caixa Econômica")

@st.cache_data(ttl=3600)
def baixar_e_tratar_dados():
    # Usando um proxy público para mascarar a requisição da nuvem e furar o bloqueio da Caixa
    url_caixa = "https://venda-imoveis.caixa.gov.br/listaweb/Lista_imoveis_PR.csv"
    url_proxy = f"https://api.allorigins.win/raw?url={url_caixa}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        # O proxy faz a requisição para a Caixa e finge que é um usuário comum
        response = requests.get(url_proxy, headers=headers, timeout=25)
        response.raise_for_status()
        
        # Garante que o conteúdo veio como texto legível em formato CSV da Caixa
        conteudo = response.content.decode('latin-1')
        
        # Se o robô da Caixa mesmo assim mandou um HTML de erro, força o erro para ir pro plano B
        if "<html" in conteudo.lower() or "<title" in conteudo.lower():
            raise Exception("Bloqueio de IP detectado na resposta.")
            
        # Lê o CSV pulando as duas linhas de metadados da Caixa
        df = pd.read_csv(io.StringIO(conteudo), skiprows=2, sep=';', on_bad_lines='skip')
        
        # Limpa os nomes das colunas de espaços extras
        df.columns = df.columns.str.strip()
        
        # Tratamento dos preços para float
        df['Preço'] = df['Preço'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)
        df['Valor de avaliação'] = df['Valor de avaliação'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)
        df['Desconto (%)'] = ((df['Valor de avaliação'] - df['Preço']) / df['Valor de avaliação'] * 100).round(1)
        
        return df
    except Exception as e:
        st.sidebar.error(f"Erro ao tentar baixar dados em tempo real: {e}")
        # PLANO B: Se tudo falhar, ele lê o arquivo 'imoveis_pr_limpo.csv' se você tiver subido ele lá no GitHub
        try:
            df = pd.read_csv("imoveis_pr_limpo.csv", sep=';', encoding='utf-8')
            return df
        except:
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
    st.warning("O site da Caixa está bloqueando todas as conexões diretas neste momento. Suba um arquivo 'imoveis_pr_limpo.csv' no seu GitHub para usar como base fixa se precisar.")
