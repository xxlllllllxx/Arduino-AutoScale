
## CONFIGURATION #########
# pip install pyserial
# pip install matplotlib
# pip install customtkinter
# pip install openpyxl

from matplotlib.patches import Arc
from matplotlib.animation import FuncAnimation
import serial
from collections import deque
import customtkinter as ctk
import src.lcs_graph as monitor
import src.lcs_calibration as calibrate
# ARDUINO or MOCK
import src.lcs_serial as serial
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib
import matplotlib.pyplot as plt
import datetime
from openpyxl import Workbook, load_workbook
import threading
import time


matplotlib.use("TkAgg")
ctk.set_appearance_mode("dark")
plt.style.use("dark_background")


title = "Arduino Project"  # for TITLE

# NOTE: Configure this port and baudrate
port = "COM3"  # check in arduino
baudrate = 9600  # check in arduino


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

        self.cal_fig = Figure(figsize=(14, 4), dpi=50, constrained_layout=False)
        self.bar_grp = self.cal_fig.add_subplot(111)
        self.bar_grp.set_ylim(self.lowest - 1, self.highest)
        self.plt_bar = self.bar_grp.bar(self.x_data, [0] * self.max_x_data)

        self.mon_fig = Figure(figsize=(14, 4), dpi=50, constrained_layout=False)
        self.line_grp = self.mon_fig.add_subplot(111)
        self.plt_line = self.line_grp.plot(self.x_data, [0] * self.max_x_data, lw=2)

        self.gauge_fig = Figure(figsize=(4, 4), dpi=50)
        self.gauge_ax = self.gauge_fig.add_subplot(111)
        self.plt_gauge = Arc((0.5, 0.5), 1, 0.5, theta1=180, theta2=180, linewidth=4)

        self.gauge_ax.add_patch(self.plt_gauge)
        self.gauge_ax.axis('off')
        self.tx_gaud = ctk.StringVar(value="GAUGE")

        # RECORD
        self.tx_record = ctk.StringVar()
        self.file_loc: str = "data/data_sheet.xlsx"
        self.workbook: Workbook = load_workbook(self.file_loc)
        self.sheet = self.workbook.active

        # CALIBRATION
        self.selected_calibration: int = 1
        self.unit: str = "kg"
        self.tx_cal = ctk.StringVar(value="[ 0.00000 ] kg")
        self.calibration_result = 1
        self.accuracy = ctk.IntVar(value=5)
        self.neg_a = ctk.StringVar(value=f"Negative Calibration  = [ {self._arduino.negative_calibration:.2f} ]")
        self.pre_a = ctk.StringVar(value=f"Precision Calibration = [ {self._arduino.precision_adjustment:.2f} ]")

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
        ctk.CTkLabel(cal_fm, text="CALIBRATION", font=self.font_title).grid(padx=self.pad, sticky="nw")
        cal_fm_graph = ctk.CTkFrame(cal_fm, width=500)
        cal_fm_graph.grid(padx=self.pad, pady=self.pad/2, sticky="nsew", row=1, column=0, columnspan=3)
        cal_fm_sel_unit = ctk.CTkFrame(cal_fm)
        cal_fm_sel_unit.grid(padx=self.pad, pady=self.pad/2, sticky="nsew", row=1, column=3, rowspan=3)
        ctk.CTkLabel(cal_fm_sel_unit, text="SETTINGS").grid(padx=self.pad, pady=self.pad, sticky="NW")
        ctk.CTkLabel(cal_fm_sel_unit, text="Enter calibration accuracy                   :").grid(padx=self.pad, pady=[0, self.pad], sticky="SEW")
        ctk.CTkEntry(cal_fm_sel_unit, textvariable=self.accuracy).grid(padx=self.pad, pady=[0, self.pad], sticky="NEW")
        ctk.CTkLabel(cal_fm_sel_unit, textvariable=self.neg_a, font=self.font_text).grid(padx=self.pad, pady=self.pad, sticky="sew")
        ctk.CTkLabel(cal_fm_sel_unit, textvariable=self.pre_a, font=self.font_text).grid(padx=self.pad, pady=self.pad, sticky="sew")

        ctk.CTkLabel(cal_fm, textvariable=self.tx_cal, font=self.font_text).grid(padx=self.pad, pady=self.pad, sticky="sew", row=4, column=2)
        ctk.CTkButton(cal_fm, text="CALIBRATE", font=self.font_button, command=self._calibrationUI).grid(
            padx=self.pad, pady=self.pad/2, sticky="sew", row=4, column=3)

        self.cal_cvs = FigureCanvasTkAgg(self.cal_fig, cal_fm_graph)
        self.cal_cvs.get_tk_widget().grid(sticky=ctk.NSEW)
        self.cal_cvs._tkcanvas.grid(padx=self.pad, pady=self.pad/2, sticky=ctk.NSEW)

        self.anim = FuncAnimation(self.cal_fig, lambda frame: self.updateCal(frame), frames=range(100), interval=self._arduino.interval + 3)

        mon_fm = ctk.CTkFrame(self.root)
        mon_fm.grid(padx=self.pad + 10, pady=self.pad,  sticky="new")
        ctk.CTkLabel(mon_fm, text="MONITOR", font=self.font_title).grid(padx=self.pad, sticky="nw")

        mon_fm_graph = ctk.CTkFrame(mon_fm, width=700)
        mon_fm_graph.grid(padx=self.pad, pady=self.pad/2, sticky="nsew", column=0, row=1, columnspan=4)

        self.mon_cvs = FigureCanvasTkAgg(self.mon_fig, mon_fm_graph)
        self.mon_cvs.get_tk_widget().grid(sticky=ctk.NSEW)
        self.mon_cvs._tkcanvas.grid(padx=self.pad, pady=self.pad/2, sticky=ctk.NSEW)

        self.anim2 = FuncAnimation(self.mon_fig, lambda frame: self.updateMon(frame), frames=range(100), interval=self._arduino.interval + 2)

        mon_fm_gaud = ctk.CTkFrame(mon_fm)
        mon_fm_gaud.grid(padx=self.pad, pady=self.pad, sticky="nsew", column=4, row=1)
        self.gauge_cvs = FigureCanvasTkAgg(self.gauge_fig, mon_fm_gaud)
        self.gauge_cvs.get_tk_widget().grid(sticky=ctk.NSEW)
        self.gauge_cvs._tkcanvas.grid(padx=self.pad, pady=self.pad/2, sticky=ctk.NSEW)

        ctk.CTkLabel(mon_fm_gaud, textvariable=self.tx_gaud, font=self.font_button).grid(sticky="NEW")

        self.anim3 = FuncAnimation(self.gauge_fig, lambda frame: self.updateGauge(frame), frames=range(100), interval=self._arduino.interval + 1)

        plt.show()

        ctk.CTkButton(mon_fm, text="SHOW FULL GRAPH", font=self.font_button, command=self._monitorUI).grid(
            padx=self.pad, pady=self.pad/2, sticky="sew", row=2, column=4)

        ctk.CTkLabel(mon_fm, text="Record label: ", font=self.font_text).grid(padx=self.pad, pady=self.pad/2, sticky="ne", row=2, column=0)
        ctk.CTkEntry(mon_fm, textvariable=self.tx_record, width=400).grid(
            padx=self.pad, pady=self.pad/2, sticky="ne", row=2, column=1)
        self.status_label = ctk.CTkLabel(mon_fm, text="", text_color="blue")
        self.status_label.grid(padx=self.pad, pady=self.pad/2, sticky="nw", row=2, column=2)
        self.logger = ctk.CTkButton(mon_fm, text="LOG", font=self.font_button, command=self._record, )
        self.logger.grid(padx=self.pad, pady=self.pad/2, sticky="nw", row=2, column=3)

        self.root.mainloop()

    def _record_thread(self):
        if self.tx_record.get():
            self.update_status("Logging", "blue")
            label: str = self.tx_record.get()
            value1: str = self._arduino.readline()
            time.sleep(self._arduino.interval/100)
            value2: str = self._arduino.readline()
            time.sleep(self._arduino.interval/100)
            value3: str = self._arduino.readline()
            dt: datetime.datetime = datetime.datetime.now()
            d: str = dt.strftime("%a, %b %d, %Y")
            t: str = dt.strftime("%I : %m : %S : %f")
            try:
                self.sheet.append([d, t, label, value1, value2, value3])
                self.workbook.save(self.file_loc)
                self.update_status("Saved!", "Green")
                self.update_record()
            except Exception as e:
                self.update_status("Error!", "red")
        else:
            self.update_status("Empty!", "orange")

        self.update_logger()
        time.sleep(3)
        self.update_status()

    def update_status(self, label: str = "", color: str = "blue"):
        self.status_label.configure(text=label, text_color=color)

    def update_record(self, txt: str = ""):
        self.tx_record.set(txt)

    def update_logger(self):
        self.logger.configure(state="normal")

    def _record(self):
        self.logger.configure(state="disabled")
        threading.Thread(target=self._record_thread).start()

    def _calibrationUI(self) -> bool:
        self._is_paused = True
        # TEST NO WEIGHT
        calibrate.UI("Calibrate without weight", self._arduino, self._calibrationCallback1, accuracy=self.accuracy.get()).start()

    def _calibrationCallback1(self, data):
        if type(data) is float:
            self._arduino.negative_calibration = data

            self.neg_a.set(value=f"Negative Calibration  = [ {self._arduino.negative_calibration:.2f} ]")
            calibrate.UI("Calibrate with weight", self._arduino, self._calibrationCallback2, accuracy=self.accuracy.get(), has_weight=True).start()

        elif type(data) is str:
            self._is_paused = False
        else:
            self._is_paused = False
            print("ERROR: Cal1")

    def _calibrationCallback2(self, data):
        if type(data) is float:
            self.calibration_result = data
            self._arduino.precision_adjustment = data
            self.tx_cal.set(value=f"Currently calibrated to [  {self.calibration_result:.5f}  ] kg")
            self.pre_a.set(value=f"Precision Calibration  = [ {self._arduino.precision_adjustment:.2f} ]")
        self._is_paused = False

    def _monitorUI(self) -> bool:
        monitor.UI(self._arduino)

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
    arduino = serial.Arduino(port, baudrate, interval=500, negative_cal=1, precision_adj=1)
    app = App(arduino)
    app.start()

    # while True: 
    #     print(arduino.readline())
