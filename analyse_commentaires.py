#!/usr/bin/env python
# coding: utf-8

# In[79]:


# On import les packages nécessaires:
#import cx_Oracle
import oracledb
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
import pattern
from pattern.fr import sentiment


# # Connexion python et oracle

# In[80]:


dsnStr = oracledb.makedsn("db-etu.univ-lyon2.fr", "1521", "DBETU")
con = oracledb.connect(user="m134", password="m134", dsn=dsnStr)
cursor = con.cursor()


# # Les fonctions nécessaires pour l'analyse

# In[43]:


#récupérer la liste des ponctuations

ponctuations = list(string.punctuation)
print(ponctuations)


# In[44]:


#liste des chiffres
chiffres = list("0123456789")
print(chiffres)


# In[45]:


#outil pour procéder à la lemmatisation:

lem = WordNetLemmatizer()


# In[46]:


#liste des mots vides

mots_vides = stopwords.words("french")

# on ajoute qlq mots vides:
liste_mots_vides = ["disneyland","disney land","disney","parc","parcs","très","trop","séjour","hôtel","hotel",
                   "lhotel","lhôtel","l'hôtel","chambre","chambres","c'est","cest","c'était","ça","cela",
                   "avant","après","n'est","n'était","déjà","donc","alors","a","cet","j'ai","si","tres"]

for i in liste_mots_vides:
    mots_vides.append(i)
    
print(mots_vides)


# In[47]:


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


# In[48]:


#fonction pour nettoyage corpus
#attention, optionnellement les documents vides sont éliminés
def nettoyage_corpus(corpus,vire_vide=True):
    #output
    output = [nettoyage_doc(doc) for doc in corpus if ((len(doc) > 0) or (vire_vide == False))]
    return output


# In[49]:


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


# In[50]:


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


# In[51]:


#la matrice des liens
def matrice_lien(corpus,trained):
    #matrice doc2vec pour la représentation à 1000 dim.
    #entraînée via word2vec sur les documents du corpus
    mat = my_corpora_2_vec(corpus,trained)

    #générer la matrice des liens
    Z = linkage(mat,method='ward',metric='euclidean')
    
    return Z


# In[52]:


#dendrogramme avec le seuil
def my_dendogram(matrice,seuil=100):
    
    plt.title("CAH")
    dendrogram(matrice,orientation='left',color_threshold=seuil)
    plt.show()


# In[53]:


#fonction pour construire une typologie à partir
#d'une représentation des termes, qu'elle soit entraînée ou pré-entraînée
#seuil par défaut = 100, mais le but est d'avoir 4 groupes
#corpus ici se présente sous la forme d'une liste de listes de tokens
def my_cah_from_doc2vec(corpus,matrice,seuil=100,nbTermes=7):

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
        df_list.append(df)

        
    #renvoyer l'indicateur d'appartenance aux groupes
    return df_list


# In[54]:


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
    return comment_words


# In[55]:


# Classent des sentiments commentaires:
def liste_sentiment(liste_note):
    liste_sen = []
    for i in liste_note:
        if i[0] < 0.2:
            liste_sen.append("Très négatif")
        elif (i[0]>=0.2)&(i[0]<=0.4):
            liste_sen.append("Négatif")
        elif (i[0]>0.4)&(i[0]<=0.6):
            liste_sen.append("Neutre")
        elif (i[0]>0.6)&(i[0]<0.8):
            liste_sen.append("Positif")
        else:
            liste_sen.append("Très positif")
    return liste_sen


# # Analyse des commentaires pour les hôtels

# In[83]:


#Importer la table 'commentaire_hotel':
query_commentaire_hotel = "SELECT * FROM COMMENTAIRE_HOTEL"
commentaire_hotel = pd.read_sql(query_commentaire_hotel, con=con)


# In[71]:


#Chargez dans une liste des commentaires pour chaque item
corpus_original_hotel = []
for i in commentaire_hotel["COMMENTAIRE"].values:
    corpus_original_hotel.append(i)


# In[72]:


#corpus après pré-traitement, sous forme de listes de liste de tokens
corpus_liste_hotel = nettoyage_corpus(corpus_original_hotel)


# In[16]:


#construire la représentation à 1000 dim.

modele_hotel = Word2Vec(corpus_liste_hotel,vector_size=1000,window=3,min_count=2,epochs=100)
words_hotel = modele_hotel.wv


# CAH

# In[19]:


#la matrice des liens
Z_hotel = matrice_lien(corpus_liste_hotel,words_hotel)


# In[39]:


#afficher le dendrogramme
my_dendogram(Z_hotel)


# In[78]:


#CAH (critère de Ward) 

cah_hotel = my_cah_from_doc2vec(corpus_liste_hotel,Z_hotel)


# Word Cloud

# In[21]:


#World Cloud:
comment_words_hotel = mots_worldcloud(commentaire_hotel["COMMENTAIRE"])
wordcloud_hotel = WordCloud(width = 800, height = 800,
                background_color ='white',
                      stopwords = mots_vides,
                min_font_size = 10).generate(comment_words_hotel)


# In[22]:


# plot WordCloud                     
plt.figure(figsize = (8, 8), facecolor = None)
plt.imshow(wordcloud_hotel)
plt.axis("off")
plt.tight_layout(pad = 0)
 
plt.show()


# Analyse des sentiments

# In[23]:


#pip install pattern


# In[73]:


list_note_hotel = [sentiment(i) for i in corpus_liste_hotel]


# In[76]:


count_hotel


# In[74]:


liste_sen_hotel  = liste_sentiment(list_note_hotel)
commentaire_hotel["Sentiments"] = liste_sen_hotel
count_hotel = commentaire_hotel["Sentiments"].value_counts()
plt.pie(count_hotel)
plt.legend(["Très négatif","Négatif","Neutre","Positif","Très positif"])


# In[75]:


tres_positif_hotel = commentaire_hotel["COMMENTAIRE"][commentaire_hotel["Sentiments"]=="Très positif"]
positif_hotel = commentaire_hotel["COMMENTAIRE"][commentaire_hotel["Sentiments"]=="Positif"]
neutre_hotel = commentaire_hotel["COMMENTAIRE"][commentaire_hotel["Sentiments"]=="Neutre"]
negatif_hotel = commentaire_hotel["COMMENTAIRE"][commentaire_hotel["Sentiments"]=="Négatif"]
tres_negatif_hotel = commentaire_hotel["COMMENTAIRE"][commentaire_hotel["Sentiments"]=="Très négatif"]


# In[29]:


tres_positif_hotel_str = mots_worldcloud(tres_positif_hotel)

wordcloud_tres_positif_hotel = WordCloud(width = 800, height = 800,
                background_color ='white',
                      stopwords = mots_vides,
                min_font_size = 10).generate(tres_positif_hotel_str)

# plot WordCloud                     
plt.figure(figsize = (8, 8), facecolor = None)
plt.imshow(wordcloud_tres_positif_hotel)
plt.axis("off")
plt.tight_layout(pad = 0)
 
plt.show()


# In[30]:


positif_hotel_str = mots_worldcloud(positif_hotel)

wordcloud_positif_hotel = WordCloud(width = 800, height = 800,
                background_color ='white',
                      stopwords = mots_vides,
                min_font_size = 10).generate(positif_hotel_str)

# plot WordCloud                     
plt.figure(figsize = (8, 8), facecolor = None)
plt.imshow(wordcloud_positif_hotel)
plt.axis("off")
plt.tight_layout(pad = 0)
 
plt.show()


# In[31]:


neutre_hotel_str = mots_worldcloud(neutre_hotel)

wordcloud_neutre_hotel = WordCloud(width = 800, height = 800,
                background_color ='white',
                      stopwords = mots_vides,
                min_font_size = 10).generate(neutre_hotel_str)

# plot WordCloud                     
plt.figure(figsize = (8, 8), facecolor = None)
plt.imshow(wordcloud_neutre_hotel)
plt.axis("off")
plt.tight_layout(pad = 0)
 
plt.show()


# In[34]:


negatif_hotel_str = mots_worldcloud(negatif_hotel)

wordcloud_negatif_hotel = WordCloud(width = 800, height = 800,
                background_color ='white',
                      stopwords = mots_vides,
                min_font_size = 10).generate(negatif_hotel_str)

# plot WordCloud                     
plt.figure(figsize = (8, 8), facecolor = None)
plt.imshow(wordcloud_negatif_hotel)
plt.axis("off")
plt.tight_layout(pad = 0)
 
plt.show()


# In[35]:


tres_negatif_hotel_str = mots_worldcloud(tres_negatif_hotel)

wordcloud_tres_negatif_hotel = WordCloud(width = 800, height = 800,
                background_color ='white',
                      stopwords = mots_vides,
                min_font_size = 10).generate(tres_negatif_hotel_str)

# plot WordCloud                     
plt.figure(figsize = (8, 8), facecolor = None)
plt.imshow(wordcloud_tres_negatif_hotel)
plt.axis("off")
plt.tight_layout(pad = 0)
 
plt.show()


# # Analyse des commentaires pour les parcs

# In[56]:


#Importer la table 'commentaire_parc':
query_commentaire_parc = "SELECT* FROM COMMENTAIRE_PARC"
commentaire_parc = pd.read_sql(query_commentaire_parc, con=con)


# In[57]:


commentaire_parc["COMMENTAIRE"] = commentaire_parc["COMMENTAIRE"].astype(str)


# In[58]:


#Chargez dans une liste les commentaires pour chaque item
corpus_original_parc = []
for i in commentaire_parc["COMMENTAIRE"].values:
    corpus_original_parc.append(i)


# In[59]:


#corpus après pré-traitement, sous forme de listes de liste de tokens
corpus_liste_parc = nettoyage_corpus(corpus_original_parc)


# In[86]:


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


# In[89]:


#CAH (critère de Ward) 

cah_parc = my_cah_from_doc2vec(corpus_liste_parc,Z_parc)


# Word Cloud

# In[39]:


comment_words_parc = mots_worldcloud(commentaire_parc["COMMENTAIRE"])
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


# In[60]:


list_note_parc = [sentiment(i) for i in corpus_liste_parc]


# In[68]:


count_parc


# In[69]:


liste_sen_parc  = liste_sentiment(list_note_parc)
commentaire_parc["Sentiments"] = liste_sen_parc
count_parc = commentaire_parc["Sentiments"].value_counts()
plt.pie(count_parc)
plt.legend(["Très négatif","Négatif","Neutre","Positif","Très positif"])


# In[62]:


tres_positif_parc = commentaire_parc["COMMENTAIRE"][commentaire_parc["Sentiments"]=="Très positif"]
positif_parc = commentaire_parc["COMMENTAIRE"][commentaire_parc["Sentiments"]=="Positif"]
neutre_parc = commentaire_parc["COMMENTAIRE"][commentaire_parc["Sentiments"]=="Neutre"]
negatif_parc = commentaire_parc["COMMENTAIRE"][commentaire_parc["Sentiments"]=="Négatif"]
tres_negatif_parc = commentaire_parc["COMMENTAIRE"][commentaire_parc["Sentiments"]=="Très négatif"]


# In[63]:


tres_positif_parc_str = mots_worldcloud(tres_positif_parc)

wordcloud_tres_positif_parc = WordCloud(width = 800, height = 800,
                background_color ='white',
                      stopwords = mots_vides,
                min_font_size = 10).generate(tres_positif_parc_str)

# plot WordCloud                     
plt.figure(figsize = (8, 8), facecolor = None)
plt.imshow(wordcloud_tres_positif_parc)
plt.axis("off")
plt.tight_layout(pad = 0)
 
plt.show()


# In[64]:


positif_parc_str = mots_worldcloud(positif_parc)

wordcloud_positif_parc = WordCloud(width = 800, height = 800,
                background_color ='white',
                      stopwords = mots_vides,
                min_font_size = 10).generate(positif_parc_str)

# plot WordCloud                     
plt.figure(figsize = (8, 8), facecolor = None)
plt.imshow(wordcloud_positif_parc)
plt.axis("off")
plt.tight_layout(pad = 0)
 
plt.show()


# In[65]:


neutre_parc_str = mots_worldcloud(neutre_parc)

wordcloud_neutre_parc = WordCloud(width = 800, height = 800,
                background_color ='white',
                      stopwords = mots_vides,
                min_font_size = 10).generate(neutre_parc_str)

# plot WordCloud                     
plt.figure(figsize = (8, 8), facecolor = None)
plt.imshow(wordcloud_neutre_parc)
plt.axis("off")
plt.tight_layout(pad = 0)
 
plt.show()


# In[66]:


negatif_parc_str = mots_worldcloud(negatif_parc)

wordcloud_negatif_parc = WordCloud(width = 800, height = 800,
                background_color ='white',
                      stopwords = mots_vides,
                min_font_size = 10).generate(negatif_parc_str)

# plot WordCloud                     
plt.figure(figsize = (8, 8), facecolor = None)
plt.imshow(wordcloud_negatif_parc)
plt.axis("off")
plt.tight_layout(pad = 0)
 
plt.show()


# In[67]:


tres_negatif_parc_str = mots_worldcloud(tres_negatif_parc)

wordcloud_tres_negatif_parc = WordCloud(width = 800, height = 800,
                background_color ='white',
                      stopwords = mots_vides,
                min_font_size = 10).generate(tres_negatif_parc_str)

# plot WordCloud                     
plt.figure(figsize = (8, 8), facecolor = None)
plt.imshow(wordcloud_tres_negatif_parc)
plt.axis("off")
plt.tight_layout(pad = 0)
 
plt.show()


# In[ ]:




