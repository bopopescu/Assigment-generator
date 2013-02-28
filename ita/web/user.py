import database
from bottle import route, post, request, redirect, response, hook
from helpers import template, msg, addMenu, safeASCII

from hashlib import sha1

from decorator import decorator


################################################################################
# model

class UserException ( Exception ):
        pass

class User:
    def __init__(self, login):
        self.login = safeASCII(login)

    
    def chckPassword(self, psw):
        return True
        
    def inRole(self, role):
        roles = self.get("roles", tuple() )
        return role in roles
        
    def getGroup(self):
        group_id = self.get("group_id") 
        # nutno importovat tady kvuli krizove zavislosti 
        from group import Group
        return Group.get( group_id )
 
    def get(self, key, default = None):
        s = request.environ.get('beaker.session')
        if s['userLogin'] == self.login:
            return s.get(key, default)
        
        row = self.getRow()
        return row[key] if key in row else default  

        
    def remove(self):         
        db = database.getConnection()        
        c = db.execute('DELETE FROM users WHERE login = ?', (self.login,))
        return c.rowcount     

    def insert(self, group_id):         
        db = database.getConnection()       
        try: 
            c = db.execute('INSERT INTO users(login, group_id) VALUES(?,?)', (self.login,group_id))
        except Exception as e:
            raise UserException("Takový uživatel již existuje")
                
        if not c.rowcount:
            raise UserException("Chyba při vkládání uživatele")                      

    #todo: cached            
    def getRow(self):
        db = database.getConnection()        
        c = db.execute('SELECT * FROM users WHERE login = ?', (self.login,))
        row = c.fetchone()             
            
        return row
         
        

    def authenticate(self, psw = None):
        row = self.getRow()

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
        s['group_id'] = row["group_id"]
        # defaultni role je student
        s['roles'] = row["roles"].split(",") if row["roles"] else ["student"]
        s.save()



    @staticmethod
    def logout():
        s = request.environ.get('beaker.session')
        
        for item in ("userLogin", "role"):
            if item in s: s.pop(item)

        s.save()   
    
        
################################################################################
# stránky

@route('/login')
def login():
    lectorLogin  = request.params.get("lector")	
    return template("login", {"lectorLogin" : lectorLogin } )    
    
@post('/login-post')
def loginSubmit():
    data = request.forms                                                                         
    usr = User( data["login"] )

    try: 
        usr.authenticate( data.get("password") )
        #redirect
        msg("Úspěšně přihlášen", "success")
        redirect( "/" ) #request.path if request.path != "/login-post" else "/"
    except UserException as e:
        msg("Došlo k chybě při přihlašování - %s" % e, "error")
        redirect('/login' + ("?lector=1" if data.get("password") else "") )
    
@route('/logout')
def logout():
    User.logout()
    msg("Odhlášení bylo úspěšné", "success")
    redirect("/")

@route('/unauthorized')
def unauthorized():
    response.status = 401 # unauthorized    
    return template("unauthorized")
    
    
###############################################################################
# callbacky

@hook("before_request")
def userMenu():
    usr = getUser() 
    if usr:
        addMenu("/logout","Odhlásit se (%s)"%usr.login,100)
    else:    
        addMenu("/login","Přihlásit se", 100)    

###############################################################################
# funkce pro komunikaci s vnějškem

def role( *allowed ):
    """ Dekorátor pro oprávnění rolí"""
    def wrapper(f, *args, **kwargs):
        s = request.environ.get('beaker.session')
        
        login =  s.get('userLogin',None)
        if not login:
            msg("Pro přístup se musíte nejdříve přihlásit")
            redirect("/login")
        
        for role in s.get('roles', tuple() ):
            if role in allowed:
                return f(*args, **kwargs)
        msg("Nemáte dostatečná oprávnění", "error")
        return unauthorized()
        
    return decorator(wrapper)
        

def getUser():
    s = request.environ.get('beaker.session')
    
    login =  s.get('userLogin',None)

    return User( login ) if login else None
