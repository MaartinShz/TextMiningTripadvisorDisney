import string, numpy as np, streamlit as st, nltk, pattern
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
from pattern.fr import sentiment
from gensim.models import Word2Vec
from scipy.cluster.hierarchy import dendrogram, linkage,fcluster
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd

mots_vides = list(stopwords.words('french'))
mots_vides.extend(x for x in ["disneyland","disney","land","parc","parcs","très","trop","séjour","hôtel","hotel","lhotel",
                                "lhôtel","lhôtel", "chambre","chambres","cest","cétait","ça","cela","avant","après","nest",
                                "nétait","déjà","donc","alors","a","cet","jai","si","tres", "le", "la", "de", "à","je","il","vous","nous","suis","est","trop", 'plus', 'avon','tout'])

ponctuations = list(string.punctuation)
chiffres = list("0123456789")
lem = WordNetLemmatizer()

def pie_charte_notes(notes):
    values_count = dict(Counter(notes))
    sizes = [value for key, value in values_count.items()]
    labels = [key for key, value in values_count.items()]
    plt.pie(sizes, labels=labels)
    plt.show()



def nettoyage(commentaire):
    commentaire = commentaire.lower()
    commentaire = ''.join([w for w in commentaire if (not w in ponctuations) and (not w in chiffres)])
    commentaire = word_tokenize(commentaire)
    commentaire = [lem.lemmatize(terme) for terme in commentaire]
    commentaire = [w for w in commentaire if not w in mots_vides]
    commentaire = [w for w in commentaire if len(w) > 3]
    commentaire = ' '.join(w for w in commentaire)
    return commentaire

def nettoyage_corpus(corpus):
    output = [nettoyage(commentaire) for commentaire in corpus]
    return output


def wordcloud(commentaires_nettoyés):
        comment = []
        comment_word = " "
        for val in commentaires_nettoyés:
                val = "".join(val)
                val = str(val)
                tokens = val.split()
                comment_word = " ".join(tokens)+" "
                comment.append(comment_word)
        comment = " ".join(com for com in comment)+" "
        comment = " ".join(w for w in comment.split(' ') if w not in mots_vides)
        wordcloud = WordCloud(width = 800, height = 800,
                background_color ='white',
                min_font_size = 10).generate(comment)
        # fig, axs = plt.subplots()
        plt.figure(figsize = (8, 8), facecolor = None)
        plt.axis("off")
        plt.figure(figsize = (8, 8), facecolor = None)
        plt.axis("off")
        plt.tight_layout(pad = 0)
        plt.imshow(wordcloud)


def liste_sentiment(corpus_nettoye):
    notes = [sentiment(x) for x in corpus_nettoye]
    liste_sen = []
    for i in notes:
        if i[0] < -0.5:
            liste_sen.append("Très négatif")
        elif (i[0]>=-0.5)&(i[0]<=0):
            liste_sen.append("Négatif")
        elif (i[0]>0)&(i[0]<=0.2):
            liste_sen.append("Neutre")
        elif (i[0]>0.2)&(i[0]<0.7):
            liste_sen.append("Positif")
        else:
            liste_sen.append("Très positif")
    dict_sentiment = dict(zip(corpus_nettoye, liste_sen))
    commentaires_positifs = [key for key, value in dict_sentiment.items() if value == 'Positif']
    commentaires_negatifs = [key for key, value in dict_sentiment.items() if value == 'Négatif']
    commentaires_tres_negatifs = [key for key, value in dict_sentiment.items() if value == 'Très Négatif']
    commentaires_tres_positifs = [key for key, value in dict_sentiment.items() if value == 'Très Positif']
    commentaires_neutres = [key for key, value in dict_sentiment.items() if value == 'Neutre']
    return liste_sen, commentaires_tres_positifs, commentaires_positifs, commentaires_neutres, commentaires_negatifs, commentaires_tres_negatifs


def fig_sentiment(sentiments):
    liste_sentiment = sentiments
    labels = set(liste_sentiment)
    sizes = [Counter(liste_sentiment)[x] for x in Counter(liste_sentiment)]
    colors = ['#AADEA7', '#FEAE65', '#E6F69D','#2D87BB']
    fig, axs = plt.subplots()
    plt.pie(sizes, labels=labels, autopct='%.2f%%', colors=colors)
    return fig, axs


def my_doc_2_vec(doc,trained):
    #dimension de représentation
    p = trained.vectors.shape[1]
    #initialiser le vecteur
    vec = np.zeros(p)
    #nombre de tokens trouvés
    nb = 0
    #traitement de chaque token du document
    for tk in doc:
        #ne traiter que les tokens reconnus
        if ((tk in trained.key_to_index.keys()) == True):
            values = trained[tk]
            vec = vec + values
            nb = nb + 1.0
    #faire la moyenne des valeurs
    #uniquement si on a trouvé des tokens reconnus bien sûr
    if (nb > 0.0):
        vec = vec/nb
    #renvoyer le vecteur
    #si aucun token trouvé, on a un vecteur de valeurs nulles
    return vec




#fonction pour représenter un corpus à partir d'une représentation
#soit entraînée, soit pré-entraînée
#sortie : représentation matricielle
def my_corpora_2_vec(corpora,trained):
    docsVec = list()
    #pour chaque document du corpus nettoyé
    for doc in corpora:
        #calcul de son vecteur
        vec = my_doc_2_vec(doc,trained)
        #ajouter dans la liste
        docsVec.append(vec)
    #transformer en matrice numpy
    matVec = np.array(docsVec)
    return matVec

#fonction pour construire une typologie à partir
#d'une représentation des termes, qu'elle soit entraînée ou pré-entraînée
#seuil par défaut = 1, mais le but est d'avoir 4 groupes
#corpus ici se présente sous la forme d'une liste de listes de tokens

#la matrice des liens
def matrice_lien(corpus,trained):
    #matrice doc2vec pour la représentation à 1000 dim.
    #entraînée via word2vec sur les documents du corpus
    mat = my_corpora_2_vec(corpus,trained)

    #générer la matrice des liens
    Z = linkage(mat,method='ward',metric='euclidean')
    
    return Z

#dendrogramme avec le seuil
def my_dendogram(matrice,seuil=0.7):
    
    #st.write("CAH")
    dendrogram(matrice,orientation='left',color_threshold=seuil)
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot()

# #fonction pour construire une typologie à partir
# #d'une représentation des termes, qu'elle soit entraînée ou pré-entraînée
# #seuil par défaut = 100, mais le but est d'avoir 4 groupes
# #corpus ici se présente sous la forme d'une liste de listes de tokens

def my_cah_from_doc2vec(corpus,matrice,seuil=0.7,nbTermes=7):
    ### permettre à l'utilisateur de choisir le seuil

    #découpage en 4 classes
    grCAH = fcluster(matrice,t=seuil,criterion='distance')

    #***************************
    #interprétation des clusters
    #***************************
    
    #parseur
    parseur = CountVectorizer(binary=True)
    
    #former corpus sous forme de liste de chaîne
    corpus_string = [" ".join(doc) for doc in corpus]
    
    #matrice MDT
    mdt = parseur.fit_transform(corpus_string).toarray()
    
    df_list =[]
    #passer en revue les groupes
    for num_cluster in range(np.max(grCAH)):
        groupe = np.where(grCAH==num_cluster+1,1,0)
        #calcul de co-occurence
        cooc = np.apply_along_axis(func1d=lambda x: np.sum(x*groupe),axis=0,arr=mdt)
        #print(cooc)
        #création d'un data frame intermédiaire
        df = pd.DataFrame(data=cooc,columns=['Fréquence'],index=parseur.get_feature_names_out())    
        #affichage des "nbTermes" termes les plus fréquents
        df = df.sort_values(by='Fréquence',ascending=False).iloc[:nbTermes,:]
        df_list.append(df)
        
    #renvoyer l'indicateur d'appartenance aux groupes
    return df_list




