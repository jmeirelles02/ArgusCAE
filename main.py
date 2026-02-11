from fastapi import FastAPI
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.tasks import tarefa_monitoramento_argus

# Configuração do Agendador
scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Função especial do FastAPI.
    Tudo antes do 'yield' roda quando o servidor liga.
    Tudo depois do 'yield' roda quando desliga.
    """
    print("--- 🚀 INICIANDO O SISTEMA ARGUS ---")
    
    # Adiciona a tarefa para rodar a cada 1 minuto (para teste rápido)
    # Num caso real, mudarias para 'hours=1'
    scheduler.add_job(
        tarefa_monitoramento_argus, 
        'interval', 
        minutes=1, 
        id='monitor_apple'
    )
    scheduler.start()
    
    # Roda uma vez logo no início para não termos de esperar 1 minuto
    print("--- Executando primeira verificação manual... ---")
    tarefa_monitoramento_argus()
    
    yield
    
    print("--- 💤 DESLIGANDO ARGUS ---")
    scheduler.shutdown()

# Criação da API
app = FastAPI(lifespan=lifespan, title="Argus API")

@app.get("/")
def status():
    return {"status": "online", "message": "O Argus está vigiando."}