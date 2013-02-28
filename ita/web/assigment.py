from bottle import route, post, request, redirect, response, hook
import database
from helpers import template, msg, addMenu, form_renderer
from user import role, getUser, User
from lecture import Lecture

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
        
    def getGroup(self):
        from group import Group
        return Group.get( self.group_id )
        
    def respond(self, response):
        """Nahraje zadání a zamkneho proti úpravám"""
        #todo: updatnout i changed
        if self.locked: raise AssigmentException("Zadání je zamčené proti úpravám")
        
        self.update( response = response, locked = 1) 


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
    
    @staticmetod
    def getPending(lector):
        """Vrátí počet nevyřízená zadání"""
        #todo
        pass
                        

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

