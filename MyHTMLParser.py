# -*- coding: utf-8 -*-
import urllib.request
from html.parser import HTMLParser

# наследуем класс HTMLParser и перегружаем методы  
class WebPageParser(HTMLParser):

    def __init__(self, html_text):
        # вызываем метод инициализации родительского класса
        super().__init__()
        self.reset()
        self.html_text = html_text
        self.mdata = ""
        self.openedTag = 0
        self.tagInside = 0
        self.topicText = ""
        # позиции, с которых начинаются текстовые блоки
        self.text_block_pos = []
        # при инициализации "скармливаем" парсеру содержимое страницы
        self.feed(self.html_text)

    def handle_starttag(self, tag, attrs):
        # находим тэг соответствующий тексту статьи
        if tag == 'span' and not self.topicText:
            if attrs[0][0] == 'class' and attrs[0][1] == "topic-header__title":
                self.topicText = "need"
        # проверяем аттрибут текстового блока, принадлежность к соответствующему классу
        if tag == 'p':
            for attr in attrs:
                if attr[0] == 'class' and attr[1] == 'topic-body__content-text':
                    # сообщаем о "находке" и отмечаем, что блок найден
                    print("Self data found: <", tag, attr[0], "=", attr[1], ">")
                    self.openedTag = 1
        # проверяем является ли тэг тэгом ссылки
        if tag == 'a':
            if attrs[0][0] == 'href':
                self.tagInside = 1
                print("-- Tag inside found: <", tag, attrs[0][0], "=", attrs[0][1], ">")

    def handle_data(self, data):
        if self.topicText == "need":
            self.topicText = data
            self.mdata = self.mdata + data + '\n'
        if self.openedTag == 1:
            self.mdata = self.mdata + '\n\n' + data
            self.openedTag = 0
        if self.tagInside == 1:    
            self.mdata = self.mdata + data
            self.tagInside = 0  

