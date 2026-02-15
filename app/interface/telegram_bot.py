from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from app.core.config import settings
from app.brain.reasoner import ArgusMind
from app.core.store import add_asset, get_user_assets, set_profile_analysis, set_user_language

mind = ArgusMind()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇧🇷 PT", callback_data='set_pt'), InlineKeyboardButton("🇺🇸 EN", callback_data='set_en')]
    ]
    msg = (
        "👁️ **Olá, sou o Argus.**\n"
        "Comandos:\n"
        "`/add TICKER` - Adicionar ativo (ex: /add BTC-USD)\n"
        "`/perfil` - Analisar sua carteira\n"
        "Escolha seu idioma:"
    )
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def add_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Use: `/add ATIVO`", parse_mode='Markdown')
        return

    ticker = context.args[0].upper()
    chat_id = update.message.chat_id
    
    success = await add_asset(chat_id, ticker)
    
    if success:
        await update.message.reply_text(f"✅ **{ticker}** adicionado.", parse_mode='Markdown')
    else:
        await update.message.reply_text(f"⚠️ **{ticker}** já existe na sua lista.", parse_mode='Markdown')

async def profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    assets = await get_user_assets(chat_id)
    
    if not assets:
        await update.message.reply_text("Adicione ativos primeiro.", parse_mode='Markdown')
        return

    msg = await update.message.reply_text("🔄 Analisando...", parse_mode='Markdown')
    
    analysis = mind.generate_profile_analysis(assets)
    await set_profile_analysis(chat_id, analysis)
    
    await context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=f"📊 **Perfil:**\n{analysis}", parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    lang = 'pt' if query.data == 'set_pt' else 'en'
    await set_user_language(query.message.chat_id, lang)
    await query.edit_message_text(text=f"Idioma definido: {lang.upper()}")

def create_bot():
    app = ApplicationBuilder().token(settings.TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("config", start))
    app.add_handler(CommandHandler("add", add_handler))
    app.add_handler(CommandHandler("perfil", profile_handler))
    app.add_handler(CallbackQueryHandler(button_handler))
    return app