# -*- coding: utf-8 -*-
"""DataExtractionAndTextAnalysis.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/13pF8-cnIOecHxLVXR6nTCHNItzH9eBFM
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from textstat.textstat import textstatistics

pip install textstat

df=pd.read_excel('/content/drive/MyDrive/Blackcoffer/Input.xlsx')[['URL_ID','URL']]
df=df.iloc[0:114]
df

contents=[]
for url in df['URL']:
    headers={'User-Agent': 'Chrome/74.0.3729.169'}
    #The User-Agent request header lets servers and network peers identify the application, operating system, vendor, and/or version of the requesting user agent.
    try:
        page=requests.get(url, headers=headers) #loading text
        print(page)
        soup=BeautifulSoup(page.content,'html.parser') #parsing text 
        title=soup.findAll('h1') #extracting title of website
        title=title[0].text
        body=soup.findAll(attrs={'class':'td-post-content'}) #extracting required content
        body=body[0].text.replace('\xa0',"  ").replace('\n',"  ") #extract text from p tags and replace end line symbols with space
        text=title+ '. '+body #merging title and content
        contents.append(text)
    except:
        contents.append(None)
        continue

df1 = pd.merge(df, pd.DataFrame(contents), left_index = True, right_index = True, how = "left")

df1.columns = ['URL_ID', 'URL', 'Text_Contents']
df1

df1.to_excel('collected_data.xlsx')

df=pd.read_excel("/content/drive/MyDrive/Blackcoffer/Output Data Structure.xlsx")
df.info()

df

#import all Stopwords
stop_words = []

StopWords_Auditor = '/content/drive/MyDrive/Blackcoffer/Stopwords/Copy of StopWords_Auditor.txt'
for stop_word in open(StopWords_Auditor, 'r').readlines():
    stop_words.append(stop_word.rstrip().upper())

StopWords_Currencies = '/content/drive/MyDrive/Blackcoffer/Stopwords/stopwords_currencies.txt'
for stop_word in open(StopWords_Currencies, 'r').readlines():
    stop_words.append(stop_word.rstrip().upper())

StopWords_Generic = '/content/drive/MyDrive/Blackcoffer/Stopwords/Copy of StopWords_Generic.txt'
for stop_word in open(StopWords_Generic, 'r').readlines():
    stop_words.append(stop_word.rstrip().upper())

StopWords_GenericLong = '/content/drive/MyDrive/Blackcoffer/Stopwords/Copy of StopWords_GenericLong.txt'
for stop_word in open(StopWords_GenericLong, 'r').readlines():
    stop_words.append(stop_word.rstrip().upper())

StopWords_DatesandNumbers= '/content/drive/MyDrive/Blackcoffer/Stopwords/Copy of StopWords_DatesandNumbers.txt'
for stop_word in open(StopWords_DatesandNumbers, 'r').readlines():
    stop_words.append(stop_word.rstrip().upper())

StopWords_Geographic= '/content/drive/MyDrive/Blackcoffer/Stopwords/Copy of StopWords_Geographic.txt'
for stop_word in open(StopWords_Geographic, 'r').readlines():
    stop_words.append(stop_word.rstrip().upper())
    
StopWords_Names= '/content/drive/MyDrive/Blackcoffer/Stopwords/Copy of StopWords_Names.txt'
for stop_word in open(StopWords_Names, 'r').readlines():
    stop_words.append(stop_word.rstrip().upper())

import nltk
nltk.download('punkt')

# Function to remove stopwords and tokenize the text data
def text_prep(x: str) -> list:
     operation = str(x).upper()
     operation= re.sub('[^a-zA-Z]+',' ', operation).strip() 
     tokens = word_tokenize(operation)
     words = [t for t in tokens if t not in stop_words]
     return words
# Applying the function on the data
tokenized_text = [text_prep(i) for i in df1['Text_Contents']]
df["tokenized_text"] = tokenized_text

df['num_words'] = df['tokenized_text'].map(lambda x: len(x))

#importing master Dictionary
positive_dict=[]
positive= '/content/drive/MyDrive/Blackcoffer/Master_Dictonary/Copy of positive-words.txt'
for word in open(positive, 'r').readlines():
    positive_dict.append(word.rstrip().upper())

negative_dict=[]
negative= '/content/drive/MyDrive/Blackcoffer/Master_Dictonary/Copy of negative-words.txt'
for word in open(negative, 'r').readlines():
    negative_dict.append(word.rstrip().upper())

positive_master=[words for words in positive_dict if words not in stop_words]
negative_master=[words for words in negative_dict if words not in stop_words]

#Positive Score
num_pos = df["tokenized_text"].map(lambda x: len([i for i in x if i in positive_master]))
df["positive_score"] = num_pos

#Negative Score
num_neg = df["tokenized_text"].map(lambda x: len([i for i in x if i in negative_master]))
df["negative_score"] = num_neg

#Polarity Score
df['polarity_score'] = round((df['positive_score'] - df['negative_score'])/(df['positive_score'] + df['negative_score'] + 0.000001), 2)

#Subjectivity Score
df['subjectivity_score'] = round((df['positive_score'] + df['negative_score'])/(df['num_words'] + 0.000001), 2)

#Average Sentence Length
df['num_sent'] = df1['Text_Contents'].map(lambda x: len(sent_tokenize(x)), na_action='ignore')
df['avg_sent_len'] = round(df['num_words']/df['num_sent'], 1)

def syllables_count(text):
  return textstatistics().syllable_count(text)
  
def complex_words(text):
  words_set = set()
  words = text
  for word in words:
    syllable_count = syllables_count(word)
    if syllable_count > 2:
      words_set.add(word)
  return len(words_set)

df['complex_words'] = df['tokenized_text'].apply(lambda x: complex_words(x))
df['complex_words_percent'] = round((df['complex_words']/df['num_words']), 2)

df['Fog_index'] = 0.4 * (df['avg_sent_len'] + df['complex_words_percent'])

df['avg_words_per_sent'] = round(df['num_words']/df['num_sent'], 2)

df['syll_count'] = df['tokenized_text'].apply(lambda x: syllables_count(" ".join(x)))
df['syll_per_word'] = df['syll_count']/df['num_words']

def psnl_pronoun(text):
  pronounRe = re.compile(r'\b(I|we|my|ours|(?-i:us))\b',re.I)
  allpronouns = pronounRe.findall(text)
  return allpronouns

df['psnl_pronouns'] = df1['Text_Contents'].map(lambda x: len(psnl_pronoun(x)), na_action='ignore')

def text_len(text):
  text = ''.join(text)
  filtered= re.sub('[^a-zA-Z]+',' ', text)
  words = [word for word in filtered.split() if word]
  avglen = sum(map(len, words))/len(words)
  return avglen

df['avg_word_len'] = df1['Text_Contents'].map(lambda x: text_len(x), na_action='ignore')

df.columns

df=df[['URL_ID', 'URL','positive_score', 'negative_score',
       'polarity_score', 'subjectivity_score', 'avg_sent_len',
       'complex_words', 'complex_words_percent', 'Fog_index',
       'avg_words_per_sent', 'syll_count', 'syll_per_word', 'psnl_pronouns',
       'avg_word_len']]

df.columns=['URL_ID', 'URL', 'POSITIVE SCORE', 'NEGATIVE SCORE', 'POLARITY SCORE', 'SUBJECTIVITY SCORE', 'AVG SENTENCE LENGTH', 'PERCENTAGE OF COMPLEX WORDS', 'FOG INDEX', 'AVG NUMBER OF WORDS PER SENTENCE', 'COMPLEX WORD COUNT', 'WORD COUNT', 'SYLLABLE PER WORD', 'PERSONAL PRONOUNS', 'AVG WORD LENGTH']
df.head()

df.to_csv('Output.csv', index = False)

data = pd.read_csv('Output.csv')
data