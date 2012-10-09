import os
import re
from random import random, choice
from math import floor

expanding = "{ukol_prvni}"

nonterminals = {}

##########################
#načtení fragmentů
files = os.listdir("segmenty")
for file in files:
    with open("segmenty\\"+file) as f:
        content = f.readlines()

    line = 0        
    tag,nonterminal = map(lambda x: x.strip(), content[(line)].split(":",2))
    line += 1

    if not nonterminal in nonterminals:
        nonterminals[nonterminal] = []

    data = {}
    data["file"] = file

    while True:
        try:
            print ( content[line].strip())
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
            value = map(lambda x: x.strip(), value.split(","))

        data[tag] = value

    nonterminals[nonterminal].append(data)
##########################

history = []

expr = re.compile("\\{(?P<name>[^ }]+)( (?P<params>[^}]*))?\\}")


def replaceNonterminal(match):
    matches = match.groupdict()
    nonterminal = matches["name"]

    if nonterminal == "cislo":
        par = matches["params"] if matches["params"] != None else "0-9"
        fr, to = map(lambda x: int(x), par.split("-"))
        return str( fr+ floor(random()*(to-fr)) )

    if nonterminal in nonterminals:
        return choice( nonterminals[nonterminal])["text"]

    return "chyba <"+nonterminal+">"
    


#parsovani
while True:
    history.append(expanding)
    print("-"*20)
    print(expanding)
    expanding, changes = expr.subn(replaceNonterminal,history[-1],1)
    if changes == 0:
        break
    

    

    expanding
    
