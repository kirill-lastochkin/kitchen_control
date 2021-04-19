import bot_messages as bm

class MenuGenerator:
    def __init__(self, db_maintainer):
        self.db_maintainer = db_maintainer
        self.max_menu_part_len = 3000

    def generate_menu_week(self, user_id):
        return "Empty week menu"

    def generate_menu_day(self, user_id):
        return "Empty day menu"

    def generate_dish(self, user_id):
        recipe = self.db_maintainer.get_random_recipe(user_id)
        title_part = recipe["title"] + '\n'
        if recipe["cooking_time"]: title_part += bm.cooking_time(recipe["cooking_time"])
        if recipe["portions"]: title_part += bm.portions(recipe["portions"])
        title_part += bm.ingridients(recipe["ingridients"])
        if recipe["url"]: title_part += recipe["url"] + '\n'

        result = [title_part,]

        instruct_part = recipe["instruction"]
        instruct_part_len = len(instruct_part)
        if instruct_part_len > self.max_menu_part_len:
            processed_len = 0
            while processed_len < instruct_part_len:
                result.append(instruct_part[processed_len : processed_len + self.max_menu_part_len])
                processed_len += self.max_menu_part_len
        else:
            result.append(instruct_part)

        return result