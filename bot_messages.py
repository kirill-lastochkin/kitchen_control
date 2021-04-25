#! /usr/bin/env python
# -*- coding: utf-8 -*-

def hello():
    return "Вышли мне свои рецепты. После этого я буду высылать тебе меню."

def help():
    return "Список доступных команд:\n\
/menu_week - <b>сгенерировать меню на неделю</b>\n\
/menu_dish - <b>получить случайный рецепт.</b> После ввода команды я предложу тебе ввести список тегов или категорию.\n\
Можно указать в одном сообщении и теги, и категории. Я учту все теги, которые ты укажешь, но категорию \
возьму только одну (первую). И можешь не задумываться о заглавных буквах, я все пойму. А еще можешь \
написать только часть слова, мне этого будет достаточно!\n\
<b>Пример:</b> <i>'кур салат'</i> => найду для тебя салат с курицей\n\
Но будь внимательней, если у тебя есть категории <i>'выпечка сладкая'</i> и <i>'выпечка несладкая'</i>, то, указав \
<i>'выпечка'</i>, ты попадешь на какую-то одну категорию (та, которую я первую увидел при обновлении базы)"

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

def day(number):
    return bold("День {}\n".format(number))

def dish(number):
    return bold("Блюдо №{}\n".format(number))

def repeating_dish(dish):
    return "Вчерашнее: {}\n".format(dish)

def bold(text):
    return "<b>{}</b>".format(text)

def italic(text):
    return "<i>{}</i>".format(text)

def wait_for_filters():
    return "Напиши мне список тегов или категорию через пробел"

def dishes_not_found():
    return "Ниче не нашел :("