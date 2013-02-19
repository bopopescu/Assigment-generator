import database
from bottle import route, request, redirect

from decorator import decorator

#con = database.getConnection()


def role( *allowed ):
    """ Dekorátor pro roli """
    def wrapper(f, *args, **kwargs):
        s = request.environ.get('beaker.session')
        role = s.get('role',None)
        
        if not role in allowed:
            print("redirect")
            redirect("/login")
        
        return f(*args, **kwargs)    
    return decorator(wrapper)
        
        
        
################################################################################
# stránky

@route('/login')
def prihlaseni():
    s = request.environ.get('beaker.session')
    s['role'] = "student" if s.get('role',"host") == "host" else "host"
    s.save()
    
    return 'Pridelena role %s' % s['role']
        