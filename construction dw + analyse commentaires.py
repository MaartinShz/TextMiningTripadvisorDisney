#!/usr/bin/env python
# coding: utf-8

# # Connexion python et oracle

# In[3]:


#pip install cx_Oracle


# In[2]:


import cx_Oracle
cx_Oracle.init_oracle_client(lib_dir="/Users/dangnguyenviet/Desktop/Master 2 SISE/instantclient_19_8")


# In[3]:


dsnStr = cx_Oracle.makedsn("db-etu.univ-lyon2.fr", "1521", "DBETU")
print(dsnStr)


# In[4]:


con = cx_Oracle.connect(user="m134", password="m134", dsn=dsnStr)
cursor = con.cursor()
print(con.version)


# In[1]:


# On import les packages nécessaires:
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


# # 1er étape : Construction datawarehouse pour les parcs dans un premiers temps (à partir des fichiers csv)

# Dans cette étape, on ne peut exécuter le code qu'une seule fois, c-a-d on ne peut exporter les fichers vers oracle qu'une seule fois.

# In[15]:


# Exporter la table "note" vers oracle:

with open('/Users/dangnguyenviet/Desktop/Master 2 SISE/cours/M2 SISE - Text mining/projet Disney Land/note.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    next(csv_reader)
    s_note = "INSERT INTO note(Id_Note, Note) VALUES(:1, :2)"
    data_note = []
    for line in csv_reader:
        data_note.append(line)
    print(data_note)
    
    for line in data_note:
        cursor.execute(s_note, line)
    con.commit()


# In[18]:


# Exporter la table "situation" vers oracle:

with open('/Users/dangnguyenviet/Desktop/Master 2 SISE/cours/M2 SISE - Text mining/projet Disney Land/situation.csv', 'r') as csv_file_situation:
    csv_situation = csv.reader(csv_file_situation, delimiter=';')
    next(csv_situation)
    s_situation = "INSERT INTO situation(Id_Situation, Situation) VALUES(:1, :2)"
    data_situation = []
    for line in csv_situation:
        data_situation.append(line)
    print(data_situation)
    
    for line in data_situation:
        cursor.execute(s_situation, line)
    con.commit()


# In[33]:


# Exporter la table "date_commentaire" vers oracle:

with open('/Users/dangnguyenviet/Desktop/Master 2 SISE/cours/M2 SISE - Text mining/projet Disney Land/date_commentaire.csv', 'r') as csv_file_date_commentaire:
    csv_date_commentaire = csv.reader(csv_file_date_commentaire, delimiter=';')
    next(csv_date_commentaire)
    s_date_commentaire = "INSERT INTO datecommentaire(Id_Datecommentaire, Mois, Année) VALUES(:1, :2, :3)"
    data_date_commentaire = []
    for line in csv_date_commentaire:
        data_date_commentaire.append(line)
    
    for line in data_date_commentaire:
        cursor.execute(s_date_commentaire, line)
    con.commit()


# In[34]:


# Exporter la table "date_sejour" vers oracle:
with open('/Users/dangnguyenviet/Desktop/Master 2 SISE/cours/M2 SISE - Text mining/projet Disney Land/date_sejour.csv', 'r') as csv_file_date_sejour:
    csv_date_sejour = csv.reader(csv_file_date_sejour, delimiter=';')
    next(csv_date_sejour)
    s_date_sejour = "INSERT INTO datesejour(Id_Datesejour, Mois, Année) VALUES(:1, :2, :3)"
    data_date_sejour = []
    for line in csv_date_sejour:
        data_date_sejour.append(line)
    
    for line in data_date_sejour:
        cursor.execute(s_date_sejour, line)
    con.commit()


# In[5]:


# On importe le fichier des commentaires scrapé du site:

os.chdir("/Users/dangnguyenviet/Desktop/Master 2 SISE/cours/M2 SISE - Text mining/projet Disney Land")
test = pd.read_table("text1.csv",sep=",",header=0)
test.info()


# In[6]:


# on extrait la localisation:

# on transforme la colonne "pays" en liste
liste_string = test["pays"].tolist()
liste_local = []

# pour chaque élément dans la liste, on cherche où il y a des chiffres, si c'est le cas, 
# on récupère son index, et on ne prend que le string juste avant les chiffres
temp = 0
for i in liste_string:
    for c in i:
        if c.isdigit():
            temp = i.index(c)
            break
    liste_local.append(i[:temp])

print(liste_local)


# In[7]:


#créer un dataframe contenant l'identifiant pour chaque localisation:

df_loca = pd.DataFrame()

# créer la colonne "localisation"
liste_loca = []
for i in liste_local:
    if i not in liste_loca:
        liste_loca.append(i)
df_loca["localisation"] = liste_loca

# créer la colonne "id_localisation"
liste_id_loca = []
for j in range(len(df_loca["localisation"])):
    id = "L_" + str(j+1)
    liste_id_loca.append(id)
df_loca["id_localisation"] = liste_id_loca

# on change la position des colonnes:
df_loca = df_loca[df_loca.columns[[1,0]]]
print(df_loca)


# In[8]:


# Exporter la table "localisation" vers oracle:
cursor = con.cursor()

s_loca = "INSERT INTO LOCALISATION(ID_LOCALISATION,LOCALISATION) VALUES(:1,:2)"


data_loca = []
for line in df_loca.values:
        data_loca.append(line)
        
for line in data_loca:
    cursor.execute(s_loca, line)
con.commit()


# In[39]:


# créer un dataframe vide nommé df_commentaire:
df_commentaire = pd.DataFrame()


# In[40]:


#Importer la table 'note' à partir de l'oracle:
query_note = """SELECT* 
           FROM NOTE
           """
note = pd.read_sql(query_note, con=con)
print(note)


# In[41]:


# on ajoute la colonne "Id_Note" au dataframe df_commentaire:

liste_note=[]
for i in range(len(test["note"])):
    if test["note"][i] == "nan":
            liste_note.append("")
    for j in range(len(note["NOTE"])):
        if test["note"][i] == note["NOTE"].astype(int)[j]:
            liste_note.append(note["ID_NOTE"][j])
df_commentaire["Id_Note"]= liste_note
print(df_commentaire)


# In[42]:


# On enlève l'espace dans le string pour la colonne "situation":
test["situation"] = test["situation"].apply(lambda x: str(x).strip())


# In[43]:


#Importer la table 'situation':
query_situation = """SELECT* 
           FROM SITUATION
           """
situation = pd.read_sql(query_situation, con=con)
print(situation)


# In[44]:


# on ajoute la colonne "Id_Situation" au dataframe df_commentaire:

liste_situation=[]
for i in range(len(test["situation"])):
    if test["situation"][i] == "nan":
            liste_situation.append("")
    for j in range(len(situation["SITUATION"])):
        if test["situation"][i] == situation["SITUATION"][j]:
            liste_situation.append(situation["ID_SITUATION"][j])

df_commentaire["Id_Situation"]= liste_situation
print(df_commentaire)


# In[45]:


#Importer la table 'localisation':
query_localisation = """SELECT* 
           FROM LOCALISATION
           """
localisation = pd.read_sql(query_localisation, con=con)
print(localisation)


# In[46]:


# on ajoute la colonne "localisation" au dataframe df_commentaire:

liste_localisation=[]
for i in range(len(liste_local)):
    if liste_local[i] == "":
            liste_localisation.append("L_1")
    for j in range(len(localisation["LOCALISATION"])):
        if liste_local[i] == localisation["LOCALISATION"][j]:
            liste_localisation.append(localisation["ID_LOCALISATION"][j])
df_commentaire["Id_Localisation"]= liste_localisation
print(df_commentaire)


# In[47]:


# on extrait mois et année:
date_list = [full_date[11:] for full_date in test["dateCommentaire"]]

# On enlève l'espace et l'accent dans le string:
date_list = [unidecode(i.strip()) for i in date_list]

date_list


# In[48]:


#Importer la table 'datecommentaire':
query_datecommentaire = """SELECT* 
           FROM DATECOMMENTAIRE
           """
datecommentaire = pd.read_sql(query_datecommentaire, con=con)
print(datecommentaire)


# In[49]:


# on crée une liste contenante mois et année en même temps:

list_moisannee_commentaire = []
list_moisannee_commentaire = datecommentaire["MOIS"] + " "+ datecommentaire["ANNÉE"]
list_moisannee_commentaire


# In[50]:


# on ajoute la colonne "id_datecommentaire" au dataframe df_commentaire:

liste_datecommentaire=[]
for i in range(len(date_list)):
    if date_list[i] == "nan":
            liste_datecommentaire.append("")
    for j in range(len(list_moisannee_commentaire)):
        if date_list[i] == list_moisannee_commentaire[j]:
            liste_datecommentaire.append(datecommentaire["ID_DATECOMMENTAIRE"][j])
df_commentaire["Id_Datecommentaire"]= liste_datecommentaire
print(df_commentaire)


# In[51]:


# on traite la colonne "dateSejour" du fichier test:
test["dateSejour"]= test["dateSejour"].apply(lambda x: str(x).replace("déc.","decembre"))
test["dateSejour"] = test["dateSejour"].apply(lambda x: str(x).replace("nov.","novembre"))
test["dateSejour"] = test["dateSejour"].apply(lambda x: str(x).replace("oct.","octobre"))
test["dateSejour"] = test["dateSejour"].apply(lambda x: str(x).replace("sept.","septembre"))
test["dateSejour"] = test["dateSejour"].apply(lambda x: str(x).replace("juil.","juillet"))
test["dateSejour"]= test["dateSejour"].apply(lambda x: str(x).replace("avr.","avril"))
test["dateSejour"] = test["dateSejour"].apply(lambda x: str(x).replace("févr.","fevrier"))
test["dateSejour"] = test["dateSejour"].apply(lambda x: str(x).replace("août","aout"))
test["dateSejour"] = test["dateSejour"].apply(lambda x: str(x).replace("jan.","janvier"))

date_list_sejour = test["dateSejour"].values.tolist()

date_list_sejour


# In[52]:


#Importer la table 'datesejour':
query_datesejour = """SELECT* 
           FROM DATESEJOUR
           """
datesejour = pd.read_sql(query_datesejour, con=con)
print(datesejour)


# In[53]:


# on crée une liste contenante mois et année en même temps:

list_moisannee_sejour = []
list_moisannee_sejour = datesejour["MOIS"] + " "+ datesejour["ANNÉE"]
list_moisannee_sejour


# In[54]:


# on ajoute la colonne "id_datesejour" au dataframe df_commentaire:

liste_datesejour=[]
for i in range(len(date_list_sejour)):
    if date_list_sejour[i] == "nan":
            liste_datesejour.append("")
    for j in range(len(list_moisannee_sejour)):
        if date_list_sejour[i] == list_moisannee_sejour[j]:
            liste_datesejour.append(datesejour["ID_DATESEJOUR"][j])
df_commentaire["Id_Datesejour"]= liste_datesejour
print(df_commentaire)


# In[55]:


# on ajoute la colonne "id_commentaire" au dataframe df_commentaire:
liste_idcommentaire=[]
for i in range(len(df_commentaire.index)):
    liste_idcommentaire.append("C_" + str(i+1))
df_commentaire["Id_Commentaire"]= liste_idcommentaire
print(df_commentaire)


# In[56]:


# on ajoute la colonne "Titre" et la colonne "Commentaire" au dataframe df_commentaire:

df_commentaire["Titre"]= test["titre"]
df_commentaire["Commentaire"]= test["commentaire"]

# on change la posistion des colonnes:
df_commentaire = df_commentaire[df_commentaire.columns[[5,0,1,3,4,2,6,7]]]

print(df_commentaire)


# In[57]:


# Exporter la table "commentaire_parc" vers oracle:
s_commentaire = "INSERT INTO commentaire_parc (Id_Commentaire, Id_Note, Id_Situation, Id_DateCommentaire,Id_DateSejour,Id_Localisation,Titre,Commentaire) VALUES (:1, :2, :3, :4, :5, :6, :7, :8)"
data_commentaire = []
for line in df_commentaire.values:
    data_commentaire.append(line)

for line in data_commentaire:
    cursor.execute(s_commentaire, line)
con.commit()        


# # 2eme étape : Mise à jour datawarehouse pour les parcs au cours du temps 

# In[114]:


#Importer la table 'note':
query_note = """SELECT* 
           FROM NOTE
           """
note = pd.read_sql(query_note, con=con)
print(note)


# In[115]:


#Importer la table 'situation':
query_situation = """SELECT* 
           FROM SITUATION
           """
situation = pd.read_sql(query_situation, con=con)
print(situation)


# In[116]:


#Importer la table 'datecommentaire':
query_datecommentaire = """SELECT* 
           FROM DATECOMMENTAIRE
           """
datecommentaire = pd.read_sql(query_datecommentaire, con=con)
print(datecommentaire)


# In[117]:


# on crée une liste contenante mois et année en même temps:

list_moisannee_commentaire = []
list_moisannee_commentaire = datecommentaire["MOIS"] + " "+ datecommentaire["ANNÉE"]
list_moisannee_commentaire


# In[118]:


#Importer la table 'datesejour':
query_datesejour = """SELECT* 
           FROM DATESEJOUR
           """
datesejour = pd.read_sql(query_datesejour, con=con)
print(datesejour)


# In[119]:


# on crée une liste contenante mois et année en même temps:

list_moisannee_sejour = []
list_moisannee_sejour = datesejour["MOIS"] + " "+ datesejour["ANNÉE"]
list_moisannee_sejour


# In[193]:


#Importer la table 'commentaire_parc':
query_commentaire_parc = """SELECT* 
           FROM COMMENTAIRE_PARC
           """
commentaire_parc = pd.read_sql(query_commentaire_parc, con=con)
print(commentaire_parc)


# In[120]:


#Importer la table 'localisation':
query_localisation = """SELECT* 
           FROM LOCALISATION
           """
localisation = pd.read_sql(query_localisation, con=con)
print(localisation)


# In[131]:


# on met la liste de la localisation de datawarehouse dans une liste:
liste_local_dw = localisation["LOCALISATION"].tolist()
liste_local_dw[0] = str(liste_local_dw[0]).replace("None","")
liste_local_dw


# In[8]:


# On importe le 2eme fichier des commentaires scrapé du site:

os.chdir("/Users/dangnguyenviet/Desktop/Master 2 SISE/cours/M2 SISE - Text mining/projet Disney Land")
test2 = pd.read_table("text2.csv",sep=",",header=0)
test2.info()


# In[20]:


# on extrait la localisation de nouveau fichier:

liste_string_new = test2["pays"].tolist()
liste_local_new = []

temp = 0
for i in liste_string_new:
    for c in i:
        if c.isdigit():
            temp = i.index(c)
            break
    liste_local_new.append(i[:temp])

print(liste_local_new)


# In[29]:


# on crée nouveaux "id_localisation" s'il y a des nouvelles localisations:

df_local_new = pd.DataFrame()
liste_localisation_new = []
for j in liste_local_new:
    if (j not in liste_local_dw)&(j!='')&(j not in liste_localisation_new):
        liste_localisation_new.append(j)
df_local_new["localisation"] = liste_localisation_new

liste_id_loca_new = []
for k in range(len(df_local_new["localisation"])):
    l = len(liste_local_dw)
    id = "L_" + str(l+k+1)
    liste_id_loca_new.append(id)
df_local_new["id_localisation"] = liste_id_loca_new 

df_local_new = df_local_new[df_local_new.columns[[1,0]]]
print(df_local_new)


# In[30]:


# Exporter des nouvelles valeurs de la table "localisation" vers oracle:
cursor = con.cursor()

s_loca = "INSERT INTO LOCALISATION(ID_LOCALISATION,LOCALISATION) VALUES(:1,:2)"

if (len(df_local_new) != 0):
    data_loca_new = []
    for line in df_local_new.values:
        data_loca_new.append(line)
        
    for line in data_loca_new:
        cursor.execute(s_loca, line)
    con.commit()


# In[33]:


# créer un dataframe vide nommé df_commentaire_new:
df_commentaire_new = pd.DataFrame()


# In[40]:


# on ajoute la colonne "Id_Note" au dataframe df_commentaire_new:

liste_note_new=[]
for i in range(len(test2["note"])):
    if test2["note"][i] == "nan":
            liste_note_new.append("")
    for j in range(len(note["NOTE"])):
        if test2["note"][i] == note["NOTE"].astype(int)[j]:
            liste_note_new.append(note["ID_NOTE"][j])
df_commentaire_new["Id_Note"]= liste_note_new
print(df_commentaire_new)


# In[41]:


# On enlève l'espace dans le string pour la colonne "situation":
test2["situation"] = test2["situation"].apply(lambda x: str(x).strip())


# In[42]:


# on ajoute la colonne "Id_Situation" au dataframe df_commentaire_new:

liste_situation_new =[]
for i in range(len(test2["situation"])):
    if test2["situation"][i] == "nan":
            liste_situation_new.append("")
    for j in range(len(situation["SITUATION"])):
        if test2["situation"][i] == situation["SITUATION"][j]:
            liste_situation_new.append(situation["ID_SITUATION"][j])

df_commentaire_new["Id_Situation"]= liste_situation_new
print(df_commentaire_new)


# In[45]:


#pour la colonne dateCommentaire du fichier test2:
# on extrait mois et année:
date_list_new = [full_date[11:] for full_date in test2["dateCommentaire"]]

# On enlève l'espace dans le string :
date_list_new = [unidecode(i.strip()) for i in date_list_new]

date_list_new


# In[47]:


# on ajoute la colonne "id_datecommentaire" au dataframe df_commentaire_new:

liste_datecommentaire_new=[]
for i in range(len(date_list_new)):
    if date_list_new[i] == "nan":
            liste_datecommentaire_new.append("")
    for j in range(len(list_moisannee_commentaire)):
        if date_list_new[i] == list_moisannee_commentaire[j]:
            liste_datecommentaire_new.append(datecommentaire["ID_DATECOMMENTAIRE"][j])
df_commentaire_new["Id_Datecommentaire"]= liste_datecommentaire_new
print(df_commentaire_new)


# In[48]:


# on traite la colonne "dateSejour" du fichier test2:
test2["dateSejour"]= test2["dateSejour"].apply(lambda x: str(x).replace("déc.","decembre"))
test2["dateSejour"] = test2["dateSejour"].apply(lambda x: str(x).replace("nov.","novembre"))
test2["dateSejour"] = test2["dateSejour"].apply(lambda x: str(x).replace("oct.","octobre"))
test2["dateSejour"] = test2["dateSejour"].apply(lambda x: str(x).replace("sept.","septembre"))
test2["dateSejour"] = test2["dateSejour"].apply(lambda x: str(x).replace("juil.","juillet"))
test2["dateSejour"]= test2["dateSejour"].apply(lambda x: str(x).replace("avr.","avril"))
test2["dateSejour"] = test2["dateSejour"].apply(lambda x: str(x).replace("févr.","fevrier"))
test2["dateSejour"] = test2["dateSejour"].apply(lambda x: str(x).replace("août","aout"))
test2["dateSejour"] = test2["dateSejour"].apply(lambda x: str(x).replace("jan.","janvier"))

date_list_sejour_new = test2["dateSejour"].values.tolist()

date_list_sejour_new


# In[50]:


# on ajoute la colonne "id_datesejour" au dataframe df_commentaire_new:

liste_datesejour_new=[]
for i in range(len(date_list_sejour_new)):
    if date_list_sejour_new[i] == "nan":
            liste_datesejour_new.append("")
    for j in range(len(list_moisannee_sejour)):
        if date_list_sejour_new[i] == list_moisannee_sejour[j]:
            liste_datesejour_new.append(datesejour["ID_DATESEJOUR"][j])
df_commentaire_new["Id_Datesejour"]= liste_datesejour_new
print(df_commentaire_new)


# In[63]:


#Importer de nouveau la table 'localisation':
query_localisation = """SELECT* 
           FROM LOCALISATION
           """
localisation = pd.read_sql(query_localisation, con=con)
print(localisation)


# In[64]:


# on ajoute la colonne "id_localisation" au dataframe df_commentaire_new:

liste_localisation_new=[]
for i in range(len(liste_local_new)):
    if (liste_local_new[i] == ""):
        liste_localisation_new.append("L_1")
    for j in range(len(localisation["LOCALISATION"])):
        if liste_local_new[i] == localisation["LOCALISATION"][j]:
            liste_localisation_new.append(localisation["ID_LOCALISATION"][j])
df_commentaire_new["Id_Localisation"]= liste_localisation_new
print(df_commentaire_new)


# In[65]:


# on ajoute la colonne "id_commentaire" au dataframe df_commentaire_new:
liste_idcommentaire_new=[]
for i in range(len(df_commentaire_new.index)):
    l = len(commentaire)
    liste_idcommentaire_new.append("C_" + str(l+i+1))
df_commentaire_new["Id_Commentaire"]= liste_idcommentaire_new
print(df_commentaire_new)


# In[66]:


# on ajoute la colonne "Titre" et la colonne "Commentaire" au dataframe df_commentaire_new:

df_commentaire_new["Titre"]= test2["titre"]
df_commentaire_new["Commentaire"]= test2["commentaire"]

# on change la position des colonnes
df_commentaire_new = df_commentaire_new[df_commentaire_new.columns[[5,0,1,2,3,4,6,7]]]

print(df_commentaire_new)


# In[67]:


# Exporter des nouvelles valeurs de la table "commentaire_parc" vers oracle:
s_commentaire = "INSERT INTO commentaire_parc (Id_Commentaire, Id_Note, Id_Situation, Id_DateCommentaire,Id_DateSejour,Id_Localisation,Titre,Commentaire) VALUES (:1, :2, :3, :4, :5, :6, :7, :8)"
data_commentaire_new = []
for line in df_commentaire_new.values:
    data_commentaire_new.append(line)

for line in data_commentaire_new:
    cursor.execute(s_commentaire, line)
con.commit()


# # Analyse des commentaires pour les parcs

# In[7]:


#Importer la table 'commentaire_parc':
query_commentaire_parc = """SELECT* 
           FROM COMMENTAIRE_PARC
           """
commentaire_parc = pd.read_sql(query_commentaire_parc, con=con)
print(commentaire_parc)


# Nettoyage des données – Préparation du corpus

# In[8]:


#Chargez dans une liste les commentaires pour chaque item
corpus_original_parc = []
for i in commentaire_parc["COMMENTAIRE"].values:
    corpus_original_parc.append(i)
corpus_original_parc


# In[9]:


#récupérer la liste des ponctuations

ponctuations = list(string.punctuation)
print(ponctuations)


# In[10]:


#liste des chiffres
chiffres = list("0123456789")
print(chiffres)


# In[11]:


#outil pour procéder à la lemmatisation:

lem = WordNetLemmatizer()


# In[13]:


#liste des mots vides

mots_vides = stopwords.words("french")

# on ajoute qlq mots vides:
mots_vides.append("disneyland")
mots_vides.append("disney land")
mots_vides.append("disney")
mots_vides.append("parc")
mots_vides.append("très")
mots_vides.append("trop")
mots_vides.append("séjour")

print(mots_vides)


# In[14]:


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


# In[15]:


#fonction pour nettoyage corpus
#attention, optionnellement les documents vides sont éliminés
def nettoyage_corpus(corpus,vire_vide=True):
    #output
    output = [nettoyage_doc(doc) for doc in corpus if ((len(doc) > 0) or (vire_vide == False))]
    return output


# In[16]:


#corpus après pré-traitement, sous forme de listes de liste de tokens
corpus_liste_parc = nettoyage_corpus(corpus_original_parc)
corpus_liste_parc


# Classification des commentaires

# In[22]:


#reconstruire la représentation ci-dessus, mais à 100 dim.

modele_parc = Word2Vec(corpus_liste_parc,vector_size=100,window=3,min_count=1,epochs=100)
words_parc = modele_parc.wv


# In[18]:


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


# In[19]:


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


# Classification ascendante hiérarchique

# In[21]:


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


# In[23]:


#A partir de la matrice de description des documents, réaliser une CAH (critère de Ward) 
#et afficher le dendrogramme

g1,mat1 = my_cah_from_doc2vec(corpus_liste_parc,words_parc,seuil=0.5)


# Word Cloud

# In[25]:


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


# In[26]:


wordcloud_parc = WordCloud(width = 800, height = 800,
                background_color ='white',
                      stopwords = mots_vides,
                min_font_size = 10).generate(comment_words_parc)


# In[27]:


# plot WordCloud                     
plt.figure(figsize = (8, 8), facecolor = None)
plt.imshow(wordcloud_parc)
plt.axis("off")
plt.tight_layout(pad = 0)
 
plt.show()


# # Construction datawarehouse pour les hôtels

# In[194]:


#Importer la table 'commentaire_hotel':
query_commentaire_hotel = """SELECT* 
           FROM COMMENTAIRE_HOTEL
           """
commentaire_hotel = pd.read_sql(query_commentaire_hotel, con=con)
print(commentaire_hotel)


# In[112]:


# On importe le fichier des commentaires pour les hôtels scrapé du site:

os.chdir("/Users/dangnguyenviet/Desktop/Master 2 SISE/cours/M2 SISE - Text mining/projet Disney Land")
test3 = pd.read_table("text_hotel.csv",sep=",",header=0)
test3.info()


# In[140]:


# on crée nouveaux "id_localisation" s'il y a des nouvelles localisations:

liste_local_new = test3["pays"].dropna().tolist()

df_local_new = pd.DataFrame()
liste_localisation_new = []
for j in liste_local_new:
    if (j not in liste_local_dw)&(j!='')&(j not in liste_localisation_new):
        liste_localisation_new.append(j)
df_local_new["localisation"] = liste_localisation_new

liste_id_loca_new = []
for k in range(len(df_local_new["localisation"])):
    l = len(liste_local_dw)
    id = "L_" + str(l+k+1)
    liste_id_loca_new.append(id)
df_local_new["id_localisation"] = liste_id_loca_new 

df_local_new = df_local_new[df_local_new.columns[[1,0]]]
print(df_local_new)


# In[141]:


# Exporter des nouvelles valeurs de la table "localisation" vers oracle:
cursor = con.cursor()

s_loca = "INSERT INTO LOCALISATION(ID_LOCALISATION,LOCALISATION) VALUES(:1,:2)"

if (len(df_local_new) != 0):
    data_loca_new = []
    for line in df_local_new.values:
        data_loca_new.append(line)
        
    for line in data_loca_new:
        cursor.execute(s_loca, line)
    con.commit()


# In[142]:


# créer un dataframe vide nommé df_commentaire_hotel:
df_commentaire_hotel = pd.DataFrame()


# In[143]:


# on ajoute la colonne "Id_Note" au dataframe df_commentaire_hotel:

liste_note_hotel=[]
for i in range(len(test3["note"])):
    if test3["note"][i] == "nan":
            liste_note_hotel.append("")
    for j in range(len(note["NOTE"])):
        if test3["note"][i] == note["NOTE"].astype(int)[j]:
            liste_note_hotel.append(note["ID_NOTE"][j])
df_commentaire_hotel["Id_Note"]= liste_note_hotel
print(df_commentaire_hotel)


# In[149]:


# On extrait le string pour la colonne "situation":
liste_situation = [str(i)[26:].capitalize() for i in test3["situation"]]
liste_situation


# In[150]:


# on ajoute la colonne "Id_Situation" au dataframe df_commentaire_hotel:

liste_situation_hotel =[]
for i in range(len(liste_situation)):
    if liste_situation[i] == "":
            liste_situation_hotel.append("")
    for j in range(len(situation["SITUATION"])):
        if liste_situation[i] == situation["SITUATION"][j]:
            liste_situation_hotel.append(situation["ID_SITUATION"][j])

df_commentaire_hotel["Id_Situation"]= liste_situation_hotel
print(df_commentaire_hotel)


# In[153]:


#pour la colonne dateCommentaire du fichier test3:
# on extrait mois et année:
date_list_hotel1 = []

for i in test3["dateCommentaire"].values:
    date_list_hotel1.append(i[i.find("(")+1:i.find(")")])

date_list_hotel = []
for i in date_list_hotel1:
    i= i.replace("déc.","decembre")
    i= i.replace("nov.","novembre")
    i= i.replace("oct.","octobre")
    i= i.replace("sept.","septembre")
    i= i.replace("juil.","juillet")
    i= i.replace("avr.","avril")
    i= i.replace("févr.","fevrier")
    i= i.replace("août","aout")
    i= i.replace("jan.","janvier")
    date_list_hotel.append(i)
    
date_list_hotel


# In[167]:


# on ajoute la colonne "id_datecommentaire" au dataframe df_commentaire_hotel:

liste_datecommentaire_hotel=[]
for i in range(len(date_list_hotel)):
    if date_list_hotel[i] not in list_moisannee_commentaire:
        for c in date_list_hotel[i]:
            if c.isdigit():
                liste_datecommentaire_hotel.append("")
            break
        
    for j in range(len(list_moisannee_commentaire)):
        if (date_list_hotel[i] == list_moisannee_commentaire[j]) & (date_list_hotel[i] != ""):
            liste_datecommentaire_hotel.append(datecommentaire["ID_DATECOMMENTAIRE"][j])
    
df_commentaire_hotel["Id_Datecommentaire"]= liste_datecommentaire_hotel
print(df_commentaire_hotel)


# In[169]:


# on traite la colonne "dateSejour" du fichier test3:

# on extrait mois et année:
date_list_sejour_hotel = [full_date[17:] for full_date in test3["dateSejour"]]

# On enlève l'espace et l'accent dans le string :
date_list_sejour_hotel = [unidecode(i.strip()) for i in date_list_sejour_hotel]

date_list_sejour_hotel


# In[170]:


# on ajoute la colonne "id_datesejour" au dataframe df_commentaire_new:

liste_datesejour_hotel=[]
for i in range(len(date_list_sejour_hotel)):
    if date_list_sejour_hotel[i] == "nan":
            liste_datesejour_hotel.append("")
    for j in range(len(list_moisannee_sejour)):
        if date_list_sejour_hotel[i] == list_moisannee_sejour[j]:
            liste_datesejour_hotel.append(datesejour["ID_DATESEJOUR"][j])
df_commentaire_hotel["Id_Datesejour"]= liste_datesejour_hotel
print(df_commentaire_hotel)


# In[171]:


#Importer de nouveau la table 'localisation':
query_localisation = """SELECT* 
           FROM LOCALISATION
           """
localisation = pd.read_sql(query_localisation, con=con)
print(localisation)


# In[188]:


# on ajoute la colonne "localisation" au dataframe df_commentaire_hotel:

liste_localisation_hotel=[]
for i in range(len(test3["pays"])):
    if (str(test3["pays"][i]) == "nan"):
        liste_localisation_hotel.append("L_1")
    for j in range(len(localisation["LOCALISATION"])):
        if test3["pays"][i] == localisation["LOCALISATION"][j]:
            liste_localisation_hotel.append(localisation["ID_LOCALISATION"][j])
df_commentaire_hotel["Id_Localisation"]= liste_localisation_hotel
print(df_commentaire_hotel)


# In[189]:


# on ajoute la colonne "id_commentaire" au dataframe df_commentaire_hotel:
liste_idcommentaire_hotel=[]
for i in range(len(df_commentaire_hotel.index)):
    l = len(commentaire_hotel)
    liste_idcommentaire_hotel.append("C_" + str(i+1))
df_commentaire_hotel["Id_Commentaire"]= liste_idcommentaire_hotel
print(df_commentaire_hotel)


# In[190]:


# on ajoute la colonne "Titre" et la colonne "Commentaire" au dataframe df_commentaire_hotel:

df_commentaire_hotel["Titre"]= test3["titre"]
df_commentaire_hotel["Commentaire"]= test3["commentaire"]

df_commentaire_hotel = df_commentaire_hotel[df_commentaire_hotel.columns[[5,0,1,2,3,4,6,7]]]

print(df_commentaire_hotel)


# In[191]:


# Exporter des nouvelles valeurs de la table "commentaire_hotel" vers oracle:
s_commentaire = "INSERT INTO commentaire_hotel (Id_Commentaire, Id_Note, Id_Situation, Id_DateCommentaire,Id_DateSejour,Id_Localisation,Titre,Commentaire) VALUES (:1, :2, :3, :4, :5, :6, :7, :8)"
data_commentaire_hotel = []
for line in df_commentaire_hotel.values:
    data_commentaire_hotel.append(line)

for line in data_commentaire_hotel:
    cursor.execute(s_commentaire, line)
con.commit()


# # Analyse des commentaires pour les hôtels

# In[6]:


#Importer la table 'commentaire_hotel':
query_commentaire_hotel = """SELECT* 
           FROM COMMENTAIRE_HOTEL
           """
commentaire_hotel = pd.read_sql(query_commentaire_hotel, con=con)
print(commentaire_hotel)


# In[28]:


#Chargez dans une liste des commentaires pour chaque item
corpus_original_hotel = []
for i in commentaire_hotel["COMMENTAIRE"].values:
    corpus_original_hotel.append(i)
corpus_original_hotel


# In[48]:


#liste des mots vides

mots_vides= stopwords.words("french")

mots_vides.append("disneyland")
mots_vides.append("disney land")
mots_vides.append("disney")
mots_vides.append("très")
mots_vides.append("trop")
mots_vides.append("séjour")
mots_vides.append("hôtel")
mots_vides.append("hotel")
mots_vides.append("lhotel")
mots_vides.append("lhôtel")
mots_vides.append("l'hôtel")
mots_vides.append("chambre")
mots_vides.append("chambres")

print(mots_vides)


# In[49]:


#corpus après pré-traitement, sous forme de listes de liste de tokens
corpus_liste_hotel = nettoyage_corpus(corpus_original_hotel)
corpus_liste_hotel


# In[50]:


#reconstruire la représentation ci-dessus, mais à 100 dim.

modele_hotel = Word2Vec(corpus_liste_hotel,vector_size=100,window=3,min_count=1,epochs=100)
words_hotel = modele_hotel.wv


# In[51]:


#A partir de la matrice de description des documents, réaliser une CAH (critère de Ward) 
#et afficher le dendrogramme

g2,mat2 = my_cah_from_doc2vec(corpus_liste_hotel,words_hotel,seuil=0.1)


# Word Cloud

# In[52]:


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


# In[53]:


wordcloud_hotel = WordCloud(width = 800, height = 800,
                background_color ='white',
                      stopwords = mots_vides,
                min_font_size = 10).generate(comment_words_hotel)


# In[54]:


# plot WordCloud                     
plt.figure(figsize = (8, 8), facecolor = None)
plt.imshow(wordcloud_hotel)
plt.axis("off")
plt.tight_layout(pad = 0)
 
plt.show()


# In[ ]:




