from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.core.models import User, Asset

async def get_or_create_user(session, chat_id: int):
    """Busca um usuário ou cria se não existir."""
    result = await session.execute(select(User).where(User.chat_id == chat_id))
    user = result.scalars().first()
    if not user:
        user = User(chat_id=chat_id)
        session.add(user)
        await session.flush() 
    return user

async def add_asset(chat_id: int, ticker: str):
    """Adiciona um ativo ao portfólio do usuário."""
    async with AsyncSessionLocal() as session:
        await get_or_create_user(session, chat_id)

        result = await session.execute(
            select(Asset).where(Asset.user_chat_id == chat_id, Asset.ticker == ticker)
        )
        if result.scalars().first():
            await session.commit()
            return False

        new_asset = Asset(user_chat_id=chat_id, ticker=ticker)
        session.add(new_asset)
        await session.commit()
        return True

async def get_user_assets(chat_id: int):
    """Retorna lista de tickers do usuário."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.chat_id == chat_id)
        )
        user = result.scalars().first()
        if user:
            await session.refresh(user, attribute_names=['assets'])
            return [asset.ticker for asset in user.assets]
        return []

async def set_profile_analysis(chat_id: int, analysis: str):
    """Salva a análise de perfil."""
    async with AsyncSessionLocal() as session:
        user = await get_or_create_user(session, chat_id)
        user.profile = analysis
        await session.commit()

async def set_user_language(chat_id: int, language: str):
    """Atualiza o idioma preferido do usuário."""
    async with AsyncSessionLocal() as session:
        user = await get_or_create_user(session, chat_id)
        user.language = language
        await session.commit()

async def get_all_users_with_assets():
    """Busca todos os usuários e seus ativos para o Pipeline."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        data_map = {}
        for user in users:
            await session.refresh(user, attribute_names=['assets'])
            
            data_map[user.chat_id] = {
                "assets": [a.ticker for a in user.assets],
                "profile": user.profile,
                "language": user.language
            }
        return data_map