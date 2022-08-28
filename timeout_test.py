import time
import random
import multiprocessing.pool
import functools

def timeout_task(max_timeout):
    """Timeout decorator, parameter in seconds."""
    def timeout_decorator(item):
        """Wrap the original function."""
        @functools.wraps(item)
        def func_wrapper(*args, **kwargs):
            """Closure for function."""
            pool = multiprocessing.pool.ThreadPool(processes=1)
            async_result = pool.apply_async(item, args, kwargs)
            try:
                # raises a TimeoutError if execution exceeds max_timeout
                return async_result.get(max_timeout)
            except multiprocessing.TimeoutError:
                raise TimeoutError("Timeout!!!!")
        return func_wrapper
    return timeout_decorator

def wait_for_condition(timeout=None, sleep_time=None):
    def decorator(cond_func):
        @functools.wraps(cond_func)
        def wrapper(*args, **kwargs):
            wait(cond_func, timeout, sleep_time, *args, **kwargs)
        return wrapper
    return decorator

def wait(cond_func, timeout, sleep_time, raise_at_timeout=True, *args, **kwargs):
    start_ns = time.perf_counter_ns()
    start = time.time()
    if timeout is None:
        timeout = float("inf")
    _sleep = sleep_time or 0.
    deadline = start + timeout
    i = 0
    condition = False
    while not condition:
        condition = cond_func(*args, **kwargs)
        i += 1
        if _sleep > 0.:
            time.sleep(_sleep)
        if time.time() > deadline:
            if raise_at_timeout:
                raise TimeoutError("TIMEOUT!!!!")
            else:
                return False
    diff = time.perf_counter_ns() - start_ns
    print(f"DONE after {i} iterations ({diff/1000./1000.:.3f} ms)!")
    return condition

def xxx(cut, timeout, sleep_time):
    @wait_for_condition(timeout, sleep_time=sleep_time)
    def lol(cut):
        return my_cond(cut)
    print(lol.__name__)
    lol(cut)

def my_cond(cut):
    return random.randint(0, 1000) <= cut

@timeout_task(2.)
def do_stuff(maxtime):
    start = time.time()
    deadline = start + maxtime
    i = 0
    while time.time() < deadline:
        time.sleep(.1)
        i += 1
        print(f"{time.time() - start:.2f}")

@timeout_task(2.)
def iterate(count, sleep):
    for i in range(count):
        print(f"{i}")
        time.sleep(sleep)

def main():
    # iterate(10, .1)
    # lol(1)
    # lol(10)
    cut = 1
    timeout = 1.
    sleep = .01
    # xxx(cut, timeout, sleep)
    print(xxx.__name__)
    # wait(lambda: random.randint(1, 1000) < cut, timeout=timeout, sleep_time=sleep)
    x = wait(lambda: my_cond(cut), timeout=timeout, sleep_time=sleep, raise_at_timeout=False)
    print(x)
    # wait(my_cond, timeout, sleep, cut=cut)
    print(wait.__name__)

lambda x: x + 1

def main_profiled():
    import cProfile
    import pstats
    with cProfile.Profile() as pr:
        main()
    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.print_stats()

if __name__ == "__main__":
    main()
    # main_profiled()
