from bs4 import BeautifulSoup
import requests
############################################ Links
#Tripadvisor Disney Land Paris
url="https://www.tripadvisor.fr/Attraction_Review-g226865-d189258-Reviews-Disneyland_Paris-Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html"
#page2
#url="https://www.tripadvisor.fr/Attraction_Review-g226865-d189258-Reviews-or10-Disneyland_Paris-Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html"
#Parc Walt Disney Studios
#"https://www.tripadvisor.fr/Attraction_Review-g226865-d285990-Reviews-Walt_Disney_Studios_Park-Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html"

#Disney Hotel New York - The Art of Marvel
#"https://www.tripadvisor.fr/Hotel_Review-g1182377-d262678-Reviews-Disney_Hotel_New_York_The_Art_of_Marvel-Chessy_Marne_la_Vallee_Seine_et_Marne_Ile_de_F.html"

#Disney Newport Bay Club
#"https://www.tripadvisor.fr/Hotel_Review-g1182377-d262679-Reviews-Disney_Newport_Bay_Club-Chessy_Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html"

#Disney Sequoia Lodge
#"https://www.tripadvisor.fr/Hotel_Review-g5599092-d262682-Reviews-Disney_Sequoia_Lodge-Coupvray_Seine_et_Marne_Ile_de_France.html"

#Disney Hotel Cheyenne
#"https://www.tripadvisor.fr/Hotel_Review-g226865-d262686-Reviews-Disney_Hotel_Cheyenne-Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html"

#Disney's Hotel Santa Fe
#"https://www.tripadvisor.fr/Hotel_Review-g5599092-d262683-Reviews-Disney_Hotel_Santa_Fe-Coupvray_Seine_et_Marne_Ile_de_France.html"

#Disney Davy Crockett Ranch
#"https://www.tripadvisor.fr/Hotel_Review-g1221082-d564634-Reviews-Disney_Davy_Crockett_Ranch-Bailly_Romainvilliers_Seine_et_Marne_Ile_de_France.html"
############################################ Request 
headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'en,mr;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}



urls=["https://www.tripadvisor.fr/Attraction_Review-g226865-d189258-Reviews-Disneyland_Paris-Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html",
    "https://www.tripadvisor.fr/Attraction_Review-g226865-d285990-Reviews-Walt_Disney_Studios_Park-Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html",
    "https://www.tripadvisor.fr/Hotel_Review-g1182377-d262678-Reviews-Disney_Hotel_New_York_The_Art_of_Marvel-Chessy_Marne_la_Vallee_Seine_et_Marne_Ile_de_F.html",
    "https://www.tripadvisor.fr/Hotel_Review-g1182377-d262679-Reviews-Disney_Newport_Bay_Club-Chessy_Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html",
    "https://www.tripadvisor.fr/Hotel_Review-g5599092-d262682-Reviews-Disney_Sequoia_Lodge-Coupvray_Seine_et_Marne_Ile_de_France.html",
    "https://www.tripadvisor.fr/Hotel_Review-g226865-d262686-Reviews-Disney_Hotel_Cheyenne-Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html",
    "https://www.tripadvisor.fr/Hotel_Review-g5599092-d262683-Reviews-Disney_Hotel_Santa_Fe-Coupvray_Seine_et_Marne_Ile_de_France.html",
    "https://www.tripadvisor.fr/Hotel_Review-g1221082-d564634-Reviews-Disney_Davy_Crockett_Ranch-Bailly_Romainvilliers_Seine_et_Marne_Ile_de_France.html"
    ]
"""
for oneUrl in urls :
    req = requests.get(urls,headers=headers,timeout=5)
    if(req.status_code == 200):
        soup = BeautifulSoup(req.content, 'html.parser')
        for x in soup.body.find_all(class_="biGQs _P fiohW eIegw"):
            print(x.text)
"""





req = requests.get(url,headers=headers,timeout=5)

#print (req.status_code) # 200 -> OK

soup = BeautifulSoup(req.content, 'html.parser')


############################################ Scraping Result


blocAvis = soup.find(attrs={"class" : "LbPSX"})

# <div class="xkSty">


print(blocAvis.find(class_="xkSty").find(class_="BrOJk u j z _F wSSLS tIqAi unMkR")["href"])

for avis in blocAvis.findAll(attrs={"class" : "_c"}):
    
    pays = avis.find(class_="biGQs _P pZUbB osNWb").text #PAYS  attention champs à vérifier
    
    titre = avis.find(class_="biGQs _P fiohW qWPrE ncFvv fOtGX").text #titre commentaire
    
    note = int(avis.find(class_="UctUV d H0")["aria-label"][0]) #note commentaire
    
    commentaire = avis.find(class_="yCeTE").text #corps du commentaire
    
    dateSejour = avis.find(class_="RpeCd")#.text #date du séjour
    if(dateSejour is not None):
        sep= dateSejour.text.find("•")-1
        #situation = dateSejour.text[sep+2:] # avoir si utile dans analyse
        dateSejour = dateSejour.text[:sep]
    else:
        dateSejour = None
    
    dateCommentaire = avis.find(class_="biGQs _P pZUbB ncFvv osNWb").text #date du commentaire
    
    photo = avis.find(class_="ajoIU _S B-") #Présence de photo: oui/non
    if(photo is not None):
        photo = "Oui"
    else:
        photo = None

nextpage = blocAvis.find(class_="xkSty").find(class_="BrOJk u j z _F wSSLS tIqAi unMkR")["href"]