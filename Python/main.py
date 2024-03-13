
## CONFIGURATION #########
# pip install pyserial
# pip install matplotlib
# pip install customtkinter

from matplotlib.patches import Arc
from matplotlib.animation import FuncAnimation
import serial
from collections import deque
import customtkinter as ctk
import src.lcs_graph as monitor
import src.lcs_calibration as calibrate
# ARDUINO or MOCK
import src.lcs_serial_mock as serial
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib
import matplotlib.pyplot as plt


matplotlib.use("TkAgg")
ctk.set_appearance_mode("dark")
plt.style.use("dark_background")
title = "Arduino Project"


# NOTE: Configure this port and baudrate
port = "" # check in arduino
baudrate = "" # check in arduino


class App:
    def __init__(self, arduino: serial.Arduino):
        self._arduino = arduino

        self.root = ctk.CTk()

        # STATE
        self.calibrated: bool = False
        self._is_calibrating: bool = False
        self.run_monitor: bool = False
        self._is_running = False
        self._is_paused = False
        self.exit: bool = False
        self._is_exiting: bool = False

        # GRAPHS
        self.highest = 1
        self.lowest = 0
        self.max_x_data: int = 100
        self.x_data = list(range(self.max_x_data))
        self.y_data = deque(maxlen=self.max_x_data)

        self.cal_fig = Figure(figsize=(12, 5), dpi=50, constrained_layout=False)
        self.bar_grp = self.cal_fig.add_subplot(111)
        self.bar_grp.set_ylim(self.lowest - 1, self.highest)
        self.plt_bar = self.bar_grp.bar(self.x_data, [0] * self.max_x_data)

        self.mon_fig = Figure(figsize=(14, 5), dpi=50, constrained_layout=False)
        self.line_grp = self.mon_fig.add_subplot(111)
        self.plt_line = self.line_grp.plot(self.x_data, [0] * self.max_x_data, lw=2)

        self.gauge_fig = Figure(figsize=(4, 4), dpi=50)
        self.gauge_ax = self.gauge_fig.add_subplot(111)
        self.plt_gauge = Arc((0.5, 0.5), 1, 0.5, theta1=180, theta2=180, linewidth=4)

        self.gauge_ax.add_patch(self.plt_gauge)
        self.gauge_ax.axis('off')
        self.tx_gaud = ctk.StringVar(value="GAUGE")

        # CALIBRATION
        self.selected_calibration: int = 1
        self.unit: str = "kg"
        self.tx_cal = ctk.StringVar(value="[ 0.00000 ] kg")
        self.calibration_result = 1
        self.accuracy = ctk.IntVar(value=5)
        self.neg_a = ctk.StringVar(value=f"Negative Calibration  = [ {self._arduino.negative_calibration} ]")
        self.pre_a = ctk.StringVar(value=f"Precision Calibration = [ {self._arduino.precision_adjustment} ]")

        # UI
        self.root.title(title)
        self.root.resizable(False, False)
        self.font_title = ('Arial', 16)
        self.font_text = ('Arial', 12)
        self.font_button = ('Arial', 14)
        self.pad = 10

    def start(self):
        cal_fm = ctk.CTkFrame(self.root)
        cal_fm.grid(padx=self.pad + 10, pady=self.pad, sticky="new")
        ctk.CTkLabel(cal_fm, text="CALIBRATION", font=self.font_title).grid(padx=self.pad, pady=self.pad, sticky="nw")
        cal_fm_graph = ctk.CTkFrame(cal_fm, width=500)
        cal_fm_graph.grid(padx=self.pad, pady=self.pad, sticky="nsew", row=1, column=0, columnspan=3, rowspan=2)
        cal_fm_sel_unit = ctk.CTkFrame(cal_fm)
        cal_fm_sel_unit.grid(padx=self.pad, pady=self.pad, sticky="nsew", row=1, column=3, rowspan=2)
        ctk.CTkLabel(cal_fm_sel_unit, text="SETTINGS").grid(padx=self.pad, pady=self.pad, sticky="NW")
        ctk.CTkLabel(cal_fm_sel_unit, text="Enter calibration accuracy     :").grid(padx=self.pad, pady=[0, self.pad], sticky="SEW")
        ctk.CTkEntry(cal_fm_sel_unit, textvariable=self.accuracy).grid(padx=self.pad, pady=[0, self.pad], sticky="NEW")
        ctk.CTkLabel(cal_fm_sel_unit, textvariable=self.neg_a, font=self.font_text).grid(padx=self.pad, pady=self.pad, sticky="sew")
        ctk.CTkLabel(cal_fm_sel_unit, textvariable=self.pre_a, font=self.font_text).grid(padx=self.pad, pady=self.pad, sticky="sew")
        
        ctk.CTkLabel(cal_fm, textvariable=self.tx_cal, font=self.font_text).grid(padx=self.pad, pady=self.pad, sticky="sew", row=1, column=4)
        ctk.CTkButton(cal_fm, text="CALIBRATE", font=self.font_button, command=self._calibrationUI).grid(
            padx=self.pad, pady=self.pad, sticky="sew", row=2, column=4)

        

        self.cal_cvs = FigureCanvasTkAgg(self.cal_fig, cal_fm_graph)
        self.cal_cvs.get_tk_widget().grid(sticky=ctk.NSEW)
        self.cal_cvs._tkcanvas.grid(padx=self.pad, pady=self.pad, sticky=ctk.NSEW)

        self.anim = FuncAnimation(self.cal_fig, lambda frame: self.updateCal(frame), frames=range(100), interval=self._arduino.interval + 3)

        mon_fm = ctk.CTkFrame(self.root)
        mon_fm.grid(padx=self.pad + 10, pady=self.pad, sticky="new")
        ctk.CTkLabel(mon_fm, text="MONITOR", font=self.font_title).grid(padx=self.pad, pady=self.pad, sticky="nw")

        mon_fm_graph = ctk.CTkFrame(mon_fm, width=700)
        mon_fm_graph.grid(padx=self.pad, pady=self.pad, sticky="nsew", column=0, row=1)

        self.mon_cvs = FigureCanvasTkAgg(self.mon_fig, mon_fm_graph)
        self.mon_cvs.get_tk_widget().grid(sticky=ctk.NSEW)
        self.mon_cvs._tkcanvas.grid(padx=self.pad, pady=self.pad, sticky=ctk.NSEW)

        self.anim2 = FuncAnimation(self.mon_fig, lambda frame: self.updateMon(frame), frames=range(100), interval=self._arduino.interval + 2)

        mon_fm_gaud = ctk.CTkFrame(mon_fm)
        mon_fm_gaud.grid(padx=self.pad, pady=self.pad, sticky="nsew", column=1, row=1)
        self.gauge_cvs = FigureCanvasTkAgg(self.gauge_fig, mon_fm_gaud)
        self.gauge_cvs.get_tk_widget().grid(sticky=ctk.NSEW)
        self.gauge_cvs._tkcanvas.grid(padx=self.pad, pady=self.pad, sticky=ctk.NSEW)

        ctk.CTkLabel(mon_fm_gaud, textvariable=self.tx_gaud, font=self.font_button).grid(sticky="NEW")

        self.anim3 = FuncAnimation(self.gauge_fig, lambda frame: self.updateGauge(frame), frames=range(100), interval=self._arduino.interval + 1)

        plt.show()

        self.root.mainloop()

    def _calibrationUI(self) -> bool:
        self._is_paused = True
        # TEST NO WEIGHT
        calibrate.UI("Calibrate without weight", self._arduino, self._calibrationCallback1, accuracy=self.accuracy.get()).start()

    def _calibrationCallback1(self, data):
        print(data)
        if type(data) is float:
            self._arduino.negative_calibration = data

            self.neg_a.set(value=f"Negative Calibration  = [ {self._arduino.negative_calibration} ]")
            calibrate.UI("Calibrate with weight", self._arduino, self._calibrationCallback2,accuracy=self.accuracy.get(), has_weight=True).start()

        elif type(data) is str:
            self._is_paused = False
        else:
            self._is_paused = False
            print("ERROR: Cal1")

    def _calibrationCallback2(self, data):
        if type(data) is float:
            self.calibration_result = data
            self._arduino.precision_adjustment = data
            self.tx_cal.set(value=f"[  {self.calibration_result:.2f}  ] kg")
            self.pre_a.set(value=f"Precision Calibration  = [ {self._arduino.precision_adjustment} ]")
        self._is_paused = False

    def _monitorUI(self) -> bool:
        result = monitor.UI()

    def updateCal(self, frame):
        if not self._is_paused:
            data = self._arduino.readline()
            self.y_data.append(data)

            self.check(data)

            for rect, h in zip(self.plt_bar, self.y_data):
                rect.set_height(h)

        return self.plt_bar

    def updateMon(self, frame):
        if not self._is_paused:
            self.x_data = list(range(len(self.y_data)))

            self.plt_line[0].set_data(self.x_data[-self.max_x_data - 1:], list(self.y_data)[-self.max_x_data:])

        return self.plt_line

    def updateGauge(self, frame):
        if not self._is_paused:
            data = self._arduino.readline()
            # self.plt_gauge.theta1 = max(0, min(90, 90 - ((data - self.lowest) / (self.highest - self.lowest) * 90)))
            self.plt_gauge.theta1 = max(0, min(180, 180 - ((data - self.lowest) / (self.highest - self.lowest) * 180)))

            self.tx_gaud.set(value=f'[ {self.lowest :.2f} / {data :.2f} kg /  {self.highest :.2f} kg ]')
        return self.plt_gauge

    def check(self, data):
        if self.highest < data:
            self.highest = data
            self.bar_grp.set_ylim(self.lowest, self.highest + 1)
            self.line_grp.set_ylim(self.lowest, self.highest + 1)
            self.line_grp.relim()
        if self.lowest > data:
            self.lowest = data
            self.bar_grp.set_ylim(self.lowest - 1, self.highest)
            self.line_grp.set_ylim(self.lowest - 1, self.highest)
            self.line_grp.relim()


if __name__ == "__main__":
    arduino = serial.Arduino(port, baudrate, interval=100, negative_cal=94, precision_adj=90)
    app = App(arduino)

    app.start()
