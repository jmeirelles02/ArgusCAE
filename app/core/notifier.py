import httpx
from app.core.config import settings

class TelegramNotifier:
    async def send_direct(self, chat_id: str, message: str):
        """Envia mensagem para um usuário específico."""
        if not settings.TELEGRAM_TOKEN:
            return

        url = f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                await client.post(url, json=payload)
            except Exception as e:
                print(f"Erro ao enviar Telegram para {chat_id}: {e}")

    async def send(self, message: str):
        """Envia para o ADMIN (fallback)."""
        if settings.TELEGRAM_CHAT_ID:
            await self.send_direct(settings.TELEGRAM_CHAT_ID, message)