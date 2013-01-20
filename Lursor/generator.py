import os
import re
import codecs
import warnings
import tokenize
from collections import namedtuple
from random import choice
from copy import copy
VERBOSE = True


NonTermTuple = namedtuple('NonTermTuple', 'params program text')

##        class callableLines:
##            def __init__(self, content):
##                self._content = content
##                self._current = 0
##                self._size = len(content) 
##                
##            def __call__(self):
##                if self._current == self._size: raise StopIteration;
##                toReturn = content[ self._current ]
##                self._current += 1
##                
##                return toReturn

def test():
    a = 1+2

class Generator:

    def __init__(self):
        self.nonterminals = {}
        pass
    
    def loadDir(self, path):
        files = os.listdir(path)
        for file in files:
            if not file.endswith(".fragment"):
                if VERBOSE: print("skipping ".ljust(10)+file)
                continue
            
            if VERBOSE: print("opening ".ljust(10)+file)
            
            with codecs.open(path+"/"+file,'r', 'utf-8') as f:
                content = f.readlines()

            try:
               self.parse(content)
            except SyntaxError as e:
                #todo: udelat z toho warn
                raise
                raise SyntaxError(" ".join( ("File", file,"-", e.msg) ) )


    def _addNonterminal(self, nonterm, text, program, params):
        """ Prida zaznam do seznamu nonterminalu """
        tup = NonTermTuple(params, program, text)

        if not nonterm in self.nonterminals:
            self.nonterminals[nonterm] = []
            
        self.nonterminals[nonterm].append(tup)


    def expand(self, text, scope = {}):
        """ scope jsou lokalni data, funkce a parametry zadane pri volani"""
        def replace(match):
            """Lokální funkce pro nahrazovani parametru"""
            matches = match.groupdict()

            # jmeno ktere nahrazujeme
            name = matches["name"]

            # parametry ktere budou použity při volání 
            outParams = matches["params"]
            if outParams != None:
                try:
                    _globals = {}
                    _locals = scope
                    # vyhodnotíme je v rámci naší local
                    outParams = eval(outParams, _globals, _locals)
                except Exception as e:
                    raise SyntaxError(" ".join("Error parsing parameters for %s"%name,"(%s)"%outParams, "-", e.msg) )
            else:
                outParams = ()

            print("parametry pro %s"%name, outParams)
            
            #todo params prevest reference ze scope do loklani kopie outParams

            # nejdrive zkontrolujeme jestli existuje v lokalnim scope (pokud existuje)
            # todo: check jsetli se str() provedl ok
            if scope != None and name in scope:
                # existuje
                # pokud je to funkce, predame ji parametry a vratime vysledek
                if callable(scope[name]):
                    return str( scope[name]( *outParams ) )
                # neni to funkce, tak z toho zkusime udelat text
                return str(scope[name])

            # nenašli jsme ve scope, zkusime načíst nonterminaly
            candidates = self.getNonterms(name, outParams)

            print("kandidatu",len(candidates))

            # zkousime dokud nenajdeme, nebo nedojdou kandidáti
            while len(candidates) > 0:
                c = choice(candidates)
                candidates.remove(c)
                
                ntParams, program, text = c

                # predame do volane sablony vstupni parametry
                nextScope = {}
                
                for i in range( len(ntParams["order"]) ):
                    name = ntParams["order"][i]
                    try:
                        value = outParams[i]
                    except IndexError:
                        value = ntParams["defaults"][name]

                    nextScope[name] = value

                nextScope["_params"] = outParams
                    
                if program != None:
                    _globals = {}
                    _locals = nextScope

                    print("volame program s",_locals)

                    try:
                        eval(program, _globals, _locals)
                    except ImportError:
                        # pokud je ImportError pri spusteni tak preskocime
                        # tim ho vyradime z uvahy a zkusime dalsi v poradi
                        continue

                
                return self.expand(text, nextScope)
            
            # dosli vsichni kandidati
            raise LookupError("Couldn't find rule to expand %s with params %a" % (name, outParams) )
        ### end replace
        
        expr = re.compile("\\{(?P<name>[a-zA-Z_][a-zA-Z0-9_]*)[ ]*(?P<params>\([^}]*\))?[ ]*\\}")
        while True:
            # pouze jedna (nejlevejsi zmena najednou
            text, changes = expr.subn(replace,text,1)
            if changes == 0:
                break
        return text

        

    def getNonterms(self, nonterm, inParams):
        """Vrátí náhodně seřazené pole použitelných nonterminalů"""
        if not nonterm in self.nonterminals: raise NameError("No definitions for nonterminal '%s'" % (nonterm,) )
        #todo: filtrovat podle poctu parametru

        # vracime melkou kopii, protoze se z toho seznamu mazou kandidati co nelze pouzit
        return copy(self.nonterminals[nonterm])
    

    def parse(self, content):
        """Zpracuje text souboru"""
        nonterm = None

        # dict nezachovava poradi vlozenych klicu, tak musime uchovavat oboje
        params = {"order":[], "defaults":{}, "all": False }

        text = []
        code = []

        currentBlock = None

        lineNo = 0

        tmp = bytes(content[lineNo],"utf-8")
        if tmp.startswith( codecs.BOM_UTF8 ):
            content[lineNo] = str( tmp[ len(codecs.BOM_UTF8): ],"utf-8") 

        # prvni radka musi byt nonterm
        try:
            
            tag,nonterm = map(lambda x: x.strip(), content[lineNo].split(":",2))

           
            if tag != "nonterminal" : raise SyntaxError(" ".join( ("line: "+str(lineNo),"first line must contain nonterminal", "-", "'%s' found"%tag)) );
        except ValueError:
            raise SyntaxError(" ".join("line: "+str(lineNo),"unknown format"));

        

        for line in content[1:]:
            lineNo += 1
            try:
                tag,data = map(lambda x: x.strip(), line.split(":",2))

                if tag in ("text", "code", "params"):
                    if tag == "params":
                        items = [item for item in map( lambda x: x.strip(),  data.split(",") ) ];

                        for item in items:
                            if item.strip() == "*":
                                params["all"] = True
                                continue
                            
                            try:
                                name, value = map(lambda x: x.strip(), item.split("=",2) )
                                value = eval(value, {})
                                params["defaults"][ name ] = value
                            except SyntaxError:
                                raise SyntaxError(" ".join("Error parsing default value for parameter %s"%name, "-", e.msg) )
                            except ValueError:
                                name = item.strip()
                                params["defaults"][ name ] = None

                            params["order"].append(name);
                                
                        continue

                    # jedna se o specialni nazev, text za dvojteckou musi byt prazdny
                    if len(data) > 0: raise SyntaxError(" ".join(("line: "+str(lineNo),"no text allowed after ':'")));

                    if tag == "text":
                        currentBlock = text
                        continue
                    
                    if tag == "code":
                        currentBlock = code
                        continue
                # zadny z nasich tagu, ignorujeme
                    
            except ValueError:
                # pri explodovani tagu doslo k chybe, takze nejspis radka neobsahuje dvojtecku
                pass

            # nevime kam patri aktualni radka
            if currentBlock == None: raise SyntaxError(" ".join(("line: "+str(lineNo),"line doesn't belong to any block")));

            currentBlock.append(line)

        if VERBOSE:
            print("parsed nonterminal '%s': %d text, %d code, %d params "%(nonterm, len(text), len(code), len(params["order"])))

        text = "".join(text)
        program = None
        
        if len(code) > 0:
            program = compile("\n".join(code),"<string>","exec")
            
        self._addNonterminal(nonterm, text, program, params)
            


g = Generator()
g.loadDir("base")
g.loadDir("cviceni3")

print( g.expand("{cviceni}"));
