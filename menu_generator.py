import bot_messages as bm
import json
import random
import os

class MenuGenerator:
    def __init__(self, db_maintainer):
        self.db_maintainer = db_maintainer
        self.max_menu_part_len = 3000
        self.last_menu_file = "last_menu.json"
        self.unused_ingridients_file = "unused_ingridients.json"

    def generate_menu_week(self, user_id, working_dir, config_file):
        random.seed()
        menu_week = []

        with open(working_dir + config_file, 'r', encoding='utf-8') as json_file:
            used_recipes = self.last_menu_used_recipes(working_dir + self.last_menu_file)
            day_idx = 0

            for day in json.load(json_file)["days"]:
                recipe_idx = -1
                menu_day = []

                for recipe in day["recipes"]:
                    recipe_idx += 1

                    if "empty" in recipe:
                        menu_day.append(self.empty_dish())
                        continue

                    if "repeat" in recipe:
                        if day_idx == 0:
                            continue

                        menu_day.append(self.get_repeated_dish(menu_week, day_idx, recipe_idx))
                        continue

                    candidate_recipes = self.db_maintainer.get_filtered(recipe["tags"], recipe["category"], user_id)

                    while candidate_recipes:
                        self.chosen_recipe = random.choice(candidate_recipes)

                        ingridients_ok = True
                        if self.chosen_recipe["ingridients"]:
                            ingridients_ok = not self.ingridients_list_contains_unused(self.chosen_recipe["ingridients"], working_dir)

                        if self.chosen_recipe["id"] not in used_recipes and ingridients_ok:
                            menu_day.append(self.chosen_recipe)
                            used_recipes.append(self.chosen_recipe["id"])
                            break
                        else:
                            candidate_recipes.remove(self.chosen_recipe)
                    else: # no recipes were found
                        menu_day.append(self.empty_dish())

                menu_week.append(menu_day)
                day_idx += 1

        self.dump_data(working_dir + self.last_menu_file, menu_week)
        return self.menu_to_messages(menu_week)

    def get_repeated_dish(self, menu_week, current_day_idx, current_recipe_idx):
        repeated_recipe = menu_week[current_day_idx - 1][current_recipe_idx]
        insert_value = { "repeat": True }
        if "empty" not in repeated_recipe: insert_value["title"] = repeated_recipe["title"]
        else: insert_value["empty"] = True
        return insert_value

    def menu_to_messages(self, menu_week):
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

    def dump_data(self, dump_file, data):
        with open(dump_file, 'w', encoding='utf-8') as out:
            out.write(json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False))

    def empty_dish(self):
        return { "empty": True }

    def generate_dish(self, user_id, keywords_text):
        random.seed()
        keywords = [keywords_text, ]
        parsed = self.parse_dish_keywords(user_id, keywords)
        if not parsed["tags"] and not parsed["category"]:
            keywords = keywords_text.split()
            parsed = self.parse_dish_keywords(user_id, keywords)

            if not parsed["tags"] and not parsed["category"]:
                return (bm.dishes_not_found(),)

        matched_recipes = self.db_maintainer.get_filtered(parsed["tags"], parsed["category"], user_id, True)
        if not matched_recipes:
            return (bm.dishes_not_found(),)

        recipe = random.choice(matched_recipes)

        title_part = self.get_recipe_full_desc(recipe)
        result = self.split_if_long_message(title_part)
        if recipe["instruction"]: result += self.split_if_long_message(recipe["instruction"])
        return result

    def parse_dish_keywords(self, user_id, keywords):
        tags = []
        category = None

        for key in keywords:
            tag = self.db_maintainer.tag(key, user_id)
            if tag: tags.append(tag)

        for key in keywords:
            category = self.db_maintainer.category(key, user_id)
            if category: break

        return { "tags": list(set(tags)), "category": category }

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

    def add_unused_ingridient(self, ingridient, working_dir):
        unused_ingridients = []
        config_file = working_dir + self.unused_ingridients_file

        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as config:
                unused_ingridients = json.load(config)

        unused_ingridients.append(ingridient)
        self.dump_data(config_file, list(set(unused_ingridients)))

    def del_unused_ingridient(self, ingridient, working_dir):
        config_file = working_dir + self.unused_ingridients_file

        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as config:
                if ingridient.lower() == bm.all().lower():
                    unused_ingridients = []
                else:
                    unused_ingridients = json.load(config)
                    unused_ingridients.remove(ingridient)

            self.dump_data(config_file, unused_ingridients)

    def list_unused_ingridients(self, working_dir):
        resurt_list = ""
        config_file = working_dir + self.unused_ingridients_file

        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as config:
                unused_ingridients = json.load(config)
                for ingridient in unused_ingridients:
                    resurt_list += str(ingridient) + "\n"

        return resurt_list

    def ingridients_list_contains_unused(self, ingridients_list, working_dir):
        config_file = working_dir + self.unused_ingridients_file

        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as config:
                unused_ingridients = json.load(config)
                for ingridient in unused_ingridients:
                    if ingridient in ingridients_list:
                        return True

        return False
