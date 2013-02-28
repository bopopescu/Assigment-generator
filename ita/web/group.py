from bottle import route, post, request, redirect, response, hook
import database
from helpers import template, msg, addMenu, form_renderer
from user import role, getUser, User

################################################################################
# model

class GroupException ( Exception ):
        pass

class Group:
    

    def __init__(self, row):
        self.data = row

    def __getattr__ (self, name):
        # pro pohodlnější přístup a nahrávání do formů 
        if name == "members": return self.getMembers()
        try:
            return self.data[name]
        except IndexError:
            raise AttributeError()


    def update(self,**kwargs):
        cmd = []
        values = []
        for key in kwargs:
            cmd.append("%s = ?" % key)
            values.append(kwargs[key])
        
        cmd = ", ".join(cmd)
        values.append(self.group_id)
        
        db = database.getConnection()        
        c = db.execute('UPDATE groups SET %s WHERE group_id =?' % cmd, values )    

        if not c.rowcount:
            raise UserException("Chyba při vkládání uživatele")               

    def getMembers(self):
        db = database.getConnection()        
        c = db.execute('SELECT * FROM users WHERE group_id =? ORDER BY login', (self.group_id,) )
        for row in c.fetchall():
            yield User( row["login"] )
        

    @staticmethod
    def get(id):
        db = database.getConnection()        
        c = db.execute('SELECT * FROM groups WHERE group_id =?', (id,) )
        row = c.fetchone()
 
        return Group( row )
        
    @staticmethod
    def insert(name, lector):
        db = database.getConnection()        
        c = db.execute('INSERT INTO groups(name, lector) VALUES (?,?)', (name,lector) )

        return Group.get( c.lastrowid )        
    
    
    
    @staticmethod
    def getAll(lector = None):
        db = database.getConnection()        
        if lector:
            c = db.execute('SELECT * FROM groups WHERE lector = ?', (lector,) )
        else:
            c = db.execute('SELECT * FROM groups WHERE 1' )            
        
        for row in c.fetchall():
            yield Group(row) 
    
        
################################################################################
# Formulář        
from wtforms import Form, BooleanField, TextField,SubmitField, validators

class GroupForm(Form):
    order = ["name", "submit"]
    name = TextField('Název', [validators.Length(min=1, max=40)])
    submit  = SubmitField('Uložit')
        
################################################################################
# stránky

@route('/groups', method=['GET', 'POST'])
@role('lector')
def list():
    """Seznam skupin"""
    
    usr = getUser() 
    
    # vložení nové skupiny
    if request.forms.get("add"):
        grp = Group.insert( request.forms.decode().get("add"), usr.login )
        if grp:
            msg("Skupina %s vytvořena" % grp.name,"success")
            redirect("/groups/edit/%i" % grp.group_id )
        else:
            msg("Chyba při vytváření skupiny","error")
            redirect(request.path)
        
    groups = Group.getAll() if usr.inRole("master") else Group.getAll(usr.login) 
    
    return template("groups", {"groups" : groups, "showLector": usr.inRole("master") } )

@route('/groups/edit/<group_id:int>', method=['GET', 'POST'])
@role('lector')    
def edit(group_id):
    """Úprava specifické skupiny včetně přidávání uživatelů"""
    
    group = Group.get( group_id )
    
    # vložení studenta
    if request.forms.get("add"):
        usr = User( request.forms.get("add") )
        try:
            usr.insert( group_id )
            msg("Student %s vložen" % usr.login,"success")
        except Exception as e: 
            msg("Chyba při vkládání studenta - %s " % e,"error")                   
                

        redirect(request.path)
    
    # odstranění studenta
    if request.query.get("remove"):
        usr = User( request.query.get("remove") )

        if usr.remove():
            msg("Student %s odstraněn"% usr.login ,"success")
        else:
            msg("Student nenalezen","error")

        redirect(request.path)
        
    form = GroupForm(request.forms.decode(), group)
    
    if request.method == 'POST' and form.validate():
        try:
            group.update( name = form.name.data )
            msg("Skupina aktualizována","success")
        except Exception as e:
            msg("Chyba při aktualizaci - %s" % e, "error")
        
        redirect(request.path)    
            
    return template("groups_edit", {"group" : group, "form": form_renderer(form) } )    
    
###############################################################################
# callbacky

@hook("before_request")
def groupMenu():
    usr = getUser() 

    if usr and usr.inRole("lector"):
        addMenu("/groups","Skupiny",50)

