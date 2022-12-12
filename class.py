
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import pandas as pd
from selenium.webdriver.chrome.options import Options
import re
from datetime import date
from datetime import timedelta


class Scraping():

    def __init__(self, URLs:list, headless:bool=False):
        
        self.headless = headless
        self.URLs = URLs
        self.usersname= []
        self.usersnote=[]
        self.userscountry=[]
        self.userscity=[]
        self.userstitle=[]
        self.userscomments=[]
        self.usersdatetrvl=[]
        self.date_comm=[]
    

        if self.headless == True:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
        else :
            chrome_options=Options()
        self.driver = webdriver.Chrome(options=chrome_options)

        try:
            self.driver.get(self.URLs)
        except:
            sys.exit(1)
        try :
            WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-reject-all-handler"]'))).click()
            WebDriverWait(self.driver,20).until(EC.element_to_be_clickable((self.driver.find_element(By.CLASS_NAME, 'TnInx')))).click()
        except :
            pass
    
    def getavis(self):

        while(True):
            content = self.driver.page_source
            soup = BeautifulSoup(content)
            try :
                site = soup.find('h1',attrs={'class':'QdLfr b d Pn'}).text
            except :
                site = None
            for x in soup.find_all(attrs={'class':'YibKl MC R2 Gi z Z BB pBbQr'}):
                try :
                    name = (x.find('a', attrs={'class':'ui_header_link uyyBf'})).text
                except :
                    name = None
                try:
                    date_comm = re.search(r'\((.*?)\)',x.find(attrs={'class':'cRVSd'}).text).group(1)
                    if date_comm == 'Hier':
                        date_comm = str(date.today() - timedelta(days = 1))
                except:
                    date_comm=None
                try :
                    note = ((x.find(attrs={'class':'Hlmiy F1'})).find('span'))['class'][1][-2]
                except:
                    note = None
                try:
                    pays = ((x.find(attrs={'class':'RdTWF'})).text).split(',')[1]
                except:
                    pays = None
                try :
                    ville = ((x.find(attrs={'class':'RdTWF'})).text).split(',')[O]
                except:
                    ville = None
                try:
                    titre = x.find(attrs={'class':'KgQgP MC _S b S6 H5 _a'}).text
                except :
                    titre = None
                try :
                    commentaire = x.find(attrs={'class':'QewHA H4 _a'}).text
                except :
                    commentaire = None
                try :
                    date = (x.find(attrs={'class':'teHYY _R Me S4 H3'}).text).split(':')[1]
                except :
                    date = None
                
                self.usersname.append(name)
                self.userscity.append(ville)
                self.userscomments.append(commentaire)
                self.userscountry.append(pays)
                self.usersdatetrvl.append(date)
                self.userstitle.append(titre)
                self.usersnote.append(note)
                self.date_comm.append(date_comm)
                self.sites = site

            time.sleep(1)
                #print(f'Auteur :{name}\nPays :{pays}\nTitre :{titre}\nCommentaire :{commentaire}\nDate :{date}\n')
            try :
                WebDriverWait(self.driver,20).until(EC.element_to_be_clickable((self.driver.find_element(By.CSS_SELECTOR, 'a[class="ui_button nav next primary "')))).click()
            except :
                break

        
        self.df =  pd.DataFrame({'Site':self.sites,
                            'Auteur':self.usersname,
                            'Ville':self.userscity,
                            'Pays':self.userscountry,
                            'Note':self.usersnote,
                            'Titre':self.userstitle,
                            'Avis':self.userscomments})
        filename = './data_'+str(site)+'.csv'
        self.df.to_csv(filename,sep=';', encoding='UTF8')

    def attrs(self):
        for attribute, value in self.__dict__.items():
            print(attribute, '=', value)


# r=Scraping('https://www.tripadvisor.fr/Hotel_Review-g1221082-d564634-Reviews-Disney_Davy_Crockett_Ranch-Bailly_Romainvilliers_Seine_et_Marne_Ile_de_France.html', headless=True)
# r.getavis()


urls = (    #'https://www.tripadvisor.fr/Hotel_Review-g1221082-d564634-Reviews-Disney_Davy_Crockett_Ranch-Bailly_Romainvilliers_Seine_et_Marne_Ile_de_France.html',
            'https://www.tripadvisor.fr/Hotel_Review-g226865-d262686-Reviews-Disney_Hotel_Cheyenne-Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html',
            'https://www.tripadvisor.fr/Hotel_Review-g5599092-d262682-Reviews-Disney_Sequoia_Lodge-Coupvray_Seine_et_Marne_Ile_de_France.html')

for x in urls:
    r=Scraping(x, True)
    r.getavis()

