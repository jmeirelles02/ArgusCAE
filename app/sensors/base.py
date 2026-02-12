from abc import ABC, abstractmethod

class Sensor(ABC):
    @abstractmethod
    async def collect(self):
        """Coleta dados da fonte externa."""
        pass

    @abstractmethod
    def process(self, raw_data):
        """Limpa e estrutura os dados (Pandas/Dict)."""
        pass