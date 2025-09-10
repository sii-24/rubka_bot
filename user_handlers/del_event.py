from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler, ContextTypes

from config import GROUP_ID
from user_handlers.get_info import WAIT_FOR_EVENT
import classes.db_connect as db_connect
from classes.Logger import logger


async def del_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger(f"del_event is triggered by {update.effective_user}")

    context.user_data['db'] = db_connect.db()
    db = context.user_data['db']
    text = "Какую заявку вы хотите удалить?"
    events_kb = InlineKeyboardMarkup([[InlineKeyboardButton(text=f"{event.place}, {event.date}", callback_data=event.id)] for event in db.get_user_events(update.effective_user.id)])
    await update.message.reply_text(text=text, reply_markup=events_kb)
    return WAIT_FOR_EVENT

async def get_deleting_event(update: Update, context: ContextTypes):
    db = context.user_data['db']
    for event in db.get_user_events(update.effective_user.id):
        if event.id == update.callback_query.data:
            context.user_data['event'] = event
    return await register_del_event(update, context)

async def register_del_event(update: Update, context: ContextTypes):
    db = context.user_data['db']
    event = context.user_data['event']

    GROUP_APPLICATION_TEXT = [f"Удалена заявка!\n",
                              f"id: {event.id}",
                              f"Дата: {event.date}",
                              f"Место: {event.place}",
                              f"Оборудование: {event.equipment}",
                              f"Работник: {db.get_worker_name(event.person_id)}\n"]
    await context.bot.send_message(chat_id=update.effective_user.id, text="Заявка удалена!")
    await context.bot.send_message(chat_id=GROUP_ID, text="\n".join(GROUP_APPLICATION_TEXT))
    db.del_event(event)
    context.user_data.clear()
    await update.callback_query.answer()
    return ConversationHandler.END


del_event_handler = ConversationHandler(
    entry_points=[CommandHandler("del_event", del_event)],
    states={
        WAIT_FOR_EVENT: [CallbackQueryHandler(get_deleting_event)]
    },
    fallbacks=[]
)