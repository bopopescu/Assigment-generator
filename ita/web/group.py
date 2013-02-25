from bottle import route, post, request, redirect, response, hook
import database
from helpers import template, msg, addMenu, form_renderer
from user import role, getUser

################################################################################
# model

class GroupException ( Exception ):
        pass

class Group:
    

    def __init__(self, row):
        self.data = row

    def __getattr__ (self, name):
        # pro pohodlnější přístup a nahrávání do formů 
        try:
            return self.data[name]
        except IndexError:
            raise AttributeError()

    @staticmethod
    def get(id):
        db = database.getConnection()        
        c = db.execute('SELECT * FROM groups WHERE group_id =?', (id,) )
        row = c.fetchone()
 
        return Group( row )
    
    @staticmethod
    def getAll():
        db = database.getConnection()        
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

@route('/groups')
@role('lector')
def list():
    """Seznam skupin"""
    groups = Group.getAll()
    return template("groups", {"groups" : groups } )

@route('/groups/edit/<group_id:int>', methods=['GET', 'POST'])
@role('lector')    
def edit(group_id):
    """Úprava specifické skupiny"""
    
    group = Group.get( group_id )
    
    form = GroupForm(request.POST, group)
    
    
    return template("groups_edit", {"group" : group, "form": form_renderer(form) } )    
    
###############################################################################
# callbacky

@hook("before_request")
def groupMenu():
    usr = getUser() 

    if usr and usr.inRole("lector"):
        addMenu("/groups","Skupiny",50)

