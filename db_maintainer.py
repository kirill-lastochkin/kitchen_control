import sqlite3
import os
import random

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
            cursor.execute("CREATE TABLE recipe_to_tags (recipe integer, tag integer)")
            conn.commit()

    def get_random_recipe(self, user_id):
        random.seed()
        with sqlite3.connect(self.name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM recipes WHERE user = :id", {"id": user_id})
            recipe_tags = cursor.fetchall()
            random_recipe_id = random.choice(recipe_tags)
            cursor.execute("SELECT * FROM recipes WHERE id = ?", random_recipe_id)
            return cursor.fetchall()

    def get_by_tags(self, tags, user_id):
        with sqlite3.connect(self.name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM tags WHERE user = :id", {"id": user_id})
            tags_to_remove = cursor.fetchall()


    def update_db(self, data, user_id):
        self.clean_db_for_user(user_id)

        categories = data["categories"]
        tags = data["tags"]
        recipes = data["recipes"]

        with sqlite3.connect(self.name) as conn:
            cursor = conn.cursor()

            for category in categories:
                cursor.execute("INSERT INTO categories (category, user) VALUES (?, ?)", (category["name"], user_id))
                category["id"] = cursor.lastrowid

            for tag in tags:
                cursor.execute("INSERT INTO tags (tag, user) VALUES (?, ?)", (tag["name"], user_id))
                tag["id"] = cursor.lastrowid

            for recipe in recipes:
                category_name = recipe["category"]
                category_id = -1

                for category in categories:
                    if category_name == category["name"]:
                        category_id = category["id"]
                        break

                cursor.execute("""INSERT INTO recipes (title, category, ingridients, cooking_time, instruction,
                               portions, url, pictures, user) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                               (recipe["name"], category_id, recipe["ingredients"], recipe["cooking_time"],
                                recipe["instructions"], recipe["portions"], recipe["url"], recipe["pictures"], user_id))

                recipe_id = cursor.lastrowid

                for tag_name in recipe["tags"]:
                    for tag_db in tags:
                        if tag_name == tag_db["name"]:
                            cursor.execute("INSERT INTO recipe_to_tags (recipe, tag) VALUES (?, ?)", (recipe_id, tag_db["id"]))
                            break

            conn.commit()


    def clean_db_for_user(self, user_id):
        with sqlite3.connect(self.name) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM tags WHERE user = :id", {"id": user_id})
            tags_to_remove = cursor.fetchall()

            if tags_to_remove:
                cursor.executemany("DELETE FROM recipe_to_tags WHERE tag = ?", tags_to_remove)
            cursor.execute("DELETE FROM categories WHERE user = :id", {"id": user_id})
            cursor.execute("DELETE FROM tags WHERE user = :id", {"id": user_id})
            cursor.execute("DELETE FROM recipes WHERE user = :id", {"id": user_id})
            conn.commit()