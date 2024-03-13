import serial


class Arduino:
    def __init__(self, port, baudrate, interval=500, negative_cal=1, precision_adj=1):
        self.interval = interval
        self._serial = serial.Serial(port=port, baudrate=baudrate)

        self.negative_calibration = negative_cal
        self.precision_adjustment = precision_adj

    def readline(self):
        try:
            raw_value = self._serial.readline().decode('utf-8').strip()
            calibrated_value = self.calibrate(float(f"{raw_value}0"))
            calibrated_value /= 10
            return calibrated_value
        except:
            print(f"ERROR")
            return 0

    def calibrate(self, raw_float: float) -> float:
        raw_float += (self.negative_calibration)
        raw_float /= (self.precision_adjustment)

        raw_float = raw_float 

        return raw_float