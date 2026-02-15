import random
from datetime import datetime

class Simulador:
    async def run(self):

        val = random.randint(100, 500)
        return {
            "source": "mock_market",
            "content": f"Asset value is {val}",
            "timestamp": datetime.now().isoformat(),
            "value": val
        }