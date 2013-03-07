import database

class ModelException ( Exception ):
        pass

class BaseModel(object):
    data = None
    
    def __init__(self, row):
        self.data = row
    
    def __getattr__ (self, name):
        #print("chci precist %s"%name, dict(self.data))
        try:
            return self.data[name]
        except IndexError:
            raise AttributeError()

    @classmethod
    def getTable(cls):
        return cls.model+"s"

    def getPrimary(self):
        return self.data[ self.getPrimaryName() ]
    
    @classmethod
    def getPrimaryName(cls):
        return cls.model+"_id"
    
    def update(self,**kwargs):
        cmd = []
        values = []
        for key in kwargs:
            cmd.append("`%s` = ?" % key)
            values.append(kwargs[key])
        
        cmd = ", ".join(cmd)
        values.append(self.getPrimary())
        
        db = database.getConnection()        
        c = db.execute('UPDATE %s SET %s WHERE %s = ?' % (self.getTable(), cmd, self.getPrimaryName() ), values )    

        if not c.rowcount:
            raise ModelException("Chyba při ukládání")
            
    def remove(self):
        #todo hooks
        db = database.getConnection()        
        c = db.execute('DELETE FROM %s WHERE %s = ?' % (self.getTable(), self.getPrimaryName() ), self.getPrimary()  )            
        
        if not c.rowcount:
            raise UserException("Chyba při mazání cvičení")  
             
    @classmethod
    def get(cls, id):
        print('SELECT * FROM %s WHERE %s =?' % (cls.getTable(), cls.getPrimaryName() ))
        db = database.getConnection()        
        c = db.execute('SELECT * FROM %s WHERE %s =?' % (cls.getTable(), cls.getPrimaryName() ), (id,) )
        row = c.fetchone()
 
        return cls( row ) if row else None             