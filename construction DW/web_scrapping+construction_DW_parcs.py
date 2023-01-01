#!/usr/bin/env python
# coding: utf-8

# # Web scraping parcs

# In[1]:


# On import les packages nécessaires:
import pandas as pd
import numpy as np
import csv
import os
import re
from unidecode import unidecode
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
from bs4 import BeautifulSoup
import requests
from datetime import timedelta, date


# In[8]:


headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'en,mr;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}




exportAvis = []


# In[30]:


def scrapParc(url, export=False):
    i=0#compteur d'avis
    while(i<17000):#url is not None): # condition à changer vérifier date du commmentaire récupérer avec la date de commmentaire le plus récent  
        #time.sleep(3)
        req = requests.get(url,headers=headers)
        #print (req.status_code) # 200 -> OK
        soup = BeautifulSoup(req.content, 'html.parser')  
        blocAvis = soup.find(attrs={"class" : "LbPSX"})
        
        #########################  Scrapping Avis
        for avis in blocAvis.findAll(attrs={"class" : "_c"}):
            i = i + 1
            pays = avis.find(class_="biGQs _P pZUbB osNWb").text #PAYS  attention champs à vérifier
            
            titre = avis.find(class_="biGQs _P fiohW qWPrE ncFvv fOtGX").text #titre commentaire
            
            note = int(avis.find(class_="UctUV d H0")["aria-label"][0]) #note commentaire
            
            commentaire = avis.find(attrs={'class':'biGQs _P pZUbB KxBGd'}).text #corps du commentaire
            
            dateSejour = avis.find(class_="RpeCd")#.text #date du séjour
            if(dateSejour is not None):
                sep= dateSejour.text.find("•")-1
                
                if(sep >0):
                    situation = dateSejour.text[sep+2:] # avoir si utile dans analyse
                    dateSejour = dateSejour.text[:sep]
                else:
                    dateSejour = dateSejour.text
                    situation = ""
            else:
                dateSejour = ""
                situation = ""
            
            dateCommentaire = avis.find(class_="biGQs _P pZUbB ncFvv osNWb").text[avis.find(class_="biGQs _P pZUbB ncFvv osNWb").text.find(" ",9)+1:] #date du commentaire
            
            photo = avis.find(class_="ajoIU _S B-") #Présence de photo: oui/non
            if(photo is not None):
                photo = True
            else:
                photo = False
                
            ### Enregistrement des données scrapper
            nomColonnes = ["pays", "titre", "note", "commentaire", "dateSejour", "situation", "dateCommentaire", "photo"]
            exportAvis.append([pays.replace(",",""), titre.replace(",",""), note, commentaire.replace(",",""), dateSejour, situation, dateCommentaire, photo])
            #print([pays, titre, note, commentaire, dateSejour, situation, dateCommentaire, photo])
            #print(dateCommentaire)
            print(i)
        ######################### next Page
        try:
            url = "https://www.tripadvisor.fr"+blocAvis.find(class_="xkSty").find(class_="BrOJk u j z _F wSSLS tIqAi unMkR")["href"]
        except:
            url = None
        ############################################ Export result
        if(export):
            with open('exportAvisParc'+ soup.title.text.replace(" ","").replace(":","") +'.csv', 'w', encoding='utf-8', newline='') as f: 
                write = csv.writer(f)
                write.writerow(nomColonnes)
                write.writerows(exportAvis)


# In[31]:


urlsParc="https://www.tripadvisor.fr/Attraction_Review-g226865-d285990-Reviews-Walt_Disney_Studios_Park-Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html"


# In[32]:


os.chdir("/Users/dangnguyenviet/Desktop/Master 2 SISE/cours/M2 SISE - Text mining/projet Disney Land")
scrapParc(url=urlsParc,export=True)


# # Connexion python et oracle

# In[99]:


import cx_Oracle
cx_Oracle.init_oracle_client(lib_dir="/Users/dangnguyenviet/Desktop/Master 2 SISE/instantclient_19_8")


# In[114]:


dsnStr = cx_Oracle.makedsn("db-etu.univ-lyon2.fr", "1521", "DBETU")
con = cx_Oracle.connect(user="m134", password="m134", dsn=dsnStr)
cursor = con.cursor()


# In[111]:


con.close()


# # Construction DW pour les parcs

# In[39]:


#Importer la table 'note':
query_note = """SELECT* 
           FROM NOTE
           """
note = pd.read_sql(query_note, con=con)
print(note)


# In[40]:


#Importer la table 'situation':
query_situation = """SELECT* 
           FROM SITUATION
           """
situation = pd.read_sql(query_situation, con=con)
print(situation)


# In[41]:


#Importer la table 'datecommentaire':
query_datecommentaire = """SELECT* 
           FROM DATECOMMENTAIRE
           """
datecommentaire = pd.read_sql(query_datecommentaire, con=con)
print(datecommentaire)


# In[42]:


# on crée une liste contenante mois et année en même temps:

list_moisannee_commentaire = []
list_moisannee_commentaire = datecommentaire["MOIS"] + " "+ datecommentaire["ANNÉE"]
list_moisannee_commentaire


# In[43]:


#Importer la table 'datesejour':
query_datesejour = """SELECT* 
           FROM DATESEJOUR
           """
datesejour = pd.read_sql(query_datesejour, con=con)
print(datesejour)


# In[44]:


# on crée une liste contenante mois et année en même temps:

list_moisannee_sejour = []
list_moisannee_sejour = datesejour["MOIS"] + " "+ datesejour["ANNÉE"]
list_moisannee_sejour


# In[46]:


#Importer la table 'localisation':
query_localisation = """SELECT* 
           FROM LOCALISATION
           """
localisation = pd.read_sql(query_localisation, con=con)
print(localisation)


# In[47]:


# on met la liste de la localisation de datawarehouse dans une liste:
liste_local_dw = localisation["LOCALISATION"].tolist()
liste_local_dw


# In[108]:


os.chdir("/Users/dangnguyenviet/Desktop/Master 2 SISE/cours/M2 SISE - Text mining/projet Disney Land")
parc = pd.read_table("parc.csv",sep=";",header=0)
parc.info()


# In[35]:


# on transforme la colonne "pays" en liste, on met tout en minuscule et on enlève les accents:
liste_local = parc["pays"].dropna().tolist()
liste_local = [unidecode(str(i).lower()) for i in liste_local]


# on extrait la localisation :
liste_local_new = []
temp = 0
for i in liste_local:
    for c in i:
        if c.isdigit():
            temp = i.index(c)
            break
    liste_local_new.append(i[:temp])

print(liste_local_new)


# In[48]:


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


# In[49]:


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


# In[50]:


#Importer de nouveau la table 'localisation':
query_localisation = """SELECT* 
           FROM LOCALISATION
           """
localisation = pd.read_sql(query_localisation, con=con)
print(localisation)


# In[51]:


# créer un dataframe vide nommé df_commentaire_parc:
df_commentaire_parc = pd.DataFrame()


# In[72]:


# on ajoute la colonne "Id_Note" au dataframe df_commentaire_parc:

liste_note_parc=[]
for i in range(len(parc["note"])):
    if parc["note"].tolist()[i] == "nan":
        liste_note_parc.append("")
    for j in range(len(note["NOTE"])):
        if parc["note"].tolist()[i] == note["NOTE"].astype(int)[j]:
            liste_note_parc.append(note["ID_NOTE"][j])
df_commentaire_parc["Id_Note"]= liste_note_parc
print(df_commentaire_parc)


# In[73]:


# On enlève l'espace dans le string pour la colonne "situation":
parc["situation"] = parc["situation"].apply(lambda x: str(x).strip())
print(parc["situation"])


# In[75]:


# on ajoute la colonne "Id_Situation" au dataframe df_commentaire_parc:

liste_situation_parc=[]
for i in range(len(parc["situation"])):
    if parc["situation"].tolist()[i] == "nan":
            liste_situation_parc.append("")
    for j in range(len(situation["SITUATION"])):
        if parc["situation"].tolist()[i] == situation["SITUATION"][j]:
            liste_situation_parc.append(situation["ID_SITUATION"][j])

df_commentaire_parc["Id_Situation"]= liste_situation_parc
print(df_commentaire_parc)


# In[80]:


#pour la colonne dateCommentaire du fichier parc:
# on extrait mois et année:
date_list_new = parc["dateCommentaire"].tolist()

# On enlève l'espace dans le string :
date_list_new = [unidecode(str(i).strip()) for i in date_list_new]

date_list_new


# In[81]:


# on ajoute la colonne "id_datecommentaire" au dataframe df_commentaire_parc

liste_datecommentaire_new=[]
for i in range(len(date_list_new)):
    if date_list_new[i] == "nan":
            liste_datecommentaire_new.append("")
    for j in range(len(list_moisannee_commentaire)):
        if date_list_new[i] == list_moisannee_commentaire[j]:
            liste_datecommentaire_new.append(datecommentaire["ID_DATECOMMENTAIRE"][j])
df_commentaire_parc["Id_Datecommentaire"]= liste_datecommentaire_new
print(df_commentaire_parc)


# In[83]:


# on traite la colonne "dateSejour" du fichier parc:
parc["dateSejour"]= parc["dateSejour"].apply(lambda x: str(x).replace("déc.","decembre"))
parc["dateSejour"] = parc["dateSejour"].apply(lambda x: str(x).replace("nov.","novembre"))
parc["dateSejour"] = parc["dateSejour"].apply(lambda x: str(x).replace("oct.","octobre"))
parc["dateSejour"] = parc["dateSejour"].apply(lambda x: str(x).replace("sept.","septembre"))
parc["dateSejour"] = parc["dateSejour"].apply(lambda x: str(x).replace("juil.","juillet"))
parc["dateSejour"]= parc["dateSejour"].apply(lambda x: str(x).replace("avr.","avril"))
parc["dateSejour"] = parc["dateSejour"].apply(lambda x: str(x).replace("févr.","fevrier"))
parc["dateSejour"] = parc["dateSejour"].apply(lambda x: str(x).replace("août","aout"))
parc["dateSejour"] = parc["dateSejour"].apply(lambda x: str(x).replace("janv.","janvier"))

date_list_sejour_new = parc["dateSejour"].values.tolist()

date_list_sejour_new


# In[84]:


# on ajoute la colonne "id_datesejour" au dataframe df_commentaire_parc:

liste_datesejour_new=[]
for i in range(len(date_list_sejour_new)):
    if date_list_sejour_new[i] == "nan":
            liste_datesejour_new.append("")
    for j in range(len(list_moisannee_sejour)):
        if date_list_sejour_new[i] == list_moisannee_sejour[j]:
            liste_datesejour_new.append(datesejour["ID_DATESEJOUR"][j])
df_commentaire_parc["Id_Datesejour"]= liste_datesejour_new
print(df_commentaire_parc)


# In[85]:


# on ajoute la colonne "id_localisation" au dataframe df_commentaire_parc:

liste_localisation_new=[]
for i in range(len(liste_local_new)):
    if (liste_local_new[i] == ""):
        liste_localisation_new.append("")
    for j in range(len(localisation["LOCALISATION"])):
        if liste_local_new[i] == localisation["LOCALISATION"][j]:
            liste_localisation_new.append(localisation["ID_LOCALISATION"][j])
df_commentaire_parc["Id_Localisation"]= liste_localisation_new
print(df_commentaire_parc)


# In[86]:


# on ajoute la colonne "id_commentaire" au dataframe df_commentaire_parc:
liste_idcommentaire_parc=[]
for i in range(len(df_commentaire_parc.index)):
    liste_idcommentaire_parc.append("C_" + str(i+1))
df_commentaire_parc["Id_Commentaire"]= liste_idcommentaire_parc
print(df_commentaire_parc)


# In[95]:


# on ajoute la colonne "Titre" et la colonne "Commentaire" au dataframe df_commentaire_parc:

df_commentaire_parc["Titre"]= parc["titre"].tolist()
df_commentaire_parc["Commentaire"]= parc["commentaire"].tolist()

# on change la posistion des colonnes:
df_commentaire_parc = df_commentaire_parc[df_commentaire_parc.columns[[1,2,3,4,5,0,6,7]]]

print(df_commentaire_parc)


# In[ ]:


#transformer toutes les colonnes en type string:
for i in df_commentaire_parc:
    df_commentaire_parc[i] = df_commentaire_parc[i].astype(str)


# In[115]:


# Exporter la table "commentaire_parc" vers oracle:
s_commentaire_parc = "INSERT INTO commentaire_parc (Id_Commentaire, Id_Note, Id_Situation, Id_DateCommentaire,Id_DateSejour,Id_Localisation,Titre,Commentaire) VALUES (:1, :2, :3, :4, :5, :6, :7, :8)"
data_commentaire_parc = []
for line in df_commentaire_parc.values:
    data_commentaire_parc.append(line)

for line in data_commentaire_parc:
    cursor.execute(s_commentaire_parc, line)
con.commit() 


# In[ ]:


# nbr d'avis parcs = 62969 (16502 en français)

