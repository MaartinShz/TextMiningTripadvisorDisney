####################################################
#                      SCRAP                       #
# DEUX FONCTIONS CAR HOTEL ET PARC SONT DIFFÉRENTS #
#     CHAQUE FONCTION RENVOIE UN DICTIONNAIRE      #
####################################################



import requests
from bs4 import BeautifulSoup
import re
from datetime import timedelta
from date import trait_date
from datetime import date
import locale

# changement de la date et l'heure en FR
locale.setlocale(locale.LC_TIME,'fr_FR.utf8')



def scrap_parc(url:str) -> dict:


    dict_avis = {}
    i = 0

    dict_mois = {'janv.':'janvier', 'février':'fevrier', 'fev.':'fevrier', 'avr.':'avril', 'juil.':'juillet', 'août':'aout', 'sept.':'septembre','oct.':'octobre', 'nov.':'novembre', 'déc.':'decembre','décembre':'decembre', 'Dec':'decembre'}


    headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate',
            'accept-language': 'en,mr;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}
    

    req = requests.get(url,headers=headers,timeout=5)
    soup = BeautifulSoup(req.content, 'html.parser')  
    blocAvis = soup.find(attrs={"class" : "LbPSX"})

    try:
        site = soup.find('h1', attrs={'class':'biGQs _P fiohW eIegw'}).text
    except:
        site = None
    
    for x in blocAvis.findAll(attrs={"class" : "_c"}):
        i += 1
        try:
            titre = x.find(attrs={'class':'yCeTE'}).text
        except:
            titre = None
        try:
            name = x.find(attrs={'class':'BMQDV _F G- wSSLS SwZTJ FGwzt ukgoS'}).text
        except:
            name = None
        try:
            note = x.find(attrs={'class':'UctUV d H0'})['aria-label'][0]
        except:
            note= None
        try:
            date = x.find(attrs={'class':'RpeCd'}).text.split('•')[0]
            date = trait_date(date, dict_mois)
        except:
            date = None
        try:
            type_voyage = x.find(attrs={'class':'RpeCd'}).text.split('•')[1]
        except:
            type_voyage=None
        try:
            date_comm = re.search(r'\d+ .+ \d+',x.find(attrs={'class':'biGQs _P pZUbB ncFvv osNWb'}).text).group(0)
            if date_comm == 'Hier':
                date_comm = str((date.today() - timedelta(days = 1)).strftime("%d %b %Y"))
            elif date_comm == "Aujourd'hui":
                date_comm = str(date.today().strftime("%d %b %Y"))
            date_comm = trait_date(date_comm, dict_mois)
        except:
            date_comm = None
        try:
            situation = re.split(r'\d+', (x.find(attrs={'class':'biGQs _P pZUbB osNWb'}).text))[0]
        except:
            situation = None
        try:
            commentaire = x.find(attrs={'class':'biGQs _P pZUbB KxBGd'}).text
        except:
            commentaire = None

        if x.find(class_="ajoIU _S B-") is not None:
            photo = True
        else:
            photo = False

        try:
            url = blocAvis.find(class_="xkSty").find(class_="BrOJk u j z _F wSSLS tIqAi unMkR").get('href')
        except:
            url = None
        if url != None:
            url = "https://www.tripadvisor.fr" + url


        dict_avis[i] = {'Type':'Parc',
                        'Site':site,
                        'Auteur':name,
                        'Titre':titre,
                        'Note':note,
                        'Date_sejour':date,
                        'Type_voyage':type_voyage,
                        'Date_commentaire':date_comm,
                        'Localisation':situation,
                        'Commentaire':commentaire,
                        'Photo':photo
                        } 
    
    return dict_avis




def scrap_hotel(url:str) -> dict:

    dict_avis = {}
    i = 0

    dict_mois = {'janv.':'janvier', 'février':'fevrier', 'fev.':'fevrier', 'avr.':'avril', 'juil.':'juillet', 'août':'aout', 'sept.':'septembre','oct.':'octobre', 'nov.':'novembre', 'déc.':'decembre','décembre':'decembre', 'Dec':'decembre'}


    headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate',
            'accept-language': 'en,mr;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}

    req = requests.get(url,headers=headers,timeout=5)
    soup = BeautifulSoup(req.content, 'html.parser') 

    try :
        site = soup.find('h1',attrs={'class':'QdLfr b d Pn'}).text
    except :
        site = None

    blocAvis = soup.find(attrs={"data-test-target" : "reviews-tab"})
        
    for x in blocAvis.findAll(attrs={"class" : "YibKl MC R2 Gi z Z BB pBbQr"}):
        i += 1
        try :
            name = (x.find('a', attrs={'class':'ui_header_link uyyBf'})).text
        except :
            name = None
        try:
            #changer date sans accent et nom mois complet
            date_comm = re.search(r'\((.*?)\)',x.find(attrs={'class':'cRVSd'}).text).group(1)
            if str(date_comm) == 'Hier':
                date_comm = str((date.today() - timedelta(days = 1)).strftime("%d %b %Y"))
            elif str(date_comm) == "Aujourd'hui":
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
            date_travel = (x.find(attrs={'class':'teHYY _R Me S4 H3'}).text).split(':')[1]
            date_travel= trait_date(date_travel, dict_mois)
        except :
            date_travel = None
        if x.find(class_="pDrIj f z") is not None:
            photo = True
        else:
            photo = False
        


        dict_avis[i] = {'Type':'Hôtel',
                        'Site':site,
                        'Auteur':name,
                        'Titre':titre,
                        'Note':note,
                        'Date_sejour':date_travel,
                        'Date_commentaire':date_comm,
                        'Localisation':situation,
                        'Commentaire':commentaire,
                        'Photo':photo
                        } 
    
    return dict_avis



