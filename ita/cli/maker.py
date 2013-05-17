import os.path
import codecs  


def run(nonterminal, path, count = None, source = None):
    import ita
    from ita import Loader, Parser, Generator
    ita.VERBOSE = False
    
    padValue = None
    if source:
        with codecs.open(source,'rb', 'utf-8-sig') as f:
            data = f.readlines()
    else:
        data = ([str(x) for x in range(count)])
        padValue = len(str(count))
        
    l = Loader(path)
    p = Parser( l )
    g = Generator( p )
                
    for name in data:
        name = name.strip()
        if padValue: name = name.rjust(padValue,"0")
        print(name)
        name += ".txt"
        text = g.run(nonterminal) 
        with codecs.open(name,'wb', 'utf-8') as f:
            f.write( text )
        
    
    
    
