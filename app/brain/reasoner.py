import json
import ollama

class ArgusMind:
    def __init__(self):
        self.model_name = "qwen2.5"

    def analyze_asset(self, ticker: str, data: dict, context: list, user_profile: str) -> dict:
        prompt = f"""
        ATUE COMO: Consultor financeiro sênior.
        PERFIL DO USUÁRIO: {user_profile}
        ATIVO: {ticker}
        DADO ATUAL: {data}
        HISTÓRICO RECENTE: {context}

        TAREFA: Analise se há algo CRÍTICO (Risco ou Oportunidade).
        REGRAS:
        1. Notifique se a urgência for 3 ou maior.
        2. Considere o perfil do usuário.
        
        SAÍDA JSON OBRIGATÓRIA: {{ "notify": bool, "message": "texto curto em pt-br", "urgency": int }}
        """
        
        try:
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                format='json'
            )
            return json.loads(response['response'])
            
        except Exception as e:
            print(f"Erro na IA Local (Analyze) para {ticker}: {e}")
            return {"notify": False, "message": "Erro na IA Local", "urgency": 0}

    def generate_profile_analysis(self, assets: list) -> str:
        prompt = f"""
        Analise o perfil de investidor de quem possui os seguintes ativos: {assets}.
        Classifique como: Conservador, Moderado ou Arrojado.
        Explique brevemente em 2 frases em português.
        """
        try:
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt
            )
            return response['response']
        except Exception as e:
            print(f"Erro na IA Local (Profile): {e}")
            return "Não foi possível analisar o perfil no momento."