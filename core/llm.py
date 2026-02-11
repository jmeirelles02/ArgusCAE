import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY não encontrada!")

client = genai.Client(api_key=api_key)

def analisar_dados(prompt: str):
    """
    Função centralizada para chamar o Gemini.
    Se precisarmos mudar de modelo no futuro, mudamos SÓ AQUI.
    """
    try:
        resposta = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        return resposta.text
    except Exception as e:
        return f"Erro na análise da IA: {e}"