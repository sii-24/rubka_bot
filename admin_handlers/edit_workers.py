from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

from services import unknown, cancel
from classes.Worker import Worker
from config import GROUP_ID, ADMINS
import classes.db_connect as db_connect
from classes.Logger import logger


WAIT_FOR_WORKER, WAIT_FOR_NAME, WAIT_FOR_ID, WAIT_FOR_EDIT = range(4)


async def edit_workers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger(f"edit_workers is triggered by {update.effective_user}")
    db = db_connect.db()
    if str(update.effective_user.id) not in ADMINS:
        return await unknown(update, context)
    kb = []
    for worker in db.get_workers():
        kb.append([InlineKeyboardButton(text=worker.name, callback_data=worker.id)])
    kb.append([InlineKeyboardButton(text="Создать нового", callback_data="new_worker")])
    kb = InlineKeyboardMarkup(kb)
    await update.message.reply_text(text="Выберите работника", reply_markup=kb)
    return WAIT_FOR_WORKER

async def new_worker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['worker'] = Worker()
    context.user_data['db'] = db_connect.db()
    context.user_data['edit_flag'] = False
    return await ask_name(update, context)

async def get_worker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['db'] = db_connect.db()
    context.user_data['worker'] = context.user_data['db'].get_worker(update.callback_query.data)
    context.user_data['edit_flag'] = True
    text=f"Текущее имя: {context.user_data['worker'].name}\nТекущий ID: {context.user_data['worker'].id}"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(text="Изменить имя", callback_data="edit_name")],
                                 [InlineKeyboardButton(text="Изменить ID", callback_data="edit_id")],
                                 [InlineKeyboardButton(text="Всё верно!", callback_data="edit_none")]])
    await context.bot.send_message(chat_id=update.effective_user.id, text=text, reply_markup=kb)
    return WAIT_FOR_EDIT

async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_user.id, text="Введите имя работника")
    return WAIT_FOR_NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    context.user_data['worker'].name = name
    text = f"Понял, имя: {name}"
    await update.message.reply_text(text)
    if context.user_data['edit_flag']:
        return await verify_data(update, context)
    else:
        return await ask_id(update, context)
    
async def ask_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_user.id, text="Введите ID работника")
    return WAIT_FOR_ID

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    id = update.message.text
    context.user_data['worker'].id = id
    text = f"Понял, ID: {id}"
    await update.message.reply_text(text)
    return await verify_data(update, context)

async def verify_data(update: Update, context: ContextTypes):
    db = context.user_data['db']
    text = [f"Проверьте правильность информации:\n",
            f"Имя: {context.user_data['worker'].name}",
            f"ID: {context.user_data['worker'].id}\n"]
    
    edit_kb = InlineKeyboardMarkup([[InlineKeyboardButton(text="Изменить имя", callback_data="edit_name")],
                                 [InlineKeyboardButton(text="Изменить ID", callback_data="edit_id")],
                                 [InlineKeyboardButton(text="Всё верно!", callback_data="edit_none")]])
    await context.bot.send_message(chat_id=update.effective_user.id, text='\n'.join(text), reply_markup=edit_kb)
    return WAIT_FOR_EDIT

async def edit_data(update: Update, context: ContextTypes):
    context.user_data['edit_flag'] = True
    data = update.callback_query.data
    await update.callback_query.answer()
    if data == 'edit_name':
        return await ask_name(update, context)
    elif data == 'edit_id':
        return await ask_id(update, context)
    else:
        return await register_edit(update, context)
    
async def register_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = context.user_data['db'] 
    logger(f"edited data: ID: {context.user_data['worker'].id}, NAME: {context.user_data['worker'].name}")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Успешно изменено!")
    db.edit_worker(context.user_data['worker'])
    context.user_data.clear()
    return ConversationHandler.END


edit_workers_handler = ConversationHandler(
    entry_points=[CommandHandler("edit_workers", edit_workers)],
    states={
        WAIT_FOR_WORKER: [CallbackQueryHandler(new_worker, pattern="new_worker"), CallbackQueryHandler(get_worker)],
        WAIT_FOR_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        WAIT_FOR_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_id)],
        WAIT_FOR_EDIT: [CallbackQueryHandler(edit_data)]
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)
