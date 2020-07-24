from bottle import route, post, request, redirect, response, hook, HTTPError, HTTPResponse
import database
from helpers import template, msg, addMenu, form_renderer
from user import role, getUser, User
from lecture import Lecture
from group import Group

################################################################################
# model
from models import Assigment
from models.base import ModelException

        
################################################################################
# stránky

############### Rozhraní pro lektora 
@route('/assigments-lector')
@role('lector')
def list():
    """Seznam odevzdaných zadání"""
    
    usr = getUser() 
    #todo pro maina zobrazit všechny

    # zjistíme v jaké jsme skupině
    assigments = Assigment.getPending( usr.login ) 
    silent = Assigment.getSilent( usr.login ) 
    
    return template("assigments_lector", {"assigments" : assigments, "silent" : silent, "showLector" : usr.inRole("main") } )



@route('/assigments-lector/<assigment_id:int>', method=['GET', 'POST'])
@role('lector')
def assigmentRate(assigment_id):
    """Úprava a obodování zadání"""
    usr = getUser() 

    assigment = Assigment.get( assigment_id ) 
    if not assigment: return HTTPError(404, "Cvičení nebylo nalezeno")
    #todo if ???: return HTTPError(403, "Nemáte oprávnění")

        

    if request.method == 'POST':
        action = request.forms.get("action")
        if (not action) or  (not action in ("lock", "rate", "unlock")): HTTPError(400, "Neznámá akce")
        print("----------action", action)
        try:
            if action == "lock":
                assigment.lock()
                msg("Řešení bylo zamčeno", "success")
            elif action == "rate":
                assigment.rate(  request.forms.get("points") )
                msg("Řešení bylo ohodnoceno", "success")
            elif action == "unlock":
                assigment.unlock()
                msg("Řešení bylo odemčeno", "success")            
        except ModelException as e:
            msg("Chyba při manipulaci: %s" %s, "error")             
        redirect('/assigments-lector')
        return

    return template("assigments_rate", {"assigment" : assigment } )

@route('/assigments-lector/download/<assigment_id:int>', method=['GET', 'POST'])
@role('lector')
def assigmentDownload(assigment_id):
    """Stažení zadání"""
    usr = getUser() 

    assigment = Assigment.get( assigment_id ) 
    if not assigment: return HTTPError(404, "Cvičení nebylo nalezeno")
    #todo if ???: return HTTPError(403, "Nemáte oprávnění")

    headers = {}
    headers['Content-Type'] = "text/txt"
    headers['Content-Disposition'] = 'attachment; filename="%s.asm"' % assigment.login

    data = assigment.response

    return HTTPResponse(data, **headers)

@route('/assigments-lector/counter')
def assigmentCount():
    """ Vrácení počtu nevyřízených zadání, použito pro aktualizaci v menu"""
    usr = getUser() 
    if (not usr) or (not usr.inRole("lector")):
        return {"status" : "error", "count" : "!"}
        
    return { "status" : "ok", "count" : Assigment.getPendingCount(usr.login) }        

############### Rozhraní pro studenta
 
@route('/assigments', method=['GET', 'POST'])
@role('student')
def list():
    """Seznam aktivních cvičení, na které se student může přihlásit"""
    
    usr = getUser() 

    # zjistíme v jaké jsme skupině
    grp = usr.getGroup()
    #todo: assert group != None
      
    lectures = Lecture.getAvailable( grp.lector ) 
    
    return template("assigments_student", {"lectures" : lectures, } )

@route('/assigments/<lecture_id:int>', method=['GET', 'POST'])
@role('student')    
def show(lecture_id):
    """Zobrazení a odevzdávání zadání """
                  
    usr = getUser()
    lec = Lecture.get( lecture_id );
    
    if not lec: return HTTPError(404, "Cvičení nebylo nalezeno")

    if not lec.isActive():
        msg("Cvičení není aktivní", "error")
        redirect("/assigments");
                      
    assigment = Assigment.getUnique( lecture_id, usr.login ) 
    
    if not assigment:
        assigment = Assigment.create( lec.lecture_id, lec.generate(), usr.login )
        msg("Cvičení bylo vygenerováno", "success")
        
    if request.method == 'POST' and request.files.response:
        try:        
            assigment.respond( request.files.response.file.read() )
            msgTxt = "Řešení bylo úspěšně odesláno";

            if request.is_xhr:
                 return HTTPResponse({"type": "success", "msg": msgTxt});
            msg(msgTxt ,"success")
            
        except Exception as e:
           msgTxt = "Chyba při odesílání řešení - %s" % e 
           
           if request.is_xhr:
                 return HTTPResponse({"type": "error", "msg": msgTxt});
                 
           msg(msgTxt, "error")
        
        redirect(request.path)
            
    return template("assigments_show", {"assigment" : assigment, "lecture": lec } )    
    
###############################################################################
# callbacky

@hook("before_request")
def lectureMenu():
    usr = getUser() 

    if usr and usr.inRole("student"):
        addMenu("/assigments","Zadání",25)
        
    if usr and usr.inRole("lector"):
        addMenu("/assigments-lector","Zadání",10, Assigment.getPendingCount(usr.login) )        

