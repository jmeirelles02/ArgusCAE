import yfinance as yf

def obter_preco_acao(ticker: str):
    """
    Apenas coleta o dado bruto. Não analisa, não salva.
    Princípio da Responsabilidade Única.
    """
    print(f"--- [SENSOR] A ler dados de {ticker}... ---")
    try:
        acao = yf.Ticker(ticker)
        dados = acao.history(period="1d")
        
        if dados.empty:
            return None
            
        return dados['Close'].iloc[-1]
    except Exception as e:
        print(f"Erro no sensor: {e}")
        return None