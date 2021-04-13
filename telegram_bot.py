#! /usr/bin/env python
# -*- coding: utf-8 -*-

import bot_token

from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

class KitchenHelperBot:
    def __init__(self, menu_action, db_update_action, random_recipe_action, random_day_menu_action, db_filename, db_file_ext="rtk"):
        self.db_filename = db_filename
        self.db_file_ext = db_file_ext

        self.menu_action = menu_action
        self.db_update_action = db_update_action
        self.random_recipe_action = random_recipe_action
        self.random_day_menu_action = random_day_menu_action

    def start_cb(self, update, context):
        context.bot.sendMessage(chat_id=update.message.chat_id, text="Вышли мне свои рецепты. После этого я буду высылать тебе меню.")
        context.bot.sendMessage(chat_id=update.message.chat_id, text="Напиши мне '/menu' чтобы получить меню на неделю. На любое другое сообщение я выдам тебе случайный рецепт.")

    def menu_cb(self, update, context):
        msg = context.bot.send_message(chat_id=update.effective_chat.id, text="Генерирую меню на неделю...")
        menu_text = self.menu_action()
        msg.edit_text(menu_text)

    def db_update_cb(self, update, context):
        file = context.bot.getFile(update.message.document.file_id)
        saved_filename = file.download(self.db_filename)
        self.db_update_action(saved_filename)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Базу обновил, спасибо!")

    def non_command_cb(self, update, context):
        action_choice = [
            [
                InlineKeyboardButton("Случайный рецепт", callback_data='random_recipe'),
                InlineKeyboardButton("Сгенерировать меню на день", callback_data='random_day_menu'),
            ]
        ]

        reply_markup = InlineKeyboardMarkup(action_choice)
        update.message.reply_text('Доступные варианты:', reply_markup=reply_markup)

    def non_command_answer_cb(self, update, context):
        query = update.callback_query
        query.answer()

        answer_text=""

        if (query.data == 'random_recipe'):
            query.edit_message_text(text=f"Генерирую случайный рецепт...")
            answer_text = self.random_recipe_action()
        elif (query.data == 'random_day_menu'):
            query.edit_message_text(text=f"Генерирую меню на день...")
            answer_text = self.random_day_menu_action()

        query.edit_message_text(text=answer_text)

    def start(self):
        updater = Updater(token=bot_token.token())
        dispatcher = updater.dispatcher

        start_handler = CommandHandler('start', self.start_cb)
        menu_handler = CommandHandler('menu', self.menu_cb)

        db_update_handler = MessageHandler(Filters.document.file_extension(self.db_file_ext), self.db_update_cb)
        non_command_handler = MessageHandler(Filters.text & (~Filters.command), self.non_command_cb)
        non_command_answer_handler = CallbackQueryHandler(self.non_command_answer_cb)

        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(menu_handler)
        dispatcher.add_handler(db_update_handler)
        dispatcher.add_handler(non_command_handler)
        dispatcher.add_handler(non_command_answer_handler)

        updater.start_polling()

if __name__ == '__main__':
    default_db_filename = './updated_db.zip'

    def menu_action():
        print("Menu is requested")
        return "Monday: nothing\nTuesday: what is love"

    def db_update_action(db_file_path):
        print("DB update is called with file:", db_file_path)

    def random_recipe_action():
        print("Generate recipe")
        return "2 eggs, 1 milk"

    def random_day_menu_action():
        print("Generate day menu")
        return "Breakfast: porrige"

    bot = KitchenHelperBot(menu_action, db_update_action, random_recipe_action, random_day_menu_action, default_db_filename)
    bot.start()