import matplotlib.pyplot as plt
import numpy as np


class TouchEventPlotHandler:
    def __init__(self, axes, slot_index, color_list):
        # self._color_list = ['tab:green', 'tab:blue', 'tab:orange', 'tab:purple', 'tab:cyan', 'tab:olive', 'tab:gray',
        #                    'tab:brown', 'tab:pink', 'tab:red']
        self.slot_index = slot_index
        self.tracking_id = -1
        self.x_record = []
        self.y_record = []
        self.points = []
        self.circles = []
        self.arrows = []
        self.timestamps = []
        self.axes = axes
        self.color = color_list[self.slot_index]
        self.annotation = None

    def plotNewTouch(self, x, y, diameter, tracking_id, timestamp, plot_circle=True):
        if np.isnan(diameter):
            diameter = 6

        if plot_circle is True:
            circle = plt.Circle((x, y), diameter, color=self.color, fill=False)
            self.axes.add_patch(circle)
            self.circles.append(circle)
        else:
            circle = plt.Circle((x, y), 6, color=self.color, fill=True)
            self.axes.add_patch(circle)
            self.circles.append(circle)

        self.annotation = self.axes.annotate(str(self.slot_index), xy=(x, y),
                                             xytext=(x + diameter * 0.6, y + diameter * 0.6), color=self.color)

        point, = self.axes.plot(x, y, marker='o', color=self.color, markersize=1)
        self.points.append(point)
        self.x_record.append(x)
        self.y_record.append(y)

        self.tracking_id = tracking_id
        self.timestamps.append(timestamp)
        return [circle, self.annotation, point]

    def plotMoveTouch(self, x, y, diameter, timestamp, plot_circle=True):
        if plot_circle is True:
            if np.isnan(diameter):
                diameter = 6
            circle = plt.Circle((x, y), diameter, color=self.color, fill=False)
            self.axes.add_patch(circle)
            self.circles.append(circle)
        else:
            circle = plt.Circle((x, y), 6, color=self.color, fill=True)
            self.axes.add_patch(circle)
            self.circles.append(circle)

        arrow = plt.arrow(self.x_record[-1], self.y_record[-1], x - self.x_record[-1], y - self.y_record[-1],
                          length_includes_head=True,
                          color=self.color,
                          linestyle='-',
                          width=1,
                          head_width=24,
                          head_length=12)
        self.arrows.append(arrow)
        self.x_record.append(x)
        self.y_record.append(y)
        self.timestamps.append(timestamp)

        point, = self.axes.plot(x, y, marker='o', color=self.color, markersize=1)
        self.points.append(point)
        return [circle, point, arrow]

    def plotLiftTouch(self, timestamp):
        point, = self.axes.plot(self.x_record[-1], self.y_record[-1], marker='x', color='r')
        self.points.append(point)
        self.timestamps.append(timestamp)
        return [point]

    def clearTouch(self):
        for a in self.arrows:
            a.remove()
        for c in self.circles:
            c.remove()
        for p in self.points:
            p.remove()
        self.annotation.remove()

    def returnArtist(self):
        artist = []
        artist.extend(self.points)
        artist.extend(self.circles)
        artist.extend(self.arrows)
        artist.append(self.annotation)
        return artist
