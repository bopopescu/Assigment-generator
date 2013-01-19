import os
import codecs
import warnings
import tokenize

VERBOSE = True 

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


class Generator:

    def __init__(self):
        pass

    def loadDir(self, path):
        files = os.listdir(path)
        for file in files:
            if not file.endswith(".fragment"):
                if VERBOSE: print("skipping "+file)
                continue
            
            if VERBOSE: print("opening "+file)
            
            with codecs.open(path+"/"+file,'r', 'utf-8') as f:
                content = f.readlines()

            try:
               self.parse(content)
            except SyntaxError as e:
                #todo: udelat z toho warn
                raise SyntaxError(" ".join( ("File", file,"-", e.msg) ) )
                

        

    def parse(self, content):
        nonterm = None

        params = []
        text = []
        code = []

        currentBlock = None

        lineNo = 0

        # prvni radka musi byt nonterm
        try:
            tag,nonterm = map(lambda x: x.strip(), content[lineNo].split(":",2))

            if tag != "nonterminal" : raise SyntaxError(" ".join("line: "+str(lineNo),"first line must contain nonterminal"));
        except ValueError:
            raise SyntaxError(" ".join("line: "+str(lineNo),"unknown format"));

        

        for line in content[1:]:
            lineNo += 1
            try:
                tag,data = map(lambda x: x.strip(), line.split(":",2))

                if tag in ("text", "code", "params"):
                    if tag == "params":
                        #todo
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
            print("parsed nonterminal %s: %d text, %d code"%(nonterm, len(text), len(code)))

        text = "\n".join(text)
        code = "\n".join(code)


            


g = Generator()
g.loadDir(".")
