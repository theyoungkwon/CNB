import matplotlib
import numpy as np

from ExpApp.Utils.constants import X_LIM, DPI, REDRAW_INTERVAL, BACKGROUND_COLOR
from ExpApp.Utils.constants import CHANNELS_NUMBER

matplotlib.use("Qt4Agg")
from matplotlib.figure import Figure
from matplotlib.animation import TimedAnimation
from matplotlib.lines import Line2D
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

graph_palette_default = [
    '#52d5fe',  # line
    '#93a0f2',  # tail
    '#93a0f2',  # head
]

graph_palette_black = [
    '#000000',  # line
    '#000000',  # tail
    '#000000',  # head
]

class GraphWidget(FigureCanvas, TimedAnimation):

    def __init__(self, is_cool):

        self.addedData = []
        self.subplots = []
        self.lines = []
        self.line_heads = []
        self.line_tails = []
        self.xlim = X_LIM
        self.n = np.linspace(0, self.xlim - 1, self.xlim)

        self.y = []
        for i in range(CHANNELS_NUMBER):
            self.y.append((self.n * 0.0) + 50)

        self.fig = Figure(figsize=(5, 5), dpi=DPI)
        if is_cool:
            self.fig.set_facecolor(BACKGROUND_COLOR)

        self.subplots = []
        for i in range(CHANNELS_NUMBER):
            palette = graph_palette_default
            line = Line2D([], [], color=palette[0], linewidth=3)
            line_tail = Line2D([], [], color=palette[1], linewidth=4)
            line_head = Line2D([], [], color=palette[2], marker='o', markeredgecolor='b')

            subplot = self.fig.add_subplot(CHANNELS_NUMBER, 1, i + 1)
            subplot.add_line(line)
            subplot.add_line(line_tail)
            subplot.add_line(line_head)
            subplot.set_xlim(0, self.xlim - 1)
            if is_cool:
                subplot.set_axis_off()

            self.lines.append(line)
            self.line_heads.append(line_head)
            self.line_tails.append(line_tail)
            self.subplots.append(subplot)

        self.sample_num = 0

        FigureCanvas.__init__(self, self.fig)
        TimedAnimation.__init__(self, self.fig, interval=REDRAW_INTERVAL, blit=True)

    def new_frame_seq(self):
        return iter(range(self.n.size))

    def _init_draw(self):
        for i in range(len(self.subplots)):
            self.subplots[i].set_ylim(-128, +128)
            for l in [self.lines[i], self.line_tails[i], self.line_heads[i]]:
                l.set_data([], [])

    def addData(self, value):
        self.addedData.append(value)
        self.sample_num = self.sample_num + 1

    def _step(self, *args):
        try:
            TimedAnimation._step(self, *args)
        except Exception as e:
            self.abc += 1
            print(str(self.abc))
            TimedAnimation._stop(self)
            pass

    def _draw_frame(self, framedata):
        margin = 2
        while len(self.addedData) > 0:
            for i in range(len(self.subplots)):
                self.y[i] = np.roll(self.y[i], -1)
                self.y[i][-1] = self.addedData[0][i]
            del (self.addedData[0])

        self._drawn_artists = []
        for i in range(len(self.subplots)):
            line = self.lines[i]
            tail = self.line_tails[i]
            head = self.line_heads[i]

            line.set_data(self.n[0: self.n.size - margin], self.y[i][0: self.n.size - margin])
            tail.set_data(np.append(self.n[-10:-1 - margin], self.n[-1 - margin]),
                          np.append(self.y[i][-10:-1 - margin], self.y[i][-1 - margin]))
            head.set_data(self.n[-1 - margin], self.y[i][-1 - margin])

            self._drawn_artists.append(line)
            self._drawn_artists.append(tail)
            self._drawn_artists.append(head)
