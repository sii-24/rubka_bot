from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler, ContextTypes

import logging

import classes.db_connect as db_connect
from classes.Logger import logger

async def my_events(update: Update, context: ContextTypes):
    logger(f"my_events is triggered by {update.effective_user}")

    db = db_connect.db()

    text = []
    for event in db.get_user_events(update.effective_user.id):
        text.append("\n".join([f"• Дата: {event.date}",
                              f"Место: {event.place}",
                              f"Оборудование: {event.equipment}",
                              f"Работник: {db.get_worker_name(event.person_id)}",
                              f"Комментарий: {event.comment}\n"]))

    await context.bot.send_message(chat_id=update.effective_user.id, text="\n".join(text))


my_events_handler = CommandHandler("my_events", my_events)
