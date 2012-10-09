from bottle import route, run, view
from generator import Generator

@route('/')
@view("index")
def index():
    data = {}
    data["start"] = "{cviceni_prvni}"
    
    g = Generator()
    

    data["output"] = g.parse(data["start"])
    data["flags"] = g.flags

    data["files"] = {}
    for file in g.usedFiles.keys():
        with open("segmenty\\"+file) as f:
                content = f.readlines()
                f.close()
        data["files"][file] = content
        
    
    
    
    return data

run(host='localhost', port=8080)
