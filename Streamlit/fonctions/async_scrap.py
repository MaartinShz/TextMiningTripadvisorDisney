import aiohttp, asyncio, cchardet, re, streamlit as st
from bs4 import BeautifulSoup
from multiprocessing import *
import locale
from datetime import *
from pymongo import MongoClient

locale.setlocale(locale.LC_TIME,'fr_FR.utf8')

dict_mois = {'janv.':'janvier', 'février':'fevrier', 'fev.':'fevrier', 'avr.':'avril', 'juil.':'juillet', 'août':'aout', 'sept.':'septembre','oct.':'octobre', 'nov.':'novembre', 'déc.':'decembre','décembre':'decembre', 'Dec':'decembre'}
today = date.today()

def trait_date(text,dictio):
    for key in dictio:
        text = text.replace(key, dictio[key]).strip()
    
    return text

headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0"}


async def fetch_page(session, url):
    async with session.get(url, headers = headers) as r:
        return await r.text()

async def fetch_urls(session, urls):
    tasks = []
    for url in urls:
        task = asyncio.create_task(fetch_page(session, url))
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results


async def main(urls):
    async with aiohttp.ClientSession() as session:
        data = await fetch_urls(session=session, urls=urls)
        return data

def get_urls_parc(contents):
    links = []
    avis = []
    for html in contents:
        soup = BeautifulSoup(html, 'lxml')
        if soup.find("a", {'aria-label':'Page suivante'}):
            links.append('https://tripadvisor.fr'+soup.find("a", {'aria-label':'Page suivante'})['href'])
        else:
            pass
        dict_avis = {}
        i = 0

        if soup.find(attrs={"class" : "LbPSX"}):
            blocAvis = soup.find(attrs={"class":"LbPSX"})
        else:
            break

        try:
            site = soup.find('h1', attrs={'class':'biGQs _P fiohW eIegw'}).text
        except:
            site = None

        for x in blocAvis.findAll(attrs={"class" : "_c"}):
            i+=1
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
                date_voyage= x.find(attrs={'class':'RpeCd'}).text.split('•')[0]
                date_voyage = trait_date(date_voyage, dict_mois)
            except:
                date_voyage = None
            if date_voyage is not None:
                if re.fullmatch(r'\d{2} [Aa-zZ]*', date_voyage):
                    date_voyage = f'{date_voyage} {today.year}'
            try:
                type_voyage = x.find(attrs={'class':'RpeCd'}).text.split('•')[1]
            except:
                type_voyage=None
            try:
                date_comm = (x.find(attrs={'class':'TreSq'}).find(attrs={'class':'biGQs _P pZUbB ncFvv osNWb'})).text
                date_comm = re.search(r'\d+ .* \d+', date_comm).group(0)
                if date_comm == 'Hier':
                    date_comm = str((today - timedelta(days = 1)).strftime("%d %b %Y"))
                elif date_comm == "Aujourd'hui":
                    date_comm = str(today.strftime("%d %b %Y"))
                date_comm = trait_date(date_comm, dict_mois)
            except:
                date_comm = None
            if date_comm is not None:
                if re.fullmatch(r'\d{2} [Aa-zZ]*', date_comm):
                    date_comm = f'{date_comm} {today.year}'
            try:
                annee_com = date_comm.split(' ')[-1]
                mois_comm = date_comm.split(' ')[-2]
            except:
                annee_com = None
                mois_comm = None
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

            dict_avis[i] = {'Type':'Parc',
                            'Site':site,
                            'Auteur':name,
                            'Situation':type_voyage,
                            'Localisation':situation,
                            'Date_commentaire':date_comm,
                            'Annee_commentaire':annee_com,
                            'Mois_commentaire':mois_comm,
                            'Date_voyage':date_voyage,
                            'Titre': titre,
                            'Note':note,
                            'Commentaire':commentaire,
                            'Photo':photo}
        avis.append(dict_avis)
    return avis, links

def get_urls_hotel(contents):
    links = []
    avis = []
    for html in contents:

        soup = BeautifulSoup(html, 'lxml')
        
        if soup.find("a", {'class':'ui_button nav next primary'}):
            links.append('https://tripadvisor.fr'+soup.find("a", {'class':'ui_button nav next primary'})['href'])
        else:
            pass
        dict_avis = {}
        i = 0

        if soup.find(attrs={"data-test-target" : "reviews-tab"}):
            blocAvis = soup.find(attrs={"data-test-target" : "reviews-tab"})
        else:
            print('pas avis')
            break

        try:
            site = soup.find('h1',attrs={'class':'QdLfr b d Pn'}).text
        except:
            site = None

        for x in blocAvis.findAll(attrs={"class" : "YibKl MC R2 Gi z Z BB pBbQr"}):
            i+=1
            try :
                name = (x.find('a', attrs={'class':'ui_header_link uyyBf'})).text
            except :
                name = None
            try:
                #changer date sans accent et nom mois complet
                date_comm = re.search(r'\((.*?)\)',x.find(attrs={'class':'cRVSd'}).text).group(1)
                if str(date_comm) == 'Hier':
                    date_comm = str((today - timedelta(days = 1)).strftime("%d %b %Y"))
                elif str(date_comm) == "Aujourd'hui":
                    date_comm = str(today.strftime("%d %b %Y"))
                date_comm = trait_date(date_comm, dict_mois)
            except:
                date_comm=None
            if date_comm is not None:
                if re.fullmatch(r'\d{2} [Aa-zZ]*', date_comm):
                    date_comm = f'{date_comm} {today.year}'
            try:
                annee_com = date_comm.split(' ')[-1]
                mois_comm = date_comm.split(' ')[-2]
            except:
                annee_com = None
                mois_comm = None
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
            if date_travel is not None:
                if re.fullmatch(r'\d{2} [Aa-zZ]*', date_travel):
                    date_travel = f'{date_travel} {today.year}'

            if x.find(class_="pDrIj f z") is not None:
                photo = True
            else:
                photo = False

            dict_avis[i] = {'Type':'Hotel',
                            'Site':site,
                            'Auteur':name,
                            'Localisation':situation,
                            'Date_commentaire':date_comm,
                            'Annee_commentaire':annee_com,
                            'Mois_commentaire':mois_comm,
                            'Date_voyage':date_travel,
                            'Titre': titre,
                            'Note':note,
                            'Commentaire':commentaire,
                            'Photo':photo}
        avis.append(dict_avis)
    return avis, links

def mongo(avis):
    client = MongoClient("mongodb://db:27017")
    db = client['disney']
    collection = db['Tripadvisor']
    for x in avis:
        for y in range(len(x)):
            avis_exists = collection.find_one({'Commentaire': x[y+1]['Commentaire'], 'Auteur':x[y+1]['Auteur'], 'Date_commentaire':x[y+1]['Date_commentaire']})
            if avis_exists:
                return 1
            collection.insert_one(x[y+1])



@st.experimental_singleton
def run():




            
    urls_Parc = ["https://www.tripadvisor.fr/Attraction_Review-g226865-d189258-Reviews-Disneyland_Paris-Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html",
                    "https://www.tripadvisor.fr/Attraction_Review-g226865-d285990-Reviews-Walt_Disney_Studios_Park-Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html"]

    urls_Hotel = ["https://www.tripadvisor.fr/Hotel_Review-g1182377-d262678-Reviews-Disney_Hotel_New_York_The_Art_of_Marvel-Chessy_Marne_la_Vallee_Seine_et_Marne_Ile_de_F.html",
                    "https://www.tripadvisor.fr/Hotel_Review-g1182377-d262679-Reviews-Disney_Newport_Bay_Club-Chessy_Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html",
                    "https://www.tripadvisor.fr/Hotel_Review-g5599092-d262682-Reviews-Disney_Sequoia_Lodge-Coupvray_Seine_et_Marne_Ile_de_France.html",
                    "https://www.tripadvisor.fr/Hotel_Review-g226865-d262686-Reviews-Disney_Hotel_Cheyenne-Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html",
                    "https://www.tripadvisor.fr/Hotel_Review-g5599092-d262683-Reviews-Disney_Hotel_Santa_Fe-Coupvray_Seine_et_Marne_Ile_de_France.html",
                    "https://www.tripadvisor.fr/Hotel_Review-g1221082-d564634-Reviews-Disney_Davy_Crockett_Ranch-Bailly_Romainvilliers_Seine_et_Marne_Ile_de_France.html"]
    count = 0
    while(True):
        data_hotel = ()
        if count == 0:
            results_parc = asyncio.run(main(urls_Parc))
            data_parc, links_parc = get_urls_parc(results_parc)
            results_hotel = asyncio.run(main(urls_Hotel))
            data_hotel, links_hotel = get_urls_hotel(results_hotel)
            avis_hotel= mongo(data_hotel)
            avis_parc = mongo(data_parc)

        else:
            results_parc = asyncio.run(main(links_parc))
            data_parc, links_parc = get_urls_parc(results_parc)
            avis_parc = mongo(data_parc)
            results_hotel = asyncio.run(main(links_hotel))
            data_hotel, links_hotel = get_urls_hotel(results_hotel)
            avis_hotel = mongo(data_hotel)
        count += 1
        if (avis_hotel == 1 and avis_parc == 1):
            resultat = 1
            break
        else:
            resultat = 0
    return resultat

