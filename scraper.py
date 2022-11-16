from bs4 import BeautifulSoup
import requests

#Tripadvisor Disney Land Paris
url="https://www.tripadvisor.fr/Attraction_Review-g226865-d189258-Reviews-Disneyland_Paris-Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html"

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
    
    
#Note
#<svg class="UctUV d H0" viewBox="0 0 128 24" width="88" height="16" aria-label="2,0 sur 5&nbsp;bulles"><path d="M 12 0C5.388 0 0 5.388 0 12s5.388 12 12 12 12-5.38 12-12c0-6.612-5.38-12-12-12z" transform=""></path><path d="M 12 0C5.388 0 0 5.388 0 12s5.388 12 12 12 12-5.38 12-12c0-6.612-5.38-12-12-12z" transform="translate(26 0)"></path><path d="M 12 0C5.388 0 0 5.388 0 12s5.388 12 12 12 12-5.38 12-12c0-6.612-5.38-12-12-12zm0 2a9.983 9.983 0 019.995 10 10 10 0 01-10 10A10 10 0 012 12 10 10 0 0112 2z" transform="translate(52 0)"></path><path d="M 12 0C5.388 0 0 5.388 0 12s5.388 12 12 12 12-5.38 12-12c0-6.612-5.38-12-12-12zm0 2a9.983 9.983 0 019.995 10 10 10 0 01-10 10A10 10 0 012 12 10 10 0 0112 2z" transform="translate(78 0)"></path><path d="M 12 0C5.388 0 0 5.388 0 12s5.388 12 12 12 12-5.38 12-12c0-6.612-5.38-12-12-12zm0 2a9.983 9.983 0 019.995 10 10 10 0 01-10 10A10 10 0 012 12 10 10 0 0112 2z" transform="translate(104 0)"></path></svg>

#Pays si renseigné
#<div class="biGQs _P pZUbB osNWb"><span>Vesoul, France</span><span class="IugUm">1 contribution</span></div>

#Titre
#<div class="biGQs _P fiohW qWPrE ncFvv fOtGX"><a target="_blank" tabindex="0" href="/ShowUserReviews-g187147-d11988977-r868484980-DisneylandR_Paris_1_or_2_Days_Ticket-Paris_Ile_de_France.html" class="BMQDV _F G- wSSLS SwZTJ FGwzt ukgoS"><span class="yCeTE">L'argent, l'argent et... l'argent</span></a></div>

#Commentaire #verifier si prends le msg en entier
#<div class="biGQs _P pZUbB KxBGd"><span class="yCeTE">L'aventure féérique commence avec un parking à 30€. Surprise, c'était autour de 15€ il y a quelque année. Plutôt fâcheux quand on a déboursé 250€ pour venir passer une journée à Disney à 2 et qu'on sort de 4h de route (essence, autoroutes...). Bon, c'est comme ça, passons. On se dit que l'on va passer une bonne journée. C'était sans compter les temps d'attente ? Entre 45 minutes et 1h15 selon l'attraction. Vous vous souvenez du fast pass ? Il est devenu payant. Avant, vous pouviez venir réserver une attraction et y revenir dans 2h sans faire la queue. C'était une "petite bouffée d'oxygène" côté file d'attente et une optimisation plutôt bien pensée. Et bien c'est devenu payant. Comptez 15€ par attraction et par personne pour ne pas faire la queue, réglable depuis l'appli Disney (la vie est bien faite) ! C'était bien évidemment hors de question. Petite parenthèse pour la bouffe tout simplement immonde sur le parc au moment de se restaurer. On est vraiment aux States, vous apprécierez si vous aimez la nourriture réchauffée et les salades en plastique (bon, ça n'était pas une surprise pour y être déjà allé, je suis mauvaise langue). Bilan de la journée ? 7 attractions pour ma part, 5 pour ma conjointe. Quel monde merveilleux. On continue. Le parc ferme à 19h30 mais... surprise, les attractions ferment à 18h30. Enfin, elles ferment à 18h30, sauf si vous avez le bracelet premium (équivalent du fast pass à la journée, disponible à partir de 180€ la journée en plus du prix du billet). Là, vous pourrez encore continuer à profiter du parc un peu plus longtemps. Frustrant une fois de plus. Bref, nous décidons de nous rendre à la projection de fin de journée et profiter du spectacle. Nous commençons à nous approcher à proximité du château pour bien voir, là où il ne manque pas de place. On aperçoit soudain un cordon de sécurité :"Vous avez votre pass ? - Comment ça ? - Oui, pour pouvoir vous placer ici, il vous faut le bracelet, sinon vous devez aller derrière". Oui, pour pouvoir profiter convenablement du spectacle, il fallait encore ce pass. Nous sommes donc allés rejoindre les gueux dans l'allée, là où on trouve les boutiques de goodies, où nous nous sommes retrouvés entassés par milliers. Impossible de faire un pas sans bousculer quelqu'un, obligés de traverser la foule en s'imposant pour avancer (alors que bien évidemment, les quelques privilégiés qui ont le pass sont eux confortablement installés devant avec tout l'espace nécessaire). Ma conjointe ne voyait même pas la projection tellement il y avait du monde. Nous avons fini par partir, écœurés de cette journée. J'étais déjà allé à Disney, on est d'accord ça n'a jamais été une association à but non lucratif et c'est bien normal, c'est une grosse machine à faire tourner. Mais là c'est trop. Vous n'accueillez pas les visiteurs, vous les dépouillez. Pour y avoir passé de très bons moments il y a quelques années, la "magie de Disney" est bien loin. Passez votre chemin et privilégiez un parc où vous serez un minimum considéré. Vous économiserez des prises de tête et un séjour hors de prix par rapport à la prestation.</span></div>

#Date du séjour
#<div class="RpeCd">oct. 2022 • En famille</div>

#Date du commentaire
#<div class="biGQs _P pZUbB ncFvv osNWb">Écrit le 9 novembre 2022</div>

#Présence de photo: oui/non # test si img dans le div
#<div class="LblVz _e q"><button class="ajoIU _S B-" aria-label="Voir l'image complète"><picture class="NhWcC _R mdkdE" style="width: 100px; height: 100px;"><img srcset="https://dynamic-media-cdn.tripadvisor.com/media/photo-o/26/cb/4e/96/le-symbole-incontournable.jpg?w=100&amp;h=-1&amp;s=1 1x,https://dynamic-media-cdn.tripadvisor.com/media/photo-o/26/cb/4e/96/le-symbole-incontournable.jpg?w=200&amp;h=200&amp;s=1 2x" src="https://dynamic-media-cdn.tripadvisor.com/media/photo-o/26/cb/4e/96/le-symbole-incontournable.jpg?w=100&amp;h=-1&amp;s=1" width="100" height="134" role="none" alt="" loading="lazy"></picture></button></div>
