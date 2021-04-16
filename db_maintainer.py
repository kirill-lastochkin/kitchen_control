import sqlite3
import os

class DbMaintainer:
    def __init__(self, db_dir):
        self.name = db_dir + "recipes.db"

        if not os.path.exists(self.name):
            self.create_tables()

    def create_tables(self):
        with sqlite3.connect(self.name) as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE categories (id integer, category text, user integer)")
            cursor.execute("CREATE TABLE tags (id integer, tag text, user integer)")
            cursor.execute("""CREATE TABLE recipes
                              (id integer, title text, category integer, ingridients text,
                              cooking_time text, instruction text, portions text, url text,
                              pictures text, user integer)""")
            cursor.execute("CREATE TABLE recipe_to_tags (recipe integer, tag integer)")
            conn.commit()

    def update_db(self, data, user_id):
        pass