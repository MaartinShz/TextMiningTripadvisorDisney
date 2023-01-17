# -*- coding: utf-8 -*-
"""
Created on Wed Dec 21 16:12:19 2022

@author: Christelle
"""

import streamlit as st
import pandas as pd
import altair as alt
from urllib.error import URLError
import pandas as pd
import numpy as np
import oracledb
import re
from unidecode import unidecode
import string
#nltk.download('wordnet')
from my_functions import my_corpora_2_vec
from my_functions import nettoyage_corpus
from my_functions import my_corpora_2_vec
from my_functions import my_cah_from_doc2vec
from my_functions import mots_worldcloud
from my_functions import liste_sentiment
from my_functions import matrice_lien
from my_functions import my_dendogram
from connexion_Oracle import connect_to_database
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from gensim.models import Word2Vec
from scipy.cluster.hierarchy import dendrogram, linkage,fcluster
from sklearn.feature_extraction.text import CountVectorizer
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pattern
from pattern.fr import sentiment


st.set_page_config(page_title="Analyse ", page_icon="📊")
st.markdown("# Analyse")
st.sidebar.header("Analyse")
st.write(
    """The aim here is to highlight the hotel data """
)


### Connexion à Oracle
con = connect_to_database()


analysis_options = ["Commentaires", "Note","Localisation"]
selected_option = st.selectbox("Select an analysis option:", analysis_options)

if selected_option == "Commentaires":
    

    
    # # Analyse des commentaires pour les hôtels
    #Importer la table 'commentaire_hotel':
    #Importer la table 'commentaire_hotel':
    query_commentaire_hotel = "SELECT COMMENTAIRE,ANNÉE FROM COMMENTAIRE_HOTEL,DATECOMMENTAIRE WHERE COMMENTAIRE_HOTEL.ID_DATECOMMENTAIRE = DATECOMMENTAIRE.ID_DATECOMMENTAIRE"
    commentaire_hotel = pd.read_sql(query_commentaire_hotel, con=con)
    st.write(commentaire_hotel)
    st.button("Re-run")
    
    
    
    #Chargez dans une liste des commentaires pour chaque item
    corpus_original_hotel = []
    for i in commentaire_hotel["COMMENTAIRE"].values:
        corpus_original_hotel.append(i)
    #corpus_original_hotel
    
    
    
    #corpus après pré-traitement, sous forme de listes de liste de tokens
    corpus_liste_hotel = nettoyage_corpus(corpus_original_hotel)
    #corpus_liste_hotel
    
    
    commentaire_hotel["corpus"] = corpus_liste_hotel
    
    #Create a list of the available years in the data
    years = commentaire_hotel['ANNÉE'].unique()
    # Use st.selectbox to create a dropdown menu to select the year
    selected_year = st.selectbox("Choisissez l'année :", years)
    
    corpus_liste_hotel_year = commentaire_hotel["corpus"][commentaire_hotel["ANNÉE"] == selected_year]
    commentaire_hotel_year = commentaire_hotel["COMMENTAIRE"][commentaire_hotel["ANNÉE"] == selected_year]
    
    ### Différentes analyses ############
    
    
    #World Cloud:
    st.markdown("## le World Cloud des commentaires")
    mots_worldcloud(commentaire_hotel_year)
    
    # Analyse des sentiments
    
    
    # on crée une liste des sentiments pour les commentaires des hotels:
    list_note_hotel = [sentiment(i) for i in corpus_liste_hotel_year]
    
    
    # on affiche pie chart:
    st.markdown("## Analyse des sentiments")
    liste_sen_hotel  = liste_sentiment(list_note_hotel)
    df_sentiment_hotel = pd.DataFrame(commentaire_hotel_year)
    df_sentiment_hotel["Sentiments"] = liste_sen_hotel
    count_hotel = df_sentiment_hotel["Sentiments"].value_counts()
    plt.pie(count_hotel)
    labels = ["Positif","Neutre","Négatif","Très positif","Très négatif"]
    plt.legend(labels, loc="best")
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot()
    
    
    # on crée un dataframe pour chaque type de sentiment:
    
    tres_positif_hotel = df_sentiment_hotel["COMMENTAIRE"][df_sentiment_hotel["Sentiments"]=="Très positif"]
    positif_hotel = df_sentiment_hotel["COMMENTAIRE"][df_sentiment_hotel["Sentiments"]=="Positif"]
    neutre_hotel = df_sentiment_hotel["COMMENTAIRE"][df_sentiment_hotel["Sentiments"]=="Neutre"]
    negatif_hotel = df_sentiment_hotel["COMMENTAIRE"][df_sentiment_hotel["Sentiments"]=="Négatif"]
    tres_negatif_hotel = df_sentiment_hotel["COMMENTAIRE"][df_sentiment_hotel["Sentiments"]=="Très négatif"]
    
    
    
    # word cloud pour les commentaires très positifs:
    st.markdown("## le World Cloud des commentaires très positifs")
    if len(tres_positif_hotel) > 0:
        mots_worldcloud(tres_positif_hotel)
    
    else:
        st.write("Il n'y a pas de commentaire très positif")
    
    
    
    
    # word cloud pour les commentaires positifs:
    st.markdown("## le World Cloud des commentaires positifs")
    
    
    if len(positif_hotel) > 0:
        
        mots_worldcloud(positif_hotel)
        
    else:
        st.write("Il n'y a pas de commentaire positif")
    
    
    
    
    # word cloud pour les commentaires neutres:
    st.markdown("## le World Cloud des commentaires neutres")
    
    
    if len(neutre_hotel) > 0:
        
        mots_worldcloud(neutre_hotel)
        
    else:
        st.write("Il n'y a pas de commentaire neutre")
    
    
    
    
    # word cloud pour les commentaires négatifs:
    st.markdown("## le World Cloud des commentaires négatifs")
    
    
    if len(negatif_hotel) > 0:
        
        mots_worldcloud(negatif_hotel)
    
    else:
        st.write("Il n'y a pas de commentaire négatif")
    
    
    
    
    # word cloud pour les commentaires très négatifs:
    st.markdown("## le World Cloud des commentaires très négatifs")
    
    
    if len(tres_negatif_hotel) > 0:
        
        mots_worldcloud(tres_negatif_hotel)
    
    else:
        st.write("Il n'y a pas de commentaire très négatif")
    
    
    
    
    
    #construire la représentation à 100 dim.
    
    modele_hotel = Word2Vec(corpus_liste_hotel_year,vector_size=100,window=3,min_count=2,epochs=100)
    words_hotel = modele_hotel.wv
    
    #la matrice des liens
    Z_hotel = matrice_lien(corpus_liste_hotel_year,words_hotel)
    #st.button("Re-run")
    
    number = st.number_input("Entrez un seuil :", min_value=5, max_value=200, step=1, format="%d", value=10)
    
    st.markdown("## le dendrogramme")
    #afficher le dendrogramme
    my_dendogram(Z_hotel,seuil=number)
    #st.button("Re-run")
    
    
    st.markdown("## Cluster de mots")
    
    #CAH (critère de Ward) 
    
    cah_hotel = my_cah_from_doc2vec(corpus_liste_hotel_year,Z_hotel,seuil=number)
    st.write(cah_hotel )
    st.button("Re-run cah")

elif selected_option == "Note":
    query_note_hotel = "SELECT ANNÉE,NOTE FROM COMMENTAIRE_HOTEL,NOTE,DATECOMMENTAIRE WHERE COMMENTAIRE_HOTEL.ID_NOTE = NOTE.ID_NOTE AND COMMENTAIRE_HOTEL.ID_DATECOMMENTAIRE = DATECOMMENTAIRE.ID_DATECOMMENTAIRE"
    note_hotel = pd.read_sql(query_note_hotel, con=con)
    st.write("note_hotel")
    ## Choisi l'année
    years = note_hotel['ANNÉE'].unique()
    # Use st.selectbox to create a dropdown menu to select the year
    selected_year = st.selectbox("Choisissez l'année :", years)
    note_hotel_year = pd.DataFrame(note_hotel["NOTE"][note_hotel["ANNÉE"] == selected_year])
    # on affiche bar chart:

    count_note_hotel = note_hotel_year["NOTE"].value_counts()
    count_note_hotel.plot(kind="bar")
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot()

    
else:
    # code to perform comment analysis
    # Importer la table "localisation":

    query_local_hotel = "SELECT ANNÉE,LOCALISATION FROM COMMENTAIRE_HOTEL,LOCALISATION,DATECOMMENTAIRE WHERE COMMENTAIRE_HOTEL.ID_LOCALISATION = LOCALISATION.ID_LOCALISATION AND COMMENTAIRE_HOTEL.ID_DATECOMMENTAIRE = DATECOMMENTAIRE.ID_DATECOMMENTAIRE"
    local_hotel = pd.read_sql(query_local_hotel, con=con)
    st.write("local_hotel")
    # On sélectionne les localisations par rapport à l'année:
    years = local_hotel['ANNÉE'].unique()
        # Use st.selectbox to create a dropdown menu to select the year
    selected_year = st.selectbox("Choisissez l'année :", years)

    local_hotel_year = pd.DataFrame(local_hotel["LOCALISATION"][local_hotel["ANNÉE"] == selected_year])
    
    # on affiche une table - les 10 localisations les plus fréquentes:

    st.write(local_hotel_year.value_counts()[:10])
con.close()



