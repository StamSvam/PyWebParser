# -*- coding: utf-8 -*-

from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests
import json
import os

# создаем класс для парсинга веб-страницы
class NewsObject(object):

    def __init__(self):
        self.url = ""
        # поле класса для хранения названия статьи
        self.title = ""
        # для хранения тела текста
        self.text = []
        # для хранения ссылок
        self.references = ['\n\tСсылки:\n']
        # для хранения настроек программы
        self.settings = {'string length': 80, 
                         'consider spaces': 1, 
                         'output file name' : 'index.txt'}
        
    def shake_site(self, _url):
        self.url = _url
        print('[ОК] Программа запущена')
        self._settings_load()
        self._get_text()
        print('[ОК] Данные получены')
        self._format_text()
        self._do_the_textfile()
        
    # реализуем открытый метод для получения кода страницы
    def create_raw_html(self, _url):
        resp = requests.get(_url)
        html_raw = BeautifulSoup(resp.text, 'lxml')
        return html_raw
        
    # получаем список с содержимым всех блоков 
    def _get_text(self):
        # находим все текстовые блоки (тэг < p >)
        html_raw = self.create_raw_html(self.url)
        """ проверяем на соответствие класса блока классу основного теста - 
             'topic-body__content-text', или заголовка статьи - 'topic-header__title'
             усложнено тем, что в конце названия класса генерируется случайная
             последовательность а ля 'topic-body__content-text hvio'
        """
        titles = html_raw.find_all('span')
        for title in titles:
            if title.has_attr('class') and ('topic-header__title' in title['class'][0]):
                self.title = title.getText()
                break
        text_blocks = html_raw.find_all('p')
        hrefs_counter = 0
        for block in text_blocks:
            if block.has_attr('class') and ('topic-body__content-text' in block['class'][0]):
                temp_text = block.getText()
                hrefs = block.find_all('a')
                # проверяем наличие ссылок внутри блока текса
                if len(hrefs):
                    """ для каждой ссылки весь текст блока делим по тексту ссылки на 2 части
                     для вставки ссылки непосредственно в текст - [https://...] - первая реализация
                     позднее было принято решениt для более удобного восприятия текста
                     вместо ссылок вставить сноски, а сами ссылки вынести в конец текста (как в документах)
                    """
                    for hr in hrefs:
                        hrefs_counter += 1
                        txt = temp_text.split(hr.getText())
                        temp_text = txt[0] + hr.getText() + " [" + str(hrefs_counter) + "]" + txt[1]
                        self.references.append(hr['href']+'\n')
                self.text.append(temp_text)

    # подготавливаем блоки текста к записи в файл по заданному формату
    # впоследствии имеет смысл усложнить форматирования для представления в формате .rtf, .doc
    def _format_text(self):
        # добавляем блокам текста элементов форммтирования
        for i in range(len(self.text)): 
            # разбиваем блок текста на слова для более удобного переноса
            block_words = self.text[i].split()
            # объявляем переменные для подсчета суммарной длины слов и строки максимальной длины
            sum_len = 0 
            final_str = ""
            # перебираем пословно и вычисляем длину каждого слова и их сумму
            # если превышает заданную - добавляем после предыдущего слова символ переноса
            for j in block_words:
                # при подсчете длины строки слова +1 - учитывается символ пробела
                # или +0 - не учитывается, в зависимости от настроек, не обязательная "фича"
                sum_len = sum_len + len(j) + self.settings['consider spaces']
                if sum_len > self.settings['string length']:
                    sum_len = len(j)
                    final_str = final_str + '\n' + j + ' '
                else:
                    final_str = final_str + j + ' '
            self.text[i] = '     ' + final_str + '\n' 
            #print(self.text[i])

    def _do_the_textfile(self):
        file_name = self.settings['output file name']
        # формируем новый путь (полный), основываясь на url статьи
        new_dir = os.getcwd() + '/' + urlparse(self.url).netloc + urlparse(self.url).path
        # проверяем наличие каталога и создаем новый
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        # в корневой директории исполняемого файла создаем файл и проводим необходимые манипуляции
        file = open(file_name, "w+")
        file.truncate(0)
        # наполнение файла содержимым из соответствующих полей класса
        file.write('\t' + self.title + '\n\n')
        for block in self.text:
            file.write(block + '\n')
        for j in range(self.settings['string length']):
            file.write('_')
        file.write(self.references[0])
        for i in range(1, len(self.references)):
            file.write('[' + str(i) + '] - ' + self.references[i])
        file.close()
        # переносим преобразованный файл в созданную директорию
        os.replace(file_name, new_dir + file_name)
        print('[ОК] Файл с данными находится по пути:' + new_dir + file_name)

    def _settings_load(self):
        file = open('settings.cfg', 'r')
        # если содержимое файла не соответствует десериализуемому словарю - игнорирует, наполняем чистый словарь
        try:
            my_dict = json.load(file)
        except Exception as e:
            print('[ERROR] Данные файла настроек повреждены! Генерируются значения по умолчанию.')
            return
        err_counter = 0
        for key, value in my_dict.items():
            if type(self.settings[key]) == type(value):
                self.settings[key] = value
            else:
                err_counter += 1
        if err_counter > 0:
            print('[WARNING] Данные файла настроек были изменены напрямую.')
            print('          Количество нарушений соответствия: ' + str(err_counter))
            print('          Взяты настройки по умолчанию. Рекомендую провести настройку программы командой [-c]')
        file.close()
    
    def settings_change(self):
        my_dict = {}
        file = open('settings.cfg', 'r')
        # если содержимое файла не соответствует десериализуемому словарю - игнорирует, наполняем чистый словарь
        try:
            my_dict = json.load(file)
            print('\n      Текущие настройки программы:')
            print(' - Максимальная длина строки в тексте:' +' \t\t' + str(my_dict['string length']))
            print(' - Учитываются пробелы при подсчете длины:' +'\t' + ('да' if my_dict['consider spaces']==0 else 'нет'))
            print(' - Имя файла для сохранения:' + '\t\t\t' + my_dict['output file name'])
        except Exception as e:
            print('[ERROR] Данные файла настроек повреждены! После ввода настроек ошибка будет устранена.')
            print('[FIXED] Продолжим.')
        inp = input('\nЖелаете внести изменения? (yes/no) yes: ')
        if not inp or inp == 'yes':
            print('[OK]')
        else:
            print('[SYSTEM] Exit')
            file.close()
            return
        file.close()
        print('\nНастройка параметров программы. Если вы хотите оставить значение по умолчанию - нажмите Enter, не внося изменения\n')
        # вводим длину строки текста
        inp = input('1. Введите максимальную длину строки в тексте (по умолчанию - 80): ')
        if not inp:
            print('[OK] Установлено значение по умолчанию.')
            my_dict['string length'] = 80
        else:
            try:
                res = int(inp)
                print('[OK]')
            except Exception:
                res = 80
                print('[WARNING] Введены неверные данные, установлено значение по умолчанию!')
            my_dict['string length'] = res
        # определяем, учитываются ли пробелы в тексте при подсчете длины
        inp = input('\n2. При подсчете длины строки учитывать пробелы? (yes/no) (по умолчанию - yes): ')
        if not inp:
            print('[OK] Установлено значение по умолчанию.')
            my_dict['consider spaces'] = 1
        else:
            if inp == 'yes':
                my_dict['consider spaces'] = 1
                print('[OK]')
            elif inp == 'no':
                my_dict['consider spaces'] = 0
                print('[OK]')
            else:
                print('[WARNING] Введены неверные данные, установлено значение по умолчанию!')
                my_dict['consider spaces'] = 1
        # вводим имя выходного файла
        inp = input('\n3. Введите имя файла для сохранения данных: (по умолчанию - index.txt): ')
        if not inp:
            print('[OK] Установлено значение по умолчанию.')
            my_dict['output file name'] = 'index.txt'
        else:
            my_dict['output file name'] = inp
            print('[OK]')
            # ниже планируется обработка имени файла и отбрасывание недопустимых в текущей ОС
        file = open('settings.cfg', 'w')
        json.dump(my_dict, file)
        file.close()
        print('\n[OK] Изменения сохранены')

        
