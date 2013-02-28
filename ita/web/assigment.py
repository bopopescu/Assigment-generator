from bottle import route, post, request, redirect, response, hook
import database
from helpers import template, msg, addMenu, form_renderer
from user import role, getUser, User

################################################################################
# model

class AssigmentException ( Exception ):
        pass

class Assigment:
    def __init__(self, row):
        self.data = row

    def __getattr__ (self, name):
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

    @staticmethod
    def get(id):
        db = database.getConnection()        
        c = db.execute('SELECT * FROM assigments WHERE assigments_id =?', (id,) )
        row = c.fetchone()
 
        return Assigment( row )
        
    @staticmethod
    def create(lecture_id, text, for_usr):
        #todo
        db = database.getConnection()        
        c = db.execute('INSERT INTO lectures(name, lector) VALUES (?,?)', (name,lector) )

        return Lecture.get( c.lastrowid )        
    
    @staticmethod
    def getAvailable(lector):
        db = database.getConnection()        
        c = db.execute('SELECT * FROM lectures WHERE lector = ? AND state != 0', (lector,) )

        for row in c.fetchall():
            yield Lecture(row) 

    
    @staticmethod
    def getByLecture(lecture_id):
        db = database.getConnection()        
        if lector:
            c = db.execute('SELECT * FROM lectures WHERE lector = ?', (lector,) )
        else:
            c = db.execute('SELECT * FROM lectures WHERE 1' )            
        
        for row in c.fetchall():
            yield Lecture(row) 
    
        
################################################################################
# stránky

@route('/assigments', method=['GET', 'POST'])
@role('student')
def list():
    """Seznam aktivních cvičení, na které se student může přihlásit"""
    
    usr = getUser() 

    # zjistíme v jaké jsme skupině
    grp = usr.getGroup()
    #todo: assert group != None
      
    assigments = Assigment.getAvailable( grp.lector_id ) 
    
    return template("assigments", {"assigments" : assigments, } )

@route('/assigments/<assigment_id:int>', method=['GET', 'POST'])
@role('student')    
def show(assigment_id):
    """Zobrazení zadání """

    assigment = Assigment.get( assigment_id )
    # todo check allowed

    if request.method == 'POST' and form.validate():
        try:
            lecture.update( name = form.name.data, text = form.text.data )
            msg("Cvičení aktualizováno","success")
        except Exception as e:
            msg("Chyba při aktualizaci - %s" % e, "error")
        
        redirect(request.path)    
            
    return template("assigments_show", {"assigment" : assigment } )    
    
###############################################################################
# callbacky

@hook("before_request")
def lectureMenu():
    usr = getUser() 

    if usr and usr.inRole("student"):
        addMenu("/assigments","Zadání",25)

