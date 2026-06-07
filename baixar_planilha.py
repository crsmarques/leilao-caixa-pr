import os
import requests
import pandas as pd

def baixar_dados_caixa():
    url = "https://venda-imoveis.caixa.gov.br/listaweb/Lista_imoveis_PR.csv"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    
    try:
        print("Buscando dados na Caixa...")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        with open("temp_pr.csv", "wb") as f:
            f.write(response.content)
            
        # Lê o arquivo ignorando os metadados da Caixa
        df = pd.read_csv("temp_pr.csv", skiprows=2, sep=';', encoding='latin-1', on_bad_lines='skip')
        df.columns = df.columns.str.strip()
        
        # Salva a planilha limpa na raiz do projeto
        df.to_csv("imoveis_pr_limpo.csv", index=False, sep=';', encoding='utf-8')
        print("Planilha atualizada com sucesso!")
        
        if os.path.exists("temp_pr.csv"):
            os.remove("temp_pr.csv")
            
    except Exception as e:
        print(f"Erro na execução: {e}")
        exit(1)

if __name__ == "__main__":
    baixar_dados_caixa()
