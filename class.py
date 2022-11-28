from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re


#Passer l'url de la page en object
class scraper(object):

    url = ''
    driver = webdriver.Chrome()

#Initialisation et ouverture de la page
    def __init__(self, scraper):
        self.url = scraper
        self.driver.get(self.url)
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-reject-all-handler"]'))).click()

#Récupération des avis
    def get_avis(self):

        reviews = self.driver.find_elements(By.CLASS_NAME,'reviewSelector')
        count = 1
        nb_avis = 0

        for r in reviews:
            count += 1
            nb_avis += 1
            auteur = ((r.find_element(By.CLASS_NAME, 'member_info').text).split('\n'))[0]
            date = (r.find_element(By.CLASS_NAME, 'ratingDate')).text
            titre = (r.find_element(By.CLASS_NAME, 'noQuotes')).text
            if len(r.find_elements(By.XPATH, '/html/body/div[2]/div[2]/div[2]/div[6]/div/div[1]/div[3]/div/div[5]/div/div['+str(count)+']/div[3]/div/div/div/div[2]/div[2]/div/p/span[1]')) > 0:
                commentaire = ((r.find_element(By.CLASS_NAME, 'partial_entry')).text).replace('...Plus', ' ') + (r.find_element(By.XPATH, '/html/body/div[2]/div[2]/div[2]/div[6]/div/div[1]/div[3]/div/div[5]/div/div['+str(count)+']/div[3]/div/div/div/div[2]/div[2]/div/p/span[1]')).get_attribute('innerHTML')
            else : commentaire = (r.find_element(By.CLASS_NAME, 'partial_entry')).text
        
            print(f"Avis numero {nb_avis}\nAuteur : {auteur}\nDate :\t{date}\nTitre :\t{titre}\nCommentaire :\t{commentaire}\n")
        
       




scraper('https://www.tripadvisor.fr/Restaurant_Review-g226865-d2095857-Reviews-Cowboy_Cookout_Barbecue-Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html').get_avis()
