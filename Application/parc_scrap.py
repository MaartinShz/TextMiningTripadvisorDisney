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
    typevoyage = []
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

                usersname.append(name)
                userscomments.append(commentaire)
                usersdatetrvl.append(date)
                userstitle.append(titre)
                usersnote.append(note)
                userdate_comm.append(date_comm)
                localisation.append(situation)
                sites.append(site)
                typevoyage.append(type_voyage)

                try:
                    your_driver.execute_script("window.scrollTo(0, 500);")
                except:
                    pass

                try:
                    WebDriverWait(your_driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[aria-label="Page suivante"]'))).click()
                except:
                    break
            
    df = pd.DataFrame({'Site':sites,
                    'Auteur':usersname,
                    'dateSejour':usersdatetrvl,
                    'typevoyage':type_voyage,
                    'dateComm':date_comm,
                    'Localisation':localisation,
                    'Note':usersnote,
                    'Titre':userstitle,
                    'Avis':userscomments})
    
    return df


