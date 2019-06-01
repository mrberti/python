# This file is executed on every boot (including wake-boot from deepsleep)
from esp import osdebug
import gc
from utils import do_connect

# osdebug(None)
do_connect()
gc.collect()
