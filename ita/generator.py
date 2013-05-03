from collections import namedtuple
from random import choice
from copy import copy
import builtins 
from . import VERBOSE
from . import MODULE_PATH


class Generator:
    currentScope = None
    counter = None
    
    def __init__(self, parser):
        def convertRules(rules):
            """ Převede slovnik nonterminálů na funkce které náhodně vyberou jednu z možných implementací """

            def wrap(nonterm):
                def wrapper(*args, **kwargs):
                    localNonterm = nonterm
                    selected = choice( rules[ localNonterm ] )

                    glob = self.getScope()
                    loc = {}

                    # pro každé volání vytvoříme unikátní ID
                    # začínáme názvem, at se to dobře debuguje
                    randId = "".join( (nonterm, "_", str(self.counter) ) )
                    self.counter += 1

                    glob['_idStack'].append( randId )
                    # provedeme kód
                    exec(selected.code, glob, loc)
                    # kod vytvoril funkci implementace
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
        self.rules = convertRules( parser.getRules() )

    def getScope(self):
        """ Vrátí aktuální prostředí pro spouštění generovanýc funkcí
            V případě potřeby ho vytvoří
        """
        if not self.currentScope:
            
            self.currentScope = {
                                # builtins, v pripade potreby tu jde orezat funkcionalita
                                '__builtins__' : builtins, 
                                # používá se pro ukládání "callstacku" šablon
                                '_idStack' : [],
                                # absolutní cesta k modulu, hodí se pro načítání souborů
                                "MODULE_PATH" : MODULE_PATH,
                                }

            self.counter = 0

            # sablony jako volatelne funkce 
            self.currentScope.update( self.rules )
        return self.currentScope

    def clearScope(self):
        """ Zahodí aktuální prostředí, takže při další žádosti bude znovu vygenerováno """
        self.currentScope = None

    def run(self, startNonterminal):
        """ Spustí daný nonterminál """
        self.clearScope()
        if not startNonterminal in self.rules: raise RuntimeError("Startovaci nonterminal %s nenalezen" % startNonterminal)
        return self.rules[startNonterminal]()
        
        

