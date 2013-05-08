from database import query
from .base import BaseModel;
from exception import *
from .lecture import Model as Lecture

import datetime
import time

class Model(BaseModel):
    STATE_NEW = 0
    STATE_LOCKED = 1
    STATE_DONE = 2
    
    model = "assigment"

    def __getattr__ (self, name):
        if name == "locked": return (self.state or 0) > Model.STATE_NEW
        if name in ("changed", "generated"):
             print(self.data[name])
             return datetime.datetime.fromtimestamp(int(self.data[name])).strftime('%Y-%m-%d %H:%M') if self.data[name] else ""
        return super(Model, self).__getattr__(name)

    def update(self, **kwargs):
        """ Aktualizuje záznam, ale přidá k němu záznam o změně """
        if not "changed" in kwargs:
            kwargs["changed"] = str(time.time()).split('.')[0]
            super(Model, self).update(**kwargs)
        
        return super(Model, self).update(**kwargs)

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
        """Vrátí nevyřízená zadání"""
        lectures = Lecture.getAll(lector)
        ids = [ str(lecture.lecture_id) for lecture in lectures ]
        
        if len(ids) == 0: raise StopIteration
        
        c = query('SELECT * FROM assigments WHERE (state = ?) AND lecture_id IN (%s) ORDER BY changed ASC' % (",".join(ids)) , (Model.STATE_LOCKED,) )
        
        for row in c.fetchall():
            yield Model(row)
            
    @staticmethod
    def getPendingCount(lector):
        """Vrátí počet nevyřízených zadání"""
        lectures = Lecture.getAll(lector)
        ids = [ str(lecture.lecture_id) for lecture in lectures ]
    
        if len(ids) == 0: return 0

        c = query('SELECT COUNT(*) AS cnt FROM assigments WHERE (state = ?) AND lecture_id IN (%s)' % (",".join(ids)) , (Model.STATE_LOCKED,) )
        
        return c.fetchone()["cnt"]
            
    @staticmethod
    def getSilent(lector):
        """Vrátí zadání, která nepotřebují vyřídit"""
        lectures = Lecture.getAll(lector)
        ids = [ str(lecture.lecture_id) for lecture in lectures ]
        
        if len(ids) == 0: raise StopIteration
        
        c = query('SELECT * FROM assigments WHERE (NOT state = ?) AND lecture_id IN (%s)  ORDER BY state ASC, generated DESC' % (",".join(ids)) , (Model.STATE_LOCKED,) )
        
        for row in c.fetchall():
            yield Model(row)            
            
    @staticmethod
    def getForLector(lector):
        """Vrátí zadaná cvičení """
        lectures = Lecture.getAll(lector)
        ids = [ str(lecture.lecture_id) for lecture in lectures ]
        
        if len(ids) == 0: raise StopIteration
        
        c = query('SELECT * FROM assigments WHERE (NOT state = ?) AND lecture_id IN (%s)' % (",".join(ids)) , (Model.STATE_NEW,) )
        
        for row in c.fetchall():
            yield Model(row)            

    @staticmethod
    def getSums(logins):
        c = query('SELECT login, SUM(points) AS points FROM assigments WHERE login IN (%s)' % (",".join(map(lambda x: "'%s'"%x,logins ))))
        for row in c.fetchall():
            yield row
    
 
    @staticmethod
    # todo lepsí pojmenovani
    def getUnique(lecture_id, login):
        
        c = query('SELECT * FROM assigments WHERE login = ? AND lecture_id = ?', (login,lecture_id) )
        row = c.fetchone()
 
        return Model( row ) if row else None
 
        
    @staticmethod
    def create(lecture_id, text, login):
        now = str(time.time()).split('.')[0]
        c = query('INSERT INTO assigments(login, generated `text`, lecture_id) VALUES (?, ?, ?, ?)', (login, now, text, lecture_id) )
        return Model.get( c.lastrowid )        
    
    