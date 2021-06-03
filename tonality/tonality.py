from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel
import glob

tokenizer = RegexTokenizer()

model = FastTextSocialNetworkModel(tokenizer=tokenizer)
messages = []
all_text_files = glob.glob('/home/vagrant/Coursework/samples/*.txt')
for text_file in all_text_files:
  data = open(text_file, 'r') 
  #print(data.read())
  data1 = data.read()
  print(data1)
  messages.append(data1)
print(messages)
results = model.predict(messages, k=2)

for message, sentiment in zip(messages, results):
    print(message, '->', sentiment)