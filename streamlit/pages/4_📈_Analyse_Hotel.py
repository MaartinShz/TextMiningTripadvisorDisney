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
from unidecode import unidecode
import string
#nltk.download('wordnet')
from my_functions import my_corpora_2_vec
from my_functions import nettoyage_corpus
from my_functions import my_cah_from_doc2vec
from my_functions import matrice_lien
from my_functions import my_dendogram
from connexion_Oracle import connect_to_database
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
    """The aim here is to highlight the hotel data """
)


### Connexion à Oracle
con = connect_to_database()
# # Analyse des commentaires pour les hôtels

# In[13]:


#Importer la table 'commentaire_hotel':
query_commentaire_hotel = """SELECT* 
           FROM COMMENTAIRE_HOTEL
           """
commentaire_hotel = pd.read_sql(query_commentaire_hotel, con=con)
st.write(commentaire_hotel)
#st.button("Re-run")

# In[14]:


#Chargez dans une liste des commentaires pour chaque item
corpus_original_hotel = []
for i in commentaire_hotel["COMMENTAIRE"].values:
    corpus_original_hotel.append(i)
#corpus_original_hotel


# In[15]:


#corpus après pré-traitement, sous forme de listes de liste de tokens
corpus_liste_hotel = nettoyage_corpus(corpus_original_hotel)
#corpus_liste_hotel


# In[16]:


#construire la représentation à 1000 dim.

modele_hotel = Word2Vec(corpus_liste_hotel,vector_size=1000,window=3,min_count=2,epochs=100)
words_hotel = modele_hotel.wv

#la matrice des liens
Z_hotel = matrice_lien(corpus_liste_hotel,words_hotel)
#st.button("Re-run")

# In[39]:

st.markdown("## le dendrogramme")
#afficher le dendrogramme
my_dendogram(Z_hotel)
#st.button("Re-run")

# In[78]:

st.markdown("## CAH (critère de Ward) ")

#CAH (critère de Ward) 

cah_hotel = my_cah_from_doc2vec(corpus_liste_hotel,Z_hotel)
st.write(cah_hotel )
#st.button("Re-run")


# Word Cloud

# In[30]:


comment_words_hotel = ''

# pour chaque mot dans commentaire_hotel["COMMENTAIRE"]:
for val in commentaire_hotel["COMMENTAIRE"].values:
     
    # convertir en string
    val = str(val)
 
    # split
    tokens = val.split()
     
    # convertir en lowercase
    for i in range(len(tokens)):
        tokens[i] = tokens[i].lower()
     
    comment_words_hotel += " ".join(tokens)+" "


# In[31]:

    #liste des mots vides

    mots_vides = stopwords.words("french")

    # on ajoute qlq mots vides:
    liste_mots_vides = ["disneyland","disney land","disney","parc","parcs","très","trop","séjour","hôtel","hotel",
                       "lhotel","lhôtel","l'hôtel","chambre","chambres","c'est","cest","c'était","ça","cela",
                       "avant","après","n'est","n'était","déjà","donc","alors","a","cet","j'ai","si"]

    for i in liste_mots_vides:
        mots_vides.append(i)

wordcloud_hotel = WordCloud(width = 800, height = 800,
                background_color ='white',
                      stopwords = mots_vides,
                min_font_size = 10).generate(comment_words_hotel)


# In[32]:

st.write("### The WordCloud ")
# Generate the WordCloud
plt.figure(figsize = (8, 8), facecolor = None)
plt.imshow(wordcloud_hotel)
plt.axis("off")
plt.tight_layout(pad = 0)
st.set_option('deprecation.showPyplotGlobalUse', False)
st.pyplot()

st.button("Re-run")
# Display the plot
con.close()



