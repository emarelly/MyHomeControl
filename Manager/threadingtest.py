import threading
import time

def f():
    time.sleep(5)

print threading.active_count()
thread1 = threading.Thread(target=f)
thread2 = threading.Thread(target=f)
thread1.start()
thread2.start()
print threading.active_count()
time.sleep(1)
print threading.active_count()
time.sleep(1)
print threading.active_count()
time.sleep(1)
print threading.active_count()
time.sleep(1)
print threading.active_count()
time.sleep(1)
print threading.active_count()
time.sleep(1)