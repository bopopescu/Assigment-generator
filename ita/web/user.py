import database
from bottle import route, post, request, redirect, response, hook
from helpers import *

from decorator import decorator

from models import User
from exception import *


###############################################################################
# funkce pro komunikaci s vnějškem

def role( *allowed ):
    """ Dekorátor pro oprávnění rolí"""
    def wrapper(f, *args, **kwargs):
        usr = User.getCurrent();

        if not usr:
            msg("Pro přístup se musíte nejdříve přihlásit")
            redirect("/login")
        
        for role in usr.read('roles', tuple() ):
            if role in allowed:
                return f(*args, **kwargs)
        msg("Nemáte dostatečná oprávnění", "error")
        return unauthorized()
        
    return decorator(wrapper)
        

def getUser():
    return User.getCurrent()    
        
################################################################################
# stránky

@route("/chosenOne",  method=['GET', 'POST'])
@role('master', 'lector')
def profil():
    """Nastavení hesla"""
    
    usr = getUser()
    
    psw = request.forms.get("psw")
    
    if psw:
        pswControl = request.forms.get("pswControl")
        if psw == pswControl:
            usr.setPassword(psw)
            msg("Hesla nastaveno","success")
        else:
            msg("Hesla se neshodují","error") 
        redirect("/chosenOne")
        
    return template("profil", {"user":usr} )

@route('/lectors', method=['GET', 'POST'])
@role('master')
def list():
    """Seznam lektorů """
    
    
    if request.params.get("promote"):
        lec = User.get( request.params.get("promote") )
        lec.addRole("master")
        msg("Lektor %s byl povýšen" % lec.login,"success")
        redirect(request.path)
        
    if request.params.get("degrade"):
        lec = User.get( request.params.get("degrade") )
        lec.removeRole("master")
        msg("Lektor %s byl ponížen :-)" % lec.login,"success")
        redirect(request.path)       
    
    # vložení nového lektora
    if request.forms.get("add"):
        login =  request.forms.decode().get("add")
        usr = User.insertLector(login, psw = login )
        if usr:
            msg("Lektor '%s' vytvořen" % usr.login, "success")
            msg("Heslo pro nového lektora bylo nastaveno na '%s'" % usr.login, "info")
        else:
            msg("Chyba při vytváření lektora","error")
        redirect("/lectors")
        
    lectors = User.getLectors() 
    
    return template("lectors", {"lectors" : lectors } )
    
@route('/lectors/delete/<login>', method=['GET', 'POST'])
def delete(login):
    """Smazání lektora"""

    usr = User.get( login )
    
    if login == getUser().login:
        msg("Nelze smazat sama sebe", "error")
        redirect("/lectors")
        

    answer = request.forms.get("answer") 
    if answer:
        if answer == "Ne": redirect("/lectors")
        if answer == "Ano":
            usr.remove()
            msg("Uživatel smazán", "success")
            redirect("/lectors")
            
    return template("question", {"question":"Skutečně chcete smazat lektora '%s'" % usr.login } )      


############
# správa přihlášení atp

@route('/login')
def login():
    if getUser(): redirect("/")
        
    lectorLogin  = request.params.get("lector")	
    return template("login", {"lectorLogin" : lectorLogin } )    
    
@post('/login-post')
def loginSubmit():
    data = request.forms                                                                         
    usr = User.get( data["login"] )

    if not usr:
     msg("Uživatel '%s' nenalezen" % data["login"], "error")
     redirect('/login' + ("?lector=1" if data.get("password") else "") )

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
        
        addMenu("/logout","Odhlásit se (%s)" % usr.login, 100)
    
        # vsem krome studentu umoznime pristup 
        if not usr.inRole("student"):
            addMenu("/chosenOne", "Profil", 97)
            
        if usr.inRole("master"):
            addMenu("/lectors", "Cvičící", 95)
        
    else:    
        addMenu("/login","Přihlásit se", 100)    


