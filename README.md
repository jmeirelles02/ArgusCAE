# Argus BackEnd

Backend de monitoramento de ativos com alertas no Telegram, coleta de mercado via Yahoo Finance e análise por LLM local (Ollama).

## Requisitos

- Python 3.11+
- Ollama instalado e em execução (para `app/brain/reasoner.py`)

## Setup

1. Instale dependências:

```bash
pip install -r requirements.txt
```

2. Crie o arquivo `.env` com base no exemplo:

```bash
cp .env.example .env
```

3. Ajuste os valores do `.env`.

## Variáveis de Ambiente

- `TELEGRAM_TOKEN`: token do bot no Telegram (obrigatório).
- `DATABASE_URL`: URL async do banco SQLAlchemy (obrigatório).
- `CHROMA_PATH`: diretório de persistência do ChromaDB (opcional, padrão `./chroma_db`).
- `TELEGRAM_CHAT_ID`: chat id admin para fallback de notificação (opcional).

Exemplo recomendado para ambiente local:

```env
TELEGRAM_TOKEN=1234567890:YOUR_TELEGRAM_BOT_TOKEN
DATABASE_URL=sqlite+aiosqlite:///./argus.db
CHROMA_PATH=./chroma_db
TELEGRAM_CHAT_ID=
```

## Executar

```bash
uvicorn main:app --reload
```

O serviço inicializa o bot do Telegram e agenda o pipeline periódico de monitoramento.
