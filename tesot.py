import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

def warpImg(img, points, w, h, inv=False):
    pts1 = np.float32(points)
    pts2 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
    if inv:
        matrix = cv2.getPerspectiveTransform(pts2, pts1)
    else:
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
    imgWarp = cv2.warpPerspective(img, matrix, (w, h))
    return imgWarp

# Image to be warped
filename = "Best values.png"
img = cv2.imread(filename)

# Initial points for warping
init_points = [[200, 400], [900, 800], [100, 200], [200, 300]]

fig, ax = plt.subplots(1, 1)
plt.subplots_adjust(left=0.25, bottom=0.25)
img_ax = plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
plt.title('Original Image')

# Sliders for adjusting points
axcolor = 'lightgoldenrodyellow'
axpoints = [plt.axes([0.25, i * 0.05, 0.65, 0.03], facecolor=axcolor) for i in range(4)]
sliders = [Slider(axp, f'Point {i//2 + 1} {"X" if i % 2 == 0 else "Y"}', 0, img.shape[1 if i % 2 == 0 else 0], init_points[i//2][i % 2]) for i, axp in enumerate(axpoints)]

def update(val):
    points = [[sliders[0].val, sliders[1].val], [sliders[2].val, sliders[3].val], [sliders[4].val, sliders[5].val], [sliders[6].val, sliders[7].val]]
    warped_img = warpImg(img, points, img.shape[1], img.shape[0])
    img_ax.set_data(cv2.cvtColor(warped_img, cv2.COLOR_BGR2RGB))
    fig.canvas.draw_idle()

for slider in sliders:
    slider.on_changed(update)

plt.show()
