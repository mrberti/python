import sys
import time
import asyncio
try:
    import matplotlib.pyplot as plt
except ImportError:
    print("matplotlib not installed")
try:
    import numpy as np
except ImportError:
    print("numpy not installed")

def is_server():
    if len(sys.argv) > 1:
        return sys.argv[1] == "-s"

def init_t(length):
    return np.zeros(length) * np.nan

def normalize_t(t, time_res=1):
    """Return normalized time vector in `s` starting at 0s. NaN values
    are dropped."""
    return t[~np.isnan(t)] / time_res - t[0]

def calc_duration(t):
    return t[-1] - t[0]

def calc_dt(t):
    return np.diff(t)

def print_statistics(t, data_length, max_n):
    delta = calc_duration(t)
    dt = calc_dt(t)
    i = len(t)
    data_sent_mb = data_length * i / 1024 / 1024
    print(f"{i}/{int(max_n)}\t{delta:.3f}s\t{i / delta:.3f} msg/s\t{delta * 1e6/i:.3f} µs/msg")
    print(f"{data_sent_mb:.3f} MB\t{data_sent_mb/delta:.3f} MB/s")
    print(f"Mean:\t{np.nanmean(dt) * 1e3:.3f} ms")
    print(f"Min:\t{np.nanmin(dt) * 1e3:.3f} ms")
    print(f"Max:\t{np.nanmax(dt) * 1e3:.3f} ms")
    print(f"Std:\t{np.nanstd(dt) * 1e3:.3f} ms")


def plot_statistics(t):
    dt = calc_dt(t)
    mean = np.nanmean(dt)
    median = np.nanmedian(dt)
    plt.subplot(2,1,1)
    plt.plot(t[1:], dt, '.')
    plt.plot([t[0], t[-1]], [mean, mean], 'r')
    plt.plot([t[0], t[-1]], [median, median], 'r--')
    plt.ylabel("dt [ms]")
    plt.xlabel("time [s]")
    plt.subplot(2,1,2)
    plt.hist(dt, 100)
    plt.show()

def loopy(func):
    def inner(loops, data, *args, **kwargs):
        t = init_t(loops)
        for i in range(loops):
            t[i] = time.time()
            func(loops, data, *args, **kwargs)
        t = normalize_t(t)
        print_statistics(t, len(data), loops)
        plot_statistics(t)
    return inner

def loopy_async(func):
    async def inner(loops, data, *args, **kwargs):
        t = init_t(loops)
        for i in range(loops):
            t[i] = time.time()
            await func(loops, data, *args, **kwargs)
        t = normalize_t(t)
        print_statistics(t, len(data), loops)
        plot_statistics(t)
    return inner
