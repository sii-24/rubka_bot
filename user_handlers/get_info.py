from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import time

import logging

from classes.Event import Event
from classes.Worker import Worker
from services import cancel
from config import GROUP_ID
import classes.db_connect as db_connect


WAIT_FOR_DATE, WAIT_FOR_PLACE, WAIT_FOR_ANOTHER_PLACE, WAIT_FOR_EQUIPMENT, WAIT_FOR_PERSON, WAIT_FOR_EDIT, WAIT_FOR_EVENT, WAIT_FOR_COMMENT = range(8)


async def ask_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await context.bot.send_message(chat_id=update.effective_user.id, text="Когда будет мероприятие?")
    return WAIT_FOR_DATE

async def get_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    day = update.message.text
    context.user_data['event'].date = day
    text = f"Понял, мероприятие будет {day}"
    await update.message.reply_text(text)
    if context.user_data['edit_flag']:
        return await verify_data(update, context)
    else:
        return await ask_place(update, context)

async def ask_place(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    place_kb = InlineKeyboardMarkup([[InlineKeyboardButton(text="Зал", callback_data="Зал")],
                                 [InlineKeyboardButton(text="Двор", callback_data="Двор")],
                                 [InlineKeyboardButton(text="Другое", callback_data="Другое")]])
    await context.bot.send_message(chat_id=update.effective_user.id, text="Где будет мероприятие?", reply_markup=place_kb)
    return WAIT_FOR_PLACE

async def get_place(update: Update, context: ContextTypes.DEFAULT_TYPE):
    place = update.callback_query.data
    await update.callback_query.answer()
    if place == "Другое":
        return await ask_another_place(update, context)
    context.user_data['event'].place = place
    text = f"Понял, мероприятие будет в: {place}"
    await context.bot.send_message(chat_id=update.effective_user.id, text=text)
    if context.user_data['edit_flag']:
        return await verify_data(update, context)
    else:
        return await ask_equipment(update, context)
    
async def ask_another_place(update: Update, context: ContextTypes):
    await context.bot.send_message(chat_id=update.effective_user.id, text="В каком месте?")
    return WAIT_FOR_ANOTHER_PLACE

async def get_another_place(update: Update, context: ContextTypes.DEFAULT_TYPE):
    place = update.message.text
    context.user_data['event'].place = place
    text = f"Понял, мероприятие будет в: {place}"
    await context.bot.send_message(chat_id=update.effective_user.id, text=text)
    if context.user_data['edit_flag']:
        return await verify_data(update, context)
    else:
        return await ask_equipment(update, context)

async def ask_equipment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await context.bot.send_message(chat_id=update.effective_user.id, text="Какое оборудование требуется?")
    return WAIT_FOR_EQUIPMENT

async def get_equipment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    equipment = update.message.text
    context.user_data['event'].equipment = equipment
    text = f"Понял, нужно: {equipment}"
    await update.message.reply_text(text)
    if context.user_data['edit_flag']:
        return await verify_data(update, context)
    else:
        return await ask_person(update, context)

async def ask_person(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    db = context.user_data['db']
    workers = [[InlineKeyboardButton(text=worker.name, callback_data=str(worker.id))] for worker in db.get_workers()]
    workers.append([InlineKeyboardButton(text="Любой", callback_data="Любой")])
    person_kb = InlineKeyboardMarkup(workers)
    await context.bot.send_message(chat_id=update.effective_user.id, text="Вы бы хотели, чтобы кто сопровождал мероприятие?", reply_markup=person_kb)
    return WAIT_FOR_PERSON

async def get_person(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = context.user_data['db']
    await update.callback_query.answer()
    if update.callback_query.data == "Любой":
        person = "Любой"
        context.user_data['event'].person_id = "0"
    else:
        person = db.get_worker_name(update.callback_query.data)
        context.user_data['event'].person_id = update.callback_query.data
        
    text = f"Понял, вы хотите чтобы мероприятие сопровождал(а) {person}"
    await context.bot.send_message(chat_id=update.effective_user.id, text=text)
    if context.user_data['edit_flag']:
        return await verify_data(update, context)
    else:
        return await ask_comment(update, context)

async def ask_comment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await context.bot.send_message(chat_id=update.effective_user.id, text="Оставьте комментарий к заявке, например, удобный способ связи")
    return WAIT_FOR_COMMENT

async def get_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    comment = update.message.text
    context.user_data['event'].comment = comment
    text = f"Понял, принял"
    await update.message.reply_text(text)
    if context.user_data['edit_flag']:
        return await verify_data(update, context)
    else:
        return await verify_data(update, context)
    
async def verify_data(update: Update, context: ContextTypes):
    db = context.user_data['db']
    text = [f"Проверьте правильность информации:\n",
            f"Дата: {context.user_data['event'].date}",
            f"Место: {context.user_data['event'].place}",
            f"Оборудование: {context.user_data['event'].equipment}",
            f"Предпочитаемый работник: {db.get_worker_name(context.user_data['event'].person_id)}",
            f"Комментарий: {context.user_data['event'].comment}\n"]
    
    edit_kb = InlineKeyboardMarkup([[InlineKeyboardButton(text="Изменить дату", callback_data="edit_date")],
                                 [InlineKeyboardButton(text="Изменить место", callback_data="edit_place")],
                                 [InlineKeyboardButton(text="Изменить оборудование", callback_data="edit_equipment")],
                                 [InlineKeyboardButton(text="Изменить работника", callback_data="edit_person")],
                                 [InlineKeyboardButton(text="Изменить комментарий", callback_data="edit_comment")],
                                 [InlineKeyboardButton(text="Всё верно!", callback_data="edit_none")]])
    await context.bot.send_message(chat_id=update.effective_user.id, text='\n'.join(text), reply_markup=edit_kb)
    return WAIT_FOR_EDIT

async def edit_data(update: Update, context: ContextTypes, register):
    context.user_data['edit_flag'] = True
    data = update.callback_query.data
    await update.callback_query.answer()
    if data == 'edit_date':
        return await ask_date(update, context)
    elif data == 'edit_place':
        return await ask_place(update, context)
    elif data == 'edit_equipment':
        return await ask_equipment(update, context)
    elif data == 'edit_person':
        return await ask_person(update, context)
    elif data == 'edit_comment':
        return await ask_comment(update, context)
    else:
        return await register(update, context)
    