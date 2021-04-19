#! /usr/bin/env python
# -*- coding: utf-8 -*-

def hello():
    return "Вышли мне свои рецепты. После этого я буду высылать тебе меню."

def help():
    return "Список доступных команд:\n\
/menu_week - сгенерировать меню на неделю\n\
/menu_day - сгенерировать меню на день\n\
/menu_dish - выслать случайный рецепт\n"

def db_updated():
    return "Базу обновил, спасибо!"

def db_update_fail(error):
    return "Ошибка обновления базы: " + error

def err_no_categories():
    return "Не создано ни одной категории"

def err_no_tags():
    return "Не создано ни одного тега"

def err_no_recipes():
    return "Нет файла рецептов"

def cooking_time(arg):
	return "Время приготовления: " + arg + '\n'

def portions(arg):
	return "Количество: " + arg + '\n'

def ingridients(arg):
	return "Ингридиенты:\n" + arg + '\n'