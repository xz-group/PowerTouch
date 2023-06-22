import os
from pathlib import Path
import matplotlib.pyplot as plt

# while True:
file_path = Path('../../coordinates.txt')
if file_path.exists():
	os.remove('../../coordinates.txt')

with open('../../events.txt') as f_read:
	lines = f_read.readlines()

for i in range(len(lines)):
	line = lines[i]
	line = line.split()

	if len(line) != 5:
		# print("Reach to the last row!")
		continue

	if line[3] == 'ABS_MT_POSITION_X':
		if lines[i+2].split()[3] == 'ABS_MT_POSITION_Y':
			time_raw = line[1]
			time_stamp = time_raw.split(']')[0]
			x_coordinate = str(int(line[4], 16))
			y_line = lines[i + 2].split()
			y_coordinate = str(int(y_line[4], 16))

			with open('../../coordinates.txt', 'a') as f_write:
				f_write.write(time_stamp)
				f_write.write(' ')
				f_write.write(x_coordinate)
				f_write.write(' ')
				f_write.write(y_coordinate)
				f_write.write(' ')
				f_write.write('\n')

with open('../../coordinates.txt') as f_read:
	lines = f_read.readlines()

#Count
count_points = len(lines)
print('The number of touches is '+str(count_points))

# Plot
x_plot = list()
y_plot = list()
for line in lines:
	x_plot.append(int(line.split()[1]))
	y_plot.append(int(line.split()[2]))

ax = plt.subplot(1, 1, 1)
ax.scatter(x_plot, y_plot, s=10)
ax.set_xlim([0, 1080])
ax.set_ylim([0, 1920])
ax.set_aspect('equal')
ax.set_title('Touch locations on the screen')
plt.gca().invert_yaxis()

plt.show()
	
