import database
from bottle import request
from hashlib import sha1

import database
from exception import *
from .base import BaseModel

_cache = {}



class Model(BaseModel):
    model = "user"
        
    def inRole(self, role):
        roles = self.read("roles")
        return role in roles
        
    def getGroup(self):
        group_id = self.read("group_id") 
        # nutno importovat tady kvuli krizove zavislosti 
        from . import Group
        return Group.get( group_id )
 
    def read(self, key, default = None):
        if key == "roles":
            #defaultní role je student
            roles = self.data[key] or "student"
            return roles.split(",")

        return self.data[key] or default

    def insert(self, group_id):         
        db = database.getConnection()       
        try: 
            c = db.execute('INSERT INTO users(login, group_id) VALUES(?,?)', (self.login,group_id))
        except Exception as e:
            raise UserException("Takový uživatel již existuje")
                
        if not c.rowcount:
            raise UserException("Chyba při vkládání uživatele")                      

    def authenticate(self, psw = None):
        row = self.data

        if not row:
            raise UserException("Uživatel nenalezen")

        if psw:
            #cvicici
            if row["password"] != sha1(psw.encode('utf-8')).hexdigest():
                raise UserException("Špatné heslo")
        else:
            if row["password"]:
                raise UserException("Uživatel není student")                           

        s = request.environ.get('beaker.session')
        s['userLogin'] = self.login
        s.save()



    @staticmethod
    def logout():
        s = request.environ.get('beaker.session')
        
        for item in ("userLogin", "role","group_id"):
            if item in s: s.pop(item)

        s.save()

    @classmethod
    def getPrimaryName(cls):
        return "login"


    @staticmethod
    def getCurrent():
        s = request.environ.get('beaker.session')
        login =  s.get('userLogin',None)
        if not login: return None;
        
        return Model.get(login)
        
    @classmethod
    def get(cls, id):
        try:
            return _cache[id]
        except KeyError:
            _cache[id] = super(Model,cls).get(id)
            
        return _cache[id]
     
    @staticmethod
    def getByGroup(group_id): 
        db = database.getConnection()  
        c = db.execute('SELECT * FROM users WHERE group_id = ? ORDER BY login', (group_id,) )
        for row in c.fetchall():
            yield Model( row )
   