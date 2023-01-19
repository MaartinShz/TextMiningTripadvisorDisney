# -*- coding: utf-8 -*-
"""
Created on Wed Dec 21 15:51:05 2022

@author: Christelle
"""

import streamlit as st
import time
import numpy as np
import oracledb
import pandas as pd
import csv
import os
import re
from unidecode import unidecode
import requests
from bs4 import BeautifulSoup
from connexion_Oracle import connect_to_database
st.set_page_config(page_title="Updating the data warehouse", page_icon="📈")

st.markdown("# Updating the data warehouse")
st.sidebar.header("Updating the data warehouse")
st.write(
    """Here we can update the comments of Internet users on the parks of DisneyLand"""
)



### Connexion à Oracle
con = connect_to_database()
#cursor = con.cursor()
# # Importer toutes les tables - dimensions


#Importer la table 'note':
query_note = "SELECT * FROM NOTE"
note = pd.read_sql(query_note, con=con)


# In[5]:


#Importer la table 'situation':
query_situation = "SELECT * FROM SITUATION"
situation = pd.read_sql(query_situation, con=con)


# In[6]:


#Importer la table 'datecommentaire':
query_datecommentaire = "SELECT * FROM DATECOMMENTAIRE"
datecommentaire = pd.read_sql(query_datecommentaire, con=con)


# In[7]:


# on crée une liste contenante mois et année en même temps:

list_moisannee_commentaire = []
list_moisannee_commentaire = datecommentaire["MOIS"] + " "+ datecommentaire["ANNÉE"]


# In[8]:


#Importer la table 'datesejour':
query_datesejour = "SELECT * FROM DATESEJOUR"
datesejour = pd.read_sql(query_datesejour, con=con)


# In[9]:


# on crée une liste contenante mois et année en même temps:

list_moisannee_sejour = []
list_moisannee_sejour = datesejour["MOIS"] + " "+ datesejour["ANNÉE"]


# In[10]:


#Importer la table 'localisation':
query_localisation = "SELECT * FROM LOCALISATION"
localisation = pd.read_sql(query_localisation, con=con)


# # Mise à jour datawarehouse pour les parcs au cours du temps 

# In[14]:


#Importer la table 'commentaire_parc':
query_commentaire_parc = "SELECT * FROM COMMENTAIRE_PARC"
commentaire_parc = pd.read_sql(query_commentaire_parc, con=con)


# In[15]:


# on transforme la colonne "Commentaire" en type string:
commentaire_parc["COMMENTAIRE"] = commentaire_parc["COMMENTAIRE"].astype(str)


# In[16]:


def trait_date(text,dictio):
    for key in dictio:
        text = text.replace(key, dictio[key]).strip()
    
    return text


# In[17]:


headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'en,mr;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}

exportAvis = []


# In[21]:


# Web scraping:
urlParc=["https://www.tripadvisor.fr/Attraction_Review-g226865-d189258-Reviews-Disneyland_Paris-Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html",
    "https://www.tripadvisor.fr/Attraction_Review-g226865-d285990-Reviews-Walt_Disney_Studios_Park-Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html"
    ]

def scrapParc(url):
    
    dict_mois = {'janv.':'janvier', 'février':'fevrier', 'févr.':'fevrier', 'avr.':'avril', 
                 'juil.':'juillet', 'août':'aout', 'sept.':'septembre','oct.':'octobre', 
                 'nov.':'novembre', 'déc.':'decembre','décembre':'decembre', 'Dec':'decembre'}
   
    usersnote=[]
    userstitle=[]
    userscomments=[]
    usersdatetrvl=[]
    userdate_comm=[]
    localisation = [] 
    usersituation = []
    
    i=0#compteur d'avis
    while(i<100):#url is not None): # condition à changer vérifier date du commmentaire récupérer avec la date de commmentaire le plus récent  
        #time.sleep(3)
        req = requests.get(url,headers=headers,timeout=100)
        #print (req.status_code) # 200 -> OK
        soup = BeautifulSoup(req.content, 'html.parser')  
        blocAvis = soup.find(attrs={"class" : "LbPSX"})
        
        #########################  Scrapping Avis
        for avis in blocAvis.findAll(attrs={"class" : "_c"}):
            i = i + 1
            pays = avis.find(class_="biGQs _P pZUbB osNWb").text #PAYS  attention champs à vérifier
            # on extrait la localisation :
            temp = 0
            for c in pays :
                if c.isdigit():
                    temp = pays.index(c)
                    break
            pays = unidecode((pays[:temp]).lower().replace(',',''))
            
            titre = avis.find(class_="biGQs _P fiohW qWPrE ncFvv fOtGX").text #titre commentaire
            
            note = int(avis.find(class_="UctUV d H0")["aria-label"][0]) #note commentaire
            
            commentaire = avis.find(attrs={'class':'biGQs _P pZUbB KxBGd'}).text #corps du commentaire
            
            dateSejour = avis.find(class_="RpeCd")#.text #date du séjour
            if(dateSejour is not None):
                sep= dateSejour.text.find("•")-1
                
                if(sep >0):
                    situation = (dateSejour.text[sep+2:]).strip() # avoir si utile dans analyse
                    dateSejour = dateSejour.text[:sep]
                else:
                    dateSejour = dateSejour.text
                    situation = ""
                dateSejour = trait_date(dateSejour, dict_mois)
            else:
                dateSejour = ""
                situation = ""
            
            dateCommentaire = avis.find(class_="biGQs _P pZUbB ncFvv osNWb").text[avis.find(class_="biGQs _P pZUbB ncFvv osNWb").text.find(" ",9)+1:] #date du commentaire
            dateCommentaire = trait_date(dateCommentaire, dict_mois)
            
            
        ######################### next Page
        try:
            url = "https://www.tripadvisor.fr"+blocAvis.find(class_="xkSty").find(class_="BrOJk u j z _F wSSLS tIqAi unMkR")["href"]
        except:
            url = None
        ############################################ Export result
        
        userscomments.append(commentaire)
        usersdatetrvl.append(dateSejour)
        userstitle.append(titre)
        usersnote.append(note)
        userdate_comm.append(dateCommentaire)
        localisation.append(pays)
        usersituation.append(situation)
        
    df = pd.DataFrame({
                            'dateSejour':usersdatetrvl,
                            'dateCommentaire':userdate_comm,
                            'pays':localisation,
                            'note':usersnote,
                            'titre':userstitle,
                            'commentaire':userscomments,
                            'situation':situation})

    return df 


# In[22]:


liste_df_parc=[]
for i in urlParc:
    res = scrapParc(i)
    liste_df_parc.append(res)
    
parc = pd.concat(liste_df_parc,ignore_index=True)


# In[24]:


# on vérifie s'il y a des nouveaux commentaires:
index_parc = []
for j,y in enumerate(commentaire_parc["COMMENTAIRE"].tolist()):
    for i, x in enumerate(parc["commentaire"].tolist()):
        if (x==y) & (i not in index_parc):
            index_parc.append(i)


# In[25]:


#on enlève les commentaires qui existent déjà dans la dw:
parc.drop(index=index_parc,inplace=True)


# In[27]:


# on crée nouveaux "id_localisation" s'il y a des nouvelles localisations:

if len(parc) > 0:
    df_local_new = pd.DataFrame()

    liste_localisation_new = []

    for j in parc["pays"].tolist():
        if (j not in localisation["LOCALISATION"].tolist())&(j!='')&(j not in liste_localisation_new):
            liste_localisation_new.append(j)

    if len(liste_localisation_new)>0:
        df_local_new["localisation"] = liste_localisation_new

        liste_id_loca_new = []
        for k in range(len(df_local_new["localisation"])):
            l = len(localisation["LOCALISATION"])
            id = "L_" + str(l+k+1)
            liste_id_loca_new.append(id)
        df_local_new["id_localisation"] = liste_id_loca_new 

        df_local_new = df_local_new[df_local_new.columns[[1,0]]]
    
        # Exporter des nouvelles valeurs de la table "localisation" vers oracle:
        cursor = con.cursor()

        s_loca = "INSERT INTO LOCALISATION(ID_LOCALISATION,LOCALISATION) VALUES(:1,:2)"
   
        data_loca_new = []
        for line in df_local_new.values:
            data_loca_new.append(line)
        
        for line in data_loca_new:
            cursor.execute(s_loca, line)
        con.commit()
        
        #Importer de nouveau la table 'localisation':
        query_localisation = "SELECT * FROM LOCALISATION"
        localisation = pd.read_sql(query_localisation, con=con) 
else:
    st.write("Il n'y a pas de nouvelle localisation")


# In[28]:


# fonction de création dataframe pour les nouveaux commentaires pour les parcs:
def df_avis_parc(data):
    
    # créer un dataframe vide nommé df_commentaire_new:
    df_commentaire_new = pd.DataFrame()
    
    # on ajoute la colonne "Id_Note" au dataframe df_commentaire_new:

    liste_note_new=[]
    for i in range(len(data["note"])):
        if data["note"].tolist()[i] == "":
            liste_note_new.append("")
        for j in range(len(note["NOTE"])):
            if data["note"].tolist()[i] == note["NOTE"].astype(int)[j]:
                liste_note_new.append(note["ID_NOTE"][j])
    df_commentaire_new["Id_Note"]= liste_note_new
    ###########################################
    # on ajoute la colonne "Id_Situation" au dataframe df_commentaire_new:

    liste_situation_new =[]
    for i in range(len(data["situation"])):
        if data["situation"].tolist()[i] == "":
            liste_situation_new.append("")
        for j in range(len(situation["SITUATION"])):
            if data["situation"].tolist()[i] == situation["SITUATION"].tolist()[j]:
                liste_situation_new.append(situation["ID_SITUATION"][j])

    df_commentaire_new["Id_Situation"]= liste_situation_new
    ###########################################
    # on ajoute la colonne "id_datecommentaire" au dataframe df_commentaire_new:

    liste_datecommentaire_new=[]
    for i in range(len(data["dateCommentaire"])):
        if data["dateCommentaire"].tolist()[i] == "":
            liste_datecommentaire_new.append("")
        for j in range(len(list_moisannee_commentaire)):
            if data["dateCommentaire"].tolist()[i] == list_moisannee_commentaire[j]:
                liste_datecommentaire_new.append(datecommentaire["ID_DATECOMMENTAIRE"][j])
    df_commentaire_new["Id_Datecommentaire"]= liste_datecommentaire_new
    ###########################################
    # on ajoute la colonne "id_datesejour" au dataframe df_commentaire_new:

    liste_datesejour_new=[]
    for i in range(len(data["dateSejour"])):
        if data["dateSejour"].tolist()[i] == "":
            liste_datesejour_new.append("")
        for j in range(len(list_moisannee_sejour)):
            if data["dateSejour"].tolist()[i] == list_moisannee_sejour[j]:
                liste_datesejour_new.append(datesejour["ID_DATESEJOUR"][j])
    df_commentaire_new["Id_Datesejour"]= liste_datesejour_new
    ###########################################
    
    # on ajoute la colonne "id_localisation" au dataframe df_commentaire_new:

    liste_localisation_new=[]
    for i in range(len(data["pays"])):
        if (data["pays"].tolist()[i] == ""):
            liste_localisation_new.append("")
        for j in range(len(localisation["LOCALISATION"])):
            if data["pays"].tolist()[i] == localisation["LOCALISATION"][j]:
                liste_localisation_new.append(localisation["ID_LOCALISATION"][j])
    df_commentaire_new["Id_Localisation"]= liste_localisation_new
    ###########################################
    
    # on ajoute la colonne "id_commentaire" au dataframe df_commentaire_new:
    liste_idcommentaire_new=[]
    for j in range(len(df_commentaire_new.index)):
        l = len(commentaire_parc)
        liste_idcommentaire_new.append("C_" + str(l+j+1))
    df_commentaire_new["Id_Commentaire"]= liste_idcommentaire_new
    ###########################################
    
    # on ajoute la colonne "Titre" et la colonne "Commentaire" au dataframe df_commentaire_new:

    df_commentaire_new["Titre"]= data["titre"].tolist()
    df_commentaire_new["Commentaire"]= data["commentaire"].tolist()

    # on change la position des colonnes
    df_commentaire_new = df_commentaire_new[df_commentaire_new.columns[[5,0,1,2,3,4,6,7]]]

    return df_commentaire_new


# In[29]:


# on export les nouveaux commentaires s'il y en a:
if len(parc) > 0:
    df_commentaire_new = df_avis_parc(parc).fillna("")
    # Exporter la table "commentaire_parc" vers oracle:
    s_commentaire_parc = "INSERT INTO commentaire_parc (Id_Commentaire, Id_Note, Id_Situation, Id_DateCommentaire,Id_DateSejour,Id_Localisation,Titre,Commentaire) VALUES (:1, :2, :3, :4, :5, :6, :7, :8)"
    data_commentaire_parc = []
    for line in df_commentaire_new.values:
        data_commentaire_parc.append(line)

    for line in data_commentaire_parc:
        cursor.execute(s_commentaire_parc, line)
    con.commit()
    
    st.write("Il y a " +str(len(data_commentaire_parc)) +" nouveaux commentaires")
    
else:
    st.write("Il n'y a pas de nouveau commentaire")
    
st.button("Re-run")

con.close()
