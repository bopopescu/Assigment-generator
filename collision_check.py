from ita import Loader, Parser, Generator
import sys
import ita
import math
from hashlib import md5
from threading import Thread, Event
import queue
import sqlite3

connection = sqlite3.connect(":memory:")
connection.isolation_level = None  # vypnutí relací 
cursor = connection.cursor()
query = cursor.execute

query("CREATE TABLE collisions (hash char(32) PRIMARY KEY NOT NULL)")


ita.VERBOSE = False

SAMPLES = 500000
WORKERS = 2

# BUFFER > WORKERS
BUFFER = 500

shouldDie = Event()
shouldDie.clear()


pendingResolve = queue.Queue(BUFFER)

threads = []
processed = 0
collisions_count = 0;

hashes = []

class WorkerThread(Thread):
    def run(self):
        global writeAccess, shouldDie
        
        loader = Loader("sablony")
        parser = Parser( loader )
        generator = Generator( parser )
        
        while not shouldDie.is_set():
            text = generator.run("cviceni")
            hashed = md5(text.encode('utf-8')).hexdigest()
            pendingResolve.put(hashed);
            


for dummy in range(WORKERS):
    t = WorkerThread()
    t.start()
    threads.append(t)

BAR_SIZE = 30
COEF = BAR_SIZE/BUFFER

try:
    while processed < SAMPLES:
        processed += 1
        hashed = pendingResolve.get()
        if processed % 100 == 0:
            bar = math.floor(pendingResolve.qsize()*COEF)
            print("["+ ("*"*bar).ljust(BAR_SIZE)+"]")
            print(processed)
        
        try:
            query("INSERT INTO collisions VALUES ('%s')" % hashed)
        except sqlite3.IntegrityError:
            collisions_count += 1
        pendingResolve.task_done()
        
        sys.stdout.flush()
        
except KeyboardInterrupt:
    pass

print("%d/%d = %1.2f%%" % (collisions_count, SAMPLES, round(collisions_count/SAMPLES*100,2)))

print("ukoncuju")

# vycistime zbytek fronty, coz umozni ukonceni vlaknum ktere cekaji na zapis do ni
try:
    while True: pendingResolve.get(False)
except queue.Empty:
    pass
    
shouldDie.set()

# pockame na ukonceni vsech vlaken
for thread in threads:
    thread.join()    

    
print("konec")