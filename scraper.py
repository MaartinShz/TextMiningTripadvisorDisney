from bs4 import BeautifulSoup
import requests

#Tripadvisor Disney
url="https://www.tripadvisor.fr/Attraction_Review-g226865-d189258-Reviews-Disneyland_Paris-Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html"


headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'en,mr;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}
req = requests.get(url,headers=headers,timeout=5)
#print (req.status_code) # 200 -> OK

soup = BeautifulSoup(req.content, 'html.parser')
#print(soup.title)

#test : Récupérer Titre page :
#<h1 class="biGQs _P fiohW eIegw" data-automation="mainH1">Disneyland Paris</h1>
for x in soup.body.find_all(class_="biGQs _P fiohW eIegw"):
    print(x.text)