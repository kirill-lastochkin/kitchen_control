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
            conn.execute("CREATE TABLE categories (id integer PRIMARY KEY AUTOINCREMENT, category text, user integer)")
            cursor.execute("CREATE TABLE tags (id integer PRIMARY KEY AUTOINCREMENT, tag text, user integer)")
            cursor.execute("""CREATE TABLE recipes
                              (id integer PRIMARY KEY AUTOINCREMENT, title text, category integer, ingridients text,
                              cooking_time text, instruction text, portions text, url text,
                              pictures text, user integer)""")
            cursor.execute("CREATE TABLE recipe_to_tags (recipe integer PRIMARY KEY, tag integer)")
            conn.commit()

    def update_db(self, data, user_id):
        self.clean_db_for_user(user_id)

        categories = data["categories"]
        tags = data["tags"]
        recipes = data["recipes"]

        tag_ids = []

        with sqlite3.connect(self.name) as conn:
            cursor = conn.cursor()

            for category in categories:
                cursor.execute("INSERT INTO categories (category, user) VALUES (?, ?)", (category, user_id))

            for tag in tags:
                cursor.execute("INSERT INTO categories (category, user) VALUES (?, ?)", (tag, user_id))



    def clean_db_for_user(self, user_id):
        with sqlite3.connect(self.name) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM tags WHERE user = :id", {"id": user_id})
            tags_to_remove = cursor.fetchall()

            cursor.executemany("DELETE FROM recipe_to_tags WHERE tag = ?", tags_to_remove)
            cursor.execute("DELETE FROM categories WHERE user = :id", {"id": user_id})
            cursor.execute("DELETE FROM tags WHERE user = :id", {"id": user_id})
            cursor.execute("DELETE FROM recipes WHERE user = :id", {"id": user_id})
            cursor.commit()