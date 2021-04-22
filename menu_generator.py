import bot_messages as bm
import json
import random
import os

class MenuGenerator:
    def __init__(self, db_maintainer):
        self.db_maintainer = db_maintainer
        self.max_menu_part_len = 3000
        self.last_menu_file = "last_menu.json"

    def generate_menu_week(self, user_id, working_dir, config_file):
        menu_week = []
        with open(working_dir + config_file, 'r', encoding='utf-8') as json_file:
            config = json.load(json_file)
            days = config["days"]
            used_recipes = self.last_menu_used_recipes(working_dir + self.last_menu_file)
            day_idx = 0

            for day in days:
                recipes = day["recipes"]
                recipe_idx = -1
                menu_day = []
                for recipe in recipes:
                    recipe_idx += 1
                    if "empty" in recipe:
                        menu_day.append({ "empty": True })
                        continue

                    if "repeat" in recipe:
                        if day_idx == 0:
                            continue

                        repeated_recipe = menu_week[day_idx - 1][recipe_idx]
                        insert_value = { "repeat": True }
                        if "empty" not in repeated_recipe: insert_value["title"] = repeated_recipe["title"]
                        else: insert_value["empty"] = True
                        menu_day.append(insert_value)
                        continue

                    category = recipe["category"]
                    tags = recipe["tags"]

                    candidate_recipes = self.db_maintainer.get_filtered(tags, category, user_id)
                    chosen_recipe = None
                    random.seed()

                    while candidate_recipes:
                        chosen_recipe = random.choice(candidate_recipes)
                        if chosen_recipe["id"] not in used_recipes:
                            menu_day.append(chosen_recipe)
                            used_recipes.append(chosen_recipe["id"])
                            break
                        else:
                            candidate_recipes.remove(chosen_recipe)
                    else:
                        menu_day.append({ "empty": True })

                menu_week.append(menu_day)
                day_idx += 1

        with open(working_dir + self.last_menu_file, 'w', encoding='utf-8') as out:
            out.write(json.dumps(menu_week, indent=4, sort_keys=True, ensure_ascii=False))

        message_set = []
        day_idx = 1
        for day in menu_week:
            message = bm.day(day_idx)
            day_idx += 1
            recipe_idx = 1

            for recipe in day:
                if "empty" in recipe:
                    continue

                message += bm.dish(recipe_idx)
                recipe_idx += 1

                name = recipe["title"]
                if "repeat" in recipe:
                    message += bm.repeating_dish(name) + '\n'
                    continue

                message += bm.italic(name) + '\n\n'
                if recipe["ingridients"]: message += recipe["ingridients"] + '\n'
                if recipe["url"]: message += recipe["url"] + '\n'
                message += '\n'

            message_set.append(message)

        return message_set

    def generate_menu_day(self, user_id):
        return ("Empty day menu", )

    def last_menu_used_recipes(self, last_menu_filepath):
        used_recipes = []

        if os.path.exists(last_menu_filepath):
            with open(last_menu_filepath, 'r', encoding='utf-8') as last_menu_file:
                last_menu = json.load(last_menu_file)

                for day in last_menu:
                    for recipe in day:
                        if "id" in recipe:
                            used_recipes.append(recipe["id"])

        return used_recipes

    def generate_dish(self, user_id):
        recipe = self.db_maintainer.get_random_recipe(user_id)
        title_part = self.get_recipe_full_desc(recipe)
        result = self.split_if_long_message(title_part)
        if recipe["instruction"]: result += self.split_if_long_message(recipe["instruction"])
        return result

    def get_recipe_short_desc(self, recipe):
        description = recipe["title"] + '\n'
        description += bm.ingridients(recipe["ingridients"])
        return description

    def get_recipe_full_desc(self, recipe):
        description = recipe["title"] + '\n'
        if recipe["cooking_time"]: description += bm.cooking_time(recipe["cooking_time"])
        if recipe["portions"]: description += bm.portions(recipe["portions"])
        if recipe["ingridients"]: description += bm.ingridients(recipe["ingridients"])
        if recipe["url"]: description += recipe["url"] + '\n'
        return description

    def split_if_long_message(self, message):
        result = []
        message_len = len(message)

        if message_len > self.max_menu_part_len:
            processed_len = 0
            while processed_len < message_len:
                result.append(message[processed_len : processed_len + self.max_menu_part_len])
                processed_len += self.max_menu_part_len
        else:
            result.append(message)

        return result