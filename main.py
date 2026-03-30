import asyncio
import re
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


def _detect_currency(ticker: str) -> str:
    """Detecta a moeda baseado no ticker: USD ou BRL"""
    ticker_upper = ticker.upper()
    if ticker_upper.endswith("-USD") or ticker_upper.endswith("USD"):
        return "USD"
    return "BRL"


def _format_currency(value: float, ticker: str) -> str:
    """Formata o valor com o símbolo correto de moeda"""
    currency = _detect_currency(ticker)
    if currency == "USD":
        return f"$ {value:.2f}"
    else:
        return f"R$ {value:.2f}".replace(".", ",")


def _format_brl(value: float, ticker: str = "") -> str:
    """Mantém compatibilidade; usa detect_currency se ticker for fornecido"""
    if ticker:
        return _format_currency(value, ticker)
    return f"R$ {value:.2f}".replace(".", ",")


def _extract_last_known_value(context: list, ticker: str) -> float | None:
    ticker_pattern = re.escape(ticker)
    match_pattern = rf"{ticker_pattern}:\s*(-?\d+(?:\.\d+)?)"

    for item in context:
        if not isinstance(item, str):
            continue
        match = re.search(match_pattern, item)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                continue
    return None


def _build_price_context(current_value: float, last_known_value: float | None, ticker: str) -> tuple[str, str]:
    if last_known_value is None:
        return "sem histórico recente", f"Valor atual: {_format_currency(current_value, ticker)}"

    delta = current_value - last_known_value
    if abs(delta) < 1e-9:
        direction = "estável"
    elif delta > 0:
        direction = "subiu"
    else:
        direction = "caiu"

    delta_percent = 0.0 if last_known_value == 0 else (delta / last_known_value) * 100
    summary = (
        f"{direction} {abs(delta_percent):.2f}% "
        f"({_format_currency(last_known_value, ticker)} -> {_format_currency(current_value, ticker)})"
    )
    detail = (
        f"Último valor conhecido: {_format_currency(last_known_value, ticker)}\n"
        f"Valor atual: {_format_currency(current_value, ticker)}\n"
        f"Movimento: {direction} {abs(delta):.2f} ({abs(delta_percent):.2f}%)"
    )
    return summary, detail


async def check_user_assets(chat_id, user_data):
    assets = user_data.get("assets", [])
    profile = user_data.get("profile", "Neutro")

    for ticker in assets:
        try:
            sensor = YFinanceSensor(ticker)
            data = await sensor.run()

            context = memory.recall(f"{ticker} price history")
            last_known_value = _extract_last_known_value(context, ticker)
            movement_summary, movement_detail = _build_price_context(data["value"], last_known_value, ticker)

            decision = mind.analyze_asset(ticker, data, context, profile)

            urgency = decision.get("urgency", 0)
            print(
                f"[DEBUG] {ticker} | Urgência: {urgency} | "
                f"Movimento: {movement_summary} | Motivo: {decision.get('message')}"
            )

            if decision.get("notify") and urgency >= 3:
                  sugestao = decision.get("sugestao", "Monitore a evolução do ativo.")
                  msg = (
                      f"🚨 {ticker}: {decision['message']}\n"
                      f"{movement_detail}\n"
                      f"Urgência: {urgency}\n\n"
                      f"💡 Sugestão: {sugestao}"
                  )
                  print(f"[Enviando Para {chat_id}] {ticker}")
                  await notifier.send_direct(chat_id, msg)

            memory.store(
                f"{ticker}: {data['value']}",
                {"source": ticker, "timestamp": data["timestamp"]}
            )

        except Exception as e:
            print(f"Erro processando {ticker} para {chat_id}: {e}")

async def pipeline():
    try:
        all_users_map = await get_all_users_with_assets()
        
        if all_users_map:
            print(f"--- Pipeline SQL: Verificando {len(all_users_map)} usuários ---")
            for chat_id, data in all_users_map.items():
                await check_user_assets(chat_id, data)
        else:
            print("--- Pipeline SQL: Nenhum usuário cadastrado ainda ---")
            
    except Exception as e:
        print(f"Erro crítico no Master Pipeline: {e}. O sistema tentará novamente no próximo ciclo.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    
    await bot_app.initialize()
    await bot_app.start()
    asyncio.create_task(bot_app.updater.start_polling())
    
    scheduler.add_job(
        pipeline, 
        'interval', 
        minutes=1, 
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