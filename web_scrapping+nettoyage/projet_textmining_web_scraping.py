#!/usr/bin/env python
# coding: utf-8

# In[18]:


# On import les packages nécessaires:
import pandas as pd
import numpy as np
import csv
import os
import re
import time
from unidecode import unidecode
from bs4 import BeautifulSoup
import requests


# In[2]:


urlHotel=["https://www.tripadvisor.fr/Hotel_Review-g1182377-d262678-Reviews-Disney_Hotel_New_York_The_Art_of_Marvel-Chessy_Marne_la_Vallee_Seine_et_Marne_Ile_de_F.html",
    "https://www.tripadvisor.fr/Hotel_Review-g1182377-d262679-Reviews-Disney_Newport_Bay_Club-Chessy_Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html",
    "https://www.tripadvisor.fr/Hotel_Review-g5599092-d262682-Reviews-Disney_Sequoia_Lodge-Coupvray_Seine_et_Marne_Ile_de_France.html",
    "https://www.tripadvisor.fr/Hotel_Review-g226865-d262686-Reviews-Disney_Hotel_Cheyenne-Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html",
    "https://www.tripadvisor.fr/Hotel_Review-g5599092-d262683-Reviews-Disney_Hotel_Santa_Fe-Coupvray_Seine_et_Marne_Ile_de_France.html",
    "https://www.tripadvisor.fr/Hotel_Review-g1221082-d564634-Reviews-Disney_Davy_Crockett_Ranch-Bailly_Romainvilliers_Seine_et_Marne_Ile_de_France.html"
    ]


# In[9]:


urlParc=["https://www.tripadvisor.fr/Attraction_Review-g226865-d189258-Reviews-Disneyland_Paris-Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html",
    "https://www.tripadvisor.fr/Attraction_Review-g226865-d285990-Reviews-Walt_Disney_Studios_Park-Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html"
    ]


# In[4]:


def trait_date(text,dictio):
    for key in dictio:
        text = text.replace(key, dictio[key]).strip()
    
    return text


# In[5]:


headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'en,mr;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}

exportAvis = []


# In[37]:


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
    while(i<10):
        req = requests.get(url,headers=headers,timeout=5)
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
        


# In[38]:


hotel = scrapHotel(urlHotel[0])
hotel.info()


# In[34]:


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
    while(i<10):#url is not None): # condition à changer vérifier date du commmentaire récupérer avec la date de commmentaire le plus récent  
        #time.sleep(3)
        req = requests.get(url,headers=headers,timeout=5)
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


# In[35]:


parc = scrapParc(urlParc[0])
parc.info()

