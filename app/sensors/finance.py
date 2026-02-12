import yfinance as yf
from datetime import datetime

class YFinanceSensor:
    def __init__(self, symbol: str):
        # Correção automática para B3 (Brasil)
        # Se tem 5 ou 6 caracteres, termina com número e não tem ponto, adiciona .SA
        if (len(symbol) >= 4 and symbol[-1].isdigit() and "." not in symbol):
             self.symbol = f"{symbol}.SA"
        else:
             self.symbol = symbol

    async def run(self):
        try:
            ticker = yf.Ticker(self.symbol)
            # Tenta obter o preço de duas formas para garantir
            price = ticker.fast_info.last_price
            
            if price is None:
                # Tentativa secundária (history) se fast_info falhar
                hist = ticker.history(period="1d")
                if not hist.empty:
                    price = hist["Close"].iloc[-1]
            
            if price is None:
                raise ValueError(f"Preço não encontrado para {self.symbol}")

            return {
                "source": f"market_{self.symbol}",
                "content": f"Current price of {self.symbol} is {price:.2f}",
                "timestamp": datetime.now().isoformat(),
                "value": price
            }
        except Exception as e:
            # Loga o erro mas não quebra o loop principal
            print(f"⚠️ Erro ao consultar {self.symbol}: {e}")
            raise e