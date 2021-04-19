#! /usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os

import bot_messages as bm

def parse_update(update_dir):
    try:
        return { "categories": parse_categories(update_dir),
                 "tags": parse_tags(update_dir),
                 "recipes": parse_recipes(update_dir) }
    except Exception as e:
        return { "error": e.args[0] }

def parse_categories(update_dir):
    filename = update_dir + "categories.json"

    if not os.path.exists(filename):
        raise Exception(bm.err_no_categories())

    categories = []
    with open(filename, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        for category in data:
            categories.append({"name": category["title"]})

    return categories

def parse_tags(update_dir):
    filename = update_dir + "tags.json"

    if not os.path.exists(filename):
        raise Exception(bm.err_no_tags())

    tags = []
    with open(filename, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        for tag in data:
            tags.append({"name": tag["title"]})

    return tags

def parse_recipes(update_dir):
    recipe_files = []
    for file in os.listdir(update_dir):
        if "recipes_" in file and file[-5:] == ".json":
            recipe_files.append(update_dir + file)

    if not recipe_files:
        raise Exception(bm.err_no_recipes())

    recipes = []
    for filename in recipe_files:
        with open(filename, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            for recipe in data:
                recipe_dict = {}

                try:
                    recipe_dict["name"] = recipe["title"]
                    recipe_dict["category"] = recipe["categories"][0]["title"]
                except (KeyError, IndexError):
                    continue

                if "tags" in recipe:
                    tags = []
                    for tag in recipe["tags"]:
                        tags.append(tag["title"])
                    recipe_dict["tags"] = tags
                else:
                    recipe_dict["tags"] = None

                if "ingredients" in recipe:
                    recipe_dict["ingredients"] = recipe["ingredients"]
                else:
                    recipe_dict["ingredients"] = None

                if "instructions" in recipe:
                    recipe_dict["instructions"] = recipe["instructions"]
                else:
                    recipe_dict["instructions"] = None

                if "pictures" in recipe:
                    pictures = ""
                    for pic in recipe["pictures"]:
                        pictures = pictures + pic.split('/')[-1] + ";"
                    recipe_dict["pictures"] = pictures
                else:
                    recipe_dict["pictures"] = None

                if "cookingTime" in recipe:
                    recipe_dict["cooking_time"] = recipe["cookingTime"]
                else:
                    recipe_dict["cooking_time"] = None

                if "quantity" in recipe:
                    recipe_dict["portions"] = recipe["quantity"]
                else:
                    recipe_dict["portions"] = None

                if "url" in recipe:
                    recipe_dict["url"] = recipe["url"]
                else:
                    recipe_dict["url"] = None

                recipes.append(recipe_dict)

    return recipes

if __name__ == '__main__':
    print(parse_update('./users/339569354/data/'))