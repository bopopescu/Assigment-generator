from database import query
from .base import BaseModel;


class Model(BaseModel):

    model = "lecture"
    
    def activate(self):
        self.update(state = 1)
    
    def deactivate(self):
        self.update(state = 0)     
        
    def isActive(self):
        return self.data["state"] == 1
        
    def generate(self):
        """Vrátí vygenerované zadání pro toto cvičení """
        from ita import Loader, Parser, Generator
        l = Loader().add("sablony")
        p = Parser( l )
        g = Generator( p )

        return g.run(self.nonterminal)
        
        
    @staticmethod
    def insert(name, lector):
        c = query('INSERT INTO lectures(name, lector) VALUES (?,?)', (name,lector) )

        return Model.get( c.lastrowid )        
    
    @staticmethod
    def getAvailable(lector):
        """Výpis aktivních cvičení daného cvičícího.
         Ten se typicky získává ze skupiny, do které je přihlášen student"""
        c = query('SELECT * FROM lectures WHERE lector = ? AND state != 0', (lector,) )

        for row in c.fetchall():
            yield Model(row) 

    
    @staticmethod
    def getAll(lector = None):
        if lector:
            c = query('SELECT * FROM lectures WHERE lector = ?', (lector,) )
        else:
            c = query('SELECT * FROM lectures WHERE 1' )            
        
        for row in c.fetchall():
            yield Model(row) 
    