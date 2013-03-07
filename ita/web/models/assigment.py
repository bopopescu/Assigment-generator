import database
from .base import BaseModel;

from .lecture import Model as Lecture

class Model(BaseModel):
    STATE_NEW = 0
    STATE_LOCKED = 1
    STATE_DONE = 2
    
    model = "assigment"

    def __getattr__ (self, name):
        if name == "locked": return (self.state or 0) > Model.STATE_NEW
        
        # pro pohodlnější přístup a nahrávání do formů 
        return super(Model, self).__getattr__(name)

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
        
        self.update( response = response, state = Model.STATE_LOCKED) 

    def unlock(self):
        """Odemkne"""
        self.update( state = Model.STATE_NEW )        
        
    def lock(self):
        self.update( state = Model.STATE_LOCKED )

    def rate(self, value):
        """Ohodnotí a zamkne zadání """
        #if self.state !=  Model.STATE_LOCKED: raise AssigmentException("Zadání nelze ohodnotit, protože není zamčené")
        
        self.update( points = value, state = Model.STATE_DONE)
    
    # statické třídy
    
    @staticmethod
    def getPending(lector):
        """Vrátí počet nevyřízená zadání"""
        lectures = Lecture.getAll(lector)
        ids = [ str(lecture.lecture_id) for lecture in lectures ]
        
        db = database.getConnection()
        
        c = db.execute('SELECT * FROM assigments WHERE (NOT state = ?) AND lecture_id IN (%s)' % (",".join(ids)) , (Model.STATE_NEW,) )
        
        for row in c.fetchall():
            yield Model(row)
            
    @staticmethod
    def getForLector(lector):
        """Vrátí zadaná cvičení """
        lectures = Lecture.getAll(lector)
        ids = [ str(lecture.lecture_id) for lecture in lectures ]
        
        db = database.getConnection()
        
        c = db.execute('SELECT * FROM assigments WHERE (NOT state = ?) AND lecture_id IN (%s)' % (",".join(ids)) , (Model.STATE_NEW,) )
        
        for row in c.fetchall():
            yield Model(row)            

    @staticmethod
    def getSums(logins):
        db = database.getConnection()
        
        c = db.execute('SELECT login, SUM(points) AS points FROM assigments WHERE login IN (%s)' % (",".join(map(lambda x: "'%s'"%x,logins ))))
        for row in c.fetchall():
            yield row
    
 
    @staticmethod
    # todo lepsí pojmenovani
    def getUnique(lecture_id, login):
        
        db = database.getConnection()        
        c = db.execute('SELECT * FROM assigments WHERE login = ? AND lecture_id = ?', (login,lecture_id) )
        row = c.fetchone()
 
        return Model( row ) if row else None
 
        
    @staticmethod
    def create(lecture_id, text, login):
        #todo
        db = database.getConnection()        
        c = db.execute('INSERT INTO assigments(login, `text`, lecture_id) VALUES (?, ?, ?)', (login, text, lecture_id) )

        return Model.get( c.lastrowid )        
    
    