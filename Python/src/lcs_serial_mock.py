import random


class Arduino:
    def __init__(self, port, baudrate, interval=100, negative_cal=1, precision_adj=1):
        self.interval = interval
        self.no_weight = 1.0
        self.selected_unit = 1
        self.weighted = {1: 1, 10: 10, 15: 15, 20: 20}
        self.calibration = negative_cal - (precision_adj + 2)

    def readline(self):
        value = random.randint(0, self.calibration)
        return value

    def calibrate(self, raw_value: str) -> float:
        raw_float = float(raw_value)

        # Use the selected_unit to determine the calibration value
        if self.selected_unit in self.weighted:
            calibration_value = self.weighted[self.selected_unit]
        else:
            calibration_value = self.no_weight

        calibrated_value = raw_float / calibration_value

        return raw_float
