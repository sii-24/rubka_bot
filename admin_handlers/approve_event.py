from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

from services import unknown, cancel
from config import GROUP_ID, ADMINS
import classes.db_connect as db_connect
from classes.Logger import logger


WAIT_FOR_WORKER = range(1)


async def approve_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger(f"approve_event is triggered by {update.effective_user}")
    await update.callback_query.answer()
    db = db_connect.db()
    
    if db.get_event(str(update.callback_query.data)[7:]).approved == "1":
        return
    
    if str(update.effective_user.id) in ADMINS:
        kb = []
        for worker in db.get_workers():
            kb.append([InlineKeyboardButton(worker.name, callback_data=f"{worker.id}_{str(update.callback_query.data)[7:]}")])
        if db.get_event(str(update.callback_query.data)[7:]).person_id != "0":
            kb.append([InlineKeyboardButton("Оставить текущего", callback_data=f"{db.get_event(str(update.callback_query.data)[7:]).person_id}_{str(update.callback_query.data)[7:]}")])
        kb = InlineKeyboardMarkup(kb)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Текущий работник: {db.get_worker_name(db.get_event(str(update.callback_query.data)[7:]).person_id)}", reply_markup=kb)

        return WAIT_FOR_WORKER

    elif str(update.effective_user.id) in db.get_workers_id() and db.get_event(str(update.callback_query.data)[7:]).person_id == "0":
        db.approve(str(update.callback_query.data)[7:], update.effective_user.id)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Заявка подтверждена! Текущий работник: {db.get_worker_name(update.effective_user.id)}")
        return ConversationHandler.END
    
    elif db.get_event(str(update.callback_query.data)[7:]).person_id == str(update.effective_user.id):
        db.approve(str(update.callback_query.data)[7:])
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Заявка подтверждена! Текущий работник: {db.get_worker_name(update.effective_user.id)}")
        return ConversationHandler.END

    else:
        return
    

async def get_worker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    db = db_connect.db()
    db.approve_event(str(update.callback_query.data).split('_')[1], str(update.callback_query.data).split('_')[0])
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Заявка подтверждена! Текущий работник: {db.get_worker_name(str(update.callback_query.data).split('_')[0])}")
    return ConversationHandler.END
    

async def diskard_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger(f"diskard_event is triggered by {update.effective_user}")
    await update.callback_query.answer()
    db = db_connect.db()
    if str(update.effective_user.id) not in ADMINS and db.get_event(str(update.callback_query.data)[7:]).approved == True:
        return

    db.del_event(str(update.callback_query.data)[7:])
    await context.bot.send_message(chat_id=GROUP_ID, text="Заявка отклонена!")


approve_event_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(approve_event, pattern=r"^approve")],
    states={
        WAIT_FOR_WORKER: [CallbackQueryHandler(get_worker)],
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)

discard_event_handler = CallbackQueryHandler(diskard_event, pattern=r"^discard")
