#! /usr/bin/env python
# -*- coding: utf-8 -*-

import bot_token

from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters

class KitchenHelperBot:
    def __init__(self, db_filename):
        self.db_filename = db_filename

    def start_cb(self, update, context):
        context.bot.sendMessage(chat_id=update.message.chat_id, text="Вышли мне свои рецепты. После этого я буду высылать тебе меню.")
        context.bot.sendMessage(chat_id=update.message.chat_id, text="Напиши мне 'Menu' чтобы получить меню на неделю. На любое другое сообщение я выдам тебе случайный рецепт.")

    def menu_cb(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Высылаю меню!")

    def db_update_cb(self, update, context):
        file = context.bot.getFile(update.message.document.file_id)
        file.download(self.db_filename)

    def non_command_cb(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Высылаю случайный рецепт.")

    def start(self):
        updater = Updater(token=bot_token.token())
        dispatcher = updater.dispatcher

        start_handler = CommandHandler('start', self.start_cb)
        menu_handler = CommandHandler('menu', self.menu_cb)

        db_update_handler = MessageHandler(Filters.document, self.db_update_cb)
        non_command_handler = MessageHandler(Filters.text & (~Filters.command), self.non_command_cb)

        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(menu_handler)
        dispatcher.add_handler(db_update_handler)
        dispatcher.add_handler(non_command_handler)

        updater.start_polling()

if __name__ == '__main__':
    default_db_filename = './updated_db.zip'
    bot = KitchenHelperBot(default_db_filename)
    bot.start()