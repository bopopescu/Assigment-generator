from .helpers import consoleFriendly
from time import sleep
import os.path

def run(nonterminal, interval, path, toAscii = True):
    import ita
    from ita import Loader, Parser, Generator
    ita.VERBOSE = False

    print("Pro ukonceni testovaciho rezimu pouzijte CTRL+C")
    if toAscii:
        print("Vystup bude preved do cisteho ASCII")

    while True:
        try:
            l = Loader().add(path)
            try:            
                p = Parser( l )
                g = Generator( p )
                
                text = g.run(nonterminal) 
                
                print( consoleFriendly(text) if toAscii else text )
            except SyntaxError as e:
                print("Syntax error",e)
                
        
            filesToBeWatched = { fileName : os.path.getmtime(fileName) for fileName, data in l.getPathsOnly() }

            changed = False
            while not changed:
                sleep(interval)
                for fileName, mtime in filesToBeWatched.items():
                    if os.path.getmtime(fileName) != mtime:
                        changed = True
                        break
            print("-"*20)
        except KeyboardInterrupt:
            print("-"*20)
            break 
        
    
    
    
