import re

# pro učely VERBOSE
import ita


def makeException(_msg, _lineno = None, file = None ):
    e = SyntaxError()

    e.msg  = _msg
    e.lineno = _lineno
    e.filename = file

    return e


class Rule:
    def __init__(self, nonterm, code, params = None, info = None):
        self.nonterm = nonterm
        self.code = code
        self.params = params
        self.info = info



#############################################################################    

class Parser:

    def __init__(self, loader):
        self.rules = {}
        self.processedPaths = {}
        self.loader = loader
        
        #automaticky načteme data, pokud je k dispozici parser
        if self.loader:
            self.parse()
        
    
    def parse(self):
        for path, data in self.loader:
            self._parse( data, path )
        return self
    
    def _parse(self, content, path):
        curLine = 0

        #todo: handle bom

        endLine = len(content)
        
        self.processedPaths[path] = {}

        try:
            while curLine != endLine:
                curLine = self._consume(content, curLine, path)
        except SyntaxError as e:
            e.filename = path
            raise e


    def _consume(self, content, curLine, path):
        """Zpracuje text souboru"""

        # preskocime prazdne radky
        while len( content[ curLine ].strip() ) == 0: curLine += 1

        try:
            tag,nonterm = map(lambda x: x.strip(), content[curLine].split(":",2))

            if tag != "nonterminal" :
                raise makeException("expected 'nonterminal', '%s' found" % tag, curLine)
            
        except ValueError:
            e = makeException("unknown format", curLine);
            raise e


        curLine += 1 # preskocime radku s nonterm
        
        # dict nezachovava poradi vlozenych klicu, tak musime uchovavat oboje
        params = {"order":[], "defaults":{}, "all": False, "raw":"" }

        text = []
        code = []

        currentBlock = None

        for line in content[curLine:]:
            curLine += 1

            if line.find(":") > 0:  # řádka obsahuje ":" na druhém nebo vyšším znaku (tzn nemůže začínat dvojtečkou)
                tag,data = map(lambda x: x.strip(), line.split(":",1))

                if tag in ("nonterminal","params", "code", "note", "text"):   # je to nějaký z podporovaných segmentů

                    if tag == "nonterminal": #narazili jsme na novou definici nonterminalu, dal uz nepokracujeme
                        curLine -= 1 #vratime ukazatel zpátky
                        break
                        
                    if tag == "params":
                        # todo: params pouzivaji uz jenom raw, zbytek muzeme zahodit...
                        params["raw"] =  data
                        items = [item for item in map( lambda x: x.strip(),  data.split(",") ) ];

                        for item in items:
                            if item.strip() == "*":
                                params["all"] = True
                                continue
                            
                            try:
                                name, value = map(lambda x: x.strip(), item.split("=",1) )
                                value = eval(value, {})
                                params["defaults"][ name ] = value
                            except SyntaxError:
                                raise SyntaxError(" ".join("Error parsing default value for parameter %s"%name, "-", e.msg) )
                            except ValueError:
                                name = item.strip()
                                params["defaults"][ name ] = None

                            params["order"].append(name);
                                
                        continue

                    if tag == "note":
                        currentBlock = "note"
                        continue

                    # jedna se o specialni blok [code|text], za dvojteckou uz nic nesmi byt
                    if len(data) > 0: raise makeException("no text allowed on the same line after ':' for block %s" % tag, curLine)

                    if tag == "text":
                        if len(text) > 0: raise makeException("duplicated block for %s" % tag, curLine)
                        currentBlock = "text"
                        continue
                    
                    if tag == "code":
                        if len(code) > 0: raise makeException("duplicated block for %s" % tag, curLine)
                        currentBlock = "code"
                        continue

                # zadny z nasich tagu, ignorujeme
                    
            # nevime kam patri aktualni radka
            if currentBlock == None: raise makeException("line doesn't belong to any block", curLine);

            if currentBlock == "note":
                # poznámka se preskakuje
                continue

            if currentBlock == "code":
                code.append(line.rstrip() )
                continue

            if currentBlock == "text":
                expr = re.compile("\\{\\{(?P<code>.*?)\\}\\}")
                identifier = re.compile(r"^[^\d\W]\w*\Z", re.UNICODE)
                #najdeme vsechny casti
                parts = expr.split(line)

                for i in range(len(parts)):
                    part = parts[i]

                    if len(part) == 0: continue # preskocime prazdne party
                    
                    if i % 2: # liché části jsou vnitřek {{...}}
                        if identifier.match(part):  # vnitrek by mohla byt sablona bez parametru
                          part = "%s() if callable(%s) else %s"%(part,part,part)
                        
                        text.append("__value.append( str(%s) )" % part )
                    else: # sudé části jsou text
                        text.append("__value.append( %s )" % repr(part) )
                        
                        


        # samotné skládání kódu
        program = ["def implementation(%s) :" % ( params["raw"] ) ]

        # první přijde vložení "code" bloku
        for line in code: program.append( "\t" + line )

        #todo: nepridavat text pokud code obsahuje return na prvni urovni
        #todo: sanity check ze je aspon kod nebo text tzn funkce ma telo

        # vložení textu
        if len(text) > 0:
            # definice
            program.append("\t__value = []");
            # napumpování obsahu
            for line in text: program.append( "\t" + line )
            # odstranění prázdných řádek
            program.append( "\t" + "while len(__value) > 0 and len(__value[-1].strip()) == 0: __value.pop()" )
            # samotný návrat
            program.append( "\t" + "return ''.join( __value )" )  

        
        self.processedPaths[path][nonterm] = self.processedPaths[path].get(nonterm,0)+1 

        if ita.VERBOSE:
            print("parsed nonterminal '%s': %d text, %d code, %d params "%(nonterm, len(text), len(code), len(params["order"])))
            #print("\n".join(program))
            


        programCompiled = compile("\n".join(program),"<string>","exec")
        
        self._addrule(nonterm, programCompiled, params, "\n".join(program) )
                

        return curLine


    def _addrule(self, nonterm, program, params, info):
        """ Prida zaznam do seznamu pravidel"""
        rule = Rule(nonterm, program, params, info)

        if not nonterm in self.rules:
            self.rules[nonterm] = []
        
        self.rules[nonterm].append(rule)
                


