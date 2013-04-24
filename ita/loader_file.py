import os
import re
import codecs
import warnings
import tokenize
from collections import namedtuple
from random import choice
from copy import copy

# pro učely VERBOSE
import ita

#############################################################################    

class FileLoader:
    def __init__(self):
        self.todo = [] 
        self.data = {}
    
    def add(self, path):
        """Přidá cestu ke zpracování. Povinná funkce pro loader."""
        self.todo.append(path)
        # fluent rozhraní
        return self
        
    def getPathsOnly(self):
        """Vrátí pouze soubory, které by byly přečteny"""
        return self.__iter__(False)
        
    def __iter__(self, includeContent = True):
        """Poskytuje iterátor. Povinná funkce pro loader."""
        # lokalni kopie todo
        todo = copy(self.todo)
        while len(todo) > 0:
            path = todo.pop()
            files = os.listdir(path)
            for fileName in files:
                # preskocime linky mimo
                if fileName in (".",".."): continue
                
                # pokud se jedna o adresar, zaradime ho do poradi a pokracujeme 
                absPath = path+"/"+fileName
                if os.path.isdir(absPath):
                    todo.insert(0,absPath)
                    continue
                # dale uz se jedna o soubor
                 
                # preskocime soubory nekoncici fragment
                if not fileName.endswith(".fragment"):
                    if ita.VERBOSE: print("skipping ".ljust(10)+fileName)
                    continue
                
                if ita.VERBOSE: print("opening ".ljust(10)+fileName)
                
                if includeContent:
                    with codecs.open(absPath,'r', 'utf-8') as f:
                        # readlines je sice narocnejsi na pamet, ale vyvazuje to zlo ktery by bylo potreba pri wrapovani bufferedreader
                       yield (absPath, f.readlines())
                else:
                       yield(absPath, None)
        



