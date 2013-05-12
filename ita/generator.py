from collections import namedtuple
from random import random
from math import floor
from copy import copy
import builtins 
from . import VERBOSE
from . import MODULE_PATH


class GeneratorException(Exception):
    def __init__(self, exception, trace):
        self.exception = exception
        self.trace = trace

    def __str__(self):
        ret = []
        ret.append("Exception: " + str(self.exception) )
        ret.append("Traceback (most recent call last):")
        for trace in self.trace:
            path, nonterm, lineno, line = trace
            ret.append("Source %s, rule for %s, line %s" % (path, nonterm, str(lineno) if lineno else "unknown") )
            if line : ret.append("\t %s" % line.strip() )
        
        return "\n".join(ret)


class Generator:
    currentScope = None
    counter = None
    
    def __init__(self, parser):
        self.trace = []

        def convertRules(rules):
            """ Převede slovnik nonterminálů na funkce které náhodně vyberou jednu z možných implementací """

            def wrap(nonterm):
                def wrapper(*args, **kwargs):
                    localNonterm = nonterm
                    localRules = copy(rules[ localNonterm ])
                    
                    #zkoušíme aplikovat nonterminál dokud nedosáhneme cíle 
                    while len(localRules) > 0:
                    
                        whichRule = floor (len(localRules)*random() )
                        selected =  localRules.pop(whichRule)

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
                        
                        #vložime zaznam to zasobniku
                        record =  ["curPath", "curNonterm", "lineno", "line" ]
                        self.trace.append( record )
                        
                        
                        
                        try:
                            retVal =  loc["implementation"](*args, **kwargs)
                        except NotImplementedError as e:
                            # pravdilo chce abychom ho nepoužili, pokračujeme tedy dále
                            self.trace.pop()
                            glob['_idStack'].pop()
                            
                            # pravidlo může vynutit ukončení více úrovní
                            # v tom případě pošleme signál výš
                            try: 
                                if e.limit > 0:
                                    e.limit -=1
                                    raise e
                            except AttributeError:
                                #exception nema nastaven limit
                                pass 
                                
                            # jinak pokračujeme v hledání
                            continue;
                            
                        except Exception as e:
                            # nastala chyba, prevedeme záznam do čitelné podoby
                            import inspect
                            
                            record[0] = loc["implementation"]._ita_path
                            record[1] = loc["implementation"]._ita_nonterminal
                            
                            record[2] = None
                            record[3] = None
    
                            try:
                                lineno = inspect.getframeinfo(inspect.trace()[1][0]).lineno
                                originalLine = loc["implementation"]._ita_originalLines[ lineno ]
                                record[2] = originalLine
                                record[3] = loc["implementation"]._ita_originalContent[ originalLine ]
                            except Exception:
                                # v případě že nemáme stack nebo není přistupná řádka
                                pass
                            raise e
                            
                        # skončili jsme, mužeme záznam odstranit
                        self.trace.pop()
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
        if not startNonterminal in self.rules: raise NameError("Startovaci nonterminal %s nenalezen" % startNonterminal)
        
        try:
            retVal = self.rules[startNonterminal]()
        except Exception as e:
            raise GeneratorException(e, self.trace)
        
        return  retVal
        
        

