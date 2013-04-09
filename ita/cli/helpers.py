import unicodedata
import re

def consoleFriendly(val):
    """Převede string na znaky bez diakritiky""" 
    ret = unicodedata.normalize('NFKD', val).encode('ascii', 'ignore').decode('utf-8')
    return ret
