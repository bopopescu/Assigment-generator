from ita_parser import Parser
from collections import namedtuple
from random import choice
from copy import copy
import builtins 
VERBOSE = False


class Generator:
    currentScope = None
    
    def __init__(self, rules):
        def convertRules(rules):
            def wrap(nonterm):
                def wrapper(*args, **kwargs):
                    # todo check number of params
                    # todo nacti defaultni params
                    localNonterm = nonterm
                    selected = choice( rules[ localNonterm ] )

                    glob = self.getScope()
                    loc = {}
                    print(localNonterm);
                    exec(selected.code, glob, loc)

                    retVal =  loc["implementation"](*args, **kwargs)

                    return retVal
                
                return wrapper
 
            calls = {}

            for nonterm in rules:
                calls[ nonterm ] = wrap(nonterm) 

            return calls
        
        self.rules = convertRules( rules )

    def getScope(self):
        if self.currentScope == None:
            self.currentScope = { '__builtins__' : builtins  }
        return self.currentScope

    def clearScope(self):
        self.currentScope = None

    def run(self, startNonterminal):
        self.clearScope()
        return self.rules[startNonterminal]()
        
        

p = Parser()

p.loadDir("base")
p.loadDir("cviceni3")

g = Generator( p.rules )
print(g.run("cviceni"))
