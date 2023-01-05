import oracledb
import asyncio
import time
from driver import driver
from date import trait_date
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
from bs4 import BeautifulSoup
from datetime import timedelta, date
import re
import pandas as pd
import requests


headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'en,mr;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}

dict_mois = {'janv.':'janvier', 'février':'fevrier', 'fev.':'fevrier', 'avr.':'avril', 'juil.':'juillet', 'août':'aout', 'sept.':'septembre','oct.':'octobre', 'nov.':'novembre', 'déc.':'decembre','décembre':'decembre', 'Dec':'decembre'}



async def scrap(url:str):
    
    titres = []
    req = requests.get(url,headers=headers,timeout=5)
    soup = BeautifulSoup(req.content, 'html.parser')
    
    blocAvis = soup.find(attrs={"data-test-target" : "reviews-tab"})
    
    for avis in blocAvis.findAll(attrs={"class" : "YibKl MC R2 Gi z Z BB pBbQr"}):
        try:
            location = ((avis.find(class_='default LXUOn small').text).replace(',',''))
        except:
            location = None
        
        titre = avis.find(class_="KgQgP MC _S b S6 H5 _a").text #titre commentaire
        
        note = avis.find(class_= "Hlmiy F1").find("span")["class"][1][-2] #note commentaire 
        # récupère balise span qui a comme class avec la note 
        # la note est l'avant dernier caractère du nom de la classe 
        
        commentaire = avis.find(class_="fIrGe _T").text #corps du commentaire
        
        #date du séjour # separer date
        try :
            #changer date sans accent et nom mois complet
            date_travel = (avis.find(attrs={'class':'teHYY _R Me S4 H3'}).text).split(':')[1]
            date_travel= trait_date(date_travel, dict_mois)
        except :
            date_travel = None
        
        if(avis.find(class_="TDKzw _R Me") is not None):
            situation = avis.find(class_="TDKzw _R Me").text[26:]
        else:
            situation = ""
        
        try:
            #changer date sans accent et nom mois complet
            date_comm = re.search(r'\((.*?)\)',avis.find(attrs={'class':'cRVSd'}).text).group(1)
            if date_comm == 'Hier':
                date_comm = str((date.today() - timedelta(days = 1)).strftime("%d %b %Y"))
            elif date_comm == "Aujourd'hui":
                date_comm = str(date.today().strftime("%d %b %Y"))
            date_comm = trait_date(date_comm, dict_mois)
        except:
            date_comm=None
        
        photo = avis.find(class_="pDrIj f z") #Présence de photo: oui/non 
        if(photo is not None):
            photo = True
        else:
            photo = False
        
        titres.append(titre)
    
    return(titres)
            


scrap("https://www.tripadvisor.fr/Hotel_Review-g1182377-d262678-Reviews-Disney_Hotel_New_York_The_Art_of_Marvel-Chessy_Marne_la_Vallee_Seine_et_Marne_Ile_de_F.html")

# oracledb.init_oracle_client()


test = {"1" : {"Auteur":"Benoit6287",
                "Titre":"Magnifiques souvenirs"},
        "2" : {"Auteur":"Snt",
                "Titre":"Le rêve pour les enfants"},
        "3" : {"Autuer":"aojfe",
                "Titre":"aofine"}
        }

i = 1

def check_comments_exists(titres:list):

    dsnStr = oracledb.makedsn("db-etu.univ-lyon2.fr", "1521", "DBETU")

    config = {"user":"m134",
              "password":"m134",
              "dsn" : dsnStr}


    con = oracledb.connect(user='m134',password='m134', dsn=dsnStr)
    cursor = con.cursor()


    # for value in reviews.values():
    #     titre = value['Titre']
    for titre in titres:
        if cursor.execute(f"select * from COMMENTAIRE_HOTEL where COMMENTAIRE_HOTEL.titre like '{titre}'").fetchone() != None:
            print(f'yes\t{titre}')
        else:
            print(f'no\t{titre}')






# async def give_review():
#     time.sleep(2)



async def main():
    result = await scrap("https://www.tripadvisor.fr/Hotel_Review-g1182377-d262678-Reviews-Disney_Hotel_New_York_The_Art_of_Marvel-Chessy_Marne_la_Vallee_Seine_et_Marne_Ile_de_F.html")
    check_comments_exists(result)


asyncio.run(main())
    
    
    

