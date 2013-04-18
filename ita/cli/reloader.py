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

    print("Stistknutim ENTER se provede pregenerovani")
    print("Pro ukonceni programu pouzijte CTRL+C")
    if toAscii:
        print("Vystup bude preved do cisteho ASCII")

    # event pro synchronizaci změny
    changed = threading.Event()
    
    # vlakno pro odchytavani zmacknuti enter
    inputing = None
    # vlakno pro timeout
    waiting = None

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
        
            # seznam souborů , které budou hlídány
            filesToBeWatched = { fileName : os.path.getmtime(fileName) for fileName, data in l.getPathsOnly() }

            if not inputing:
                # vlákno inputing muže existovat, 
                # input nelze spustit 2x (jde ale bude se čekat na ukončeni prvniho)
                # pokud dojde k reload z duvodu změny souboru puvodni input porad bezi
                # to je take duvod proc se pouziva stejny event
                inputing = InputThread(changed)
                inputing.start()

            if not waiting:
                # timeout vlakno, startujeme jen když je není z dřívějška
                waiting = WaitingThread(changed, interval)
                waiting.start()

            
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
                    # force smazani
                    del waiting
                    # nutno zachovat existenci promenne
                    waiting = None
                    
                    if immortal:
                    # pokud doslo k timeoutu ale ne ke zmene souboru, musime nastartovat vlakno znovu
                        waiting = WaitingThread(changed, interval)
                        waiting.start()   
                
                elif inputing.fired: # vlákno vstupu => keypress
                    immortal = False
                    # force smazani
                    del inputing
                    # nutno zachovat existenci promenne 
                    inputing = None
            
            changed.clear()      
            
            print("-"*20)
                    
        except KeyboardInterrupt:
            print("-"*20)
            break 
        
    
    
    
