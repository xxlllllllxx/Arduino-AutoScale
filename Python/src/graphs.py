import matplotlib.pyplot as plt
from matplotlib.patches import Arc
from matplotlib.animation import FuncAnimation
from collections import deque


class Graphs:
    def __init__(self, arduino):
        self.arduino = arduino
        self.fig, ((self.ax1, self.ax2), (self.ax3, self.ax4)) = plt.subplots(2, 2)

        self.max_data = 100
        self.x_data = list(range(self.max_data))
        self.y_data_line = deque(maxlen=self.max_data)
        self.y_data_bar = deque(maxlen=self.max_data)

        self.bar_plot = self.ax2.bar(self.x_data, [0] * self.max_data)
        self.line_plot, = self.ax1.plot(self.x_data, [0] * self.max_data, lw=1)
        self.scatter_plot = self.ax3.scatter(self.x_data, [0]*self.max_data, s=1)

        self.largest = 0

        self.gauge_arc: Arc = Arc((0.5, 0.5), 0.7, 0.7, theta1=180, theta2=180, color='skyblue', linewidth=4)

        self.ax4.add_patch(self.gauge_arc)
        self.tx_element = self.ax4.text(0.5, 0.5, 'GAUGE', ha='center', va='center', fontsize=8)
        self.ax4.axis('off')

        ani = FuncAnimation(self.fig, self.update, frames=range(100), interval=200)

        plt.show()

    def update(self, frame):
        try:
            data = self.arduino.readline()
            value = float(data)

            self.y_data_line.append(value)
            self.y_data_bar.append(value)

            if self.largest < value:
                self.largest = value
                self.ax1.set_ylim(0, self.largest)
                self.ax2.set_ylim(0, self.largest)
                self.ax3.set_ylim(0, self.largest)
                # ax4.set_ylim(0, largest)
                self.ax1.relim()

            # BAR
            for i, bar in enumerate(self.bar_plot):
                if i < len(self.y_data_bar):
                    bar.set_height(self.y_data_bar[i])

            # LINE
            self.line_plot.set_data(self.x_data[-len(self.y_data_line):], self.y_data_line)

            # SCATTER
            self.scatter_plot.set_offsets([(x, y) for x, y in zip(self.x_data[-len(self.y_data_line):], self.y_data_line)])

            # GAUGE
            self.gauge_arc.theta1 = (180 - (value / self.largest * 180))
            self.text_element.set_text(f'{value} / {self.largest}')

        except Exception as e:
            print(f"Error reading data: {e}")

        return self.line_plot, self.bar_plot, self.scatter_plot, self.gauge_arc
