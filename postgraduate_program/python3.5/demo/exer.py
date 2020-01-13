import os
import time

a = int(time.time())
time.sleep(3)
b = int(time.time())
print([a, b])
list = [str(b), str(a)]
print(sorted(list))