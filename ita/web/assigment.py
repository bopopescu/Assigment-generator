from bottle import route, post, request, redirect, response, hook, HTTPError
import database
from helpers import template, msg, addMenu, form_renderer
from user import role, getUser, User
from lecture import Lecture
from group import Group

################################################################################
# model

class AssigmentException ( Exception ):
        pass

class Assigment:
    STATE_NEW = 0
    STATE_LOCKED = 1
    STATE_DONE = 2

    def __init__(self, row):
        self.data = row

    def __getattr__ (self, name):
        if name == "locked": return (self.state or 0) > Assigment.STATE_NEW
        
        # pro pohodlnější přístup a nahrávání do formů 
        try:
            return self.data[name]
        except IndexError:
            raise AttributeError()

    def isAllowed(self, usr = None):
        if not usr: usr = getUser()
        if user.inRole("lector"): return True
        if user.login == self.login: return True

        return False
        
    def getLecture(self):
        from lecture import Lecture
        return Lecture.get( self.lecture_id )
        
    def respond(self, response):
        """Nahraje zadání a zamkneho proti úpravám"""
        #todo: updatnout i changed
        if self.locked: raise AssigmentException("Zadání je zamčené proti úpravám")
        
        self.update( response = response, state = Assigment.STATE_LOCKED) 

    def unlock(self):
        """Odemkne"""
        self.update( state = Assigment.STATE_NEW )        
        
    def lock(self):
        self.update( state = Assigment.STATE_LOCKED )

    def rate(self, value):
        """Ohodnotí a zamkne zadání """
        if self.state !=  Assigment.STATE_LOCKED: raise AssigmentException("Zadání nelze ohodnotit, protože není zamčené")
        
        self.update( points = value, state = Assigment.STATE_DONE)
    

    def update(self,**kwargs):
        cmd = []
        values = []
        for key in kwargs:
            cmd.append("`%s` = ?" % key)
            values.append(kwargs[key])
        
        cmd = ", ".join(cmd)
        values.append(self.lecture_id)
        
        db = database.getConnection()        
        c = db.execute('UPDATE assigments SET %s WHERE assigment_id = ?' % cmd, values )    

        if not c.rowcount:
            raise UserException("Chyba při ukládání")    

    
    # statické třídy
    
    @staticmethod
    def getPending(lector):
        """Vrátí počet nevyřízená zadání"""
        lectures = Lecture.getAll(lector)
        ids = [ str(lecture.lecture_id) for lecture in lectures ]
        
        db = database.getConnection()
        
        c = db.execute('SELECT * FROM assigments WHERE (NOT state = ?) AND lecture_id IN (%s)' % (",".join(ids)) , (Assigment.STATE_NEW,) )
        
        for row in c.fetchall():
            yield Assigment(row) 
                        

    @staticmethod
    def get(id):
        db = database.getConnection()        
        c = db.execute('SELECT * FROM assigments WHERE assigment_id =?', (id,) )
        row = c.fetchone()
 
        return Assigment( row ) if row else None
 
    @staticmethod
    # todo lepsí pojmenovani
    def getUnique(lecture_id, login):
        
        db = database.getConnection()        
        c = db.execute('SELECT * FROM assigments WHERE login = ? AND lecture_id = ?', (login,lecture_id) )
        row = c.fetchone()
 
        return Assigment( row ) if row else None
 
        
    @staticmethod
    def create(lecture_id, text, login):
        #todo
        db = database.getConnection()        
        c = db.execute('INSERT INTO assigments(login, `text`, lecture_id) VALUES (?, ?, ?)', (login, text, lecture_id) )

        return Assigment.get( c.lastrowid )        
    
    
        
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

