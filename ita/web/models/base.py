from database import query

class ModelException ( Exception ):
        pass

class BaseModel(object):
    data = None
    
    def __init__(self, row):
        self.data = row
    
    def __getattr__ (self, name):
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
        
        c = query('UPDATE %s SET %s WHERE %s = ?' % (self.getTable(), cmd, self.getPrimaryName() ), values )    

        if not c.rowcount:
            raise ModelException("Chyba při ukládání")
            
    def remove(self):
        #todo hooks
        c = query('DELETE FROM %s WHERE %s = ?' % (self.getTable(), self.getPrimaryName() ), (self.getPrimary(),)  )            
        
        if not c.rowcount:
            raise ModelException("Chyba při mazání")  
             
    @classmethod
    def get(cls, id):
        c = query('SELECT * FROM %s WHERE %s = ?' % (cls.getTable(), cls.getPrimaryName() ), (id,) )
        row = c.fetchone()
 
        return cls( row ) if row else None             