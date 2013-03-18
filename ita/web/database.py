import sqlite3
import inspect
import config
from bottle import request

""" Zpřístupňuje DB, pro každý požadavek vytvoří jenom 1 spojení. """

def makeSQLiteconnection(handle):
    """ Vytvoří spojení a uloží na něj odkaz přes handle"""
    con = sqlite3.connect(handle)
    con.isolation_level = None
    con.row_factory = sqlite3.Row
    return con

def clearSQLiteconnection(handle):
    """Smaže spojení z požadavku"""
    request._dbConnection.pop(handle)


def getSQliteConnection(handle):
    """ Vrátí vytvořené spojení pokud existuje, pokud ne tak ho vytvoří """
    try:
      return request._dbConnection[handle]
    except AttributeError:
      request._dbConnection = {}
      request._dbConnection[handle] = makeSQLiteconnection(handle)
      return request._dbConnection[handle]  
    except KeyError:
      request._dbConnection[handle] = makeSQLiteconnection(handle) 
      return request._dbConnection[handle] 
    except:
      raise

        
if config.database["storage"] == "sqlite":   
    def getConnection():
        return  getSQliteConnection( config.database["path"] )
  
  
  
  

from hashlib import sha1

con = getConnection()
con.execute("DROP TABLE IF EXISTS users")
con.execute("CREATE TABLE users (login char(8)  PRIMARY KEY NOT NULL, password char(40) NULL,  roles char(20) NULL, group_id INT NULL)")
con.execute("INSERT INTO users VALUES ('xtomec06', NULL, NULL, 1)")
con.execute("INSERT INTO users VALUES ('xtest', '%s', 'lector' , NULL)" %  (sha1("test".encode('utf-8')).hexdigest(),) )
con.execute("INSERT INTO users VALUES ('master', '%s', 'master,lector' , NULL)" %  (sha1("test".encode('utf-8')).hexdigest(),) )

con.execute("DROP TABLE IF EXISTS groups")
con.execute("CREATE TABLE groups (group_id INTEGER PRIMARY KEY AUTOINCREMENT, name char(40) NOT NULL, lector char(8) NOT NULL )")
con.execute("INSERT INTO groups VALUES (NULL,'Skupina 01', 'xtest')")
con.execute("INSERT INTO groups VALUES (NULL,'Skupina náhradní', 'master')")

con.execute("DROP TABLE IF EXISTS lectures")
con.execute("CREATE TABLE lectures (lecture_id INTEGER PRIMARY KEY AUTOINCREMENT, name char(40) NOT NULL, lector char(8) NOT NULL, `nonterminal` char(32) , state INT NULL, shared INT NULL)")
con.execute("INSERT INTO lectures(name, lector,nonterminal, state) VALUES ('Cvičení 1. - logické operace', 'xtest','cviceni', 1)")
con.execute("INSERT INTO lectures(name, lector, nonterminal) VALUES ('Cvičení 2. - hospoda', 'xtest', 'cislo')")

con.execute("DROP TABLE IF EXISTS assigments")
con.execute("""CREATE TABLE assigments (assigment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        login char(8) NOT NULL,
                                        lecture_id INT NOT NULL,
                                        generated INT NULL,
                                        changed INT NULL,
                                        `text` TEXT,
                                        `response` TEXT,
                                        state INT NULL,
                                        points FLOAT)""")
con.execute("INSERT INTO assigments(login, lecture_id, `text`, response, state) VALUES ('xtomec06', 1, 'generovany', 'odpoved', 1)")


con.commit()  