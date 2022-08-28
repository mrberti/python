import time
import os
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor

def worker(count):
    for i in range(count):
        print(f"PID {os.getpid()}: {time.time()}: {i}")
        if i >= 2:
            raise ValueError("TOO BIG!!!")
        time.sleep(1.)
    return i

def wrapped_worker(target, q: mp.Queue, *args, **kwargs):
    response = target(*args, **kwargs)
    q.put((target.__name__, response))

def t_wrap(target, q: mp.Queue, *args, **kwargs):
    p = mp.Process(target=wrapped_worker, args=(target, q,) + args, kwargs=kwargs)
    p.start()
    return p

def main():
    q = mp.Queue()
    p = t_wrap(target=worker, q=q, count=3)
    p.join()
    print(q.get())

def main_future():
    executor = ThreadPoolExecutor(5)
    fut = executor.submit(worker, count=1)
    fut2 = executor.submit(worker, count=4)
    fut.add_done_callback(lambda x: print(f"fut done! {x.result()}"))
    print(fut.result())
    print(fut2.exception())
    executor.shutdown(wait=False)
    print("done")

if __name__ == "__main__":
    # main()
    main_future()
    main_future()
