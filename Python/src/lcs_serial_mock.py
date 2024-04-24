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


class Arduino:
    def __init__(self, port, baudrate, interval=500, negative_cal=1, precision_adj=1):
        self.interval = interval

        self.negative_calibration = negative_cal
        self.precision_adjustment = precision_adj

    def readline(self, cal: bool = False, cal2: bool = False):
        value = random.randint(0, 10)
        return self.calibrate(value, cal, cal2)

    def calibrate(self, raw_float: float,  cal1: bool = False,  cal2: bool = False) -> float:
        if cal1:
            return raw_float

        if cal2:
            return raw_float + (self.negative_calibration)
        raw_float += (self.negative_calibration)
        raw_float /= (self.precision_adjustment)

        return raw_float
