from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler, ContextTypes

from config import ADMINS
from services import unknown
import classes.db_connect as db_connect
from classes.Logger import logger


async def get_stat(update: Update, context: ContextTypes):
    db = db_connect.db()

    if str(update.effective_user.id) not in db.get_workers_id():
        return await unknown(update, context)
    
    logger(f"get_stat is triggered by Admin: {str(update.effective_user)[4:]}")

    stat = db.get_stat()
    text = [f"Активные заявки: {stat.active_events}", f"Архивные заявки: {stat.archive_events}", f"Всего заявок: {stat.all_events}\n", "Активные:\n"]

    for event in db.get_active_events():
        text.append("\n".join([f"• ID: {event.id}",
                              f"Дата: {event.date}",
                              f"Место: {event.place}",
                              f"Оборудование: {event.equipment}",
                              f"Работник: {db.get_worker_name(event.person_id)}",
                              f"Комментарий: {event.comment}",
                              f"Контакт: {event.contact}",
                              f"Статус: {'Подтверждено' if event.approved else 'Не подтверждено'}\n"]))
        
    text.append("\nЗавершенные:\n")
    for event in db.get_archive_events():
        text.append("\n".join([f"• ID: {event.id}",
                              f"Дата: {event.date}",
                              f"Место: {event.place}",
                              f"Оборудование: {event.equipment}",
                              f"Работник: {db.get_worker_name(event.person_id)}",
                              f"Комментарий: {event.comment}",
                              f"Контакт: {event.contact}",
                              f"Статус: {'Подтверждено' if event.approved else 'Не подтверждено'}\n"]))
        
    await context.bot.send_message(chat_id=update.effective_chat.id, text="\n".join(text))


get_stat_handler = CommandHandler("get_stat", get_stat)
