import yfinance as yf
from datetime import datetime

class YFinanceSensor:
    def __init__(self, symbol: str):
        if (len(symbol) >= 4 and symbol[-1].isdigit() and "." not in symbol):
             self.symbol = f"{symbol}.SA"
        else:
             self.symbol = symbol

    async def run(self):
        try:
            ticker = yf.Ticker(self.symbol)
            price = ticker.fast_info.last_price
            
            if price is None:
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
            print(f"⚠️ Erro ao consultar {self.symbol}: {e}")
            raise e