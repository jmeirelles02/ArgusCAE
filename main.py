import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.database import init_db
from app.core.store import get_all_users_with_assets
from app.brain.memory import MemoryBank
from app.brain.reasoner import ArgusMind
from app.sensors.finance import YFinanceSensor
from app.core.notifier import TelegramNotifier
from app.interface.telegram_bot import create_bot

memory = MemoryBank()
mind = ArgusMind()
notifier = TelegramNotifier()
scheduler = AsyncIOScheduler()
bot_app = create_bot()

async def check_user_assets(chat_id, user_data):
    assets = user_data.get("assets", [])
    profile = user_data.get("profile", "Neutro")

    for ticker in assets:
        try:
            sensor = YFinanceSensor(ticker)
            data = await sensor.run()
            
            context = memory.recall(f"{ticker} price history")
            decision = mind.analyze_asset(ticker, data, context, profile)
            
            urgency = decision.get("urgency", 0)
            print(f"[DEBUG] {ticker} | Urgência: {urgency} | Motivo: {decision.get('message')}")
            
            if decision.get("notify") and urgency >= 5:
                msg = f"🚨 {ticker}: {decision['message']}\n(Urgência: {urgency})"
                await notifier.send_direct(chat_id, msg)
            
            memory.store(
                f"{ticker}: {data['value']}", 
                {"source": ticker, "timestamp": data["timestamp"]}
            )
            
        except Exception as e:
            print(f"Erro processando {ticker}: {e}")

async def pipeline():
    """Loop principal: Busca usuários no DB e inicia verificação."""
    try:
        all_users_map = await get_all_users_with_assets()
        
        if all_users_map:
            print(f"--- Pipeline SQL: Verificando {len(all_users_map)} usuários ---")
            for chat_id, data in all_users_map.items():
                await check_user_assets(chat_id, data)
        else:
            print("--- Pipeline SQL: Nenhum usuário cadastrado ainda ---")
            
    except Exception as e:
        print(f"Erro crítico no Pipeline: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    
    await bot_app.initialize()
    await bot_app.start()
    asyncio.create_task(bot_app.updater.start_polling())
    
    scheduler.add_job(
        pipeline, 
        'interval', 
        minutes=5, 
        max_instances=1,
        misfire_grace_time=60
    )
    scheduler.start()
    
    print("Argus Online")
    yield
    
    await bot_app.updater.stop()
    await bot_app.stop()
    await bot_app.shutdown()
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)