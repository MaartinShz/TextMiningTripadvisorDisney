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
from connexion_Oracle import connect_to_database
from my_functions import matrice_lien
from my_functions import my_dendogram
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



### Connexion à Oracle
con = connect_to_database()


#Importer la table 'commentaire_parc':
query_commentaire_parc = """SELECT* 
           FROM COMMENTAIRE_PARC
           """
commentaire_parc = pd.read_sql(query_commentaire_parc, con=con)



# In[34]:


commentaire_parc["COMMENTAIRE"] = commentaire_parc["COMMENTAIRE"].astype(str)

st.write(commentaire_parc)
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

# In[87]:


#la matrice des liens
Z_parc = matrice_lien(corpus_liste_parc,words_parc)


# In[88]:


#afficher le dendrogramme
my_dendogram(Z_parc)


# In[ ]:


#CAH (critère de Ward) 

st.markdown("## CAH (critère de Ward) ")
cah_parc = my_cah_from_doc2vec(corpus_liste_parc,Z_parc)

st.write(cah_parc )
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



