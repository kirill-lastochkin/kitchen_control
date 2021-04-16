#! /usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os

def parse_update(update_dir):
    return { "categories": parse_categories(update_dir),
             "tags": parse_tags(update_dir),
             "recipes": parse_recipes(update_dir) }

def parse_categories(update_dir):
    filename = update_dir + "categories.json"
    categories = []
    with open(filename, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        for category in data:
            categories.append(category["title"])

    return categories

def parse_tags(update_dir):
    filename = update_dir + "tags.json"
    tags = []
    with open(filename, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        for tag in data:
            tags.append(tag["title"])

    return tags

def parse_recipes(update_dir):
    recipe_files = []
    for file in os.listdir(update_dir):
        if "recipes_" in file and file[-5:] == ".json":
            recipe_files.append(update_dir + file)

    recipes = []
    for filename in recipe_files:
        with open(filename, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            for recipe in data:
                recipe_dict = {}

                try:
                    tags = []
                    for tag in recipe["tags"]:
                        tags.append(tag["title"])

                    recipe_dict["name"] = recipe["title"]
                    recipe_dict["category"] = recipe["categories"][0]["title"]
                    recipe_dict["tags"] = tags
                    recipe_dict["ingredients"] = recipe["ingredients"]
                    recipe_dict["instructions"] = recipe["instructions"]
                except KeyError:
                    continue

                if "pictures" in recipe:
                    pictures = ""
                    for pic in recipe["pictures"]:
                        pictures = pictures + pic.split('/')[-1] + ";"
                    recipe_dict["pictures"] = pictures

                if "cookingTime" in recipe:
                    recipe_dict["cooking_time"] = recipe["cookingTime"]

                if "quantity" in recipe:
                    recipe_dict["portions"] = recipe["quantity"]

                if "url" in recipe:
                    recipe_dict["url"] = recipe["url"]

                recipes.append(recipe_dict)

    return recipes

if __name__ == '__main__':
    print(parse_update('./users/339569354/temp/'))