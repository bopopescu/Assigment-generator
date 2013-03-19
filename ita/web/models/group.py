from database import query
from .base import BaseModel
from .user import Model as User
from exception import *



class Model(BaseModel):
    model = "group"

    def __init__(self, row):
        self.data = row

    def __getattr__ (self, name):
        # pro pohodlnější přístup a nahrávání do formů 
        if name == "members": return self.getMembers()
        return super(Model, self).__getattr__(name)
 
    def getResults(self):
        logins = [member.login for member in self.getMembers() ]
        
        from assigment import Assigment
        sums = Assigment.getSums(logins)
        
        result = { login : 0 for login in logins }
        
        for sum in sums:
            #todo: docasny fix dokud se nebudou mazat pri uzivateli i vysledky
            if not sum["login"] in logins: continue 
            result[sum["login"]] = sum["points"] or 0
            
        return result 
        
        
    def getMembers(self):
        return User.getByGroup(self.group_id)
 
        
    @staticmethod
    def insert(name, lector):
        c = query('INSERT INTO groups(name, lector) VALUES (?,?)', (name,lector) )

        return Model.get( c.lastrowid )        
    
    @staticmethod
    def getAll(lector = None):
        if lector:
            c = query('SELECT * FROM groups WHERE lector = ?', (lector,) )
        else:
            c = query('SELECT * FROM groups WHERE 1' )            
        
        for row in c.fetchall():
            yield Model(row) 