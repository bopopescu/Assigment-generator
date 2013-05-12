import unicodedata
import re

def consoleFriendly(val):
    """Převede string na znaky bez diakritiky"""
    # vstup může být None, na něm by dekodovani zkolabovalo
    if not val: return "" 
    ret = unicodedata.normalize('NFKD', val).encode('ascii', 'ignore').decode('utf-8')
    return ret
