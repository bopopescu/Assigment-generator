import database
from bottle import route, post, request, redirect, response, hook
from helpers import template, msg, addMenu

from decorator import decorator


################################################################################
# model

class UserException ( Exception ):
        pass

class User:
    def __init__(self, login):
        self.login = login

    
    def chckPassword(self, psw):
        return True

    def authenticate(self, psw = None):
        if psw:
            # cvicici
            pass 
        else:
            #student
            db = database.getConnection()        
            c = db.execute('SELECT * FROM students WHERE login = ?', (self.login,))
            row = c.fetchone()
            
            if not row:
                raise UserException("Student nenalezen")


            s = request.environ.get('beaker.session')
            s['userLogin'] = self.login
            s['role'] = "student"
            s.save()
    
        
        db = database.getConnection()        
        #c = db.execute('SELECT title, content FROM posts WHERE id = ?', (post_id,))
        row = c.fetchone()

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
    return template("login")    
    
@post('/login-post')
def loginSubmit():
    data = request.forms
    usr = User( data["login"] )
    
    try: 
        usr.authenticate()
        #redirect
        msg("Úspěšně přihlášen", "success")
        redirect( request.path if request.path != "/login-post" else "/" )
    except UserException as e:
        msg("Došlo k chybě při přihlašování - %s" % e, "error")
        redirect("/login")
    
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
        role = s.get('role',None)
        
        if not role in allowed:
            if role == None:
                msg("Pro přístup se musíte nejdříve přihlásit")
                redirect("/login")
            else:
                msg("Nemáte dostatečná oprávnění", "error")
                redirect("/unauthorized")
                
        
        return f(*args, **kwargs)    
    return decorator(wrapper)
        

def getUser():
    s = request.environ.get('beaker.session')
    
    login =  s.get('userLogin',None)

    return User( login ) if login else None
