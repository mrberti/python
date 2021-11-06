import time
import machine

# Custom modules
import board


# Global parameters
DELAY_US_SHORT = 355
DELAY_US_LONG = 3 * 355
if "8266" in board.__CPU__:
    TIMING_CORRECTION_US = 220
elif "esp32" in board.__CPU__:
    # TODO
    TIMING_CORRECTION_US = 0
else:
    raise NotImplementedError("No TIMING_CORRECTION_US defined.")

DEFAULT_TIMING = (
    DELAY_US_SHORT, # 0_high
    DELAY_US_LONG,  # 0_low
    DELAY_US_LONG,  # 1_high
    DELAY_US_SHORT, # 1_low
)

class RF433(object):
    def __init__(self, tx_pin_no, timing=None, timing_correction=None):
        self.tx_pin_no = tx_pin_no
        self.tx = machine.Pin(tx_pin_no, machine.Pin.OUT)
        # Timing is a 4-tuple: 0_high, 0_low, 1_high, 1_low, in us
        # See also:
        # https://docs.micropython.org/en/latest/library/machine.html#machine.bitstream
        if timing is None:
            timing = DEFAULT_TIMING
        self.timing = timing
        self.correct_timing(timing_correction)

    def correct_timing(self, timing_correction=None):
        if timing_correction is None:
            timing_correction = TIMING_CORRECTION_US
        self.timing_c = (
            self.timing[0] + timing_correction,
            self.timing[1] - timing_correction,
            self.timing[2] + timing_correction,
            self.timing[3] - timing_correction
        )

    def create_time_vector(self, data):
        t = [0]
        i = 0
        for bit in data:
            if bit == "0":
                t_on = self.timing_c[0] + t[i]
                t_off = self.timing_c[1] + t_on
            else:
                t_on = self.timing_c[2] + t[i]
                t_off = self.timing_c[3] + t_on
            t.append(t_on)
            t.append(t_off)
            i += 2
        del t[0]
        return t

    def send_code(self, data, count=10):
        t_vector = self.create_time_vector(data)
        for _ in range(count):
            start = time.ticks_us()
            state = True
            for t in t_vector:
                self.tx.value(state)
                state = not state
                end = start + t
                while time.ticks_us() < end:
                    pass
            self.tx.off()
            time.sleep(10e-3)
