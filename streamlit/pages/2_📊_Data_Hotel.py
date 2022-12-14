# -*- coding: utf-8 -*-
"""
Created on Wed Dec 21 15:51:05 2022

@author: Christelle
"""

import streamlit as st
import time
import numpy as np
import cx_Oracle
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
    """Here we can update the comments of Internet users on the hotels of DisneyLand"""
)

### Connexion à Oracle
con = connect_to_database()
cursor = con.cursor()

# # Importer toutes les tables - dimensions¶

# In[5]:


#Importer la table 'note':
query_note = """SELECT* 
           FROM NOTE
           """
note = pd.read_sql(query_note, con=con)


# In[6]:


#Importer la table 'situation':
query_situation = """SELECT* 
           FROM SITUATION
           """
situation = pd.read_sql(query_situation, con=con)


# In[7]:


#Importer la table 'datecommentaire':
query_datecommentaire = """SELECT* 
           FROM DATECOMMENTAIRE
           """
datecommentaire = pd.read_sql(query_datecommentaire, con=con)


# In[8]:


# on crée une liste contenante mois et année en même temps:

list_moisannee_commentaire = []
list_moisannee_commentaire = datecommentaire["MOIS"] + " "+ datecommentaire["ANNÉE"]


# In[9]:


#Importer la table 'datesejour':
query_datesejour = """SELECT* 
           FROM DATESEJOUR
           """
datesejour = pd.read_sql(query_datesejour, con=con)


# In[10]:


# on crée une liste contenante mois et année en même temps:

list_moisannee_sejour = []
list_moisannee_sejour = datesejour["MOIS"] + " "+ datesejour["ANNÉE"]


# In[11]:


#Importer la table 'localisation':
query_localisation = """SELECT* 
           FROM LOCALISATION
           """
localisation = pd.read_sql(query_localisation, con=con)


# # Mise à jour datawarehouse pour les hôtels au cours du temps

# In[12]:


#Importer la table 'commentaire_hotel':
query_commentaire_hotel = """SELECT* 
           FROM COMMENTAIRE_HOTEL
           """
commentaire_hotel = pd.read_sql(query_commentaire_hotel, con=con)


# In[15]:


def trait_date(text,dictio):
    for key in dictio:
        text = text.replace(key, dictio[key]).strip()
    
    return text


# In[16]:


headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'en,mr;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}

exportAvis = []


# In[13]:


# Web scraping:
urlHotel=["https://www.tripadvisor.fr/Hotel_Review-g1182377-d262678-Reviews-Disney_Hotel_New_York_The_Art_of_Marvel-Chessy_Marne_la_Vallee_Seine_et_Marne_Ile_de_F.html",
    "https://www.tripadvisor.fr/Hotel_Review-g1182377-d262679-Reviews-Disney_Newport_Bay_Club-Chessy_Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html",
    "https://www.tripadvisor.fr/Hotel_Review-g5599092-d262682-Reviews-Disney_Sequoia_Lodge-Coupvray_Seine_et_Marne_Ile_de_France.html",
    "https://www.tripadvisor.fr/Hotel_Review-g226865-d262686-Reviews-Disney_Hotel_Cheyenne-Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html",
    "https://www.tripadvisor.fr/Hotel_Review-g5599092-d262683-Reviews-Disney_Hotel_Santa_Fe-Coupvray_Seine_et_Marne_Ile_de_France.html",
    "https://www.tripadvisor.fr/Hotel_Review-g1221082-d564634-Reviews-Disney_Davy_Crockett_Ranch-Bailly_Romainvilliers_Seine_et_Marne_Ile_de_France.html"
    ]

def scrapHotel(url):
    dict_mois = {'janv.':'janvier', 'février':'fevrier', 'févr.':'fevrier', 'avr.':'avril', 
                 'juil.':'juillet', 'août':'aout', 'sept.':'septembre','oct.':'octobre', 
                 'nov.':'novembre', 'déc.':'decembre','décembre':'decembre', 'Dec':'decembre'}
   
    usersnote=[]
    userstitle=[]
    userscomments=[]
    usersdatetrvl=[]
    userdate_comm=[]
    localisation = []   
 
    i=0  #compteur d'avis
    while(i<100):
        req = requests.get(url,headers=headers,timeout=100)
        soup = BeautifulSoup(req.content, 'html.parser')
        
        blocAvis = soup.find(attrs={"data-test-target" : "reviews-tab"})
        
        for avis in blocAvis.findAll(attrs={"class" : "YibKl MC R2 Gi z Z BB pBbQr"}):
            i = i + 1
            if(avis.find(class_="default LXUOn small") is not None):
                pays = unidecode((avis.find(class_="default LXUOn small").text).replace(',','').lower())
            else:
                pays = ""
            
            titre = avis.find(class_="KgQgP MC _S b S6 H5 _a").text #titre commentaire
            
            note = avis.find(class_= "Hlmiy F1").find("span")["class"][1][-2] #note commentaire 
            # récupère balise span qui a comme class avec la note 
            # la note est l'avant dernier caractère du nom de la classe 
            
            commentaire = avis.find(class_="fIrGe _T").text #corps du commentaire
            
            #date du séjour # separer date
            if(avis.find(class_="teHYY _R Me S4 H3") is not None):
                dateSejour = avis.find(class_="teHYY _R Me S4 H3").text[17:]
                dateSejour = trait_date(dateSejour, dict_mois)
            else:
                dateSejour = ""
           
            
            date_comm = avis.find(class_="cRVSd").text#date du commentaire # verif mois et année
            date_comm = date_comm[date_comm.find("(")+1:date_comm.find(")")]
            date_comm = trait_date(date_comm, dict_mois)
           
        try:
            url = "https://www.tripadvisor.fr"+blocAvis.find(class_="ui_button nav next primary")["href"]
        except:
            url = None

        ############################################ Export result
        
        userscomments.append(commentaire)
        usersdatetrvl.append(dateSejour)
        userstitle.append(titre)
        usersnote.append(note)
        userdate_comm.append(date_comm)
        localisation.append(pays)
        
        
    df = pd.DataFrame({
                            'dateSejour':usersdatetrvl,
                            'dateCommentaire':userdate_comm,
                            'pays':localisation,
                            'note':usersnote,
                            'titre':userstitle,
                            'commentaire':userscomments})

    return df 


# In[17]:


liste_df_hotel=[]
for i in urlHotel:
    res = scrapHotel(i)
    liste_df_hotel.append(res)
    
hotel = pd.concat(liste_df_hotel,ignore_index=True)


# In[18]:


# on vérifie s'il y a des nouveaux commentaires:
index_hotel = []
for j,y in enumerate(commentaire_hotel["COMMENTAIRE"].tolist()):
    for i, x in enumerate(hotel["commentaire"].tolist()):
        if (x==y) & (i not in index_hotel):
            index_hotel.append(i)


# In[19]:


#on enlève les commentaires qui existent déjà dans la dw:
hotel.drop(index=index_hotel,inplace=True)


# In[21]:


# on crée nouveaux "id_localisation" s'il y a des nouvelles localisations:

if len(hotel) > 0:
    df_local_new_hotel = pd.DataFrame()

    liste_localisation_new_hotel = []

    for j in hotel["pays"].tolist():
        if (j not in localisation["LOCALISATION"].tolist())&(j!='')&(j not in liste_localisation_new_hotel):
            liste_localisation_new_hotel.append(j)

    if len(liste_localisation_new_hotel)>0:
        df_local_new_hotel["localisation"] = liste_localisation_new_hotel

        liste_id_loca_new_hotel = []
        for k in range(len(df_local_new_hotel["localisation"])):
            l = len(localisation["LOCALISATION"])
            id = "L_" + str(l+k+1)
            liste_id_loca_new_hotel.append(id)
        df_local_new_hotel["id_localisation"] = liste_id_loca_new_hotel

        df_local_new_hotel = df_local_new_hotel[df_local_new_hotel.columns[[1,0]]]
    
        # Exporter des nouvelles valeurs de la table "localisation" vers oracle:
        cursor = con.cursor()

        s_loca = "INSERT INTO LOCALISATION(ID_LOCALISATION,LOCALISATION) VALUES(:1,:2)"
   
        data_loca_new_hotel = []
        for line in df_local_new_hotel.values:
            data_loca_new_hotel.append(line)
        
        for line in data_loca_new_hotel:
            cursor.execute(s_loca, line)
        con.commit()
    
        st.write("Il y a " + str(len(df_local_new_hotel)) + " nouvelles localisations")
        
        #Importer de nouveau la table 'localisation':
        query_localisation = """SELECT* 
           FROM LOCALISATION
           """
        localisation = pd.read_sql(query_localisation, con=con)
        
else:
   st.write("Il n'y a pas de nouvelle localisation")


# In[22]:


# fonction de création dataframe pour les nouveaux commentaires pour les hotels:
def df_avis_hotel(data):
    
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
        l = len(commentaire_hotel)
        liste_idcommentaire_new.append("C_" + str(l+j+1))
    df_commentaire_new["Id_Commentaire"]= liste_idcommentaire_new
    ###########################################
    
    # on ajoute la colonne "Titre" et la colonne "Commentaire" au dataframe df_commentaire_new:

    df_commentaire_new["Titre"]= data["titre"].tolist()
    df_commentaire_new["Commentaire"]= data["commentaire"].tolist()

    # on change la position des colonnes
    df_commentaire_new = df_commentaire_new[df_commentaire_new.columns[[4,0,1,2,3,5,6]]]

    return df_commentaire_new


# In[23]:


# on export les nouveaux commentaires s'il y en a:
if len(hotel) > 0:
    df_commentaire_new_hotel = df_avis_hotel(hotel).fillna("")
    # Exporter la table "commentaire_hotel" vers oracle:
    s_commentaire_hotel = "INSERT INTO commentaire_hotel (Id_Commentaire, Id_Note, Id_DateCommentaire,Id_DateSejour,Id_Localisation,Titre,Commentaire) VALUES (:1, :2, :3, :4, :5, :6, :7)"
    data_commentaire_hotel = []
    for line in df_commentaire_new_hotel.values:
        data_commentaire_hotel.append(line)

    for line in data_commentaire_hotel:
        cursor.execute(s_commentaire_hotel, line)
    con.commit()
    
    st.write("Il y a " +str(len(data_commentaire_hotel)) +" nouveaux commentaires")
    
else:
    st.write("Il n'y a pas de nouveau commentaire")


# Streamlit widgets automatically run the script from top to bottom. Since
# this button is not connected to any other logic, it just causes a plain
# rerun.
st.button("Re-run")

con.close()
