from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from services import *

from config import TOKEN
from user_handlers.new_event import new_event_handler
from user_handlers.edit_event import edit_event_handler
from user_handlers.del_event import del_event_handler
from user_handlers.my_events import my_events_handler

from admin_handlers.get_events import get_events_handler
from admin_handlers.get_stat import get_stat_handler
from admin_handlers.approve_event import approve_event_handler, discard_event_handler
from admin_handlers.edit_workers import edit_workers_handler


bot = ApplicationBuilder().token(TOKEN).build()

#Вспомогательные
bot.add_handler(CommandHandler("start", help))
bot.add_handler(CommandHandler("help", help))
bot.add_handler(CommandHandler("get_id", get_id))
bot.add_handler(CommandHandler("get_group_id", get_group_id))
bot.add_handler(CommandHandler("cancel", cancel))

#user_handlers
bot.add_handler(new_event_handler)
bot.add_handler(edit_event_handler)
bot.add_handler(del_event_handler)
bot.add_handler(my_events_handler)

#admin_handlers
bot.add_handler(get_events_handler)
bot.add_handler(get_stat_handler)
bot.add_handler(approve_event_handler)
bot.add_handler(discard_event_handler)
bot.add_handler(edit_workers_handler)

bot.add_handler(MessageHandler(filters.ALL, unknown))

bot.run_polling()
