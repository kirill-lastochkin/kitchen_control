import bot_messages as bm
import json
import random

class MenuGenerator:
    def __init__(self, db_maintainer):
        self.db_maintainer = db_maintainer
        self.max_menu_part_len = 3000

    def generate_menu_week(self, user_id, config_file):
        with open(config_file, 'r', encoding='utf-8') as json_file:
            config = json.load(json_file)
            days = config["days"]

            menu_week = []
            day_idx = 0

            for day in days:
                recipes = day["recipes"]
                recipe_idx = 0
                menu_day = []
                for recipe in recipes:
                    if "empty" in recipe:
                        continue

                    if "repeat" in recipe:
                        # todo read prev recipe
                        if recipe_idx == 0: continue
                        continue

                    category = recipe["category"]
                    tags = recipe["tags"]

                    candidate_recipes = self.db_maintainer.get_filtered(tags, category, user_id)
                    random.seed()
                    chosen_recipe = random.choice(candidate_recipes)

                    menu_day.append(chosen_recipe)

                    #exclude from prev week menu

                    recipe_idx += 1

                menu_week.append(menu_day)
                day_idx += 1

        print(menu_week)

        return ("Empty week menu", )

    def generate_menu_day(self, user_id):
        return ("Empty day menu", )

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