import os

start = "{ukol_prvni}"


##########################
#načtení fragmentů

nonterminals = {}

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
print(nonterminals)

