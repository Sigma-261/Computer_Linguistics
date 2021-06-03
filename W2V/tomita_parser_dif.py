from pymongo import MongoClient
from bs4 import BeautifulSoup
from itertools import groupby
import os
import sys
import pymorphy2
morph = pymorphy2.MorphAnalyzer()

def replace_sen(sentence):
  objects =[]
  
  #чтение файла с объектами
  f = open('/home/vagrant/tomita-parser/build/bin/objects_lemm.txt', 'r')
  
  #запись в лист объектов
  for line in f:
    objects.append(line.replace('\n',''))
  f.close()
  
  #счетчик объектов
  i = 1
  for object in objects:
    n = sentence.find(str(object))
    if(n>0):
      #num_obj = open('/home/vagrant/tomita-parser/build/bin/num_objects.txt', 'a')
      d = "объект" + str(i)
      sentence = sentence.replace(object, d)
      #num_obj.write(d+'\n')
      #num_obj.close()
    i+=1
  return sentence

def mending_pretty():
  with open('/home/vagrant/tomita-parser/build/bin/pretty.html', 'r') as f:
    req_list =[]
    for eachLine in f:                                                                 
      req_list.append(eachLine)
    text_pretty = '\n'.join(req_list).replace('</html>','')
    text_pretty = text_pretty+'</html>'
  f = open('/home/vagrant/tomita-parser/build/bin/pretty.html', 'w+')
  f.seek(0)
  f.write(text_pretty)
  f.close()
  
def parsing_pretty(collection_sentence):
  #чтение файла pretty.html
  with open("/home/vagrant/tomita-parser/build/bin/pretty.html", "r") as f:
    contents = f.read()
    soup = BeautifulSoup(contents, 'lxml')
    
    #Парсинг таблицы с номерами
    trs = soup.find('table').find('tbody').find_all('tr')
    numbers = []
    for tr in trs:
      a = tr.find('a')
      if(a):
        a_link = a.get('href')
        a_link =a_link.replace('#','')
        numbers.append(a_link)
        
    #очистка дубликатов
    new_numbers = [el for el, _ in groupby(numbers)]
    
    #Парсинг номера предложения
    as_ = soup.find('body').find_all('a')
    numbers_sentence = []
    #открытие временного файла для записи изменненого текста новости 
    temp_file = open('/home/vagrant/tomita-parser/build/bin/temp_text_news.txt', 'w+')
    for a in as_:
      a_name = a.get('name')
      #если a имеет параметр "name"
      if(a_name):
        i = False
        for number in new_numbers:
          #если имя предложения равно номеру из таблицы
          if(a_name == number):
            i = True
            numbers_sentence.append(a_name)
            spans = a.find_all('span')
            word =[]
            for span in spans:
              span_text = span.get_text()
              word.append(span_text)
            sentence = ' '.join(word)
            
            #запись предложения с упоминанием в коллекцию с предложениями
            data = {'sentence':sentence}    
            write_mongo(collection_sentence, data)  
            
            #функция леммитизации
            def lemmatize(sentence):
              words = sentence.split()
              res = list()
              for word in words:
                p = morph.parse(word)[0]
                res.append(p.normal_form)
              return res
            change_sen_file = open('/home/vagrant/tomita-parser/build/bin/change_sentences.txt', 'a')
            #изменение предложений
            sentence_change = ' '.join(lemmatize(sentence))
            sentence = replace_sen(sentence_change)
            
            #записываем предложения в файлы
            change_sen_file.write(sentence+'\n')
            temp_file.write(sentence)
            
            change_sen_file.close()
        #если a имеет параметр "name" и не имеет персон
        if(i == False):  
          spans = a.find_all('span')
          word =[]
          for span in spans:
            span_text = span.get_text()
            word.append(span_text)
          sentence = ' '.join(word)
          
          #записываем предложения в файл
          temp_file.write(sentence)
          
    #закрываем временный файд
    temp_file.close()
    
  #закрываем файл pretty.html
  f.close()

#функция записи в бд
def write_mongo(collect, data):
  return collect.insert_one(data).inserted_id

#главная функция
def main():

  #подключение к монго
  client = MongoClient('localhost',27017)
  db = client['VpravdaDB']
  collection = db['Vpravda']
  collection_sentence = db['VpravdaSentence']
  #изменение файла pretty.html
  mending_pretty()
  #парсинг файла pretty.html
  parsing_pretty(collection_sentence)

#точка входа
if __name__ == '__main__':
  main()