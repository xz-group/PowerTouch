import os
from pathlib import Path
import matplotlib.pyplot as plt

with open('../../coordinates.txt') as f_read:
    lines = f_read.readlines()

# Count
count_points = len(lines)
print('The number of touches is ' + str(count_points))

# Plot
x_plot = list()
y_plot = list()
for line in lines:
    x_plot.append(int(line.split()[1]))
    y_plot.append(int(line.split()[2]))

    ax = plt.subplot(1, 1, 1)
    # ax.scatter(x_plot, y_plot, s=10)
    ax.plot(x_plot, y_plot, '-o')
    ax.set_xlim([0, 1080])
    ax.set_ylim([0, 1920])
    ax.set_aspect('equal')
    ax.set_title('Touch locations on the screen')
    plt.gca().invert_yaxis()

    plt.show()
