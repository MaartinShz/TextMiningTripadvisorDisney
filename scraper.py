from bs4 import BeautifulSoup
import requests
import csv

############################################ Links
urlsParc=["https://www.tripadvisor.fr/Attraction_Review-g226865-d189258-Reviews-Disneyland_Paris-Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html",
    "https://www.tripadvisor.fr/Attraction_Review-g226865-d285990-Reviews-Walt_Disney_Studios_Park-Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html"
    ]

urlHotel=["https://www.tripadvisor.fr/Hotel_Review-g1182377-d262678-Reviews-Disney_Hotel_New_York_The_Art_of_Marvel-Chessy_Marne_la_Vallee_Seine_et_Marne_Ile_de_F.html",
    "https://www.tripadvisor.fr/Hotel_Review-g1182377-d262679-Reviews-Disney_Newport_Bay_Club-Chessy_Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html",
    "https://www.tripadvisor.fr/Hotel_Review-g5599092-d262682-Reviews-Disney_Sequoia_Lodge-Coupvray_Seine_et_Marne_Ile_de_France.html",
    "https://www.tripadvisor.fr/Hotel_Review-g226865-d262686-Reviews-Disney_Hotel_Cheyenne-Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html",
    "https://www.tripadvisor.fr/Hotel_Review-g5599092-d262683-Reviews-Disney_Hotel_Santa_Fe-Coupvray_Seine_et_Marne_Ile_de_France.html",
    "https://www.tripadvisor.fr/Hotel_Review-g1221082-d564634-Reviews-Disney_Davy_Crockett_Ranch-Bailly_Romainvilliers_Seine_et_Marne_Ile_de_France.html"
    ]
############################################ Request

headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'en,mr;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}




exportAvis = []
############################################ Scraping Result For Parks
def scrapParc(url, export=False):
    i=0#compteur d'avis
    while(i<450):#url is not None): # condition à changer vérifier date du commmentaire récupérer avec la date de commmentaire le plus récent  
        #time.sleep(3)
        req = requests.get(url,headers=headers,timeout=5)
        #print (req.status_code) # 200 -> OK
        soup = BeautifulSoup(req.content, 'html.parser')  
        blocAvis = soup.find(attrs={"class" : "LbPSX"})
        
        #########################  Scrapping Avis
        for avis in blocAvis.findAll(attrs={"class" : "_c"}):
            i = i + 1
            pays = avis.find(class_="biGQs _P pZUbB osNWb").text #PAYS  attention champs à vérifier
            
            titre = avis.find(class_="biGQs _P fiohW qWPrE ncFvv fOtGX").text #titre commentaire
            
            note = int(avis.find(class_="UctUV d H0")["aria-label"][0]) #note commentaire
            
            commentaire = avis.find(attrs={'class':'biGQs _P pZUbB KxBGd'}).text #corps du commentaire
            
            dateSejour = avis.find(class_="RpeCd")#.text #date du séjour
            if(dateSejour is not None):
                sep= dateSejour.text.find("•")-1
                
                if(sep >0):
                    situation = dateSejour.text[sep+2:] # avoir si utile dans analyse
                    dateSejour = dateSejour.text[:sep]
                else:
                    dateSejour = dateSejour.text
                    situation = ""
            else:
                dateSejour = ""
                situation = ""
            
            dateCommentaire = avis.find(class_="biGQs _P pZUbB ncFvv osNWb").text[avis.find(class_="biGQs _P pZUbB ncFvv osNWb").text.find(" ",9)+1:] #date du commentaire
            
            photo = avis.find(class_="ajoIU _S B-") #Présence de photo: oui/non
            if(photo is not None):
                photo = True
            else:
                photo = False
                
            ### Enregistrement des données scrapper
            nomColonnes = ["pays", "titre", "note", "commentaire", "dateSejour", "situation", "dateCommentaire", "photo"]
            exportAvis.append([pays.replace(",",""), titre.replace(",",""), note, commentaire.replace(",",""), dateSejour, situation, dateCommentaire, photo])
            #print([pays, titre, note, commentaire, dateSejour, situation, dateCommentaire, photo])
            print(dateCommentaire)
            print(i)
        ######################### next Page
        try:
            url = "https://www.tripadvisor.fr"+blocAvis.find(class_="xkSty").find(class_="BrOJk u j z _F wSSLS tIqAi unMkR")["href"]
        except:
            url = None
        ############################################ Export result
        if(export):
            with open('exportAvisParc'+ soup.title.text.replace(" ","").replace(":","") +'.csv', 'w', encoding='utf-8', newline='') as f: 
                write = csv.writer(f)
                write.writerow(nomColonnes)
                write.writerows(exportAvis)
        ###########################################




############################################ Scraping Result For Hotel
def scrapHotel(url, export = False):
    i=0  #compteur d'avis
    while(i<100):
        req = requests.get(url,headers=headers,timeout=5)
        soup = BeautifulSoup(req.content, 'html.parser')
        
        blocAvis = soup.find(attrs={"data-test-target" : "reviews-tab"})
        
        for avis in blocAvis.findAll(attrs={"class" : "YibKl MC R2 Gi z Z BB pBbQr"}):
            i = i + 1
            if(avis.find(class_="default LXUOn small") is not None):
                pays = avis.find(class_="default LXUOn small").text 
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
            else:
                dateSejour = ""
            
            if(avis.find(class_="TDKzw _R Me") is not None):
                situation = avis.find(class_="TDKzw _R Me").text
            else:
                situation = ""
            
            dateCommentaire = avis.find(class_="cRVSd").text#date du commentaire # verif mois et année
            
            photo = avis.find(class_="pDrIj f z") #Présence de photo: oui/non 
            if(photo is not None):
                photo = True
            else:
                photo = False
                
            nomColonnes = ["pays", "titre", "note", "commentaire", "dateSejour", "situation", "dateCommentaire", "photo"]
            exportAvis.append([pays.replace(",",""), titre.replace(",",""), note, commentaire.replace(",",""), dateSejour, situation, dateCommentaire, photo])
            #print([pays, titre, note, commentaire, dateSejour, situation, dateCommentaire, photo])
            #print(dateCommentaire)
            print(i)
            
        try:
            url = "https://www.tripadvisor.fr"+blocAvis.find(class_="ui_button nav next primary")["href"]
        except:
            url = None

        ############################################ Export result
        if(export):
            with open('exportAvisHotel_'+ soup.title.text.replace(" ","").replace(":","") +'.csv', 'w', encoding='utf-8', newline='') as f: 
                write = csv.writer(f)
                write.writerow(nomColonnes)
                write.writerows(exportAvis)
        ###########################################
url="https://www.tripadvisor.fr/Attraction_Review-g226865-d189258-Reviews-Disneyland_Paris-Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html"
scrapParc(url, True)
#url="https://www.tripadvisor.fr/Hotel_Review-g1182377-d262678-Reviews-Disney_Hotel_New_York_The_Art_of_Marvel-Chessy_Marne_la_Vallee_Seine_et_Marne_Ile_de_F.html"
#scrapHotel(url, True)

