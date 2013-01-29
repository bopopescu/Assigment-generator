from ita_parser import Parser
from collections import namedtuple
from random import choice
from copy import copy
VERBOSE = False


class Generator:
    def __init__(self, rules):
        def convertRules(rules):
            def wrap(nonterm):
                def wrapper(*args, **kwargs):
                    # todo check number of params
                    localNonterm = nonterm
                    selected = choice( rules[ localNonterm ] )

                    glob = {}
                    loc = {}
                    print(selected.nonterm)
                    print(selected.info)
                    exec(selected.code, glob, loc)
                    return loc["implementation"](*args, **kwargs)
                return wrapper

            calls = {}

            for nonterm in rules:
                print("dipl "+nonterm)

                calls[ nonterm ] = wrap(nonterm) 

            return calls
        
        self.rules = convertRules( rules )

p = Parser()

p.loadDir("base")
#p.loadDir("cviceni3")

g = Generator( p.rules )
print(g.rules["cislo"](0,5))
