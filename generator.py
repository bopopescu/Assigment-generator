import os
import re
from random import random, choice
from math import floor
import codecs

expanding = "{cviceni_prvni}"


class Generator:
    nonterminals = {}
    
    def __init__(self):
        if len(self.nonterminals) == 0:
            self.loadFragments()
        pass


    def replaceNonterminal(self,match):
        matches = match.groupdict()
        nonterminal = matches["name"]

        if nonterminal == "cislo":
            par = matches["params"] if matches["params"] != None else "0-9"
            fr, to = map(lambda x: int(x), par.split("-"))
            return str( fr+ floor(random()*(to-fr)) )

        if nonterminal in self.nonterminals:
            replacement = choice( self.nonterminals[nonterminal])
            
            self.usedFiles[ replacement["file"] ] = 1
            if "priznaky" in replacement:
                for flag in replacement["priznaky"]:  self.flags[ flag ] = 1
            return replacement["text"]

        return "chyba <"+nonterminal+">"
            

    def parse(self, expanding):
        history = []
        expr = re.compile("\\{(?P<name>[^ }]+)( (?P<params>[^}]*))?\\}")

        self.usedFiles = {}
        self.flags = {}

        #parsovani
        while True:
            history.append(expanding)
            #oly one change at time
            expanding, changes = expr.subn(self.replaceNonterminal,history[-1],1)
            if changes == 0:
                break

        return expanding            


    ##########################
    #načtení fragmentů
    def loadFragments(self, path = "segmenty"):
        files = os.listdir(path)
        for file in files:
            with codecs.open(path+"/"+file,'r', 'utf-8') as f:
                content = f.readlines()

            line = 0        
            tag,nonterminal = map(lambda x: x.strip(), content[(line)].split(":",2))
            line += 1

            if not nonterminal in self.nonterminals:
                self.nonterminals[nonterminal] = []

            data = {}
            data["file"] = file

            while True:
                try:
                    tag,value = map(lambda x: x.strip(), content[line].split(":",2))
                    line += 1
                except IndexError:
                    print("Error in file "+file)
                    break

                if tag == "text":
                    value = "".join(content[line:])
                    data[tag] = value
                    break
                elif tag == "priznaky":
                    value = list(map(lambda x: x.strip(), value.split(",")))

                data[tag] = value

            self.nonterminals[nonterminal].append(data)
    ##########################

#g = Generator()
#print(g.parse(expanding))
#print(g.flags)


    
