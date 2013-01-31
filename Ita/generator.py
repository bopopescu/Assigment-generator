from ita_parser import Parser
from collections import namedtuple
from random import choice
from copy import copy
import builtins 
VERBOSE = False


class Generator:
    currentScope = None
    counter = None
    
    def __init__(self, rules):
        def convertRules(rules):
            """ Převede slovnik nonterminálů na funkce které náhodně vyberou jednu z možných implementací """

            def wrap(nonterm):
                def wrapper(*args, **kwargs):
                    localNonterm = nonterm
                    selected = choice( rules[ localNonterm ] )

                    glob = self.getScope()
                    loc = {}

                    # pro každé volání vytvoříme unikátní ID začínající názvem at se to dobře debuguje
                    randId = "".join( (nonterm, "_", str(self.counter) ) )
                    self.counter += 1

                    glob['_idStack'].append( randId )
                    
                    exec(selected.code, glob, loc)
                    retVal =  loc["implementation"](*args, **kwargs)

                    glob['_idStack'].pop()

                    return retVal
                
                return wrapper

             
            calls = {}

            # pro všechny nonterminály v zadaných pravidlech vytvoříme funkci která z nich bude náhodně vybírat
            for nonterm in rules:
                calls[ nonterm ] = wrap(nonterm) 

            return calls
        
        # samotné převedení
        self.rules = convertRules( rules )

    def getScope(self):
        """ Vrátí aktuální prostředí pro spouštění generovanýc funkcí
            V případě potřeby ho vytvoří.
        """
        if self.currentScope == None:
            # builtins, v pripade potrby tu jde orezat funkcionalita
            self.currentScope = { '__builtins__' : builtins,
                                  '_idStack' : []  
                                  }

            self.counter = 0

            # sablony jako volatelne funkce 
            self.currentScope.update( self.rules )
        return self.currentScope

    def clearScope(self):
        """ Zahodí aktuální prostředí, takže při další žádosti bude znovu vygenerováno """
        self.currentScope = None

    def run(self, startNonterminal):
        self.clearScope()
        return self.rules[startNonterminal]()
        
        

p = Parser()

p.loadDir("base")
p.loadDir("cviceni3")

g = Generator( p.rules )
print(g.run("cviceni"))
