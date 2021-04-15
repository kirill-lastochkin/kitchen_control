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