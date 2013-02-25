from bottle import route, post, request, redirect, response, hook
import database
from helpers import template, msg, addMenu
from user import role, getUser

################################################################################
# model

class GroupException ( Exception ):
        pass

class Group:
    

    def __init__(self, row):
        self.data = row
    
    @staticmethod
    def getAll():
        db = database.getConnection()        
        c = db.execute('SELECT * FROM groups WHERE 1' )
        
        # yield se chova zvlasne bo kod je spousten v contextu sablony... 
        groups = []
        
        for row in c.fetchall():
            groups.append( Group(row) )
            
        return groups
    
        
################################################################################
# stránky


@route('/groups')
@role('lector')
def list():
    groups = Group.getAll()
    return template("groups", {"groups" : groups } )
    
###############################################################################
# callbacky

@hook("before_request")
def groupMenu():
    usr = getUser() 

    if usr and usr.inRole("lector"):
        addMenu("/groups","Skupiny",50)

