import database
from bottle import request
from hashlib import sha1

from database import query
from exception import *
from .base import BaseModel
from bottle import request

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

    @staticmethod
    def insert(login,  group_id = None, roles = None, psw = None):
        if psw:
            psw = sha1(psw.encode('utf-8')).hexdigest()         
        try: 
            c = query('INSERT INTO users(login, group_id, roles, password) VALUES(?,?,?,?)', (login, group_id, roles, psw))
        except Exception as e:
            print(e)
            raise UserException("Takový uživatel již existuje")
                
        if not c.rowcount:
            raise UserException("Chyba při vkládání uživatele")
            
        return Model.get( login )                              

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
            request._locals["userCache"]
        except KeyError:
            request._locals["userCache"] = {} 

        try:            
            return request._locals["userCache"][id]
        except KeyError:
            request._locals["userCache"][id] = super(Model,cls).get(id)
            
        return request._locals["userCache"][id]

    @staticmethod
    def getLectors():
        c = query('SELECT * FROM users WHERE NOT password IS NULL',  )
        for row in c.fetchall():
            yield Model(row) 
     
    @staticmethod
    def getByGroup(group_id): 
        c = query('SELECT * FROM users WHERE group_id = ? ORDER BY login', (group_id,) )
        for row in c.fetchall():
            yield Model( row )
   