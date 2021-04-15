from telegram_bot import KitchenHelperBot
from menu_generator import MenuGenerator
from db_maintainer import DbMaintainer

import os

class KitchenHelper:
    def __init__(self):
        self.init_dirs()
        self.init_db()
        self.init_bot()

    def start(self):
        self.bot.start()

    def create_menu_week(self, user_id):
        print("Random week menu requested for user", user_id)
        return MenuGenerator().generate_menu_week(user_id)

    def create_menu_day(self, user_id):
        print("Random day menu requested for user", user_id)
        return MenuGenerator().generate_menu_day(user_id)

    def get_dish(self, user_id):
        print("Random dish requested for user", user_id)
        return MenuGenerator().generate_dish(user_id)

    def process_db_update(self, db_filename, user_id):
        print("DB update requested for user", user_id)
        DbMaintainer().update_db(db_filename, user_id)

    def user_appeared(self, user_id):
        print("User started with ID =", user_id)
        self.init_dir(self.users_dir + str(user_id))

    def init_dirs(self):
        update_dir = "./updates/"
        self.db_update_path = update_dir + "update.zip"
        self.users_dir = "./users/"
        self.logs_dir = "./logs/"

        self.init_dir(update_dir)
        self.init_dir(self.users_dir)
        self.init_dir(self.logs_dir)

    def init_dir(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def init_db(self):
        DbMaintainer().init("./")

    def init_bot(self):
        actions = { 'menu_week': self.create_menu_week,
                    'menu_day': self.create_menu_day,
                    'menu_dish': self.get_dish,
                    'db_update': self.process_db_update,
                    'new_user': self.user_appeared }

        self.bot = KitchenHelperBot(actions, self.db_update_path)

def main():
    kh = KitchenHelper()
    kh.start()

if __name__ == '__main__':
    main()