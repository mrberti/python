import time
import sys
from multiprocessing import shared_memory

SHM_NAME = "xxx"
SHM_SIZE = 1024
DATA = b"x" * SHM_SIZE
N = 100000

argv = sys.argv
is_server = False
if len(argv) > 1:
    if argv[1] == "-s": is_server = True

if is_server:
    shm = shared_memory.SharedMemory(create=True, size=SHM_SIZE, name=SHM_NAME)
else:
    shm = shared_memory.SharedMemory(size=SHM_SIZE, name=SHM_NAME)

try:
    shm.buf[0] = 0
    for i in range(int(N) + 1):
        if is_server:
            while shm.buf[0] == 0:
                time.sleep(0)
            shm.buf[0] = 0
            for x in range(1, len(shm.buf)):
                shm.buf[x] = DATA[x]
            # print(shm.buf)
        else:
            while shm.buf[0] == 1:
                time.sleep(0)
            shm.buf[0] = 1
            # print(shm.buf)
except:
    pass
finally:
    shm.close()
    if is_server:
        shm.unlink()