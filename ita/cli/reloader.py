import ita
from time import sleep
import os.path

def run():
    from ita import Loader, Parser, Generator
    ita.VERBOSE = False


    while True:
        l = Loader().add("ita/sablony")
        p = Parser( l )
        g = Generator( p )
        print( g.run("cviceni") )
    
        filesToBeWatched = { path : os.path.getmtime(path) for path in p.processedPaths.keys()}

        changed = False
        while not changed:
            sleep(1)
            for path, mtime in filesToBeWatched.items():
                if os.path.getmtime(path) != mtime:
                    changed = True
                    break
    
    
    
