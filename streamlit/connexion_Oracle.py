
import oracledb

def connect_to_database():
    dsn_str = oracledb.makedsn("db-etu.univ-lyon2.fr", "1521", "DBETU")
    con = oracledb.connect(user="m134", password="m134", dsn=dsn_str)
    return con
