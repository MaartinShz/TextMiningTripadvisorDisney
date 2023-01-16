#!/usr/bin/env python
# coding: utf-8

# In[1]:


# On import les packages nécessaires:
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
#import gensim
#from gensim.models import Word2Vec
from scipy.cluster.hierarchy import dendrogram, linkage,fcluster
from sklearn.feature_extraction.text import CountVectorizer
import matplotlib.pyplot as plt
#pip install wordcloud
from wordcloud import WordCloud
import pattern
from pattern.fr import sentiment


# # Connexion python et oracle

# In[2]:


dsnStr = oracledb.makedsn("db-etu.univ-lyon2.fr", "1521", "DBETU")
con = oracledb.connect(user="m134", password="m134", dsn=dsnStr)
cursor = con.cursor()


# # Les fonctions nécessaires pour l'analyse

# In[3]:


#récupérer la liste des ponctuations

ponctuations = list(string.punctuation)
print(ponctuations)


# In[4]:


#liste des chiffres
chiffres = list("0123456789")
print(chiffres)


# In[5]:


#outil pour procéder à la lemmatisation:

lem = WordNetLemmatizer()


# In[6]:


#liste des mots vides

mots_vides = stopwords.words("french")

# on ajoute qlq mots vides:
liste_mots_vides = ["disneyland","disney land","disney","parc","parcs","très","trop","séjour","hôtel","hotel",
                   "lhotel","lhôtel","l'hôtel","chambre","chambres","c'est","cest","c'était","ça","cela",
                   "avant","après","n'est","n'était","déjà","donc","alors","a","cet","j'ai","si","tres"]

for i in liste_mots_vides:
    mots_vides.append(i)
    
print(mots_vides)


# In[7]:


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


# In[8]:


#fonction pour nettoyage corpus
#attention, optionnellement les documents vides sont éliminés
def nettoyage_corpus(corpus,vire_vide=True):
    #output
    output = [nettoyage_doc(doc) for doc in corpus if ((len(doc) > 0) or (vire_vide == False))]
    return output


# In[9]:


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


# In[10]:


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


# In[11]:


#la matrice des liens
def matrice_lien(corpus,trained):
    #matrice doc2vec pour la représentation à 1000 dim.
    #entraînée via word2vec sur les documents du corpus
    mat = my_corpora_2_vec(corpus,trained)

    #générer la matrice des liens
    Z = linkage(mat,method='ward',metric='euclidean')
    
    return Z


# In[12]:


#dendrogramme avec le seuil
def my_dendogram(matrice,seuil=100):
    
    plt.title("CAH")
    dendrogram(matrice,orientation='left',color_threshold=seuil)
    plt.show()


# In[13]:


#fonction pour construire une typologie à partir
#d'une représentation des termes, qu'elle soit entraînée ou pré-entraînée
#seuil par défaut = 10, mais le but est d'avoir 4 groupes
#corpus ici se présente sous la forme d'une liste de listes de tokens
def my_cah_from_doc2vec(corpus,matrice,seuil=10,nbTermes=7):

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
        print(df)

        
    #renvoyer l'indicateur d'appartenance aux groupes
    return df


# In[14]:


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
 
    plt.show()
    
    return comment_words


# In[15]:


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


# # Analyse des commentaires pour les hôtels

# In[16]:


#Importer la table 'commentaire_hotel':
query_commentaire_hotel = "SELECT COMMENTAIRE,ANNÉE FROM COMMENTAIRE_HOTEL,DATECOMMENTAIRE WHERE COMMENTAIRE_HOTEL.ID_DATECOMMENTAIRE = DATECOMMENTAIRE.ID_DATECOMMENTAIRE"
commentaire_hotel = pd.read_sql(query_commentaire_hotel, con=con)


# In[17]:


#Chargez dans une liste des commentaires pour chaque item
corpus_original_hotel = []
for i in commentaire_hotel["COMMENTAIRE"].values:
    corpus_original_hotel.append(i)


# In[18]:


#corpus après pré-traitement, sous forme de listes de liste de tokens
corpus_liste_hotel = nettoyage_corpus(corpus_original_hotel)


# In[19]:


commentaire_hotel["corpus"] = corpus_liste_hotel


# In[20]:


# on sélectionne des commentaires en fonction de l'année:
year = "2022"
corpus_liste_hotel_year = commentaire_hotel["corpus"][commentaire_hotel["ANNÉE"] == year]
commentaire_hotel_year = commentaire_hotel["COMMENTAIRE"][commentaire_hotel["ANNÉE"] == year]


# CAH

# In[79]:


#construire la représentation à 100 dim.

modele_hotel = Word2Vec(corpus_liste_hotel_year,vector_size=100,window=3,min_count=2,epochs=100)
words_hotel = modele_hotel.wv


# In[19]:


#la matrice des liens
Z_hotel = matrice_lien(corpus_liste_hotel_year,words_hotel)


# In[39]:


#afficher le dendrogramme
my_dendogram(Z_hotel)


# In[78]:


#CAH (critère de Ward) 

cah_hotel = my_cah_from_doc2vec(corpus_liste_hotel_year,Z_hotel)


# Word Cloud

# In[22]:


#World Cloud:
mots_worldcloud(commentaire_hotel_year)


# Analyse des sentiments

# In[34]:


# on crée une liste des sentiments pour les commentaires des hotels:
list_note_hotel = [sentiment(i) for i in corpus_liste_hotel_year]


# In[123]:


# on affiche pie chart:
liste_sen_hotel  = liste_sentiment(list_note_hotel)
df_sentiment_hotel = pd.DataFrame(commentaire_hotel_year)
df_sentiment_hotel["Sentiments"] = liste_sen_hotel
count_hotel = df_sentiment_hotel["Sentiments"].value_counts()
plt.pie(count_hotel)
labels = ["Positif","Neutre","Négatif","Très positif","Très négatif"]
plt.legend(labels, loc="best")


# In[124]:


# on crée un dataframe pour chaque type de sentiment:

tres_positif_hotel = df_sentiment_hotel["COMMENTAIRE"][df_sentiment_hotel["Sentiments"]=="Très positif"]
positif_hotel = df_sentiment_hotel["COMMENTAIRE"][df_sentiment_hotel["Sentiments"]=="Positif"]
neutre_hotel = df_sentiment_hotel["COMMENTAIRE"][df_sentiment_hotel["Sentiments"]=="Neutre"]
negatif_hotel = df_sentiment_hotel["COMMENTAIRE"][df_sentiment_hotel["Sentiments"]=="Négatif"]
tres_negatif_hotel = df_sentiment_hotel["COMMENTAIRE"][df_sentiment_hotel["Sentiments"]=="Très négatif"]


# In[146]:


# word cloud pour les commentaires très positifs:
if len(tres_positif_hotel) > 0:
    mots_worldcloud(tres_positif_hotel)

else:
    print("Il n'y a pas de commentaire très positif")


# In[147]:


# word cloud pour les commentaires positifs:

if len(positif_hotel) > 0:
    
    mots_worldcloud(positif_hotel)
    
else:
    print("Il n'y a pas de commentaire positif")


# In[39]:


# word cloud pour les commentaires neutres:

if len(neutre_hotel) > 0:
    
    mots_worldcloud(neutre_hotel)
    
else:
    print("Il n'y a pas de commentaire neutre")


# In[61]:


# word cloud pour les commentaires négatifs:

if len(negatif_hotel) > 0:
    
    mots_worldcloud(negatif_hotel)

else:
    print("Il n'y a pas de commentaire négatif")


# In[148]:


# word cloud pour les commentaires très négatifs:

if len(tres_negatif_hotel) > 0:
    
    mots_worldcloud(tres_negatif_hotel)

else:
    print("Il n'y a pas de commentaire très négatif")


# Analyse note pour les hotels

# In[63]:


# Importer la table "note":

query_note_hotel = "SELECT ANNÉE,NOTE FROM COMMENTAIRE_HOTEL,NOTE,DATECOMMENTAIRE WHERE COMMENTAIRE_HOTEL.ID_NOTE = NOTE.ID_NOTE AND COMMENTAIRE_HOTEL.ID_DATECOMMENTAIRE = DATECOMMENTAIRE.ID_DATECOMMENTAIRE"
note_hotel = pd.read_sql(query_note_hotel, con=con)


# In[72]:


# On sélectionne les notes par rapport à l'année:

note_hotel_year = pd.DataFrame(note_hotel["NOTE"][note_hotel["ANNÉE"] == year])


# In[75]:


# on affiche bar chart:

count_note_hotel = note_hotel_year["NOTE"].value_counts()
count_note_hotel.plot(kind="bar")
plt.show()


# Analyse des localisations pour les hotels

# In[78]:


# Importer la table "localisation":

query_local_hotel = "SELECT ANNÉE,LOCALISATION FROM COMMENTAIRE_HOTEL,LOCALISATION,DATECOMMENTAIRE WHERE COMMENTAIRE_HOTEL.ID_LOCALISATION = LOCALISATION.ID_LOCALISATION AND COMMENTAIRE_HOTEL.ID_DATECOMMENTAIRE = DATECOMMENTAIRE.ID_DATECOMMENTAIRE"
local_hotel = pd.read_sql(query_local_hotel, con=con)


# In[106]:


# On sélectionne les localisations par rapport à l'année:

local_hotel_year = pd.DataFrame(local_hotel["LOCALISATION"][local_hotel["ANNÉE"] == year])


# In[114]:


# on affiche une table - les 10 localisations les plus fréquentes:

local_hotel_year.value_counts()[:10]


# # Analyse des commentaires pour les parcs

# In[115]:


#Importer la table 'commentaire_parc':

query_commentaire_parc = "SELECT COMMENTAIRE,ANNÉE FROM COMMENTAIRE_PARC,DATECOMMENTAIRE WHERE COMMENTAIRE_PARC.ID_DATECOMMENTAIRE = DATECOMMENTAIRE.ID_DATECOMMENTAIRE"
commentaire_parc = pd.read_sql(query_commentaire_hotel, con=con)


# In[116]:


commentaire_parc["COMMENTAIRE"] = commentaire_parc["COMMENTAIRE"].astype(str)


# In[117]:


#Chargez dans une liste les commentaires pour chaque item
corpus_original_parc = []
for i in commentaire_parc["COMMENTAIRE"].values:
    corpus_original_parc.append(i)


# In[118]:


#corpus après pré-traitement, sous forme de listes de liste de tokens
corpus_liste_parc = nettoyage_corpus(corpus_original_parc)


# In[119]:


commentaire_parc["corpus"] = corpus_liste_parc


# In[120]:


# on sélectionne des commentaires en fonction de l'année:
year = "2022"
corpus_liste_parc_year = commentaire_parc["corpus"][commentaire_parc["ANNÉE"] == year]
commentaire_parc_year = commentaire_parc["COMMENTAIRE"][commentaire_parc["ANNÉE"] == year]


# CAH

# In[86]:


#construire la représentation à 100 dim.

modele_parc = Word2Vec(corpus_liste_parc_year,vector_size=100,window=3,min_count=2,epochs=100)
words_parc = modele_parc.wv


# In[87]:


#la matrice des liens
Z_parc = matrice_lien(corpus_liste_parc_year,words_parc)


# In[88]:


#afficher le dendrogramme
my_dendogram(Z_parc)


# In[89]:


#CAH (critère de Ward) 

cah_parc = my_cah_from_doc2vec(corpus_liste_parc_year,Z_parc)


# Word Cloud

# In[149]:


# word cloud:

mots_worldcloud(commentaire_parc_year)


# Analyse des sentiments

# In[127]:


# on crée une liste des sentiments pour les commentaires des parcs:

list_note_parc = [sentiment(i) for i in corpus_liste_parc_year]


# In[128]:


# on affiche pie chart:

liste_sen_parc  = liste_sentiment(list_note_parc)
df_sentiment_parc = pd.DataFrame(commentaire_parc_year)
df_sentiment_parc["Sentiments"] = liste_sen_parc
count_parc = df_sentiment_parc["Sentiments"].value_counts()
plt.pie(count_parc)
plt.legend(["Positif","Neutre","Négatif","Très positif","Très négatif"])
plt.show()


# In[129]:


# on crée un dataframe pour chaque type de sentiment:

tres_positif_parc = df_sentiment_parc["COMMENTAIRE"][df_sentiment_parc["Sentiments"]=="Très positif"]
positif_parc = df_sentiment_parc["COMMENTAIRE"][df_sentiment_parc["Sentiments"]=="Positif"]
neutre_parc = df_sentiment_parc["COMMENTAIRE"][df_sentiment_parc["Sentiments"]=="Neutre"]
negatif_parc = df_sentiment_parc["COMMENTAIRE"][df_sentiment_parc["Sentiments"]=="Négatif"]
tres_negatif_parc = df_sentiment_parc["COMMENTAIRE"][df_sentiment_parc["Sentiments"]=="Très négatif"]


# In[130]:


# word cloud pour les commentaires très positifs:

if len(tres_positif_parc) > 0:
    
    mots_worldcloud(tres_positif_parc)

else:
    print("Il n'y a pas de commentaire très positif")


# In[131]:


# word cloud pour les commentaires positifs:

if len(positif_parc) > 0:
    
    mots_worldcloud(positif_parc)

else:
    print("Il n'y a pas de commentaire positif")


# In[132]:


# word cloud pour les commentaires neutres:

if len(neutre_parc) > 0:

    mots_worldcloud(neutre_parc)

else:
    print("Il n'y a pas de commentaire neutre")


# In[133]:


# word cloud pour les commentaires négatifs:

if len(negatif_parc) > 0:
    
    mots_worldcloud(negatif_parc)

else:
    print("Il n'y a pas de commentaire négatif")


# In[134]:


# word cloud pour les commentaires très négatifs:

if len(tres_negatif_parc) > 0:

    mots_worldcloud(tres_negatif_parc)

else:
    print("Il n'y a pas de commentaire très négatif")


# Analyse notes pour les parcs

# In[135]:


# Importer la table "note":
query_note_parc = "SELECT ANNÉE,NOTE FROM COMMENTAIRE_PARC,NOTE,DATECOMMENTAIRE WHERE COMMENTAIRE_PARC.ID_NOTE = NOTE.ID_NOTE AND COMMENTAIRE_PARC.ID_DATECOMMENTAIRE = DATECOMMENTAIRE.ID_DATECOMMENTAIRE"
note_parc = pd.read_sql(query_note_parc, con=con)


# In[136]:


# On sélectionne les notes par rapport à l'année:

note_parc_year = pd.DataFrame(note_parc["NOTE"][note_parc["ANNÉE"] == year])


# In[137]:


# on affiche bar chart:
count_note_parc = note_parc_year["NOTE"].value_counts()
count_note_parc.plot(kind="bar")
plt.show()


# Analyse localisations pour les parcs

# In[138]:


# Importer la table "localisation":
query_local_parc = "SELECT ANNÉE,LOCALISATION FROM COMMENTAIRE_PARC,LOCALISATION,DATECOMMENTAIRE WHERE COMMENTAIRE_PARC.ID_LOCALISATION = LOCALISATION.ID_LOCALISATION AND COMMENTAIRE_PARC.ID_DATECOMMENTAIRE = DATECOMMENTAIRE.ID_DATECOMMENTAIRE"
local_parc = pd.read_sql(query_local_parc, con=con)


# In[139]:


# On sélectionne les localisations par rapport à l'année:

local_parc_year = pd.DataFrame(local_parc["LOCALISATION"][local_parc["ANNÉE"] == year])


# In[140]:


# on affiche une table - les 10 localisations les plus fréquentes:
local_parc_year.value_counts()[:10]


# Analyse situation pour les parcs

# In[25]:


# Importer la table "situation":

query_situation = "SELECT ANNÉE,SITUATION FROM COMMENTAIRE_PARC,SITUATION,DATECOMMENTAIRE WHERE COMMENTAIRE_PARC.ID_SITUATION = SITUATION.ID_SITUATION AND COMMENTAIRE_PARC.ID_DATECOMMENTAIRE = DATECOMMENTAIRE.ID_DATECOMMENTAIRE"
situation = pd.read_sql(query_situation, con=con)


# In[26]:


# On sélectionne les localisations par rapport à l'année:

situation_year = pd.DataFrame(situation["SITUATION"][situation["ANNÉE"] == year])


# In[27]:


# on affiche bar chart:

count_situation = situation_year["SITUATION"].value_counts()
count_situation.plot(kind="bar")
plt.show()

