from .helpers import consoleFriendly
from time import sleep
import os.path
import threading
import _thread

class WaitingThread(threading.Thread):
        
    def __init__(self, event, sleep = 1):
        super(WaitingThread, self).__init__()
        # daemon thread se při ukončeni main vlakna vynuceně ukončí
        # něco co python nepodporuje    
        self.daemon = True
        self._event = event
        self._sleep =  sleep
        
        self.fired = False
        

    def run(self):
        sleep(self._sleep)
        self.fired = True
        self._event.set()

class InputThread(threading.Thread):
        
    def __init__(self, event):
        super(InputThread, self).__init__()
        self.daemon = True
        self._event = event
        
        self.fired = False

    def run(self):
        input()
        self.fired = True
        self._event.set()


          

def run(nonterminal, interval, path, toAscii = True):
    import ita
    from ita import Loader, Parser, Generator
    ita.VERBOSE = False

    print("Pro ukonceni testovaciho rezimu pouzijte CTRL+C")
    if toAscii:
        print("Vystup bude preved do cisteho ASCII")

    # event pro synchronizaci změny
    changed = threading.Event()
    
    # vlakno pro odchytavani zmacknuti enter
    inputing = None

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

            
            waiting = WaitingThread(changed, interval)
            waiting.start()
            
            if not inputing:
                # vlákno inputing muže existovat, 
                # input nelze spustit 2x (jde ale bude se čekat na ukončeni prvniho) a pokud dojde k reload z duvodu změny souboru
                # puvodni input porad bezi
                # to je take duvod proc se pozuziva stejny event
                inputing = InputThread(changed)
                inputing.start()
            
            immortal = True
            while immortal:
                #čekáme na změnu
                changed.wait()
            
                # zjistíme kdo změnil stav
                
                if waiting.fired: # čekací vlákno vyvolalo vyjímku  => timeout
                    for fileName, mtime in filesToBeWatched.items():
                        if os.path.getmtime(fileName) != mtime:
                            immortal = False
                            break
                    #restartujeme cekani
                    del waiting
                    waiting = WaitingThread(changed, interval)
                    waiting.start()   
                
                elif inputing.fired: # vlákno vstupu => keypress
                    #restartovat ho nemá cenu, protože bude stejně přepsáno
                    immortal = False
                    #force smazani
                    del inputing
                    #nastavime, aby se priste smazal 
                    inputing = None
            
            changed.clear()      
            
            print("-"*20)
                    
        except KeyboardInterrupt:
            print("-"*20)
            break 
        
    
    
    
