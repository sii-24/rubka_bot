from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, ConversationHandler
import telegram

from config import ADMINS
from classes.Logger import logger


async def get_id(update: telegram.Update, context):
    if str(update.effective_user.id) not in ADMINS:
        return await unknown(update, context)
    logger(f"get_id is triggered by {update.effective_user}")
    await update.message.reply_text(update.effective_user.id)


async def get_group_id(update: telegram.Update, context):
    if str(update.effective_user.id) not in ADMINS:
        return await unknown(update, context)
    logger(f"get_group_id is triggered by {update.effective_user}")
    await update.message.reply_text(update.effective_chat.id)


async def cancel(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    logger(f"cancel is triggered by {update.effective_user}")
    context.user_data.clear()
    await update.message.reply_text("Операция прервана!")
    return ConversationHandler.END


async def help(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    logger(f"help is triggered by {update.effective_user}")
    text = [f"Вас приветствует бот для подачи заявок на сопровождение мероприятия световиками и звуковиками нашей школы!\n",
            f"Доступные команды:",
            f"/help - справка",
            f"/cancel - отменить текущую операцию",
            f"/my_events - получить список активных заявок",
            f"/new_event - создать новую заявку",
            f"/edit_event - изменить существующую заявку",
            f"/del_event - удалить существующую заявку"]
    await update.message.reply_text("\n".join(text))


async def unknown(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Неизвестная команда!")
