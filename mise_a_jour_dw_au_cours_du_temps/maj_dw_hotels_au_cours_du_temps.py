# On import les packages nÃ©cessaires:
import pandas as pd
import numpy as np

from scrapping.database.connexion_Oracle import connect_to_database
# #Connexion BDD
con = connect_to_database()
cursor = con.cursor()

########## Importer toutes les tables - dimensionsÂ¶

###Importer la table 'note':
query_note = "SELECT * FROM NOTE"
note = pd.read_sql(query_note, con=con)


###Importer la table 'datecommentaire':
query_datecommentaire = "SELECT * FROM DATECOMMENTAIRE"
datecommentaire = pd.read_sql(query_datecommentaire, con=con)

# on crée une liste contenante mois et annÃ©e en mÃªme temps:
list_moisannee_commentaire = []
list_moisannee_commentaire = datecommentaire["MOIS"] + " "+ datecommentaire["ANNÉE"]

###Importer la table 'datesejour':
query_datesejour = "SELECT * FROM DATESEJOUR"
datesejour = pd.read_sql(query_datesejour, con=con)

# on crée une liste contenante mois et annÃ©e en mÃªme temps:
list_moisannee_sejour = []
list_moisannee_sejour = datesejour["MOIS"] + " "+ datesejour["ANNÉE"]

###Importer la table 'localisation':
query_localisation = "SELECT * FROM LOCALISATION"
localisation = pd.read_sql(query_localisation, con=con)

# # Mise à jour datawarehouse pour les hÃ´tels au cours du temps

###Importer la table 'commentaire_hotel':
query_commentaire_hotel = "SELECT * FROM COMMENTAIRE_HOTEL"
commentaire_hotel = pd.read_sql(query_commentaire_hotel, con=con)


#from scrapping.hotel_scrap import *

urlHotel=["https://www.tripadvisor.fr/Hotel_Review-g1182377-d262678-Reviews-Disney_Hotel_New_York_The_Art_of_Marvel-Chessy_Marne_la_Vallee_Seine_et_Marne_Ile_de_F.html",
    "https://www.tripadvisor.fr/Hotel_Review-g1182377-d262679-Reviews-Disney_Newport_Bay_Club-Chessy_Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html",
    "https://www.tripadvisor.fr/Hotel_Review-g5599092-d262682-Reviews-Disney_Sequoia_Lodge-Coupvray_Seine_et_Marne_Ile_de_France.html",
    "https://www.tripadvisor.fr/Hotel_Review-g226865-d262686-Reviews-Disney_Hotel_Cheyenne-Marne_la_Vallee_Seine_et_Marne_Ile_de_France.html",
    "https://www.tripadvisor.fr/Hotel_Review-g5599092-d262683-Reviews-Disney_Hotel_Santa_Fe-Coupvray_Seine_et_Marne_Ile_de_France.html",
    "https://www.tripadvisor.fr/Hotel_Review-g1221082-d564634-Reviews-Disney_Davy_Crockett_Ranch-Bailly_Romainvilliers_Seine_et_Marne_Ile_de_France.html"
    ]

#avishotel = scraping_hotel(urlHotel)

avishotel= [
    ["test",999] 
]

for avis in avishotel:
    #SELECT si champs des dimension dans la bdd
    
    selectDateCommentaire = cursor.execute("SELECT * from DATECOMMENTAIRE WHERE ID_DATECOMMENTAIRE = :iddateCommentaire", iddateCommentaire=avis[0]).fetchone()
    print(selectDateCommentaire)
    if selectDateCommentaire is None:
        cursor.execute("INSERT INTO DATECOMMENTAIRE(ID_DATECOMMENTAIRE,MOIS, ANNÉE) VALUES (:iddateCommentaire, :mois, :annee)", iddateCommentaire = avis, mois = avis, annee = avis)
        
    selectDateSejour = cursor.execute("SELECT * from DATESEJOUR WHERE ID_DATESEJOUR = :iddateSejour", iddateSejour=avis[0]).fetchone()
    print(selectDateSejour)
    if selectDateSejour is None:
        cursor.execute("INSERT INTO DATESEJOUR(ID_DATESEJOUR,MOIS, ANNÉE) VALUES (:iddateSejour, :mois, :annee)", iddateSejour = avis, mois = avis, annee = avis)
    
    selectLocalisation = cursor.execute("SELECT * from LOCALISATION WHERE ID_LOCALISATION = :idLocalisation", idLocalisation=avis[0]).fetchone()
    print(selectLocalisation)
    if selectDateSejour is None:
        cursor.execute("INSERT INTO LOCALISATION(ID_LOCALISATION,LOCALISATION) VALUES (:id, :note)", avis)

    selectNote = cursor.execute("SELECT * from NOTE WHERE ID_NOTE = :idnote", idnote=avis[0]).fetchone()
    print(selectNote)
    if selectNote is None:
        cursor.execute("INSERT INTO NOTE(ID_NOTE,NOTE) VALUES (:id, :note)", avis)
    
    
    cursor.execute("INSERT INTO COMMENTAIRE_HOTEL(ID_COMMENTAIRE, ID_NOTE,ID_DATECOMMENTAIRE, ID_DATESEJOUR, ID_LOCALISATION, TITRE, COMMENTAIRE) VALUES (:id, :note)", avis)
    con.commit()


#Importer de nouveau la table 'localisation':
#localisation = pd.read_sql(query_localisation, con=con)
#note =pd.read_sql(query_note, con=con)
#print(note)







##############################################################################


"""
# on vÃ©rifie s'il y a des nouveaux commentaires:
index_hotel = []
for j,y in enumerate(commentaire_hotel["COMMENTAIRE"].tolist()):
    for i, x in enumerate(hotel["commentaire"].tolist()):
        if (x==y) & (i not in index_hotel):
            index_hotel.append(i)




#on enlÃ¨ve les commentaires qui existent dÃ©jÃ  dans la dw:
hotel.drop(index=index_hotel,inplace=True)



#on crée nouveaux "id_localisation" s'il y a des nouvelles localisations:

if len(hotel) > 0:
    df_local_new_hotel = pd.DataFrame()

    liste_localisation_new_hotel = []

    for j in hotel["pays"].tolist():
        if (j not in localisation["LOCALISATION"].tolist())&(j!='')&(j not in liste_localisation_new_hotel):
            liste_localisation_new_hotel.append(j)

    if len(liste_localisation_new_hotel)>0:
        df_local_new_hotel["localisation"] = liste_localisation_new_hotel

        liste_id_loca_new_hotel = []
        for k in range(len(df_local_new_hotel["localisation"])):
            l = len(localisation["LOCALISATION"])
            id = "L_" + str(l+k+1)
            liste_id_loca_new_hotel.append(id)
        df_local_new_hotel["id_localisation"] = liste_id_loca_new_hotel

        df_local_new_hotel = df_local_new_hotel[df_local_new_hotel.columns[[1,0]]]
    
        # Exporter des nouvelles valeurs de la table "localisation" vers oracle:
        cursor = con.cursor()

        s_loca = "INSERT INTO LOCALISATION(ID_LOCALISATION,LOCALISATION) VALUES(:1,:2)"


        data_loca_new_hotel = []
        for line in df_local_new_hotel.values:
            data_loca_new_hotel.append(line)
        
        for line in data_loca_new_hotel:
            cursor.execute(s_loca, line)
        con.commit()
    
        print("Il y a " + str(len(df_local_new_hotel)) + " nouvelles localisations")
        
        #Importer de nouveau la table 'localisation':
        query_localisation = "SELECT * FROM LOCALISATION"
        localisation = pd.read_sql(query_localisation, con=con)
        
else:
    print("Il n'y a pas de nouvelle localisation")


# fonction de crÃ©ation dataframe pour les nouveaux commentaires pour les hotels:
def df_avis_hotel(data):
    
    # crÃ©er un dataframe vide nommÃ© df_commentaire_new:
    df_commentaire_new = pd.DataFrame()
    
    # on ajoute la colonne "Id_Note" au dataframe df_commentaire_new:

    liste_note_new=[]
    for i in range(len(data["note"])):
        if data["note"].tolist()[i] == "":
            liste_note_new.append("")
        for j in range(len(note["NOTE"])):
            if data["note"].tolist()[i] == note["NOTE"].astype(int)[j]:
                liste_note_new.append(note["ID_NOTE"][j])
    df_commentaire_new["Id_Note"]= liste_note_new
    ###########################################
    
    # on ajoute la colonne "id_datecommentaire" au dataframe df_commentaire_new:

    liste_datecommentaire_new=[]
    for i in range(len(data["dateCommentaire"])):
        if data["dateCommentaire"].tolist()[i] == "":
            liste_datecommentaire_new.append("")
        for j in range(len(list_moisannee_commentaire)):
            if data["dateCommentaire"].tolist()[i] == list_moisannee_commentaire[j]:
                liste_datecommentaire_new.append(datecommentaire["ID_DATECOMMENTAIRE"][j])
    df_commentaire_new["Id_Datecommentaire"]= liste_datecommentaire_new
    ###########################################
    # on ajoute la colonne "id_datesejour" au dataframe df_commentaire_new:

    liste_datesejour_new=[]
    for i in range(len(data["dateSejour"])):
        if data["dateSejour"].tolist()[i] == "":
            liste_datesejour_new.append("")
        for j in range(len(list_moisannee_sejour)):
            if data["dateSejour"].tolist()[i] == list_moisannee_sejour[j]:
                liste_datesejour_new.append(datesejour["ID_DATESEJOUR"][j])
    df_commentaire_new["Id_Datesejour"]= liste_datesejour_new
    ###########################################
    
    # on ajoute la colonne "id_localisation" au dataframe df_commentaire_new:

    liste_localisation_new=[]
    for i in range(len(data["pays"])):
        if (data["pays"].tolist()[i] == ""):
            liste_localisation_new.append("")
        for j in range(len(localisation["LOCALISATION"])):
            if data["pays"].tolist()[i] == localisation["LOCALISATION"][j]:
                liste_localisation_new.append(localisation["ID_LOCALISATION"][j])
    df_commentaire_new["Id_Localisation"]= liste_localisation_new
    ###########################################
    
    # on ajoute la colonne "id_commentaire" au dataframe df_commentaire_new:
    liste_idcommentaire_new=[]
    for j in range(len(df_commentaire_new.index)):
        l = len(commentaire_hotel)
        liste_idcommentaire_new.append("C_" + str(l+j+1))
    df_commentaire_new["Id_Commentaire"]= liste_idcommentaire_new
    ###########################################
    
    # on ajoute la colonne "Titre" et la colonne "Commentaire" au dataframe df_commentaire_new:

    df_commentaire_new["Titre"]= data["titre"].tolist()
    df_commentaire_new["Commentaire"]= data["commentaire"].tolist()

    # on change la position des colonnes
    df_commentaire_new = df_commentaire_new[df_commentaire_new.columns[[4,0,1,2,3,5,6]]]

    return df_commentaire_new


# on export les nouveaux commentaires s'il y en a:
if len(hotel) > 0:
    df_commentaire_new_hotel = df_avis_hotel(hotel).fillna("")
    # Exporter la table "commentaire_hotel" vers oracle:
    s_commentaire_hotel = "INSERT INTO commentaire_hotel (Id_Commentaire, Id_Note, Id_DateCommentaire,Id_DateSejour,Id_Localisation,Titre,Commentaire) VALUES (:1, :2, :3, :4, :5, :6, :7)"
    data_commentaire_hotel = []
    for line in df_commentaire_new_hotel.values:
        data_commentaire_hotel.append(line)

    for line in data_commentaire_hotel:
        cursor.execute(s_commentaire_hotel, line)
    con.commit()
    
    print("Il y a " +str(len(data_commentaire_hotel)) +" nouveaux commentaires")
    
else:
    print("Il n'y a pas de nouveau commentaire")
"""

