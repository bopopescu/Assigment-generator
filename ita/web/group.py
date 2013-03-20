from bottle import route, post, request, redirect, response, hook, HTTPResponse
import database
from helpers import *
from user import role, getUser, User, unauthorized

################################################################################
# model

from models import Group
    
        
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

@route('/groups/download/<group_id:int>', method=['GET'])
@role('lector')    
def download(group_id):
    """Stažení výsledků skupiny ve wis formátu"""
    
    user = getUser()
    group = Group.get( group_id )
    
    if not ( user.inRole("master") or group.lector == user.login):
        return unauthorized()

    headers = {}
    headers['Content-Type'] = "text/csv"
    headers['Content-Disposition'] = 'attachment; filename="%s.csv"' %  slug(group.name)

    #Formát CSV: 1. ID, 2. jméno, 3. login, 4. body, 5. celk.body, 6. datum, 7. login zadávajícího
    #při importu musí být zachováno pořadí sloupců, stačí vyplnit sloupce 3. a 4., případně 6.
    date = today()
    data = []
    results = group.getResults()
    for login, points in results.items():
        data.append(";;%s;%s;;%s;%s;" % (login, points, date, group.lector) );

    data = "\n".join(data)

    return HTTPResponse(data, **headers)
    
@route('/groups/edit/<group_id:int>', method=['GET', 'POST'])
@role('lector')    
def edit(group_id):
    """Úprava specifické skupiny včetně přidávání uživatelů"""
    
    #todo: is allowed
    
    group = Group.get( group_id )
    
    # vložení studenta
    if request.forms.get("add"):
        try:
            usr = User.insert( request.forms.get("add"), group_id )
            msg("Student %s vložen" % usr.login,"success")
        except Exception as e: 
            msg("Chyba při vkládání studenta - %s " % e,"error")                   
                

        redirect(request.path)
    
    # odstranění studenta
    if request.query.get("remove"):
        usr = User.get( request.query.get("remove") )

        if not usr:
            msg("Student nenalezen","error")
        elif usr.remove():
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
    
@route('/groups/delete/<group_id:int>', method=['GET', 'POST'])
def delete(group_id):
    """Smaže skupinu"""

    group = Group.get( group_id )

    answer = request.forms.get("answer") 
    if answer:
        if answer == "Ne": redirect("/groups")
        if answer == "Ano":
            group.remove()
            msg("Skupina smazána","success")
            redirect("/groups")
            
    return template("question", {"question":"Skutečně chcete smazat skupinu '%s'" % group.name } )            
    
###############################################################################
# callbacky

@hook("before_request")
def groupMenu():
    usr = getUser() 

    if usr and usr.inRole("lector"):
        addMenu("/groups","Skupiny",50)

