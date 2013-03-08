from bottle import route, post, request, redirect, response, hook, HTTPError
import database
from helpers import template, msg, addMenu, form_renderer
from user import role, getUser, User
from lecture import Lecture
from group import Group

################################################################################
# model
from models import Assigment


        
################################################################################
# stránky

############### Rozhraní pro lektora 
@route('/assigments-lector')
@role('lector')
def list():
    """Seznam odevzdaných zadání"""
    
    usr = getUser() 

    # zjistíme v jaké jsme skupině
    assigments = Assigment.getPending( usr.login ) 
    
    return template("assigments_lector", {"assigments" : assigments, "showLector" : usr.inRole("master") } )



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
        if action == "lock":
            assigment.lock()
            msg("Řešení bylo zamčeno", "success")
        elif action == "rate":
            assigment.rate(  request.forms.get("points") )
            msg("Řešení bylo ohodnoceno", "success")
        elif action == "unlock":
            assigment.unlock()
            msg("Řešení bylo odemčeno", "success")            
            
        redirect('/assigments-lector')

    return template("assigments_rate", {"assigment" : assigment } )




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
        
    if request.method == 'POST':
        try:        
            assigment.respond( request.forms.decode().get("response") )
            msg("Řešení bylo odesláno","success")
        except Exception as e:
            msg("Chyba při odesílání řešení - %s" % e, "error")
            raise e
        
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
        addMenu("/assigments-lector","Zadání",10)        

