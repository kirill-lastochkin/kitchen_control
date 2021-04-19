from telegram_bot import KitchenHelperBot
from menu_generator import MenuGenerator
from db_maintainer import DbMaintainer
from update_parser import parse_update

import os
import zipfile
import shutil

class KitchenHelper:
    def __init__(self):
        self.init_dirs()
        self.init_db()
        self.init_menu_generator()
        self.init_bot()

    def start(self):
        self.bot.start()

    def create_menu_week(self, user_id):
        print("Random week menu requested for user", user_id)
        return self.menu_generator.generate_menu_week(user_id)

    def create_menu_day(self, user_id):
        print("Random day menu requested for user", user_id)
        return self.menu_generator.generate_menu_day(user_id)

    def get_dish(self, user_id):
        print("Random dish requested for user", user_id)
        return self.menu_generator.generate_dish(user_id)

    def process_db_update(self, db_filename, user_id):
        print("DB update requested for user", user_id)

        extract_update_dir = self.user_dir(user_id) + "temp/"
        data_dir = self.user_dir(user_id) + "data/"

        self.init_dir(extract_update_dir)
        self.init_dir(data_dir)

        with zipfile.ZipFile(db_filename, 'r') as zip_ref:
            zip_ref.extractall(extract_update_dir)

        update_data = parse_update(extract_update_dir)
        if "error" in update_data:
            self.clean_user_temp_data(user_id)
            return { "result": False, "error": update_data["error"]}

        self.db_maintainer.update_db(update_data, user_id)

        os.replace(db_filename, self.user_dir(user_id) + "update.zip")
        self.clean_user_data(user_id)

        for file in os.listdir(extract_update_dir):
            if file[-4:] == ".jpg" or file[-4:] == ".png":
                os.replace(extract_update_dir + file, data_dir + file)

        self.clean_user_temp_data(user_id)
        return { "result": True }

    def user_appeared(self, user_id):
        print("User started with ID =", user_id)
        self.init_dir(self.users_dir + str(user_id))

    def init_dirs(self):
        update_dir = "./updates/"
        self.db_update_path = update_dir + "update.zip"
        self.users_dir = "./users/"
        self.logs_dir = "./logs/"
        self.db_dir = "./db/"

        self.init_dir(update_dir)
        self.init_dir(self.users_dir)
        self.init_dir(self.logs_dir)
        self.init_dir(self.db_dir)

    def init_dir(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def init_db(self):
        self.db_maintainer = DbMaintainer(self.db_dir)

    def init_menu_generator(self):
        self.menu_generator = MenuGenerator(self.db_maintainer)

    def user_dir(self, user_id):
        return self.users_dir + str(user_id) + '/'

    def clean_user_temp_data(self, user_id):
        shutil.rmtree(self.user_dir(user_id) + "temp/")

    def clean_user_data(self, user_id):
        data_dir = self.user_dir(user_id) + "data/"
        for file in os.listdir(data_dir):
            shutil.rmtree(data_dir + file)

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