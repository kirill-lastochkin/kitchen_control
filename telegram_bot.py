import bot_token
import bot_messages as bm
import time
import sys
import threading

from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, KeyboardButton, ParseMode

class KitchenHelperBot:
    def __init__(self, actions, db_filename, db_file_ext="rtk"):
        self.db_filename = db_filename
        self.db_file_ext = db_file_ext
        self.actions = actions

    def start(self):
        self.updater = Updater(token=bot_token.token())
        dispatcher = self.updater.dispatcher

        dispatcher.add_handler(CommandHandler('start', self.start_cb))
        dispatcher.add_handler(CommandHandler('menu_week', self.menu_week_cb))
        dispatcher.add_handler(CommandHandler('menu_day', self.menu_day_cb))
        dispatcher.add_handler(CommandHandler('menu_dish', self.menu_dish_cb))
        dispatcher.add_handler(CommandHandler('help', self.help_cb))
        dispatcher.add_handler(CommandHandler('kill', self.kill_cb))

        dispatcher.add_handler(MessageHandler(Filters.document.file_extension(self.db_file_ext), self.db_update_cb))
        dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), self.help_cb))

        self.updater.start_polling()

    def stop(self):
        self.updater.stop()
        self.updater.is_idle = False

    def start_cb(self, update, context):
        main_menu_keyboard = [KeyboardButton('/menu_week'),
                              KeyboardButton('/menu_day'),
                              KeyboardButton('/menu_dish'),
                              KeyboardButton('/help')]

        reply_kb_markup = ReplyKeyboardMarkup.from_row(main_menu_keyboard, resize_keyboard=True, one_time_keyboard=False)

        context.bot.sendMessage(chat_id=update.message.chat_id, text=bm.hello())
        context.bot.send_message(chat_id=update.message.chat_id, text=bm.help(), reply_markup=reply_kb_markup)

        user_id = update.message.from_user['id']
        self.actions['new_user'](user_id)

    def menu_week_cb(self, update, context):
        user_id = update.message.from_user['id']
        menu_parts = self.actions['menu_week'](user_id)

        for part in menu_parts:
            context.bot.send_message(chat_id=update.effective_chat.id, text=part, parse_mode=ParseMode.MARKDOWN)

    def menu_day_cb(self, update, context):
        user_id = update.message.from_user['id']
        menu_parts = self.actions['menu_day'](user_id)

        for part in menu_parts:
            context.bot.send_message(chat_id=update.effective_chat.id, text=part)

    def menu_dish_cb(self, update, context):
        user_id = update.message.from_user['id']
        menu_parts = self.actions['menu_dish'](user_id)

        for part in menu_parts:
            context.bot.send_message(chat_id=update.effective_chat.id, text=part)

    def db_update_cb(self, update, context):
        user_id = update.message.from_user['id']
        file = context.bot.getFile(update.message.document.file_id)
        saved_filename = file.download(self.db_filename)
        result = self.actions['db_update'](saved_filename, user_id)
        if result["result"]:
            context.bot.send_message(chat_id=update.effective_chat.id, text=bm.db_updated())
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=bm.db_update_fail(result["error"]))

    def help_cb(self, update, context):
        context.bot.send_message(chat_id=update.message.chat_id, text=bm.help())

    def kill_cb(self, update, context):
        print("Got kill command!")
        try:
            from admin_data import kill_password
            password = context.args[0]
            if password != kill_password():
                return
        except:
            return

        #context.bot.send_message(chat_id=update.message.chat_id, text="No!")
        #time.sleep(1)
        #context.bot.send_message(chat_id=update.message.chat_id, text="No, please!")
        #time.sleep(1)
        context.bot.send_message(chat_id=update.message.chat_id, text="Bot was executed.")
        threading.Thread(target=self.stop).start()


if __name__ == '__main__':
    actions = { 'menu_week': lambda user_id: "Empty week menu",
                'menu_day': lambda user_id: "Empty day menu",
                'menu_dish': lambda user_id: "Empty dish",
                'db_update': lambda db_file_path, user_id: print("DB updated:", db_file_path),
                'new_user': lambda user_id: print("New user with ID:", user_id) }

    default_db_filename = './updated_db.zip'

    bot = KitchenHelperBot(actions, default_db_filename)
    bot.start()