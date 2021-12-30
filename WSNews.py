# -*- coding: utf-8 -*-

#from MyHTMLParser import WebPageParser
from WebsiteShaking import NewsObject
import getopt, sys

cmd_args = sys.argv
args_list = cmd_args[1:]
if not args_list:
    print('[ERROR] Необходимо указать URL. Подробнее: --help (-h)')
    sys.exit(2)

short_args = "hu:ci"
long_args = ["help", "url=", "config", "info"]

try:
    arguments, values = getopt.getopt(args_list, short_args, long_args)
except getopt.error as err:
    print("[ERROR]" + str(err))
    sys.exit(2)

no = NewsObject()

for arg, value in arguments:
    if arg in ("-c", "--config"):
        no.settings_change()
    elif arg in ("-h", "--help"):
        print ("\n   Список команд:\n"
               "   --help (-h)\t\tПомощь, вывод возможных команд\n"
               "   --url (-u)\t\tЗадает URL страницы, с которой необходимо брать данные\n"
               "   --config (-c)\tЗапускает утилиту настройки программы\n"
               "   --info (-i)\t\tПодробное описание программы")
    elif arg in ("-u", "--url"):
        no.shake_site(value)
    elif arg in ("-i", "--info"):
        # отображение файла с информацией
        pass




