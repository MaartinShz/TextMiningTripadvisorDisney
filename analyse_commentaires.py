#!/usr/bin/env python
# coding: utf-8

# In[1]:


# On import les packages nécessaires:
import cx_Oracle
import pandas as pd
import numpy as np
import csv
import os
import re
from unidecode import unidecode
import string
#nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from gensim.models import Word2Vec
from scipy.cluster.hierarchy import dendrogram, linkage,fcluster
from sklearn.feature_extraction.text import CountVectorizer
import matplotlib.pyplot as plt
#pip install wordcloud
from wordcloud import WordCloud


# # Connexion python et oracle

# In[2]:


cx_Oracle.init_oracle_client(lib_dir="/Users/dangnguyenviet/Desktop/Master 2 SISE/instantclient_19_8")


# In[3]:


dsnStr = cx_Oracle.makedsn("db-etu.univ-lyon2.fr", "1521", "DBETU")
con = cx_Oracle.connect(user="m134", password="m134", dsn=dsnStr)
cursor = con.cursor()


# # Les fonctions nécessaires pour l'analyse

# In[4]:


#récupérer la liste des ponctuations

ponctuations = list(string.punctuation)
print(ponctuations)


# In[5]:


#liste des chiffres
chiffres = list("0123456789")
print(chiffres)


# In[6]:


#outil pour procéder à la lemmatisation:

lem = WordNetLemmatizer()


# In[7]:


#liste des mots vides

mots_vides = stopwords.words("french")

# on ajoute qlq mots vides:
liste_mots_vides = ["disneyland","disney land","disney","parc","très","trop","séjour","hôtel",
                   "lhotel","l'hôtel","chambre","chambres","c'est","cest","c'était","ça","cela",
                   "avant","après","n'est","n'était","déjà","donc","alors"]

for i in liste_mots_vides:
    mots_vides.append(i)
    
print(mots_vides)


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


# In[12]:


#fonction pour construire une typologie à partir
#d'une représentation des termes, qu'elle soit entraînée ou pré-entraînée
#seuil par défaut = 1, mais le but est d'avoir 4 groupes
#corpus ici se présente sous la forme d'une liste de listes de tokens
def my_cah_from_doc2vec(corpus,trained,seuil=1.0,nbTermes=7):

    #matrice doc2vec pour la représentation à 100 dim.
    #entraînée via word2vec sur les documents du corpus
    mat = my_corpora_2_vec(corpus,trained)

    #dimension
    #mat.shape

    #générer la matrice des liens
    Z = linkage(mat,method='ward',metric='euclidean')

    #affichage du dendrogramme
    plt.title("CAH")
    dendrogram(Z,orientation='left',color_threshold=0)
    plt.show()

    #affichage du dendrogramme avec le seuil
    plt.title("CAH")
    dendrogram(Z,orientation='left',color_threshold=seuil)
    plt.show()

    #découpage en 4 classes
    grCAH = fcluster(Z,t=seuil,criterion='distance')
    #print(grCAH)

    #comptage
    print(np.unique(grCAH,return_counts=True))

    #***************************
    #interprétation des clusters
    #***************************
    
    #parseur
    parseur = CountVectorizer(binary=True)
    
    #former corpus sous forme de liste de chaîne
    corpus_string = [" ".join(doc) for doc in corpus]
    
    #matrice MDT
    mdt = parseur.fit_transform(corpus_string).toarray()
    print("Dim. matrice documents-termes = {}".format(mdt.shape))
    
    #passer en revue les groupes
    for num_cluster in range(np.max(grCAH)):
        print("")
        #numéro du cluster à traiter
        print("Numero du cluster = {}".format(num_cluster+1))
        groupe = np.where(grCAH==num_cluster+1,1,0)
        effectifs = np.unique(groupe,return_counts=True)
        print("Effectifs = {}".format(effectifs[1][1]))
        #calcul de co-occurence
        cooc = np.apply_along_axis(func1d=lambda x: np.sum(x*groupe),axis=0,arr=mdt)
        #print(cooc)
        #création d'un data frame intermédiaire
        tmpDF = pd.DataFrame(data=cooc,columns=['freq'],index=parseur.get_feature_names_out())    
        #affichage des "nbTermes" termes les plus fréquents
        print(tmpDF.sort_values(by='freq',ascending=False).iloc[:nbTermes,:])
        
    #renvoyer l'indicateur d'appartenance aux groupes
    return grCAH, mat


# # Analyse des commentaires pour les hôtels

# In[ ]:


#Importer la table 'commentaire_hotel':
query_commentaire_hotel = """SELECT* 
           FROM COMMENTAIRE_HOTEL
           """
commentaire_hotel = pd.read_sql(query_commentaire_hotel, con=con)
print(commentaire_hotel)


# In[ ]:


#Chargez dans une liste des commentaires pour chaque item
corpus_original_hotel = []
for i in commentaire_hotel["COMMENTAIRE"].values:
    corpus_original_hotel.append(i)
corpus_original_hotel


# In[ ]:


#corpus après pré-traitement, sous forme de listes de liste de tokens
corpus_liste_hotel = nettoyage_corpus(corpus_original_hotel)
corpus_liste_hotel


# In[ ]:


#construire la représentation à 1000 dim.

modele_hotel = Word2Vec(corpus_liste_hotel,vector_size=1000,window=3,min_count=2,epochs=100)
words_hotel = modele_hotel.wv


# CAH

# In[ ]:


#A partir de la matrice de description des documents, réaliser une CAH (critère de Ward) 
#et afficher le dendrogramme

g2,mat2 = my_cah_from_doc2vec(corpus_liste_hotel,words_hotel,seuil=100)


# Word Cloud

# In[ ]:


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


# In[ ]:


wordcloud_hotel = WordCloud(width = 800, height = 800,
                background_color ='white',
                      stopwords = mots_vides,
                min_font_size = 10).generate(comment_words_hotel)


# In[ ]:


# plot WordCloud                     
plt.figure(figsize = (8, 8), facecolor = None)
plt.imshow(wordcloud_hotel)
plt.axis("off")
plt.tight_layout(pad = 0)
 
plt.show()


# # Analyse des commentaires pour les parcs

# In[13]:


#Importer la table 'commentaire_parc':
query_commentaire_parc = """SELECT* 
           FROM COMMENTAIRE_PARC
           """
commentaire_parc = pd.read_sql(query_commentaire_parc, con=con)
print(commentaire_parc)


# In[14]:


commentaire_parc["COMMENTAIRE"] = commentaire_parc["COMMENTAIRE"].astype(str)


# In[15]:


#Chargez dans une liste les commentaires pour chaque item
corpus_original_parc = []
for i in commentaire_parc["COMMENTAIRE"].values:
    corpus_original_parc.append(i)
corpus_original_parc


# In[16]:


#corpus après pré-traitement, sous forme de listes de liste de tokens
corpus_liste_parc = nettoyage_corpus(corpus_original_parc)
corpus_liste_parc


# In[17]:


#construire la représentation à 1000 dim.

modele_parc = Word2Vec(corpus_liste_parc,vector_size=1000,window=3,min_count=2,epochs=100)
words_parc = modele_parc.wv


# CAH

# In[18]:


#A partir de la matrice de description des documents, réaliser une CAH (critère de Ward) 
#et afficher le dendrogramme

g1,mat1 = my_cah_from_doc2vec(corpus_liste_parc,words_parc,seuil=100)


# Word Cloud

# In[19]:


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


# In[20]:


wordcloud_parc = WordCloud(width = 800, height = 800,
                background_color ='white',
                      stopwords = mots_vides,
                min_font_size = 10).generate(comment_words_parc)


# In[21]:


# plot WordCloud                     
plt.figure(figsize = (8, 8), facecolor = None)
plt.imshow(wordcloud_parc)
plt.axis("off")
plt.tight_layout(pad = 0)
 
plt.show()

