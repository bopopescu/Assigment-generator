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
    # nežravá verze
    reInlineCode = re.compile("\\{\\{(.*?)\\}\\}")
    reCapture = re.compile("(?P<code>.*?)>>(?P<target>[^\d\W]\w*\Z)")
    reIdentifier = re.compile(r"^[^\d\W]\w*\Z", re.UNICODE)

    def __init__(self, *args, standardLib = True ):
        self.rules = {}
        self.processedPaths = {}
        self.loaders = list(args)
        
        if standardLib  :
            from ita import FileLoader
            self.loaders.append( FileLoader(ita.MODULE_PATH+"/template_lib") )
        
        #automaticky načteme data, pokud je k dispozici parser
        if len(self.loaders) < 0:
            raise TypeError("Parser requires at least one Loader implementation to be passed")
        
        self._parseAll()
        
    def getRules(self):
        """Vrátí všechny načtená pravidla. Povinná metoda."""
        return self.rules
    
    def _parseAll(self):
        """ Naparsuje všechny zdroje z loaderu """
        for loader in self.loaders:
            for path, data in loader:
                # pokud zkoušíme načíst zdroj s id který již existuje, tak ho přeskočíme
                if path in self.processedPaths: continue
                self._parse( data, path )
        return self
    
    def _parse(self, content, path):
        """Naparsuje jeden zdroj """
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
        """Zpracuje content od řádky curLine načtením nonterminálu
            path se používá na záznam jako klíč pro záznam které nonterminály byly z této cesty načteny 
            vrací řádku na které skončil  """

        def addToBlock( block, what ):
            """ Přidá do bloku danou řádku spolu s číslem na kterém řádka je"""
           
            block.append( (curLine, what) )


        # preskocime prazdne radky
        while len( content[ curLine ].strip() ) == 0: curLine += 1

        try:
            tag,nonterm = map(lambda x: x.strip(), content[curLine].split(":",2))

            if tag != "nonterminal" :
                raise makeException("expected 'nonterminal', '%s' found" % tag, curLine)
            
        except ValueError:
            e = makeException("unknown format", curLine);
            raise e


        curLine += 1 # preskocime radku s nonterm, protoze jsme ji uz zpracovali
        
        
        params = ""; 

        text = []
        code = []
        
        # mapování z kodovych radek na puvodni text
        originalLines = {}
        # mapovani puvodnich radek textu na text ktery obsahovali
        originalContent = {}

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
                        params =  data
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

            originalContent[curLine] = line

            # nevime kam patri aktualni radka
            if currentBlock == None: raise makeException("line doesn't belong to any block", curLine);

            if currentBlock == "note":
                # poznámka se preskakuje
                continue

            if currentBlock == "code":
                addToBlock(code, line.rstrip())
                continue

            if currentBlock == "text":

                #najdeme vsechny casti
                parts = self.reInlineCode.split(line)

                for i in range(len(parts)):
                    part = parts[i]

                    if len(part) == 0: continue # preskocime prazdne party
                    
                    if i % 2: # sudé (v indexech jsou to ale liché) části jsou vnitřek {{...}}
                        capture = self.reCapture.match(part)
                        
                        # specialni syntax pro zachyceni promenne 
                        if capture:
                            data = capture.groupdict();
                            addToBlock(text, "%s = (%s); __value.append( str(%s) )" % (data["target"], data["code"], data["target"]))

                        elif self.reIdentifier.match(part):  # vnitrek by mohla byt sablona bez parametru
                                                           # tu pozname tak ze to vypada jeko identifikator a je volatelny 
                          part = "(%s() if callable(%s) else %s)"%(part,part,part)
                        addToBlock(text, "__value.append( str(%s) )" % part )
                    else: # liché části jsou text (v indexech to jsou ale sudé)
                        addToBlock(text, "__value.append( %s )" % repr(part) )
                        
                        


        # samotné skládání kódu
        program = []
        # při výjimce se použije pro přepočet původních řádek
        programCounter = 1

        program.append("def implementation(%s) :" % params)
        
        # první přijde vložení "code" bloku
        
        for lineno, line in code:
            programCounter += 1
            originalLines[programCounter] = lineno
            program.append( "\t" + line )

        #todo: sanity check ze je aspon kod nebo text tzn funkce ma telo

        # vložení textu
        if len(text) > 0:
            # definice
            program.append("\t__value = []");
            programCounter += 1
            # napumpování obsahu
            
            for lineno, line in text:
                programCounter +=1
                originalLines[programCounter] = lineno
                program.append( "\t" + line )

             
            
            # odstranění prázdných řádek
            program.append( "\t" + "while len(__value) > 0 and len(__value[-1].strip()) == 0: __value.pop()" )
            # samotný návrat
            program.append( "\t" + "return ''.join( __value )" )  

        #vložime info o zdroji
        program.append("implementation._ita_path = %s" % repr(path))
        program.append("implementation._ita_nonterminal = %s" % repr(nonterm))
        program.append("implementation._ita_originalLines = %s" % repr(originalLines))
        program.append("implementation._ita_originalContent = %s" % repr(originalContent))


        
        self.processedPaths[path][nonterm] = self.processedPaths[path].get(nonterm,0)+1 

        if ita.VERBOSE:
            print("parsed nonterminal '%s': %d text, %d code, %s"%(nonterm, len(text), len(code), params))
            #print("\n".join(program))
            

        try:
            programCompiled = compile("\n".join(program),"<string>","exec")
        except SyntaxError as e:
            e.lineno = originalLines[e.lineno] 
            raise( e )
        
        self._addrule(nonterm, programCompiled, params, "\n".join(program) )
                

        return curLine


    def _addrule(self, nonterm, program, params, info):
        """ Prida zaznam do seznamu pravidel"""
        rule = Rule(nonterm, program, params, info)

        if not nonterm in self.rules:
            self.rules[nonterm] = []
        
        self.rules[nonterm].append(rule)
                


