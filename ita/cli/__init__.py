import sys
import os
from . import reloader as cli_reloader
from . import maker as cli_maker

def dieWithHelp(detail = None, defaults = None):
    """Vytiskne chybovou hlášku v případě nerozpoznanéího formátu parametrů"""
    #todo: stderr
    
    if detail:
        print(detail)
    else:
        print("Nerozpoznany format parametru, musi byt ve formatu '-nazev[ hodnota]'")
    
    if defaults:
        print("Defaultní parametry:")
        print(sys.argv[0].split(os.sep)[-1], end=" ")
        for key, value  in defaults.items():
            if type(value) is bool and value == True:
                print("-%s" % (key,), end=" ")
            else:
                print("-%s %s" % (key,value), end=" ")
        print()
    sys.exit(1)

def getParams(defaults):
    """Přečte parametry z příkazové řádky, pokud se vyskytne nějaký který nezná (=nemá defaultní hodnotu) tak vyhodí chybu"""

    # precteme parametry bez nazvu souboru  
    params = sys.argv[1:]
    parsedParams = {}
    
    i = 0
    paramCount = len(params)
    while i < paramCount:
        param = params[i]
        i += 1
        
        # parametr je ve formátu "-nazev[ hodnota]"
        if param[0] != "-": dieWithHelp()

        #ziskame parametr a jeho hodnotu, pokud je jenom pritomen, je jeho hodnota true
        name = param[1:]
    
        if name == "help": dieWithHelp("Napoveda", defaults)
        
        #je to posledni parametr, nebo nasledujici zacina pomlckou
        if (i >= paramCount) or (params[i][0] == "-"):
            # parametr je jenom přitomny, povazujeme ho za true
            value = True
        else:
            # hodnota je nasledujici parametr 
            value = params[i]
            i += 1
        
        if name in parsedParams: dieWithHelp("Duplicitní parametr %s" % name)
        parsedParams[name] = value


    for key, value in parsedParams.items():
        # kontrola jestli nemáme zadaný některý parametr navíc
        if not key in defaults: dieWithHelp("Neocekavany parametr %s \nDefaultni parametry %s" % (key, str(defaults)) )  
        # nastavíme novou hodnotu
        defaults[key] = value

    return defaults    

def reloader():
    params = getParams({"nonterminal" : "cislo", "interval" : 1, "path" : "sablony", "toAscii":True})
    params["interval"] = int(params["interval"])
    
    cli_reloader.run(**params);
    
def maker():
    params = getParams({"nonterminal" : "cislo", "source" : None, "count" : None, "path" : "sablony",})
    if params["count"]: params["count"] = int(params["count"])
    
    if not  params["count"] and not  params["source"]:
        dieWithHelp("Either count or source must be specified")
    
    cli_maker.run(**params);    
    
    
    
    
__ALL__ = ["reloader", "maker", "params"]    