from bottle import route, post, request, redirect, response, hook
import database
from helpers import template, msg, addMenu, form_renderer
from user import role, getUser, User

################################################################################
# model

class LectureException ( Exception ):
        pass

class Lecture:

    def __init__(self, row):
        self.data = row

    def __getattr__ (self, name):
        # pro pohodlnější přístup a nahrávání do formů 
        if name == "assigments": return self.getAssigments()
        try:
            return self.data[name]
        except IndexError:
            raise AttributeError()

    def activate(self):
        self.update(state = 1)
    
    def deactivate(self):
        self.update(state = 0)        

    def update(self,**kwargs):
        cmd = []
        values = []
        for key in kwargs:
            cmd.append("`%s` = ?" % key)
            values.append(kwargs[key])
        
        cmd = ", ".join(cmd)
        values.append(self.lecture_id)
        
        db = database.getConnection()        
        c = db.execute('UPDATE lectures SET %s WHERE lecture_id = ?' % cmd, values )    

        if not c.rowcount:
            raise UserException("Chyba při vkládání uživatele")               

    def getAssigments(self):
        db = database.getConnection()        
        c = db.execute('SELECT * FROM users WHERE lecture_id =? ORDER BY login', (self.lecture_id,) )
        for row in c.fetchall():
            yield User( row["login"] )
        

    @staticmethod
    def get(id):
        db = database.getConnection()        
        c = db.execute('SELECT * FROM lectures WHERE lecture_id =?', (id,) )
        row = c.fetchone()
 
        return Lecture( row )
        
    @staticmethod
    def insert(name, lector):
        db = database.getConnection()        
        c = db.execute('INSERT INTO lectures(name, lector) VALUES (?,?)', (name,lector) )

        return Lecture.get( c.lastrowid )        
    
    
    
    @staticmethod
    def getAll(lector = None):
        db = database.getConnection()        
        if lector:
            c = db.execute('SELECT * FROM lectures WHERE lector = ?', (lector,) )
        else:
            c = db.execute('SELECT * FROM lectures WHERE 1' )            
        
        for row in c.fetchall():
            yield Lecture(row) 
    
        
################################################################################
# Formulář        
from wtforms import Form, BooleanField, TextField,SubmitField,TextAreaField,  validators

class LectureForm(Form):
    order = ["name","text", "submit"]
    name = TextField('Název', [validators.Length(min=1, max=40)])
    text = TextAreaField('Zadání')
    submit  = SubmitField('Uložit')
        
################################################################################
# stránky

@route('/lectures', method=['GET', 'POST'])
@role('lector')
def list():
    """Seznam cvičení"""
    
    usr = getUser() 
    
    if request.params.get("activate"):
        lec = Lecture.get( request.params.get("activate") )
        lec.activate()
        msg("Cvičení %s bylo zapnuto" % lec.name,"success")
        redirect(request.path)
        
    if request.params.get("deactivate"):
        lec = Lecture.get( request.params.get("deactivate") )
        lec.deactivate()
        msg("Cvičení %s bylo vypnuto" % lec.name,"success")
        redirect(request.path)        
    
    # vložení nového cvičení
    if request.forms.decode().get("add"):
        lec = Lecture.insert( request.forms.get("add"), usr.login )
        if lec:
            msg("Cvičení %s vytvořeno" % lec.name,"success")
            redirect("/lectures/edit/%i" % lec.lecture_id )
        else:
            msg("Chyba při vytváření cvičení","error")
            redirect(request.path)
        
    lectures = Lecture.getAll() if usr.inRole("master") else Lecture.getAll(usr.login) 
    
    return template("lectures", {"lectures" : lectures, "showLector": usr.inRole("master") } )

@route('/lectures/edit/<lecture_id:int>', method=['GET', 'POST'])
@role('lector')    
def edit(lecture_id):
    """Úprava specifické skupiny včetně přidávání uživatelů"""
    
    lecture = Lecture.get( lecture_id )
    form = LectureForm(request.forms.decode(), lecture)

    if request.method == 'POST' and form.validate():
        try:
            lecture.update( name = form.name.data, text = form.text.data )
            msg("Cvičení aktualizováno","success")
        except Exception as e:
            msg("Chyba při aktualizaci - %s" % e, "error")
        
        redirect(request.path)    
            
    return template("lectures_edit", {"lecture" : lecture, "form": form_renderer(form) } )    
    
###############################################################################
# callbacky

@hook("before_request")
def lectureMenu():
    usr = getUser() 

    if usr and usr.inRole("lector"):
        addMenu("/lectures","Cvičení",25)

