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



def scrap(url:str):
    
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

        


# def scraping_hotel(urls:list):

#     dict_mois = {'janv.':'janvier', 'février':'fevrier', 'fev.':'fevrier', 'avr.':'avril', 'juil.':'juillet', 'août':'aout', 'sept.':'septembre','oct.':'octobre', 'nov.':'novembre', 'déc.':'decembre','décembre':'decembre', 'Dec':'decembre'}
#     usersname= []
#     usersnote=[]
#     userstitle=[]
#     userscomments=[]
#     usersdatetrvl=[]
#     userdate_comm=[]
#     localisation = []   
#     sites = [] 
#     your_driver = driver()
#     urls = urls

#     for url in urls:

#         try:
#            your_driver.get(url)
#         except:
#             sys.exit(1)
            
#             # Reject cookies
#         try :
#             WebDriverWait(your_driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-reject-all-handler"]'))).click()
#             WebDriverWait(your_driver,20).until(EC.element_to_be_clickable((your_driver.find_element(By.CLASS_NAME, 'TnInx')))).click()
#         except :
#             pass

#         while(True):

#             time.sleep(1)

#             content =your_driver.page_source
#             soup = BeautifulSoup(content, "lxml")

#             try :
#                 site = soup.find('h1',attrs={'class':'QdLfr b d Pn'}).text
#             except :
#                 site = None

#             for x in soup.find_all(attrs={'class':'YibKl MC R2 Gi z Z BB pBbQr'}):
#                 #regarder si le id est unique
#                 # try:
#                 #     id_review = x.find(attrs={'class':'WAllg _T'})['data-reviewid']
#                 # except:
#                 #     id_review = None
#                 try :
#                     name = (x.find('a', attrs={'class':'ui_header_link uyyBf'})).text
#                 except :
#                     name = None
#                 try:
#                     #changer date sans accent et nom mois complet
#                     date_comm = re.search(r'\((.*?)\)',x.find(attrs={'class':'cRVSd'}).text).group(1)
#                     if date_comm == 'Hier':
#                         date_comm = str((date.today() - timedelta(days = 1)).strftime("%d %b %Y"))
#                     elif date_comm == "Aujourd'hui":
#                         date_comm = str(date.today().strftime("%d %b %Y"))
#                     date_comm = trait_date(date_comm, dict_mois)
#                 except:
#                     date_comm=None
#                 try :
#                     note = ((x.find(attrs={'class':'Hlmiy F1'})).find('span'))['class'][1][-2]
#                 except:
#                     note = None
#                 #Mettre ville et pays ensemble 
#                 try:
#                     situation = ((x.find(class_='default LXUOn small').text).replace(',',''))
#                 except:
#                     situation = None
#                 try:
#                     titre = x.find(attrs={'class':'KgQgP MC _S b S6 H5 _a'}).text
#                 except :
#                     titre = None
#                 try :
#                     commentaire = x.find(attrs={'class':'QewHA H4 _a'}).text
#                 except :
#                     commentaire = None
#                 try :
#                     #changer date sans accent et nom mois complet
#                     date_travel = (x.find(attrs={'class':'teHYY _R Me S4 H3'}).text).split(':')[1]
#                     date_travel= trait_date(date_travel, dict_mois)
#                 except :
#                     date_travel = None
                
#                 usersname.append(name)
#                 userscomments.append(commentaire)
#                 usersdatetrvl.append(date_travel)
#                 userstitle.append(titre)
#                 usersnote.append(note)
#                 userdate_comm.append(date_comm)
#                 localisation.append(situation)
#                 sites.append(site)

#                 try:
#                     your_driver.execute_script("window.scrollTo(0, 500);")
#                 except:
#                     pass


#             # Change page
#             try :
#                 WebDriverWait(your_driver,20).until(EC.element_to_be_clickable((your_driver.find_element(By.CSS_SELECTOR, 'a[class="ui_button nav next primary "')))).click()
#             except :
#                 break


#     df = pd.DataFrame({'Site':sites,
#                             'Auteur':usersname,
#                             'dateSejour':usersdatetrvl,
#                             'dateComm':userdate_comm,
#                             'Localisation':localisation,
#                             'Note':usersnote,
#                             'Titre':userstitle,
#                             'Avis':userscomments})

#     return df 