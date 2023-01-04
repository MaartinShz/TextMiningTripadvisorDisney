# -*- coding: utf-8 -*-
"""
Created on Wed Dec 21 16:12:19 2022

@author: Christelle
"""

import streamlit as st
import pandas as pd
import altair as alt
from urllib.error import URLError
import pandas as pd
import numpy as np
import cx_Oracle
import re
from my_functions import my_corpora_2_vec
from my_functions import nettoyage_corpus
from my_functions import my_cah_from_doc2vec
#nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from gensim.models import Word2Vec
from scipy.cluster.hierarchy import dendrogram, linkage,fcluster
from sklearn.feature_extraction.text import CountVectorizer
import matplotlib.pyplot as plt
from wordcloud import WordCloud

st.set_page_config(page_title="Analyse ", page_icon="📊")
st.markdown("# Analyse")
st.sidebar.header("Analyse")
st.write(
    """The aim here is to highlight the data from the parks  """
)



try:
    cx_Oracle.init_oracle_client(lib_dir="C:/Users/USER/Documents/Master_SISE/Projet/Text_mining/instantclient_21_8")
except cx_Oracle.ProgrammingError as e:
    # Client library is already initialized, do nothing
    pass

dsnStr = cx_Oracle.makedsn("db-etu.univ-lyon2.fr", "1521", "DBETU")
con = cx_Oracle.connect(user="m134", password="m134", dsn=dsnStr)



#Importer la table 'commentaire_parc':
query_commentaire_parc = """SELECT* 
           FROM COMMENTAIRE_PARC
           """
commentaire_parc = pd.read_sql(query_commentaire_parc, con=con)
st.write(commentaire_parc)


# In[34]:


commentaire_parc["COMMENTAIRE"] = commentaire_parc["COMMENTAIRE"].astype(str)


# In[35]:


#Chargez dans une liste les commentaires pour chaque item
corpus_original_parc = []
for i in commentaire_parc["COMMENTAIRE"].values:
    corpus_original_parc.append(i)
corpus_original_parc


# In[36]:


#corpus après pré-traitement, sous forme de listes de liste de tokens
corpus_liste_parc = nettoyage_corpus(corpus_original_parc)
corpus_liste_parc


# In[37]:


#construire la représentation à 1000 dim.

modele_parc = Word2Vec(corpus_liste_parc,vector_size=1000,window=3,min_count=2,epochs=100)
words_parc = modele_parc.wv


# CAH

# In[18]:


#A partir de la matrice de description des documents, réaliser une CAH (critère de Ward) 
#et afficher le dendrogramme


g1,mat1 = my_cah_from_doc2vec(corpus_liste_parc,words_parc,seuil=100)


# Word Cloud

# In[38]:


comment_words_parc = ''

# pour chaque mot dans commentaire["COMMENTAIRE"]:
for val in commentaire_parc["COMMENTAIRE"].values:
     
    # convertir en string
    val = str(val)
 
    # split
    tokens = val.split()
     
    # convertir en lowercase
    for i in range(len(tokens)):
        tokens[i] = tokens[i].lower()
     
    comment_words_parc += " ".join(tokens)+" "


# In[39]:


    #liste des mots vides

    mots_vides = stopwords.words("french")

    # on ajoute qlq mots vides:
    liste_mots_vides = ["disneyland","disney land","disney","parc","parcs","très","trop","séjour","hôtel","hotel",
                       "lhotel","lhôtel","l'hôtel","chambre","chambres","c'est","cest","c'était","ça","cela",
                       "avant","après","n'est","n'était","déjà","donc","alors","a","cet","j'ai","si"]

    for i in liste_mots_vides:
        mots_vides.append(i)
        
wordcloud_parc = WordCloud(width = 800, height = 800,
                background_color ='white',
                      stopwords = mots_vides,
                min_font_size = 10).generate(comment_words_parc)


# In[40]:


# plot WordCloud                     
plt.figure(figsize = (8, 8), facecolor = None)
plt.imshow(wordcloud_parc)
plt.axis("off")
plt.tight_layout(pad = 0)
 
plt.show()




con.close()



