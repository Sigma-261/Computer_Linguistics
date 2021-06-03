from razdel import sentenize
import re
import os
import glob
import nltk
from nltk.stem import WordNetLemmatizer 
import pymorphy2
from pymongo import MongoClient
morph = pymorphy2.MorphAnalyzer()

def tomita_text_news(PATH, collection):

  #запись всех документов
  cursor = collection.find({})
  num_sent = 0
  for document in cursor:
  
    #создание одного файла по пути
    name = PATH + "sentences_news_" + str(num_sent)
    
    #открываем файл
    sentence_file_w = open(name + ".txt", "w")
    sentence_file_w.seek(0)
    
    #запись в файл текст новости по предложениям из документа
    for it in list(sentenize(document["text_news"])):
      sentence_file_w.write(it.text +'\n')
      
    #закрываем файл
    sentence_file_w.close()
    text_news=[]
    temp_text_news=[]
    
    #чтение из файла текста новости
    sentence_file_r = open(name + ".txt", "r")
    for line in sentence_file_r:
      text_news.append(line.replace('\n', ''))
      
    #закрываем файл
    sentence_file_r.close()
    
    #записываем в файл томиты текст новости
    file_input = open('/home/vagrant/tomita-parser/build/bin/input.txt', 'w+')
    for line in text_news:
      file_input.write(line+'\n')
      
    #закрываем файл
    file_input.close()
    
    #запускаем томиту
    os.system("./tomita-parser config.proto")
    
    #запускаем скрипт для парсинга томиты
    os.system("python3 /home/vagrant/tomita-parser/build/bin/tomita_parser_dif.py")
    
    #чтение из временного файла с измененным текстом новости
    temp_file = open('/home/vagrant/tomita-parser/build/bin/temp_text_news.txt', 'r')
    for line in temp_file:
      temp_text_news.append(line.replace('\n', ''))
      
    #закрываем файл
    temp_file.close()
    
    #открываем файл и записываем измененый текст новости
    sentence_file = open(name + ".txt", "w+")
    for line in temp_text_news:
      sentence_file.write(line+' ')
      
    #закрываем файл
    sentence_file.close() 
    
    num_sent+=1

#главная функция
def main():
  open('/home/vagrant/tomita-parser/build/bin/change_sentences.txt', 'w').close()
  #подключение к монго
  client = MongoClient('localhost',27017)
  db = client['VpravdaDB']
  collection = db['Vpravda']
  collection_sentence = db['VpravdaSentence']
  
  #очищение коллекции с предложениями
  collection_sentence.delete_many({})
  
  #путь к папке с преложениями
  PATH = "/home/vagrant/tomita-parser/build/bin/packs_text_news/"
  
  #если папки не существует, то создает ее
  if not os.path.exists(PATH):
    os.makedirs(PATH)
    
  #чтение всех файлов в папке
  files = glob.glob('/home/vagrant/tomita-parser/build/bin/packs_text_news/*.txt')
  
  #очищение папки
  for f in files:
    os.remove(f)
    
  #функция для томиты парсера
  tomita_text_news(PATH, collection)

#точка входа
if __name__ == '__main__':
  main()