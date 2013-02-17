#! /usr/bin/python3
from bottle import route, run, view
from generator import Generator
import codecs

@route('/')
@view("index")
def index():
    data = {}
    data["start"] = "{cviceni_prvni}"
    
    g = Generator()
    

    data["output"] = g.parse(data["start"])
    data["flags"] = g.flags
    print(g.flags)
    data["files"] = {}
    for file in g.usedFiles.keys():
       with codecs.open("segmenty/"+file,'r', 'utf-8') as f:
            content = f.readlines()
            f.close()
       data["files"][file] = content
        
    
    
    
    return data

run(host='0.0.0.0', port=8080)
