import json
from google import genai
from google.genai import types
from app.core.config import settings

class ArgusMind:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        # ALTERAÇÃO AQUI: Usando o alias 'latest' que é mais seguro
        self.model_name = "gemini-2.5-flash"

    def analyze_asset(self, ticker: str, data: dict, context: list, user_profile: str) -> dict:
        prompt = f"""
        ATUE COMO: Argus, consultor financeiro.
        PERFIL: {user_profile}
        ATIVO: {ticker}
        DADO ATUAL: {data}
        HISTÓRICO: {context}

        TAREFA: Analise riscos ou oportunidades.
        SAÍDA JSON: {{ "notify": bool, "message": "texto curto pt-br", "urgency": int }}
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Erro no Gemini (Analyze): {e}")
            # Retorna estrutura segura para não travar o sistema
            return {"notify": False, "message": "Erro na IA", "urgency": 0}

    def generate_profile_analysis(self, assets: list) -> str:
        prompt = f"""
        Analise o perfil de investidor de quem tem: {assets}.
        Responda em 2 frases curtas.
        """
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Erro no Gemini (Profile): {e}")
            return "Análise indisponível no momento."