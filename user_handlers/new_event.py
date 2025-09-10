from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import time
from functools import partial

import logging

from classes.Event import Event
from user_handlers.get_info import *
from services import cancel
from config import GROUP_ID
import classes.db_connect as db_connect
from classes.Logger import logger

async def new_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger(f"new_event is triggered by {update.effective_user}")

    context.user_data['event'] = Event()
    context.user_data['db'] = db_connect.db()
    context.user_data['edit_flag'] = False
    return await ask_date(update, context)


async def register_application(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['event'].id = str(int(time.time()))
    context.user_data['event'].contact = str(update.effective_user)[4:]
    context.user_data['event'].approved = False
    context.user_data['event'].active = True
    context.user_data['event'].user_id = update.effective_user.id
    db = context.user_data['db']
    USER_APPLICATION_TEXT = [f"Заявка принята!",
                             f"Скоро с вами свяжутся.\n",
                             f"Ваши данные:",
                             f"Дата: {context.user_data['event'].date}",
                             f"Место: {context.user_data['event'].place}",
                             f"Оборудование: {context.user_data['event'].equipment}",
                             f"Предпочитаемый работник: {db.get_worker_name(context.user_data['event'].person_id)}",
                             f"Комментарий: {context.user_data['event'].comment}\n"]

    GROUP_APPLICATION_TEXT = [f"Новая заявка!\n",
                              f"id: {context.user_data['event'].id}",
                              f"Дата: {context.user_data['event'].date}",
                              f"Место: {context.user_data['event'].place}",
                              f"Оборудование: {context.user_data['event'].equipment}",
                              f"Предпочитаемый работник: {db.get_worker_name(context.user_data['event'].person_id)}",
                              f"Комментарий: {context.user_data['event'].comment}\n"]
    
    approve_kb = InlineKeyboardMarkup([[InlineKeyboardButton(text="Подтвердить", callback_data=f"approve{context.user_data['event'].id}")], [InlineKeyboardButton("Отклонить", callback_data=f"discard{context.user_data['event'].id}")]])
    await context.bot.send_message(chat_id=update.effective_user.id, text="\n".join(USER_APPLICATION_TEXT))
    await context.bot.send_message(chat_id=GROUP_ID, text="\n".join(GROUP_APPLICATION_TEXT), reply_markup=approve_kb)
    db.add_event(context.user_data['event'])
    context.user_data.clear()
    return ConversationHandler.END


new_event_handler = ConversationHandler(
    entry_points=[CommandHandler("new_event", new_event)],
    states={
        WAIT_FOR_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_date)],
        WAIT_FOR_PLACE: [CallbackQueryHandler(get_place)],
        WAIT_FOR_ANOTHER_PLACE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_another_place)],
        WAIT_FOR_EQUIPMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_equipment)],
        WAIT_FOR_PERSON: [CallbackQueryHandler(get_person)],
        WAIT_FOR_COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_comment)],
        WAIT_FOR_EDIT: [CallbackQueryHandler(partial(edit_data, register=register_application))]
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)
