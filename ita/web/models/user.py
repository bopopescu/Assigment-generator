import database
from bottle import request
from hashlib import sha1

from database import query
from helpers import slug
from exception import *
from .base import BaseModel
from bottle import request


class Model(BaseModel):
    
    def __init__(self, row, lector = None):
        self.data = row        
        self.isLector = self.detectLector(lector)

    def detectLector(self, par):
        if par in (True, False): return par
        
        if "password" in dict(self.data).keys() : return True
        
        return False
        
    def inRole(self, role):
        roles = self.read("roles")
        return role in roles
        
    def addRole(self, role):
        if not self.isLector:
            raise NotImplementedError("Roles are supported only for lectors")
            
        roles = self.read("roles")
        roles.append(role)
        
        newRoles = ",".join(set(roles))
        c = query('UPDATE lectors SET roles=? WHERE login = ?', (newRoles, self.login))
        
    def removeRole(self, role):
        if not self.isLector:
            raise NotImplementedError("Roles are supported only for lectors")
            
        roles = self.read("roles")

        try:
            roles.remove(role)
            newRoles = ",".join(set(roles))
            c = query('UPDATE lectors SET roles=? WHERE login = ?', (newRoles, self.login))        
        except ValueError:
            # role neni nastavena
            pass
        
                     
        
    def getGroup(self):
        print(self.isLector , self.read("roles"))
        group_id = self.read("group_id") 
        # nutno importovat tady kvuli krizove zavislosti 
        from . import Group
        return Group.get( group_id )
 
    def read(self, key, default = None):
        if key == "roles":
            # pokud se jedná o lektora, má role přiděleny
            if self.isLector:  return self.data["roles"].split(",")

            #jinak o studenta                
            return ("student",)

        return self.data[key] or default
        
    def setPassword(self, psw):
        self.update( password = sha1(psw.encode('utf-8')).hexdigest() )
        

    @staticmethod
    def insertLector(login, psw, roles = "lector"):
        login = slug(login)
        
        psw = sha1(psw.encode('utf-8')).hexdigest()
                 
        try: 
            c = query('INSERT INTO lectors(login, roles, password) VALUES(?,?,?)', (login, roles or "", psw))
        except Exception as e:
            raise UserException("Takový uživatel již existuje")
                
        if not c.rowcount:
            raise UserException("Chyba při vkládání uživatele")
            
        return Model.get( login )    
        
    @staticmethod
    def insertStudent(login,  group_id = None):
        login = slug(login)
        
        try: 
            c = query('INSERT INTO students(login, group_id) VALUES(?,?)', (login, group_id, ))
        except Exception as e:
            raise UserException("Takový uživatel již existuje")
                
        if not c.rowcount:
            raise UserException("Chyba při vkládání uživatele")
            
        return Model.get( login )                                      

    def authenticate(self, psw = None):
        row = self.data

        if not row:
            raise UserException("Uživatel nenalezen")

        if self.isLector:
            if not psw:
                raise UserException("Uživatel není student - je potřeba heslo")                           
            
            if row["password"] != sha1(psw.encode('utf-8')).hexdigest():
                raise UserException("Špatné heslo")

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
        
    def remove(self):
        table = "lectors" if self.isLector else "students" 
        c = query('DELETE FROM %s WHERE login = ?' % table , (self.read("login"),)  )            
        
        if not c.rowcount:
            raise UserException("Chyba při mazání")        
        
    @classmethod
    def get(cls, id, isStudent = False):
        try:
            request._locals["userCache"]
        except KeyError:
            request._locals["userCache"] = {} 

        try:            
            return request._locals["userCache"][id]
        except KeyError:
            request._locals["userCache"][id] = None

            # zkusíme najít nejprve lektora a pak studenta            
            for table in ("lectors", "students") if not isStudent else ("lectors",):
                c = query('SELECT * FROM %s WHERE login = ?' % (table,), (id,) )
                row = c.fetchone()
                data = Model( row ) if row else None 
                request._locals["userCache"][id] = data
                if data: break
            
        return request._locals["userCache"][id]

    @staticmethod
    def getLectors():
        c = query('SELECT * FROM lectors',  )
        for row in c.fetchall():
            yield Model(row) 
     
    @staticmethod
    def getByGroup(group_id): 
        c = query('SELECT * FROM students WHERE group_id = ? ORDER BY login', (group_id,) )
        for row in c.fetchall():
            yield Model( row )
   