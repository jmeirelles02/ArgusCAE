import random
from datetime import datetime

class MockSensor:
    async def run(self):
        # Simula uma variação abrupta de valor
        val = random.randint(100, 500)
        return {
            "source": "mock_market",
            "content": f"Asset value is {val}",
            "timestamp": datetime.now().isoformat(),
            "value": val
        }