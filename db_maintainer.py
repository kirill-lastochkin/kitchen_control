#! /usr/bin/env python
# -*- coding: utf-8 -*-

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

    def get_filtered(self, tags, category, user_id, allow_empty_category=False):
        with sqlite3.connect(self.name) as conn:
            cursor = conn.cursor()

            recipe_ids = self.get_recipe_ids(tags, user_id, cursor)
            category_id = self.get_category_id_by_name(category, user_id, cursor)
            
            if (not category_id and not allow_empty_category) or not recipe_ids:
                return []

            matched_recipes = []
            for recipe_id in recipe_ids:
                if category_id:
                    cursor.execute("SELECT title, ingridients, cooking_time, instruction, portions, url FROM recipes WHERE id = ? AND category = ?",
                                  (recipe_id, category_id))
                else:
                    cursor.execute("SELECT title, ingridients, cooking_time, instruction, portions, url FROM recipes WHERE id = ?",
                                  (recipe_id,))

                try:
                    title, ingridients, cooking_time, instruction, portions, url = cursor.fetchall().pop()
                    matched_recipes.append({ "title": title,
                                             "id": recipe_id,
                                             "ingridients": ingridients,
                                             "cooking_time": cooking_time,
                                             "instruction": instruction,
                                             "portions": portions,
                                             "url": url })
                except IndexError:
                    continue

            return matched_recipes

    def get_recipe_ids(self, tags, user_id, cursor):
        recipe_ids = []

        if tags:
            tag_ids = self.get_tag_ids_by_name(tags, user_id, cursor)
            recipe_ids = self.get_recipe_ids_by_tags(tag_ids, cursor)
        else:
            cursor.execute("SELECT id FROM recipes WHERE user = :id", {"id": user_id})
            for r in cursor.fetchall():
                recipe_ids.append(r[0])

        return recipe_ids

    def get_tag_ids_by_name(self, tags, user_id, cursor):
        sql_args = [user_id, ]
        sql = "SELECT id FROM tags WHERE user = ?"

        if tags:
            sql += " AND ("

            for tag in tags:
                sql += "tag = ?"
                if tag != tags[-1]:
                    sql += " OR "
                else:
                    sql += ")"

                sql_args.append(tag)

        cursor.execute(sql, sql_args)
        results = cursor.fetchall()
        tag_ids = []
        for r in results:
            tag_ids.append(r[0])

        return tag_ids

    def get_recipe_ids_by_tags(self, tag_ids, cursor):
        recipe_ids = []
        for tag in tag_ids:
            cursor.execute("SELECT recipe FROM recipe_to_tags WHERE tag = ?", (tag,))
            results = cursor.fetchall()
            for r in results:
                recipe_ids.append(r[0])

        return list(set(recipe_ids))

    def get_category_id_by_name(self, category, user_id, cursor):
        cursor.execute("SELECT id FROM categories WHERE user = ? AND category = ?", (user_id, category))
        try:
            return cursor.fetchall()[0][0]
        except IndexError:
            return None

    def tag(self, tag, user_id):
        with sqlite3.connect(self.name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT tag FROM tags WHERE user = ?", (user_id,))
            tags = cursor.fetchall()
            for t in tags:
                if tag.lower() in t[0].lower():
                    return t[0]
            return None

    def category(self, category, user_id):
        with sqlite3.connect(self.name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT category FROM categories WHERE user = ?", (user_id,))
            categories = cursor.fetchall()
            for c in categories:
                if category.lower() in c[0].lower():
                    return c[0]
            return None

    def update_db(self, data, user_id):
        self.clean_db_for_user(user_id)

        categories = data["categories"]
        tags = data["tags"]
        recipes = data["recipes"]

        with sqlite3.connect(self.name) as conn:
            cursor = conn.cursor()

            # fill categories table
            for category in categories:
                cursor.execute("INSERT INTO categories (category, user) VALUES (?, ?)", (category["name"], user_id))
                category["id"] = cursor.lastrowid

            # fill tags table
            for tag in tags:
                cursor.execute("INSERT INTO tags (tag, user) VALUES (?, ?)", (tag["name"], user_id))
                tag["id"] = cursor.lastrowid

            # fill recipes table
            for recipe in recipes:

                # find category ID
                category_id = None
                for category in categories:
                    if recipe["category"] == category["name"]:
                        category_id = category["id"]
                        break

                cursor.execute("""INSERT INTO recipes (title, category, ingridients, cooking_time, instruction,
                               portions, url, pictures, user) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                               (recipe["name"], category_id, recipe["ingredients"], recipe["cooking_time"],
                                recipe["instructions"], recipe["portions"], recipe["url"], recipe["pictures"], user_id))

                recipe_id = cursor.lastrowid

                # empty tags list for recipe is allowed
                if not recipe["tags"]:
                    continue

                # fill recipe_to_tags map
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
