from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler, ContextTypes

from config import ADMINS
from services import unknown
import classes.db_connect as db_connect
from classes.Logger import logger


async def get_events(update: Update, context: ContextTypes):
    db = db_connect.db()
    if str(update.effective_user.id) not in db.get_workers_id():
        return await unknown(update, context)
    
    logger(f"get_events is triggered by Admin: {str(update.effective_user)[4:]}")

    text = []
    for event in db.get_all_events():
        text.append("\n".join([f"• ID: {event.id}",
                              f"Дата: {event.date}",
                              f"Место: {event.place}",
                              f"Оборудование: {event.equipment}",
                              f"Работник: {db.get_worker_name(event.person_id)}",
                              f"Комментарий: {event.comment}",
                              f"Контакт: {event.contact}",
                              f"Статус: {'Подтверждено' if event.approved else 'Не подтверждено'}\n"]))
        
    await context.bot.send_message(chat_id=update.effective_chat.id, text="\n".join(text))


get_events_handler = CommandHandler("get_events", get_events)
