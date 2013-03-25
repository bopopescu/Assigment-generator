from bottle import route, post, request, redirect, response, hook
import database
from helpers import template, msg, addMenu, form_renderer
from user import role, getUser, unauthorized

################################################################################
# model
from models import Lecture
        
################################################################################
# Formulář        
from wtforms import Form, BooleanField, TextField,SubmitField,TextAreaField,  validators

class LectureForm(Form):
    order = ["name","nonterminal", "submit"]
    name = TextField('Název', [validators.Length(min=1, max=40)])
    nonterminal = TextField('Startovací nonterminál', [validators.Length(min=1, max=40)])
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
    if request.forms.get("add"):
        lec = Lecture.insert( request.forms.decode().get("add"), usr.login )
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
    """Úprava specifické cvičení"""
    
    lecture = Lecture.get( lecture_id )
    form = LectureForm(request.forms.decode(), lecture)
    user = getUser()

    if not ( user.inRole("master") or lecture.lector == user.login):
        return unauthorized()

    if request.method == 'POST' and form.validate():
        try:
            lecture.update( name = form.name.data, nonterminal = form.nonterminal.data )
            msg("Cvičení aktualizováno","success")
        except Exception as e:
            msg("Chyba při aktualizaci - %s" % e, "error")
        
        redirect(request.path)    
        
    try:
        text =  lecture.generate() 
    except Exception as e:
        text = "Došlo k chybě : \n %s      \n %s" % (type(e).__name__, e)        
         
    return template("lectures_edit", {"lecture" : lecture, "form": form_renderer(form), "text": text } )    

@route('/lectures/delete/<lecture_id:int>', method=['GET', 'POST'])
def delete(lecture_id):
    """Smaže cvičení"""

    lecture = Lecture.get( lecture_id )
    user = getUser()

    if not ( user.inRole("master") or lecture.lector == user.login):
        return unauthorized()


    answer = request.forms.get("answer") 
    if answer:
        if answer == "Ne": redirect("/lectures")
        if answer == "Ano":
            lecture.remove()
            msg("Cvičení smazáno","success")
            redirect("/lectures")
            
    return template("question", {"question":"Skutečně chcete smazat cvičení '%s'" % lecture.name } )    
    
###############################################################################
# callbacky

@hook("before_request")
def lectureMenu():
    usr = getUser() 

    if usr and usr.inRole("lector"):
        addMenu("/lectures","Cvičení",25)

