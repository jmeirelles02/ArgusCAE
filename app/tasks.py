from sensors.finance import obter_preco_acao
from core.llm import analisar_dados
from core.memoria import salvar_memoria, buscar_memoria
from core.notify import enviar_alerta
import datetime

def tarefa_monitoramento_argus():
    print(f"\n⏰ [ARGUS - AUTO] Ciclo iniciado...")
    
    ticker = "AAPL"
    
    # 1. Busca Contexto
    memorias = buscar_memoria(f"Como estava a ação {ticker}?")
    contexto = memorias if memorias else "Sem dados anteriores."

    # 2. Sensor
    preco = obter_preco_acao(ticker)
    if not preco: return

    # 3. Cérebro (COM EXEMPLOS MATEMÁTICOS)
    prompt = f"""
    Atue como um sistema de ALERTA DE CRISE.
    
    Contexto Anterior: {contexto}
    Preço ATUAL: ${preco:.2f}
    
    TAREFA: Classifique a variação de preço.
    
    REGRAS RÍGIDAS DE MATEMÁTICA:
    - Variação menor que $3.00 dolares = RUÍDO DE MERCADO -> Classifique como [NORMAL].
    - Variação maior que $5.00 dolares = MOVIMENTO REAL -> Classifique como [URGENTE].
    
    EXEMPLOS (USE COMO REFERÊNCIA):
    - De $278.00 para $278.60 (Mudou $0.60) -> Resposta: [NORMAL] Flutuação mínima.
    - De $278.00 para $275.00 (Mudou $3.00) -> Resposta: [NORMAL] Variação padrão.
    - De $278.00 para $270.00 (Mudou $8.00) -> Resposta: [URGENTE] Queda brusca detectada!
    
    Sua resposta deve começar ESTRITAMENTE com [NORMAL] ou [URGENTE].
    """
    
    analise = analisar_dados(prompt)
    print(f"🤖 [IA Pensou]: {analise}")

    # 4. Decisão de Ação
    if "[URGENTE]" in analise:
        mensagem_limpa = analise.replace("[URGENTE]", "").strip()
        print("🚨 ALERTA REAL DETECTADO! Enviando Popup...")
        enviar_alerta("ALERTA FINANCEIRO!", mensagem_limpa)
        salvar_memoria(f"ALERTA: {mensagem_limpa}", {"tipo": "alerta", "ticker": ticker})
        
    else:
        print(f"✅ Modo Silencioso (Normal). Nada a fazer.")
        # Salva na memória apenas para manter o histórico
        salvar_memoria(f"Rotina: {ticker} a ${preco:.2f}", {"tipo": "rotina", "ticker": ticker})

    print("🏁 Ciclo finalizado.")