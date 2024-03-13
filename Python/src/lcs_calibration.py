
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from matplotlib.figure import Figure
from matplotlib.patches import Arc
from matplotlib.animation import FuncAnimation
import matplotlib
import matplotlib.pyplot as plt


matplotlib.use("TkAgg")
ctk.set_appearance_mode("dark")
plt.style.use("dark_background")


class UI:
    def __init__(self, title, arduino, callback_function):
        print(f"START: {title}")
        self.root = ctk.CTk()
        self.root.title(title)
        self.callback_function = callback_function
        self._arduino = arduino

        self.root.protocol("WM_DELETE_WINDOW", self.cancel_callback)

        self.stable = []

        self.gauge_fig = Figure(figsize=(4, 4), dpi=50)
        self.gauge_ax = self.gauge_fig.add_subplot(111)
        self.plt_gauge = Arc((0.5, 0.5), 1, 0.5, theta1=180, theta2=180, linewidth=4)

        self.gauge_ax.add_patch(self.plt_gauge)
        self.gauge_ax.axis('off')
        self.tx_gaud = ctk.StringVar(self.root, value="GAUGE")
        self.tx_list = ctk.StringVar(self.root, value="VALUE: ")

        self.is_stable = False
        self.is_cancelled = False
        self.started = False

        self.highest = 1
        self.lowest = 0

        self.root.title(title)
        self.root.resizable(False, False)
        self.font_title = ('Arial', 16)
        self.font_text = ('Arial', 12)
        self.font_button = ('Arial', 14)
        self.pad = 10

    def close_window(self):
        self.is_cancelled = True
        self.is_stable = True
        self.root.destroy()

    def start(self):
        mon_fm_gaud = ctk.CTkFrame(self.root)
        mon_fm_gaud.grid(padx=self.pad, pady=self.pad, sticky="nsew", column=0, row=0, columnspan=3)
        self.gauge_cvs = FigureCanvasTkAgg(self.gauge_fig, mon_fm_gaud)
        self.gauge_cvs.get_tk_widget().grid(sticky=ctk.NSEW, row=0, column=0)
        self.gauge_cvs._tkcanvas.grid(padx=self.pad, pady=self.pad, sticky=ctk.NSEW,  row=0, column=0)

        ctk.CTkLabel(mon_fm_gaud, textvariable=self.tx_gaud, font=self.font_button).grid(sticky="NEW")
        ctk.CTkLabel(self.root, textvariable=self.tx_list, font=self.font_button).grid(sticky="SEW", row=0, column=3)


        ctk.CTkButton(self.root, text="Cancel", command=self.cancel_callback).grid(padx=self.pad, pady=self.pad, row=1, column=2)
        self.btn_ok = ctk.CTkButton(self.root, text="START", command=self.ok_callback)
        self.btn_ok.grid(padx=self.pad, pady=self.pad, row=1, column=3)
        
        
        self.anim3 = FuncAnimation(self.gauge_fig, lambda frame: self.updateGauge(frame), frames=range(100), interval=100)
        plt.show()
        self.root.mainloop()

    def cancel_callback(self):
        self.is_cancelled = True
        self.is_stable = True
        try:
            if self.root.winfo_exists():
                self.root.after(0, self.callback_function, "NO VALUE")
                self.root.after(0, self.close_window)
        except Exception as e:
            print(f"Error in cancel_callback: {e}")

    def ok_callback(self):
        if self.is_stable:
            try:
                if self.root.winfo_exists():
                    self.root.after(0, self.callback_function, self.stable[0])
                    self.root.after(0, self.close_window)
            except Exception as e:
                print(f"Error in cancel_callback: {e}")
        else:
            self.anim3.resume()
            self.started = True
            self.btn_ok.configure(True,text="OK", state="disabled")

    def updateGauge(self, frame):
        if self.started:
            data = self._arduino.readline()
            self.stable.insert(0, data)
            if (len(self.stable) >= 5):
                self.stable.pop()
                if all(d == self.stable[0] for d in self.stable):
                    print(self.stable)
                    self.is_stable = True
                    self.anim3.pause()
                    self.btn_ok.configure(True,state="normal")

            if self.highest < data:
                self.highest = data
            if self.lowest > data:
                self.lowest = data
            self.plt_gauge.theta1 = max(0, min(180, 180 - ((data - self.lowest) / (self.highest - self.lowest) * 180)))

            self.tx_gaud.set(value=f'[ {self.lowest :.2f} / {data :.2f} kg /  {self.highest :.2f} kg ]')
            self.tx_list.set(value=f"[ LIST of values: ]\n\n [ {" ] kg\n [ ".join(str(d) for d in self.stable)} ] kg")

            return self.plt_gauge
        
        else:
            return self.plt_gauge

    def test(self, cal: str) -> bool:
        print(cal)
        return True

# CALIBRATIONS value
# negative calibration -> value = value - neg_cal      tare()
# float adjustment -> value = value / adj_cal

# ADD weight
# 1kg value -> v1 = value (with 1kg)
# 2kg value -> v2 = value (with 2kg)
    
def callback_function(x):
    print(f"END: {x}")


if __name__ == "__main__":
    UI("TEST", arduino=serial.Arduino("0", 0, 100, 94, 90), callback_function=callback_function).start()

