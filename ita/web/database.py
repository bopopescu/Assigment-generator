import sqlite3
import mysql.connector
import inspect
import config
from bottle import request, hook

""" Zpřístupňuje DB, pro každý požadavek vytvoří jenom 1 spojení. """

#############################################################
# Sqlite
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
    args = list(args)
    
    if args[0].startswith("CREATE TABLE"):
        # dotaz je v dialektu MySQL
        args[0] = args[0].replace("AUTO_INCREMENT","AUTOINCREMENT")
        # SQLite nepodporuje charset
        args[0] = args[0].replace("CHARACTER SET utf8 COLLATE utf8_czech_ci ","")

    try:
        c = request._dbCursor
    except AttributeError:
        c = getConnectionSQLite().cursor()
        request._dbCursor = c
    return c.execute(*args, **kwargs)

#############################################################
# MySQL

class MySQLDictCursor(mysql.connector.cursor.MySQLCursor):
    def dictonize(self, row):
        columns = self.description 
        row = self._row_to_python(row)
        return {columns[index][0]:column for index, column in enumerate(row)}     

    def fetchone(self):
        row = self._fetch_row()
        if row:
            return self.dictonize(row)
        return None

    def fetchall(self):
        if not self._have_unread_result():
            raise errors.InterfaceError("No result set to fetch from.")
        res = []
        (rows, eof) = self._connection.get_rows()
        self._rowcount = len(rows)
        for i in range(0, self._rowcount):
            res.append(self.dictonize(rows[i]))
        self._handle_eof(eof)
        return res

def getConnectionMySQL():
    """ Vrátí existující / vytvoří spojení pro tento požadavek. 
        Podporuje pouze 1 připojení!  """
    try:
        return request._dbConnection
    except AttributeError:
        params = {          
            'host': "localhost",
            'database': "ita",
            'user': "",
            'password': "",
            'charset': "utf8",
            'use_unicode': True,
            'get_warnings': True,
            'autocommit': True, 
            'port': 3306}
        params.update(config.database)

        params.pop("storage") # odstranime parametr ktery neni platny pro spojeni        
        if "reset" in params : params.pop("reset") 
        
        con = mysql.connector.Connect(**params)
        con.isolation_level = None  # vypnutí relací 
        request._dbConnection = con 
        return request._dbConnection 

def queryMySQL(*args, **kwargs):
    args = list(args)
    # fix SQLite dialect > MySql
    # sice %s umozni i formatovani ale zase se tluce s vestavenym % formatovanim
    args[0] = args[0].replace("?","%s")
    
    
    try:
        c = request._dbCursor
    except AttributeError:
        c = MySQLDictCursor( getConnectionMySQL() )
        request._dbCursor = c
    
    c.execute(*args)

    return c 


################################################################################


################################################################################

        
if config.database["storage"] == "sqlite":
    query = querySQLite
elif config.database["storage"] == "mysql":
    query = queryMySQL
else:
    raise NotImplemented("Typ DB není podporován")

  
@hook("after_request")
def cleanUp():
    """Smaže spojení z požadavku
        Totožné pro SQLite i pro MySQL
    """
    try:
        request._dbConnection.close()
        del request._dbConnection
    except: pass
    
    try:
        request._dbCursor.close()
        del request._dbCursor
    except: pass



from hashlib import sha1

if "reset" in config.database and  config.database["reset"]:
    query("DROP TABLE IF EXISTS lectors")
    query("DROP TABLE IF EXISTS students")
    query("DROP TABLE IF EXISTS groups")
    query("DROP TABLE IF EXISTS lectures")
    query("DROP TABLE IF EXISTS assigments")
    
query("""CREATE TABLE IF NOT EXISTS lectors (login char(8) PRIMARY KEY NOT NULL,
                             password char(40) NULL,
                             roles char(20) NULL)""")

query("""CREATE TABLE IF NOT EXISTS students (login char(8) PRIMARY KEY NOT NULL,
                             group_id INT NULL)""")



query("""CREATE TABLE IF NOT EXISTS groups (group_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                              name char(40) CHARACTER SET utf8 COLLATE utf8_czech_ci NOT NULL,
                              lector char(8) NOT NULL )""")



query("""CREATE TABLE IF NOT EXISTS lectures (lecture_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                                name char(40) CHARACTER SET utf8 COLLATE utf8_czech_ci NOT NULL,
                                lector char(8) NOT NULL,
                                `nonterminal` char(32),
                                state INT NULL,
                                shared INT NULL)""")

query("""CREATE TABLE IF NOT EXISTS assigments (assigment_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                                        login char(8) NOT NULL,
                                        lecture_id INT NOT NULL,
                                        generated INT NULL,
                                        changed INT NULL,
                                        `text` TEXT,
                                        `response` TEXT,
                                        state INT NULL,
                                        points FLOAT)""")                                    

if "reset" in config.database and  config.database["reset"]:                                    
    query("INSERT INTO lectors VALUES ('xtest', '%s', 'lector')" %  (sha1("test".encode('utf-8')).hexdigest(),) )
    query("INSERT INTO lectors VALUES ('main', '%s', 'lector,main')" %  (sha1("test".encode('utf-8')).hexdigest(),) )                                    
    query("INSERT INTO students VALUES ('xtomec06', 1)")                                    
    query("INSERT INTO groups VALUES (NULL,'Skupina 01', 'xtest')")
    query("INSERT INTO groups VALUES (NULL,'Skupina náhradní', 'main')")

    query("INSERT INTO lectures(name, lector,nonterminal, state) VALUES ('Cvičení 1. - logické operace', 'xtest','cviceni3', 1)")
    query("INSERT INTO lectures(name, lector, nonterminal) VALUES ('Cvičení 2. - hospoda', 'xtest', 'cislo')")
    query("INSERT INTO assigments(login, lecture_id, `text`, response, state) VALUES ('xtomec06', 1, 'generovany', 'odpoved', 1)")
    

    
    
   