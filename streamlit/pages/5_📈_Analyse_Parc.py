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
    """The aim here is to highlight the data from the parks  """
)



### Connexion à Oracle
con = connect_to_database()

analysis_options = ["Commentaires", "Note","Localisation","Situations"]
selected_option = st.selectbox("Select an analysis option:", analysis_options)

if selected_option == "Commentaires":
    
    #Importer la table 'commentaire_parc':

    query_commentaire_parc = "SELECT COMMENTAIRE,ANNÉE FROM COMMENTAIRE_PARC,DATECOMMENTAIRE WHERE COMMENTAIRE_PARC.ID_DATECOMMENTAIRE = DATECOMMENTAIRE.ID_DATECOMMENTAIRE"
    commentaire_parc = pd.read_sql(query_commentaire_parc, con=con)
    commentaire_parc["COMMENTAIRE"] = commentaire_parc["COMMENTAIRE"].astype(str)
    st.write(commentaire_parc)
    #Chargez dans une liste les commentaires pour chaque item
    
    corpus_original_parc = []
    for i in commentaire_parc["COMMENTAIRE"].values:
        corpus_original_parc.append(i)
   #corpus après pré-traitement, sous forme de listes de liste de tokens
    corpus_liste_parc = nettoyage_corpus(corpus_original_parc)
    
    commentaire_parc["corpus"] = corpus_liste_parc
    
    
    # On sélectionne les localisations par rapport à l'année:
    years = commentaire_parc['ANNÉE'].unique()
        # Use st.selectbox to create a dropdown menu to select the year
    selected_year = st.selectbox("Choisissez l'année :", years)
    
    
    corpus_liste_parc_year = commentaire_parc["corpus"][commentaire_parc["ANNÉE"] == selected_year]
    commentaire_parc_year = commentaire_parc["COMMENTAIRE"][commentaire_parc["ANNÉE"] == selected_year]
    
    
    
    #World Cloud:
    st.markdown("## le World Cloud des commentaires")
    mots_worldcloud(commentaire_parc_year)
    
# on crée une liste des sentiments pour les commentaires des parcs:
    st.markdown("## Analyse des sentiments")
    list_note_parc = [sentiment(i) for i in corpus_liste_parc_year]
    liste_sen_parc  = liste_sentiment(list_note_parc)
    df_sentiment_parc = pd.DataFrame(commentaire_parc_year)
    df_sentiment_parc["Sentiments"] = liste_sen_parc
    count_parc = df_sentiment_parc["Sentiments"].value_counts()
    plt.pie(count_parc)
    plt.legend(["Positif","Neutre","Négatif","Très positif","Très négatif"])
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot()
    
# on crée un dataframe pour chaque type de sentiment:

    tres_positif_parc = df_sentiment_parc["COMMENTAIRE"][df_sentiment_parc["Sentiments"]=="Très positif"]
    positif_parc = df_sentiment_parc["COMMENTAIRE"][df_sentiment_parc["Sentiments"]=="Positif"]
    neutre_parc = df_sentiment_parc["COMMENTAIRE"][df_sentiment_parc["Sentiments"]=="Neutre"]
    negatif_parc = df_sentiment_parc["COMMENTAIRE"][df_sentiment_parc["Sentiments"]=="Négatif"]
    tres_negatif_parc = df_sentiment_parc["COMMENTAIRE"][df_sentiment_parc["Sentiments"]=="Très négatif"]

    # word cloud pour les commentaires très positifs:
    st.markdown("## le World Cloud des commentaires très positifs")
    if len(tres_positif_parc) > 0:
        
        mots_worldcloud(tres_positif_parc)
    
    else:
        st.write("Il n'y a pas de commentaire très positif")
    

    
    # word cloud pour les commentaires positifs:
    st.markdown("## le World Cloud des commentaires positifs")
    if len(positif_parc) > 0:
        
        mots_worldcloud(positif_parc)
    
    else:
        st.write("Il n'y a pas de commentaire positif") 
    
    # word cloud pour les commentaires neutres:
    st.markdown("## le World Cloud des commentaires neutres")
    if len(neutre_parc) > 0:
    
        mots_worldcloud(neutre_parc)
    
    else:
        st.write("Il n'y a pas de commentaire neutre")
    
    # word cloud pour les commentaires négatifs:
    st.markdown("## le World Cloud des commentaires négatifs")
    if len(negatif_parc) > 0:
        
        mots_worldcloud(negatif_parc)
    
    else:
        st.write("Il n'y a pas de commentaire négatif")
    
    
    # word cloud pour les commentaires très négatifs:
    st.markdown("## le World Cloud des commentaires très négatifs")

    if len(tres_negatif_parc) > 0:
    
        mots_worldcloud(tres_negatif_parc)

    else:
        st.write("Il n'y a pas de commentaire très négatif")
        
    #construire la représentation à 100 dim.
    modele_parc = Word2Vec(corpus_liste_parc_year,vector_size=100,window=3,min_count=2,epochs=100)
    words_parc = modele_parc.wv
    
  
        #la matrice des liens
    Z_parc = matrice_lien(corpus_liste_parc_year,words_parc)
    number = st.number_input("Entrez un seuil :", min_value=5, max_value=200, step=1, format="%d", value=10)
    st.markdown("## le dendrogramme")
    #afficher le dendrogramme
    my_dendogram(Z_parc,seuil=number)
    
    
    #CAH (critère de Ward) 
    st.markdown("## Cluster de mots ")
    cah_parc = my_cah_from_doc2vec(corpus_liste_parc_year,Z_parc,seuil=number)
    st.write(cah_parc )
    
    
elif selected_option == "Note":
        # Importer la table "note":
    query_note_parc = "SELECT ANNÉE,NOTE FROM COMMENTAIRE_PARC,NOTE,DATECOMMENTAIRE WHERE COMMENTAIRE_PARC.ID_NOTE = NOTE.ID_NOTE AND COMMENTAIRE_PARC.ID_DATECOMMENTAIRE = DATECOMMENTAIRE.ID_DATECOMMENTAIRE"
    note_parc = pd.read_sql(query_note_parc, con=con)
    st.write(note_parc)
    # On sélectionne les notes par rapport à l'année:
    years = note_parc['ANNÉE'].unique()
         # Use st.selectbox to create a dropdown menu to select the year
    selected_year = st.selectbox("Choisissez l'année :", years)
    note_parc_year = pd.DataFrame(note_parc["NOTE"][note_parc["ANNÉE"] == selected_year])
    
# on affiche bar chart:
    count_note_parc = note_parc_year["NOTE"].value_counts()
    count_note_parc.plot(kind="bar")
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot()
    
 
    
 
elif selected_option == "Localisation":
        # Importer la table "localisation":
    query_local_parc = "SELECT ANNÉE,LOCALISATION FROM COMMENTAIRE_PARC,LOCALISATION,DATECOMMENTAIRE WHERE COMMENTAIRE_PARC.ID_LOCALISATION = LOCALISATION.ID_LOCALISATION AND COMMENTAIRE_PARC.ID_DATECOMMENTAIRE = DATECOMMENTAIRE.ID_DATECOMMENTAIRE"
    local_parc = pd.read_sql(query_local_parc, con=con)
    st.write(local_parc)
    
    # On sélectionne les localisations par rapport à l'année:
    years = local_parc['ANNÉE'].unique()
         # Use st.selectbox to create a dropdown menu to select the year
    selected_year = st.selectbox("Choisissez l'année :", years)
    local_parc_year = pd.DataFrame(local_parc["LOCALISATION"][local_parc["ANNÉE"] == selected_year])    
   
    # on affiche une table - les 10 localisations les plus fréquentes:
    st.write(local_parc_year.value_counts()[:10])


    
else:
        # Importer la table "situation":
    
    query_situation = "SELECT ANNÉE,SITUATION FROM COMMENTAIRE_PARC,SITUATION,DATECOMMENTAIRE WHERE COMMENTAIRE_PARC.ID_SITUATION = SITUATION.ID_SITUATION AND COMMENTAIRE_PARC.ID_DATECOMMENTAIRE = DATECOMMENTAIRE.ID_DATECOMMENTAIRE"
    situation = pd.read_sql(query_situation, con=con)
    st.write(situation)
    
    # On sélectionne les localisations par rapport à l'année:
    years = situation['ANNÉE'].unique()
          # Use st.selectbox to create a dropdown menu to select the year
    selected_year = st.selectbox("Choisissez l'année :", years)
    situation_year = pd.DataFrame(situation["SITUATION"][situation["ANNÉE"] == selected_year])
   
    # on affiche bar chart:
    
    count_situation = situation_year["SITUATION"].value_counts()
    count_situation.plot(kind="bar")
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot()

con.close()



