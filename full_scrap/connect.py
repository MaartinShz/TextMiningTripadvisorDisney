####################################################
#            CONNECTION À LA BDD MONGO             #
# VÉRIFIER SI LE TEXTE DU COMMENTAIRE EXISTE DÉJÀ. #
#           S'IL N'EXISTE PAS ON L'ÉCRIT           #
####################################################



from pymongo import MongoClient


def write_db(avis:dict):
    # connection à la base de donnée en local
    client = MongoClient("mongodb://root:root@localhost:27017/")
    # connection à la db
    db_name = client["disney"]
    # connection à la collection
    collection = db_name["disney"]

    # check si le text du commentaire existe déjà
    for x in avis:
        if collection.count_documents({'Commentaire':avis[x]['Commentaire']}, limit=1):
            return 0
        else:
            collection.insert_one(avis[x])
            
