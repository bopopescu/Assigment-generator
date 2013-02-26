import sqlite3
import inspect
import config
from bottle import request

""" Zpřístupňuje DB, pro každý požadavek vytvoří jenom 1 spojení. """

def makeSQLiteconnection(handle):
    """ Vytvoří spojení a uloží na něj odkaz přes handle"""
    con = sqlite3.connect(handle)
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


class SQLitePlugin(object):
    ''' Based on plugin tutorial 
        http://bottlepy.org/docs/dev/plugindev.html#plugin-example-sqliteplugin
     '''
    name = 'sqlite'
    api = 2

    def __init__(self, autocommit=True, keyword='db'):
         self.dbfile = config.database["path"]
         self.autocommit = autocommit
         self.keyword = keyword

    def setup(self, app):
        ''' Make sure that other installed plugins don't affect the same
            keyword argument.'''
        for other in app.plugins:
            if not isinstance(other, SQLitePlugin): continue
            if other.keyword == self.keyword:
                raise PluginError("Found another sqlite plugin with "\
                "conflicting settings (non-unique keyword).")

    def apply(self, callback, context):
        # Override global configuration with route-specific values.
        conf = context.config.get('sqlite') or {}
        dbfile = conf.get('dbfile', self.dbfile)
        autocommit = conf.get('autocommit', self.autocommit)

        keyword = conf.get('keyword', self.keyword)

        # Test if the original callback accepts a 'db' keyword.
        # Ignore it if it does not need a database handle.
        args = inspect.getargspec(context.callback)[0]

        if keyword not in args:
            return callback

        def wrapper(*args, **kwargs):
            #todo: omezzit připojení na jeden
            
            # Connect to the database
            db = getSQliteConnection(dbfile)
            # This enables column access by name: row['column_name']
            # Add the connection handle as a keyword argument.
            kwargs[keyword] = db

            try:
                rv = callback(*args, **kwargs)
                if autocommit: db.commit()
            except sqlite3.IntegrityError as e:
                db.rollback()
                raise HTTPError(500, "Database Error", e)
            finally:
                db.close()
                clearSQLiteconnection(dbfile)
            return rv

        # Replace the route callback with the wrapped one.
        return wrapper
        
        
if config.database["storage"] == "sqlite":   
    def getConnection():
        return  getSQliteConnection( config.database["path"] )
    DBPlugin = SQLitePlugin        
  
  
  

from hashlib import sha1

con = getConnection()
con.execute("DROP TABLE IF EXISTS users")
con.execute("CREATE TABLE users (user_id INTEGER PRIMARY KEY AUTOINCREMENT,  login char(8) NOT NULL, password char(40) NULL,  roles char(20) NULL, group_id INT NULL)")
con.execute("INSERT INTO users VALUES (NULL, 'xtomec06', NULL, NULL, 1)")
con.execute("INSERT INTO users VALUES (NULL, 'xtest', '%s', 'lector' , NULL)" %  (sha1("test".encode('utf-8')).hexdigest(),) )

con.execute("DROP TABLE IF EXISTS groups")
con.execute("CREATE TABLE groups (group_id INTEGER PRIMARY KEY AUTOINCREMENT, name char(40) NOT NULL, lector char(8) NOT NULL )")
con.execute("INSERT INTO groups VALUES (NULL,'Skupina', 'test')")

con.commit()  