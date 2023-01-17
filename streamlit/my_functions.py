# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 15:16:57 2023

@author: USER
"""
import pandas as pd
import streamlit as st
import altair as alt
from urllib.error import URLError
import pandas as pd
import numpy as np
from wordcloud import WordCloud
import re
from unidecode import unidecode
import string
import matplotlib.pyplot as plt
#nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from gensim.models import Word2Vec
from scipy.cluster.hierarchy import dendrogram, linkage,fcluster
from sklearn.feature_extraction.text import CountVectorizer
#récupérer la liste des ponctuations

ponctuations = list(string.punctuation)
#print(ponctuations)


# In[5]:


#liste des chiffres
chiffres = list("0123456789")
#print(chiffres)


# In[6]:


#outil pour procéder à la lemmatisation:

lem = WordNetLemmatizer()


# In[29]:



#liste des mots vides

mots_vides = stopwords.words("french")

# on ajoute qlq mots vides:
liste_mots_vides = ["disneyland","disney land","disney","parc","parcs","très","trop","séjour","hôtel","hotel",
                   "lhotel","lhôtel","l'hôtel","chambre","chambres","c'est","cest","c'était","ça","cela",
                   "avant","après","n'est","n'était","déjà","donc","alors","a","cet","j'ai","si","tres"]

for i in liste_mots_vides:
    mots_vides.append(i)
    
#print(mots_vides)

# In[8]:


#fonction pour nettoyage document (chaîne de caractères)
#le document revient sous la forme d'une liste de tokens
def nettoyage_doc(doc_param):
    #passage en minuscule
    doc = doc_param.lower()
    #retrait des ponctuations
    doc = "".join([w for w in list(doc) if not w in ponctuations])
    #retirer les chiffres
    doc = "".join([w for w in list(doc) if not w in chiffres])
    #transformer le document en liste de termes par tokénisation
    doc = word_tokenize(doc)
    #lematisation de chaque terme
    doc = [lem.lemmatize(terme) for terme in doc]
    #retirer les stopwords
    doc = [w for w in doc if not w in mots_vides]
    #retirer les termes de moins de 2 caractères
    doc = [w for w in doc if len(w)>=3]
    #fin
    return doc


# In[9]:


#fonction pour nettoyage corpus
#attention, optionnellement les documents vides sont éliminés
def nettoyage_corpus(corpus,vire_vide=True):
    #output
    output = [nettoyage_doc(doc) for doc in corpus if ((len(doc) > 0) or (vire_vide == False))]
    return output


# In[10]:


#fonction pour transformer un document en vecteur
#à partir des tokens qui le composent
#entrée : doc à traiter
#         modèle entrainé ou préentrainé
#sortie : vecteur représentant le document
def my_doc_2_vec(doc,trained):
    #dimension de représentation
    p = trained.vectors.shape[1]
    #initialiser le vecteur
    vec = np.zeros(p)
    #nombre de tokens trouvés
    nb = 0
    #traitement de chaque token du document
    for tk in doc:
        #ne traiter que les tokens reconnus
        if ((tk in trained.key_to_index.keys()) == True):
            values = trained[tk]
            vec = vec + values
            nb = nb + 1.0
    #faire la moyenne des valeurs
    #uniquement si on a trouvé des tokens reconnus bien sûr
    if (nb > 0.0):
        vec = vec/nb
    #renvoyer le vecteur
    #si aucun token trouvé, on a un vecteur de valeurs nulles
    return vec


# In[11]:


#fonction pour représenter un corpus à partir d'une représentation
#soit entraînée, soit pré-entraînée
#sortie : représentation matricielle
def my_corpora_2_vec(corpora,trained):
    docsVec = list()
    #pour chaque document du corpus nettoyé
    for doc in corpora:
        #calcul de son vecteur
        vec = my_doc_2_vec(doc,trained)
        #ajouter dans la liste
        docsVec.append(vec)
    #transformer en matrice numpy
    matVec = np.array(docsVec)
    return matVec

#fonction pour construire une typologie à partir
#d'une représentation des termes, qu'elle soit entraînée ou pré-entraînée
#seuil par défaut = 1, mais le but est d'avoir 4 groupes
#corpus ici se présente sous la forme d'une liste de listes de tokens

#la matrice des liens
def matrice_lien(corpus,trained):
    #matrice doc2vec pour la représentation à 1000 dim.
    #entraînée via word2vec sur les documents du corpus
    mat = my_corpora_2_vec(corpus,trained)

    #générer la matrice des liens
    Z = linkage(mat,method='ward',metric='euclidean')
    
    return Z


# In[38]:


#dendrogramme avec le seuil
def my_dendogram(matrice,seuil=10):
    
    #st.write("CAH")
    dendrogram(matrice,orientation='left',color_threshold=seuil)
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot()


# In[77]:


#fonction pour construire une typologie à partir
#d'une représentation des termes, qu'elle soit entraînée ou pré-entraînée
#seuil par défaut = 100, mais le but est d'avoir 4 groupes
#corpus ici se présente sous la forme d'une liste de listes de tokens
def my_cah_from_doc2vec(corpus,matrice,seuil=10,nbTermes=7):
    ### permettre à l'utilisateur de choisir le seuil

    #découpage en 4 classes
    grCAH = fcluster(matrice,t=seuil,criterion='distance')

    #***************************
    #interprétation des clusters
    #***************************
    
    #parseur
    parseur = CountVectorizer(binary=True)
    
    #former corpus sous forme de liste de chaîne
    corpus_string = [" ".join(doc) for doc in corpus]
    
    #matrice MDT
    mdt = parseur.fit_transform(corpus_string).toarray()
    
    df_list =[]
    #passer en revue les groupes
    for num_cluster in range(np.max(grCAH)):
        groupe = np.where(grCAH==num_cluster+1,1,0)
        #calcul de co-occurence
        cooc = np.apply_along_axis(func1d=lambda x: np.sum(x*groupe),axis=0,arr=mdt)
        #print(cooc)
        #création d'un data frame intermédiaire
        df = pd.DataFrame(data=cooc,columns=['Fréquence'],index=parseur.get_feature_names_out())    
        #affichage des "nbTermes" termes les plus fréquents
        df = df.sort_values(by='Fréquence',ascending=False).iloc[:nbTermes,:]
        #df_list.append(df)
        st.write(df)

        
    #renvoyer l'indicateur d'appartenance aux groupes
    return df_list


# Préparation pour worldcloud:
def mots_worldcloud(data):
    comment_words = ''

    # pour chaque mot dans data:
    for val in data.values:
     
        # convertir en string
        val = str(val)
 
        # split
        tokens = val.split()
     
        # convertir en lowercase
        for i in range(len(tokens)):
            tokens[i] = tokens[i].lower()
     
        comment_words += " ".join(tokens)+" "
        
    wordcloud = WordCloud(width = 800, height = 800,
                background_color ='white',
                      stopwords = mots_vides,
                min_font_size = 10).generate(comment_words)

    # plot WordCloud                     
    plt.figure(figsize = (8, 8), facecolor = None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad = 0)
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot()
    
    return comment_words


# Classent des sentiments commentaires:
def liste_sentiment(liste_note):
    liste_sen = []
    for i in liste_note:
        if i[0] < -0.5:
            liste_sen.append("Très négatif")
        elif (i[0]>=-0.5)&(i[0]<=0):
            liste_sen.append("Négatif")
        elif (i[0]>0)&(i[0]<=0.2):
            liste_sen.append("Neutre")
        elif (i[0]>0.2)&(i[0]<0.7):
            liste_sen.append("Positif")
        else:
            liste_sen.append("Très positif")
    return liste_sen
