#!/usr/bin/env python
# coding: utf-8

# # Web scraping hôtels

# In[2]:


#pip install driver
#pip install selenium
#pip install undetected_chromedriver


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
from datetime import timedelta, date


# In[96]:


def trait_date(text,dictio):
    for key in dictio:
        text = text.replace(key, dictio[key]).strip()
    
    return text


# In[97]:


from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc


def driver():

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = uc.Chrome(options=chrome_options)
    
    return driver


# In[16]:


def scraping_hotel(urls:list):

    dict_mois = {'janv.':'janvier', 'février':'fevrier', 'févr.':'fevrier', 'avr.':'avril', 
                 'juil.':'juillet', 'août':'aout', 'sept.':'septembre','oct.':'octobre', 
                 'nov.':'novembre', 'déc.':'decembre','décembre':'decembre', 'Dec':'decembre'}
    usersname= []
    usersnote=[]
    userstitle=[]
    userscomments=[]
    usersdatetrvl=[]
    userdate_comm=[]
    localisation = []   
    sites = [] 
    your_driver = driver()
    urls = urls

    for url in urls:

        try:
           your_driver.get(url)
        except:
            sys.exit(1)
            
            # Reject cookies
        try :
            WebDriverWait(your_driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-reject-all-handler"]'))).click()
            WebDriverWait(your_driver,20).until(EC.element_to_be_clickable((your_driver.find_element(By.CLASS_NAME, 'TnInx')))).click()
        except :
            pass

        while(True):

            time.sleep(1)

            content =your_driver.page_source
            soup = BeautifulSoup(content, "lxml")

            try :
                site = soup.find('h1',attrs={'class':'QdLfr b d Pn'}).text
            except :
                site = None

            for x in soup.find_all(attrs={'class':'YibKl MC R2 Gi z Z BB pBbQr'}):
                #regarder si le id est unique
                # try:
                #     id_review = x.find(attrs={'class':'WAllg _T'})['data-reviewid']
                # except:
                #     id_review = None
                try :
                    name = (x.find('a', attrs={'class':'ui_header_link uyyBf'})).text
                except :
                    name = None
                try:
                    #changer date sans accent et nom mois complet
                    date_comm = re.search(r'\((.*?)\)',x.find(attrs={'class':'cRVSd'}).text).group(1)
                    if date_comm == 'Hier':
                        date_comm = str((date.today() - timedelta(days = 1)).strftime("%d %b %Y"))
                    elif date_comm == "Aujourd'hui":
                        date_comm = str(date.today().strftime("%d %b %Y"))
                    date_comm = trait_date(date_comm, dict_mois)
                except:
                    date_comm=None
                try :
                    note = ((x.find(attrs={'class':'Hlmiy F1'})).find('span'))['class'][1][-2]
                except:
                    note = None
                #Mettre ville et pays ensemble 
                try:
                    situation = ((x.find(class_='default LXUOn small').text).replace(',',''))
                except:
                    situation = None
                try:
                    titre = x.find(attrs={'class':'KgQgP MC _S b S6 H5 _a'}).text
                except :
                    titre = None
                try :
                    commentaire = x.find(attrs={'class':'QewHA H4 _a'}).text
                except :
                    commentaire = None
                try :
                    #changer date sans accent et nom mois complet
                    date_travel = (x.find(attrs={'class':'teHYY _R Me S4 H3'}).text).split(':')[1]
                    date_travel= trait_date(date_travel, dict_mois)
                except :
                    date_travel = None
                
                usersname.append(name)
                userscomments.append(commentaire)
                usersdatetrvl.append(date_travel)
                userstitle.append(titre)
                usersnote.append(note)
                userdate_comm.append(date_comm)
                localisation.append(situation)
                sites.append(site)

                try:
                    your_driver.execute_script("window.scrollTo(0, 500);")
                except:
                    pass


            # Change page
            try :
                WebDriverWait(your_driver,20).until(EC.element_to_be_clickable((your_driver.find_element(By.CSS_SELECTOR, 'a[class="ui_button nav next primary "')))).click()
            except :
                break


    df = pd.DataFrame({'Site':sites,
                            'Auteur':usersname,
                            'dateSejour':usersdatetrvl,
                            'dateComm':userdate_comm,
                            'Localisation':localisation,
                            'Note':usersnote,
                            'Titre':userstitle,
                            'Avis':userscomments})

    return df 


# In[18]:


urlHotel=["https://www.tripadvisor.fr/Hotel_Review-g1182377-d262678-Reviews-Disney_Hotel_New_York_The_Art_of_Marvel-Chessy_Marne_la_Vallee_Seine_et_Marne_Ile_de_F.html",
    "https://www.tripadvisor.fr/Hotel_Review-g1182377-d262679-Reviews-Disney_Newport_Bay_Club-Chessy_Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html",
    "https://www.tripadvisor.fr/Hotel_Review-g5599092-d262682-Reviews-Disney_Sequoia_Lodge-Coupvray_Seine_et_Marne_Ile_de_France.html",
    "https://www.tripadvisor.fr/Hotel_Review-g226865-d262686-Reviews-Disney_Hotel_Cheyenne-Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html",
    "https://www.tripadvisor.fr/Hotel_Review-g5599092-d262683-Reviews-Disney_Hotel_Santa_Fe-Coupvray_Seine_et_Marne_Ile_de_France.html",
    "https://www.tripadvisor.fr/Hotel_Review-g1221082-d564634-Reviews-Disney_Davy_Crockett_Ranch-Bailly_Romainvilliers_Seine_et_Marne_Ile_de_France.html"
    ]


# In[20]:


hotel = scraping_hotel(urls=urlHotel)


# In[21]:


import os
os.chdir("/Users/dangnguyenviet/Desktop/Master 2 SISE/cours/M2 SISE - Text mining/projet Disney Land")
hotel.to_csv('hotel.csv', sep=";", encoding='utf-8', index=False)


# # Connexion python et oracle

# In[4]:


import cx_Oracle
cx_Oracle.init_oracle_client(lib_dir="/Users/dangnguyenviet/Desktop/Master 2 SISE/instantclient_19_8")


# In[5]:


dsnStr = cx_Oracle.makedsn("db-etu.univ-lyon2.fr", "1521", "DBETU")
print(dsnStr)


# In[6]:


con = cx_Oracle.connect(user="m134", password="m134", dsn=dsnStr)
cursor = con.cursor()


# # Construction DW pour les hotels

# In[ ]:


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


# In[ ]:


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


# In[27]:


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


# In[28]:


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


# In[7]:


#Importer la table 'note':
query_note = """SELECT* 
           FROM NOTE
           """
note = pd.read_sql(query_note, con=con)
print(note)


# In[8]:


#Importer la table 'situation':
query_situation = """SELECT* 
           FROM SITUATION
           """
situation = pd.read_sql(query_situation, con=con)
print(situation)


# In[9]:


#Importer la table 'datecommentaire':
query_datecommentaire = """SELECT* 
           FROM DATECOMMENTAIRE
           """
datecommentaire = pd.read_sql(query_datecommentaire, con=con)
print(datecommentaire)


# In[10]:


# on crée une liste contenante mois et année en même temps:

list_moisannee_commentaire = []
list_moisannee_commentaire = datecommentaire["MOIS"] + " "+ datecommentaire["ANNÉE"]
list_moisannee_commentaire


# In[11]:


#Importer la table 'datesejour':
query_datesejour = """SELECT* 
           FROM DATESEJOUR
           """
datesejour = pd.read_sql(query_datesejour, con=con)
print(datesejour)


# In[12]:


# on crée une liste contenante mois et année en même temps:

list_moisannee_sejour = []
list_moisannee_sejour = datesejour["MOIS"] + " "+ datesejour["ANNÉE"]
list_moisannee_sejour


# In[13]:


#os.chdir("/Users/dangnguyenviet/Desktop/Master 2 SISE/cours/M2 SISE - Text mining/projet Disney Land")
#hotel = pd.read_table("hotel.csv",sep=";",header=0)
#hotel.info()


# In[71]:


# on transforme la colonne "localisation" en liste, on met tout en minuscule et on enlève les accents:
liste_local = hotel["Localisation"].dropna().tolist()
liste_local = [unidecode(str(i).lower()) for i in liste_local]

# on élimine les chiffres:
liste_local1 = []
for i in liste_local:
    for c in i:
        if c.isdigit():
            liste_local1.append("")
            break
        else:
            liste_local1.append(i)

#créer un dataframe contenant l'identifiant pour chaque localisation:
df_local = pd.DataFrame()

# créer la colonne "localisation"           
liste_loca = []       
for i in liste_local1:
    if i not in liste_loca :
        liste_loca.append(i)
    
df_local["localisation"] = liste_loca

# créer la colonne "id_localisation"
liste_id_loca = []
for j in range(len(df_local["localisation"])):
    id = "L_" + str(j+1)
    liste_id_loca.append(id)
df_local["id_localisation"] = liste_id_loca

# on change la position des colonnes:
df_local = df_local[df_local.columns[[1,0]]]
print(df_local)


# In[72]:


# Exporter la table "localisation" vers oracle:
cursor = con.cursor()

s_loca = "INSERT INTO LOCALISATION(ID_LOCALISATION,LOCALISATION) VALUES(:1,:2)"


data_loca = []
for line in df_local.values:
        data_loca.append(line)
        
for line in data_loca:
    cursor.execute(s_loca, line)
con.commit()


# In[14]:


# créer un dataframe vide nommé df_commentaire_hotel:
df_commentaire_hotel = pd.DataFrame()


# In[17]:


# on ajoute la colonne "Id_Note" au dataframe df_commentaire_hotel:

liste_note_hotel=[]
for i in range(len(hotel["Note"])):
    if hotel["Note"][i] == None:
            liste_note_hotel.append("")
    for j in range(len(note["NOTE"])):
        if hotel["Note"][i] == note["NOTE"].astype(int)[j]:
            liste_note_hotel.append(note["ID_NOTE"][j])
df_commentaire_hotel["Id_Note"]= liste_note_hotel
print(df_commentaire_hotel)


# In[18]:


# on transforme la colonne "dateComm" en liste
date_comm_hotel = hotel["dateComm"].tolist()

# on ajoute la colonne "id_datecommentaire" au dataframe df_commentaire_hotel:

liste_datecommentaire_hotel=[]
for i in range(len(date_comm_hotel)):
    if date_comm_hotel[i] not in list_moisannee_commentaire:
        for c in date_comm_hotel[i]:
            if c.isdigit():
                liste_datecommentaire_hotel.append("DC_03")
            break
        
    for j in range(len(list_moisannee_commentaire)):
        if (date_comm_hotel[i] == list_moisannee_commentaire[j]) & (date_comm_hotel[i] != ""):
            liste_datecommentaire_hotel.append(datecommentaire["ID_DATECOMMENTAIRE"][j])
    
df_commentaire_hotel["Id_Datecommentaire"]= liste_datecommentaire_hotel
print(df_commentaire_hotel)


# In[55]:


# on transforme la colonne "dateSejour" en liste
date_sejour_hotel = hotel["dateSejour"].fillna("")

# on ajoute la colonne "id_datesejour" au dataframe df_commentaire_hotel:
liste_datesejour_hotel=[]
for i in range(len(date_sejour_hotel)):
    if date_sejour_hotel[i] == "":
            liste_datesejour_hotel.append("")
    for j in range(len(list_moisannee_sejour)):
        if date_sejour_hotel[i] == list_moisannee_sejour[j]:
            liste_datesejour_hotel.append(datesejour["ID_DATESEJOUR"][j])
df_commentaire_hotel["Id_Datesejour"]= liste_datesejour_hotel
print(df_commentaire_hotel)


# In[73]:


#Importer de nouveau la table 'localisation':
query_localisation = """SELECT* 
           FROM LOCALISATION
           """
localisation = pd.read_sql(query_localisation, con=con)
print(localisation)


# In[89]:


# traitement pour la colonne "Localisation" du dataframe "hotel": on enlève les accents et on met tout en minuscule
liste_local_hotel = hotel["Localisation"].tolist()
liste_local_hotel = [unidecode(str(i).lower()) for i in liste_local_hotel]

# on élimine les chiffres:
liste_local_hotel1 = []
for i in liste_local_hotel:
    if i =="nan":
        liste_local_hotel1.append("")
    elif i != "nan":
        for c in i:
            if c.isdigit():
                liste_local_hotel1.append("")
                break
        else:
            liste_local_hotel1.append(i)
            
# on ajoute la colonne "id_localisation" au dataframe df_commentaire_hotel:           
liste_localisation_hotel = []
for i in range(len(liste_local_hotel1)):
    if liste_local_hotel1[i] == "":
            liste_localisation_hotel.append("")
    for j in range(len(localisation["LOCALISATION"])):
        if liste_local_hotel1[i] == localisation["LOCALISATION"][j]:
            liste_localisation_hotel.append(localisation["ID_LOCALISATION"][j])
                                        
df_commentaire_hotel["Id_Localisation"]= liste_localisation_hotel
print(df_commentaire_hotel)


# In[90]:


# on ajoute la colonne "id_commentaire" au dataframe df_commentaire_hotel:
liste_idcommentaire_hotel=[]
for i in range(len(df_commentaire_hotel.index)):
    liste_idcommentaire_hotel.append("C_" + str(i+1))
df_commentaire_hotel["Id_Commentaire"]= liste_idcommentaire_hotel
print(df_commentaire_hotel)


# In[91]:


# on ajoute la colonne "Titre" et la colonne "Commentaire" au dataframe df_commentaire_hotel:

df_commentaire_hotel["Titre"]= hotel["Titre"]
df_commentaire_hotel["Commentaire"]= hotel["Avis"]

df_commentaire_hotel = df_commentaire_hotel[df_commentaire_hotel.columns[[4,0,1,2,3,5,6]]]

print(df_commentaire_hotel)


# In[92]:


# Exporter des nouvelles valeurs de la table "commentaire_hotel" vers oracle:
s_commentaire_hotel = "INSERT INTO commentaire_hotel (Id_Commentaire, Id_Note, Id_DateCommentaire,Id_DateSejour,Id_Localisation,Titre,Commentaire) VALUES (:1, :2, :3, :4, :5, :6, :7)"
data_commentaire_hotel = []
for line in df_commentaire_hotel.values:
    data_commentaire_hotel.append(line)

for line in data_commentaire_hotel:
    cursor.execute(s_commentaire_hotel, line)
con.commit()


# In[ ]:


# nbr d'avis hotel = 51454 (21006 en français)

