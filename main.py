import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Imports internos
from app.core.database import init_db
from app.core.store import get_all_users_with_assets
from app.brain.memory import MemoryBank
from app.brain.reasoner import ArgusMind
from app.sensors.finance import YFinanceSensor
from app.core.notifier import TelegramNotifier
from app.interface.telegram_bot import create_bot

# Instâncias Globais
memory = MemoryBank()
mind = ArgusMind()
notifier = TelegramNotifier()
scheduler = AsyncIOScheduler()
bot_app = create_bot()

async def check_user_assets(chat_id, user_data):
    """Processa os ativos de um único usuário."""
    assets = user_data.get("assets", [])
    profile = user_data.get("profile", "Neutro")

    for ticker in assets:
        try:
            # 1. Coleta
            sensor = YFinanceSensor(ticker)
            data = await sensor.run()
            
            # 2. Memória
            context = memory.recall(f"{ticker} price history")
            
            # 3. Análise (com Perfil)
            decision = mind.analyze_asset(ticker, data, context, profile)
            
            # 4. Ação (apenas se Urgência >= 5)
            if decision.get("notify") and decision.get("urgency", 0) >= 5:
                msg = f"🚨 **{ticker}**: {decision['message']}\n(Urgência: {decision['urgency']})"
                print(f"[ENVIANDO PARA {chat_id}] {ticker}")
                await notifier.send_direct(chat_id, msg)
            
            # 5. Armazenamento
            memory.store(
                f"{ticker}: {data['value']}", 
                {"source": ticker, "timestamp": data["timestamp"]}
            )
            
        except Exception as e:
            print(f"Erro processando {ticker} para {chat_id}: {e}")

async def master_pipeline():
    """Loop principal: Busca usuários no DB e inicia verificação."""
    try:
        # Busca dicionário {chat_id: {assets: [], profile:Str}} do Postgres
        all_users_map = await get_all_users_with_assets()
        
        if all_users_map:
            print(f"--- Pipeline SQL: Verificando {len(all_users_map)} usuários ---")
            for chat_id, data in all_users_map.items():
                await check_user_assets(chat_id, data)
        else:
            print("--- Pipeline SQL: Nenhum usuário cadastrado ainda ---")
            
    except Exception as e:
        print(f"Erro crítico no Master Pipeline: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Inicializa DB (Cria tabelas)
    await init_db()
    
    # 2. Inicializa Bot Telegram (Polling)
    await bot_app.initialize()
    await bot_app.start()
    asyncio.create_task(bot_app.updater.start_polling())
    
    # 3. Inicializa Scheduler
    scheduler.add_job(master_pipeline, 'interval', minutes=2)
    scheduler.start()
    
    print("🚀 Argus Online e Rodando!")
    yield
    
    # Shutdown
    await bot_app.updater.stop()
    await bot_app.stop()
    await bot_app.shutdown()
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)