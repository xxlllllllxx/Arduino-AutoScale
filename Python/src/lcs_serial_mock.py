import random


class Arduino:
    def __init__(self, port, baudrate, interval=100, negative_cal=1, precision_adj=1):
        self.interval = interval
        
        self.negative_calibration = 0
        self.precision_adjustment = 1

    def readline(self):
        value = random.randint(0, 10)
        return self.calibrate(value)

    def calibrate(self, raw_float: float) -> float:
        raw_float += (self.negative_calibration)
        raw_float /= (self.precision_adjustment)
        print(raw_float)

        raw_float = raw_float 

        return raw_float