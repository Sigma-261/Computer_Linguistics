from tkinter import *
import tkinter as tk
from tkinter import ttk
from pymongo import MongoClient
from progress.bar import IncrementalBar
from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel
from bs4 import BeautifulSoup
from tqdm import tqdm
import requests
import time
import threading
import csv
import os
import sys

client = MongoClient('localhost',27017)
db = client['VpravdaDB']
collection = db['Vpravda']
collection_sentence = db['VpravdaSentence']
collection_objects = db['Objects']

def show_frame(frame):
    frame.tkraise()

#Главное окно
win = tk.Tk()
win.attributes('-fullscreen', True)

#Левая и правая часть экрана
frame_left = LabelFrame(win, text="СТРАНИЦЫ")
frame_right = tk.Frame(win)

#Окна
frame_right_func = tk.Frame(frame_right)
frame_right_bd = tk.Frame(frame_right)
frame_right_syn = tk.Frame(frame_right)
frame_right_ton = tk.Frame(frame_right)


wrapper_bd = LabelFrame(frame_right_bd, text="БАЗА ДАННЫХ")
wrapper_elem_bd = LabelFrame(frame_right_bd, text="ВЫБРАННЫЙ ЭЛЕМЕНТ")

wrapper_func = LabelFrame(frame_right_func, text="ФУНКЦИИ")
wrapper_sent = LabelFrame(frame_right_func, text="ПРЕДЛОЖЕНИЯ")

frame_left.pack(fill="both",side = LEFT, padx=20, pady=10)
frame_right.pack(fill="both", expand="yes", padx=20, pady=10)
wrapper_bd.pack(fill="both")
wrapper_elem_bd.pack(fill="both")
wrapper_func.pack(fill="both", padx=20, pady=10)
wrapper_sent.pack(fill="both", padx=20, pady=10)

my_list_sen = Listbox(wrapper_sent, height=25)
my_list_sen.pack(fill="both", expand="yes", padx=20, pady=10)



my_list_per = Listbox(frame_right_syn)
my_list_per.pack(fill="both",side = LEFT, padx=20, pady=10)

my_list_syn = Listbox(frame_right_syn)
my_list_syn.pack(fill="both", expand="yes")

for frame in (frame_right_func, frame_right_bd, frame_right_syn, frame_right_ton):
  frame.grid(row=0,column=0,sticky='nsew')
  


def parser_site():
  n = entry_time.get()
  m = n*60*60
  os.system("python3 /home/vagrant/tomita-parser/build/bin/parser_site.py")
  threading.Timer(int(m), parser_site).start()
  
def big_parser_site():
  os.system("python3 /home/vagrant/tomita-parser/build/bin/big_parser_site.py")
  
def tomita():
  os.system("python3 /home/vagrant/tomita-parser/build/bin/write_tomita.py")
  
def model_w2v():
  os.system("spark-submit /home/vagrant/tomita-parser/build/bin/word2vec.py")

def natasha():
  a = my_list_per.get(ANCHOR)
  element={"name_object" : a}
  n = collection_objects.find_one(element)
  element = n["num_object"]
  os.system("spark-submit /home/vagrant/tomita-parser/build/bin/search_natasha.py"+ " " +str(element))
  
  my_list_syn.delete(0,'end')
  f = open('/home/vagrant/tomita-parser/build/bin/syn1.txt')
  for line in f:
    line = line.replace('\n', '')
    my_list_syn.insert(END,line)
  f.close()
  
def w2v():
  a = my_list_per.get(ANCHOR)
  element={"name_object" : a}
  n = collection_objects.find_one(element)
  element = n["num_object"]
  os.system("spark-submit /home/vagrant/tomita-parser/build/bin/w2v_syn.py"+ " " +str(element))

  my_list_syn.delete(0,'end')
  f = open('/home/vagrant/tomita-parser/build/bin/syn.txt')
  for line in f:
    line = line.replace('\n', '')
    my_list_syn.insert(END,line)
  f.close()


entry_time = Entry(wrapper_func)
entry_time.pack(fill='x', ipady=5)

parser_btn = tk.Button(wrapper_func, text='ПАРСЕР САЙТА',command=parser_site)
parser_btn.pack(fill='x', ipady=5)

big_parser_btn = tk.Button(wrapper_func, text='БОЛЬШОЙ ПАРСЕР САЙТА',command=big_parser_site)
big_parser_btn.pack(fill='x', ipady=5)

tomita_btn = tk.Button(wrapper_func, text='ТОМИТА',command=tomita)
tomita_btn.pack(fill='x', ipady=5)

w2v_btn = tk.Button(wrapper_func, text='ОБУЧИТЬ МОДЕЛЬ',command=model_w2v)
w2v_btn.pack(fill='x', ipady=5)

w2v_btn = tk.Button(frame_right_syn, text='ПОКАЗАТЬ СИНОНИМЫ',command=w2v)
w2v_btn.pack(fill='x', ipady=15)

natasha_btn = tk.Button(frame_right_syn, text='ПОКАЗАТЬ СЛОВА',command=natasha)
natasha_btn.pack(fill='x', ipady=15)

frame_func_btn = tk.Button(frame_left, text='ФУНКЦИИ',command=lambda:show_frame(frame_right_func))
frame_func_btn.pack(fill='x', ipady=15)

#==================Frame 2 code

frame_bd_btn = tk.Button(frame_left, text='БАЗА ДАННЫХ',command=lambda:show_frame(frame_right_bd))
frame_bd_btn.pack(fill='x', ipady=15)

#==================Frame 3 code

frame_syn_btn = tk.Button(frame_left, text='СИНОНИМЫ',command=lambda:show_frame(frame_right_syn))
frame_syn_btn.pack(fill='x',ipady=15)

#==================Frame 4 code

frame_ton_btn = tk.Button(frame_left, text='ТОНАЛЬНОСТЬ',command=lambda:show_frame(frame_right_ton))
frame_ton_btn.pack(fill='x',ipady=15)

my_tree_bd = ttk.Treeview(wrapper_bd, height="16")
my_tree_bd.pack(expand="yes")

my_tree_ton = ttk.Treeview(frame_right_ton, height="30")
my_tree_ton.pack(fill="both", expand="yes")

my_tree_bd['columns'] = ("ID", "NAME", "DATE", "LINK","TEXT_NEWS", "LINK_VIDEO")
my_tree_ton['columns'] = ("Sentence", "Tonality")
  
my_tree_bd.column("#0", width=0, stretch=NO)  
my_tree_bd.column("ID", anchor=CENTER, width=180)  
my_tree_bd.column("NAME", anchor=W , width=300)  
my_tree_bd.column("DATE", anchor=W, width=140)  
my_tree_bd.column("LINK", anchor=W, width=200)  
my_tree_bd.column("TEXT_NEWS", anchor=W, width=250) 
my_tree_bd.column("LINK_VIDEO",anchor=W, width=200)

my_tree_bd.heading("#0", text="", anchor=CENTER) 
my_tree_bd.heading("ID", text="ID",anchor=CENTER)  
my_tree_bd.heading("NAME", text="NAME",anchor=CENTER)  
my_tree_bd.heading("DATE", text="DATE",anchor=CENTER)  
my_tree_bd.heading("LINK", text="LINK",anchor=CENTER) 
my_tree_bd.heading("TEXT_NEWS", text="TEXT_NEWS",anchor=CENTER)  
my_tree_bd.heading("LINK_VIDEO", text="LINK_VIDEO", anchor=CENTER) 

my_tree_ton.column("#0", width=0, stretch=NO)  
my_tree_ton.column("Sentence", anchor=W, width=850)  
my_tree_ton.column("Tonality", anchor=CENTER , width=460)  

my_tree_ton.heading("#0", text="", anchor=W) 
my_tree_ton.heading("Sentence", text="Sentence",anchor=CENTER)  
my_tree_ton.heading("Tonality", text="Tonality",anchor=CENTER)  

def record():
  my_tree_bd.delete(*my_tree_bd.get_children())
  cursor = collection.find({})
  count=0
  for document in cursor:
    my_tree_bd.insert(parent='', index='end', iid=count, text="",values=(document["_id"],document["name_news"],document["date_news"],document["link_news"],document["text_news"], document["link_video"]))
    count+=1

def update_list_sen():
  my_list_sen.delete(0,'end')
  cursor = collection_sentence.find({})
  count=1
  for document in cursor:
    my_list_sen.insert(END,str(count)+") "+ document["sentence"])
    count+=1

update_sen_btn = Button(wrapper_sent, text='ОБНОВИТЬ',command=update_list_sen)
update_sen_btn.pack(fill='x', expand="yes")

f = open('/home/vagrant/tomita-parser/build/bin/list_w2v.txt')
for line in f:
  line = line.replace('\n', '')
  my_list_per.insert(END,line)
f.close()
 
def update_tony():
  tokenizer = RegexTokenizer()

  model = FastTextSocialNetworkModel(tokenizer=tokenizer)
  messages = []

  cursor1 = collection_sentence.find({})
  for document in cursor1:
    messages.append(document["sentence"])
  results = model.predict(messages, k=2)
  for message, sentiment in zip(messages, results):
    my_tree_ton.insert(parent='', index='end', text="",values=(message, sentiment))

btn2 = Button(frame_right_ton, text='ОБНОВИТЬ',command=update_tony)
btn2.pack(fill="both", expand="yes")

btn1 = Button(wrapper_bd, text='ОБНОВИТЬ',command=record)
btn1.pack(fill='x')

def select_record():
  id_box.delete(0, END)
  name_box.delete(0, END)
  date_box.delete(0, END)
  link_box.delete(0, END)
  text_box.delete('1.0', END)
  video_box.delete(0, END)
  selected = my_tree_bd.focus()
  
  values = my_tree_bd.item(selected, 'values')
  
  id_box.insert(0, values[0])
  name_box.insert(1, values[1])
  date_box.insert(2, values[2])
  link_box.insert(3, values[3])
  text_box.insert('4.0', values[4])
  video_box.insert(5, values[5])

def clicker(e):
  select_record()

il = Label(wrapper_elem_bd, text = "ID")
il.grid(row=0, column=0)

nl = Label(wrapper_elem_bd, text = 'NAME')
nl.grid(row=1,column=0)

dl = Label(wrapper_elem_bd, text = 'DATE')
dl.grid(row=2,column=0)

ll = Label(wrapper_elem_bd, text = 'LINK')
ll.grid(row=3,column=0)

tl = Label(wrapper_elem_bd, text = 'LINK_VIDEO')
tl.grid(row=4,column=0)

vl = Label(wrapper_elem_bd, text = 'TEXT_NEWS')
vl.grid(row=5,column=0)

id_box=Entry(wrapper_elem_bd, width=150)
id_box.grid(row=0,column=1,columnspan=5)

name_box=Entry(wrapper_elem_bd, width=150)
name_box.grid(row=1,column=1,columnspan=5)

date_box=Entry(wrapper_elem_bd, width=150)
date_box.grid(row=2,column=1,columnspan=5)

link_box=Entry(wrapper_elem_bd, width=150)
link_box.grid(row=3,column=1,columnspan=5)

video_box=Entry(wrapper_elem_bd, width=150)
video_box.grid(row=4,column=1,columnspan=5)

text_box=Text(wrapper_elem_bd, width=150, height=14, fg='black', wrap=WORD)
text_box.grid(row=5,column=1,columnspan=5)

my_tree_bd.bind("<Double-1>", clicker)

show_frame(frame_right_func)



win.mainloop()