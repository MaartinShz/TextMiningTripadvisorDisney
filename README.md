### Dans un terminal de commande

## Vérifier que docker compose est installé

<pre><code>docker-compose -v</code></pre>

## Cloner le repo et créer les containers

<pre><code> git clone https://github.com/MaartinShz/TextMiningTripadvisorDisney.git && cd TextMiningTripadvisorDisney && docker compose up -d</code></pre>

## Services
<p>Pour chaque service recopier le lien correspondant dans un navigateur</p>
<p>mongo-express => locahost:6082
   streamlit => localhost:8501</p>
   
   
### PS : Vérifier que docker-desktop est lancé. Si ce n'est pas le cas, ouvir l'application


### Composition du fichier yml

## La base
<p> Le fonctionnement de l'application nécessite une base de donnée. Cette base de donnée est sur mongodb. Elle est sur le port 2017</p>

## Base GUI
<p> Afin de pouvoir visualiser la base de donnée, un container est dédié à mongo-express. En se connectant sur le port 6082 il est possible de visualiser la base de données</p>

## Application Streamlit
<p> L'application streamlit est sur le port 8501</p>

## Mise à jour de la base
<p>Afin de mettre régulièrement la base à jour, un container est chargé de lancer tous les jours à une heure du matin un script python chargé du scrap et de l'insertion dans la base.</p>

## Mongo-seed
<p>Permet d'importer un fichier de données au format .json lors du démarrage du container de la base.
