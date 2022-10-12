import time
from typing import Callable, Tuple, Dict, Any
from dataclasses import dataclass, field
# from threading import Thread as Process, Event
# from queue import Queue
from multiprocessing import Process, Queue, Event
from queue import Empty

stop_event = Event()

@dataclass
class Ticket:
    name: str
    task: Callable
    args: Tuple = field(default_factory=tuple)
    kwargs: Dict = field(default_factory=dict)
    callback: Callable = None
    cbargs: Tuple = field(default_factory=tuple)
    cbkwargs: Dict = field(default_factory=dict)
    result: Any = None

def worker(qin: Queue, qout: Queue, is_stopped: Event):
    print("Worker started")
    while not is_stopped.is_set():
        try:
            ticket: Ticket = qin.get(timeout=.05)
        except Empty:
            continue
        print(ticket.name)
        ticket.result = ticket.task(*ticket.args, **ticket.kwargs)
        if ticket.callback:
            ticket.callback(ticket.result, *ticket.cbargs, **ticket.cbkwargs)
        qout.put(ticket)
    print("Worker stopped")

def do_something(arg1, arg2):
    print(arg1, arg2)
    return arg1 + arg2

def cb(result):
    print(f"Callback result: {result}")
    time.sleep(1.)
    print(f"Callback done {result}")

def main():
    qin = Queue()
    qout = Queue()
    proc = Process(target=worker, args=(qin, qout, stop_event))
    proc.start()
    for i in range(10):
        time.sleep(.1)
        ticket = Ticket(
            "my_ticket",
            task=do_something,
            # args=(i,),
            kwargs={"arg1": i, "arg2": i},
            callback=cb,
        )
        qin.put(ticket)
    while True:
        result = qout.get()
        print(f"GOT RESULT! {result}")
        qsize = qin.qsize()
        if qsize == 0:
            break
        print(f"Waiting for queue: {qsize} left")
        print(f"Q OUT: {qout.qsize()}")
        time.sleep(.1)
    stop_event.set()
    print("Joining process")
    proc.join(timeout=1.)

if __name__ == "__main__":
    try:
        main()
    except:
        raise
    finally:
        stop_event.set()
    # time.sleep(5.)
