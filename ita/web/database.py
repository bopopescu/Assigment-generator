import sqlite3
import inspect
import config
from bottle import request, hook

""" Zpřístupňuje DB, pro každý požadavek vytvoří jenom 1 spojení. """

#############################################################
# Sqlite


def clearSQLite():
    """Smaže spojení z požadavku"""
    try:
        request._dbConnection.close()
        del request._dbConnection
    except: pass
    
    try:
        request._dbCursor.close()
        del request._dbCursor
    except: pass

def getConnectionSQLite():
    """ Vrátí existující / vytvoří spojení pro tento požadavek. 
        Podporuje pouze 1 připojení!  """
    try:
        return request._dbConnection
    except AttributeError:
        path = config.database["path"]
        
        con = sqlite3.connect(path)
        con.isolation_level = None  # vypnutí relací 
        con.row_factory = sqlite3.Row
        request._dbConnection = con 
        return request._dbConnection 

def querySQLite(*args, **kwargs):
    try:
        c = request._dbCursor
    except AttributeError:
        c = getConnectionSQLite().cursor()
        request._dbCursor = c
    return c.execute(*args, **kwargs)


################################################################################
        
if config.database["storage"] == "sqlite":
    query = querySQLite
    clearConnection = clearSQLite
elif config.database["storage"] == "mysql":
    getConnection = connectMySQL
    clearConnection = clearMySQL
  
@hook("after_request")
def cleanUp():
    clearConnection()


from hashlib import sha1

query("DROP TABLE IF EXISTS users")
query("CREATE TABLE users (login char(8)  PRIMARY KEY NOT NULL, password char(40) NULL,  roles char(20) NULL, group_id INT NULL)")
query("INSERT INTO users VALUES ('xtomec06', NULL, NULL, 1)")
query("INSERT INTO users VALUES ('xtest', '%s', 'lector' , NULL)" %  (sha1("test".encode('utf-8')).hexdigest(),) )
query("INSERT INTO users VALUES ('master', '%s', 'master,lector' , NULL)" %  (sha1("test".encode('utf-8')).hexdigest(),) )

query("DROP TABLE IF EXISTS groups")
query("CREATE TABLE groups (group_id INTEGER PRIMARY KEY AUTOINCREMENT, name char(40) NOT NULL, lector char(8) NOT NULL )")
query("INSERT INTO groups VALUES (NULL,'Skupina 01', 'xtest')")
query("INSERT INTO groups VALUES (NULL,'Skupina náhradní', 'master')")

query("DROP TABLE IF EXISTS lectures")
query("CREATE TABLE lectures (lecture_id INTEGER PRIMARY KEY AUTOINCREMENT, name char(40) NOT NULL, lector char(8) NOT NULL, `nonterminal` char(32) , state INT NULL, shared INT NULL)")
query("INSERT INTO lectures(name, lector,nonterminal, state) VALUES ('Cvičení 1. - logické operace', 'xtest','cviceni', 1)")
query("INSERT INTO lectures(name, lector, nonterminal) VALUES ('Cvičení 2. - hospoda', 'xtest', 'cislo')")

query("DROP TABLE IF EXISTS assigments")
query("""CREATE TABLE assigments (assigment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        login char(8) NOT NULL,
                                        lecture_id INT NOT NULL,
                                        generated INT NULL,
                                        changed INT NULL,
                                        `text` TEXT,
                                        `response` TEXT,
                                        state INT NULL,
                                        points FLOAT)""")
query("INSERT INTO assigments(login, lecture_id, `text`, response, state) VALUES ('xtomec06', 1, 'generovany', 'odpoved', 1)")


#con.commit()  