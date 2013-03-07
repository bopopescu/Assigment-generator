import database
from .base import BaseModel;


class Model(BaseModel):

    model = "lecture"
    
    def activate(self):
        self.update(state = 1)
    
    def deactivate(self):
        self.update(state = 0)     
        
    def generate(self):
        """Vrátí vygenerované zadání pro toto cvičení """
        from ita import ita_parser
        from ita import generator
    
        p = ita_parser.Parser()
    
        p.loadDir("ita/sablony")
    
        print(p.files)
    
        g = generator.Generator( p.rules )
        
        return g.run(self.nonterminal)
        
        
    @staticmethod
    def insert(name, lector):
        db = database.getConnection()        
        c = db.execute('INSERT INTO lectures(name, lector) VALUES (?,?)', (name,lector) )

        return Model.get( c.lastrowid )        
    
    @staticmethod
    def getAvailable(lector):
        """Výpis aktivních cvičení daného cvičícího.
         Ten se typicky získává ze skupiny, do které je přihlášen student"""
        db = database.getConnection()        
        c = db.execute('SELECT * FROM lectures WHERE lector = ? AND state != 0', (lector,) )

        for row in c.fetchall():
            yield Model(row) 

    
    @staticmethod
    def getAll(lector = None):
        db = database.getConnection()        
        if lector:
            c = db.execute('SELECT * FROM lectures WHERE lector = ?', (lector,) )
        else:
            c = db.execute('SELECT * FROM lectures WHERE 1' )            
        
        for row in c.fetchall():
            yield Model(row) 
    