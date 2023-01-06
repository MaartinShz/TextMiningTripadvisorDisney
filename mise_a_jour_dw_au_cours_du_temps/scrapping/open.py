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

def scraping_hotel(urls:list):

    dict_mois = {'janv.':'janvier', 'février':'fevrier', 'fev.':'fevrier', 'avr.':'avril', 'juil.':'juillet', 'août':'aout', 'sept.':'septembre','oct.':'octobre', 'nov.':'novembre', 'déc.':'decembre','décembre':'decembre', 'Dec':'decembre'}
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
                    date = (x.find(attrs={'class':'teHYY _R Me S4 H3'}).text).split(':')[1]
                    date = trait_date(date, dict_mois)
                except :
                    date = None
                
                usersname.append(name)
                userscomments.append(commentaire)
                usersdatetrvl.append(date)
                userstitle.append(titre)
                usersnote.append(note)
                userdate_comm.append(date_comm)
                localisation.append(situation)
                sites.append(site)


            # Change page
            try :
                WebDriverWait(your_driver,20).until(EC.element_to_be_clickable((your_driver.find_element(By.CSS_SELECTOR, 'a[class="ui_button nav next primary "')))).click()
            except :
                break


    df = pd.DataFrame({'Site':sites,
                            'Auteur':usersname,
                            'dateSejour':usersdatetrvl,
                            'dateComm':date_comm,
                            'Localisation':localisation,
                            'Note':usersnote,
                            'Titre':userstitle,
                            'Avis':userscomments})

    return df  

def scraping_parc(urls:list):


    dict_mois = {'janv.':'janvier', 'février':'fevrier', 'fev.':'fevrier', 'avr.':'avril', 'juil.':'juillet', 'août':'aout', 'sept.':'septembre','oct.':'octobre', 'nov.':'novembre', 'déc.':'decembre','décembre':'decembre', 'Dec':'decembre'}
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
            #WebDriverWait(your_driver,20).until(EC.element_to_be_clickable((your_driver.find_element(By.CLASS_NAME, 'TnInx')))).click()
        except :
            pass

        while(True):

            time.sleep(1)

            content =your_driver.page_source
            soup = BeautifulSoup(content, "lxml")


            try:
                site = soup.find('h1', attrs={'class':'biGQs _P fiohW eIegw'}).text
            except:
                site = None

            for x in soup.find(attrs={'class':'LbPSX'}).find_all(attrs={'class':'_c'}):
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

                usersname.append(name)
                userscomments.append(commentaire)
                usersdatetrvl.append(date)
                userstitle.append(titre)
                usersnote.append(note)
                userdate_comm.append(date_comm)
                localisation.append(situation)
                sites.append(site)

            try:
                time.sleep(2)
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[aria-label="Page suivante"]'))).click()
            except:
                break
            
    df = pd.DataFrame({'Site':sites,
                    'Auteur':usersname,
                    'dateSejour':usersdatetrvl,
                    'dateComm':date_comm,
                    'Localisation':localisation,
                    'Note':usersnote,
                    'Titre':userstitle,
                    'Avis':userscomments})
    
    return df
                


