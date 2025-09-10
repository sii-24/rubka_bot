from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from functools import partial

from classes.Event import Event
from config import GROUP_ID
import classes.db_connect as db_connect
from user_handlers.new_event import *
from classes.Logger import logger


async def edit_event(update: Update, context: ContextTypes):
    logger(f"edit_event is triggered by {update.effective_user}")
    
    context.user_data['event'] = Event()
    context.user_data['db'] = db_connect.db()
    context.user_data['edit_flag'] = True
    db = context.user_data['db']
    text = "Какую заявку вы хотите изменить?"
    events_kb = InlineKeyboardMarkup([[InlineKeyboardButton(text=f"{event.place}, {event.date}", callback_data=event.id)] for event in db.get_user_events(update.effective_user.id)])
    await update.message.reply_text(text=text, reply_markup=events_kb)
    return WAIT_FOR_EVENT


async def get_editing_event(update: Update, context: ContextTypes):
    db = context.user_data['db']
    for event in db.get_user_events(update.effective_user.id):
        if event.id == update.callback_query.data:
            context.user_data['event'] = event
    return await verify_data(update, context)


async def register_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = context.user_data['db']
    USER_APPLICATION_TEXT = [f"Заявка изменена!\n",
                             f"Ваши данные:",
                             f"Дата: {context.user_data['event'].date}",
                             f"Место: {context.user_data['event'].place}",
                             f"Оборудование: {context.user_data['event'].equipment}",
                             f"Предпочитаемый работник: {db.get_worker_name(context.user_data['event'].person_id)}",
                             f"Комментарий: {context.user_data['event'].comment}\n"]

    GROUP_APPLICATION_TEXT = [f"Изменена заявка!\n",
                              f"id: {context.user_data['event'].id}",
                              f"Дата: {context.user_data['event'].date}",
                              f"Место: {context.user_data['event'].place}",
                              f"Оборудование: {context.user_data['event'].equipment}",
                              f"Предпочитаемый работник: {db.get_worker_name(context.user_data['event'].person_id)}",
                              f"Комментарий: {context.user_data['event'].comment}\n"]
    await context.bot.send_message(chat_id=update.effective_user.id, text="\n".join(USER_APPLICATION_TEXT))
    await context.bot.send_message(chat_id=GROUP_ID, text="\n".join(GROUP_APPLICATION_TEXT))
    db.edit_event(context.user_data['event'])
    context.user_data.clear()
    return ConversationHandler.END


edit_event_handler = ConversationHandler(
    entry_points=[CommandHandler("edit_event", edit_event)],
    states={
        WAIT_FOR_DATE: [MessageHandler(filters.TEXT, get_date)],
        WAIT_FOR_PLACE: [CallbackQueryHandler(get_place)],
        WAIT_FOR_ANOTHER_PLACE: [MessageHandler(filters.TEXT, get_another_place)],
        WAIT_FOR_EQUIPMENT: [MessageHandler(filters.TEXT, get_equipment)],
        WAIT_FOR_PERSON: [CallbackQueryHandler(get_person)],
        WAIT_FOR_COMMENT: [MessageHandler(filters.TEXT, get_comment)],
        WAIT_FOR_EDIT: [CallbackQueryHandler(partial(edit_data, register=register_edit))],
        WAIT_FOR_EVENT: [CallbackQueryHandler(get_editing_event)]
    },
    fallbacks=[]
)
