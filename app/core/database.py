from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# Cria o motor de conexão assíncrono
engine = create_async_engine(settings.DATABASE_URL, echo=False)

# Fábrica de sessões
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Classe base para os Models
class Base(DeclarativeBase):
    pass

# Dependência para pegar o banco (Dependency Injection)
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Função para criar as tabelas no início (simples, sem Alembic por enquanto)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)