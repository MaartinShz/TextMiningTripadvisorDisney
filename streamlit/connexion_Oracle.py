# -*- coding: utf-8 -*-
"""
Created on Fri Jan  6 11:00:57 2023

@author: USER
"""
import cx_Oracle
import cx_Oracle

def connect_to_database():
    try:
        cx_Oracle.init_oracle_client(lib_dir="C:/Users/USER/Documents/Master_SISE/Projet/Text_mining/instantclient_21_8")
    except cx_Oracle.ProgrammingError as e:
        # Client library is already initialized, do nothing
        pass

    dsn_str = cx_Oracle.makedsn("db-etu.univ-lyon2.fr", "1521", "DBETU")
    con = cx_Oracle.connect(user="m134", password="m134", dsn=dsn_str)

    return con
