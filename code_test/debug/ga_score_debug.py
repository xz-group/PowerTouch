import numpy as np
import statistics
import matplotlib.pyplot as plt


def normalized_sigmoid_fkt(a, b, x):
    """
    Returns array of a horizontal mirrored normalized sigmoid function
    output between 0 and 1
    Function parameters a = center; b = width
    """
    s = 1 / (1 + np.exp(b * (a - x)))
    return s


fig, ((ax1, ax2), (ax3, ax4), (ax5, ax6)) = plt.subplots(3, 2)
plt.subplots_adjust(wspace=.5)
plt.subplots_adjust(hspace=.5)

std_y = np.linspace(10, 400, 100)
std_score_y = normalized_sigmoid_fkt(-0.5, 10, -std_y / 200)
ax1.plot(std_y, std_score_y, label='200')

std_y = np.linspace(10, 400, 100)
std_score_y = normalized_sigmoid_fkt(-0.5, 10, -std_y / 100)
ax1.plot(std_y, std_score_y, label='100')

ax1.set_title('Std Score Y')
ax1.set_ylabel('std_score_y')
ax1.set_xlabel('std_y')
ax1.legend()
ax1.grid()

std_y = np.linspace(10, 400, 100)
std_score_y = normalized_sigmoid_fkt(-0.5, 10, -std_y / 200)
ax2.plot(std_y, std_score_y, label='200')

std_y = np.linspace(10, 400, 100)
std_score_y = normalized_sigmoid_fkt(50, -0.05, std_y)
ax2.plot(std_y, std_score_y, label='200_eq')

ax2.set_title('Std Score Y')
ax2.set_ylabel('std_score_y')
ax2.set_xlabel('std_y')
ax2.legend()
ax2.grid()

mean_absolute_error_y = np.linspace(10, 900, 100)
# error_score_y = normalized_sigmoid_fkt(-0.5, 10, -mean_absolute_error_y / 500)
# ax3.plot(mean_absolute_error_y, error_score_y, label='500')

error_score_y = normalized_sigmoid_fkt(100, -0.05, mean_absolute_error_y)
ax3.plot(mean_absolute_error_y, error_score_y, label='500_eq')

ax3.set_title('Error Score Y')
ax3.set_ylabel('error_score_y')
ax3.set_xlabel('mean_absolute_error_y')
ax3.legend()
ax3.grid()

# hit_rate = np.linspace(0, 1, 100)
# error_hit_rate = normalized_sigmoid_fkt(0.5, 10, hit_rate)
# ax4.plot(hit_rate, error_hit_rate, label='500')
#
# ax4.set_title('Error Score Y')
# ax4.set_ylabel('error_score_y')
# ax4.set_xlabel('mean_absolute_error_y')
# ax4.legend()
# ax4.grid()
#
# error_score = error_score_y
plt.show()
