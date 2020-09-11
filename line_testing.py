from PIL import Image, ImageDraw
import cv2
import numpy as np
from matplotlib import pyplot as plt
from pprint import pprint
from Line import Line
import itertools

# img = cv2.imread('images/fuzzy_sudoku.jpg')
# img = cv2.imread('images/sudoku.jpg')
# img = cv2.imread('images/sudoku1.jpg')
# img = cv2.imread('images/web_sudoku2.PNG')
img = cv2.imread('images/web_sudoku.PNG')

lower = 90
higher = 180
apSize = 3
print("lower: ", lower, "higher: ", higher, 'apertureSize: ', apSize)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(gray, lower, higher, apertureSize=apSize)

if apSize == 7 or apSize == 5:
    kernel = np.ones((3, 3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)

    kernel = np.ones((5, 5), np.uint8)
    edges = cv2.erode(edges, kernel, iterations=1)

# plt.imshow(edges)
# plt.show()

height, width, channels = img.shape

# num_lines = 1000
# count = 1
# while num_lines > 100:
#     lines = cv2.HoughLines(edges, 1, np.pi/180, 100 + 50*count)
#     num_lines = len(lines)
#     print(len(lines))
#     print("count: ", 100+50*count)
#     count += 1


lines = cv2.HoughLines(edges, 1, np.pi/180, 150)


if not lines.any():
    print('No lines were found')
    exit()

# line filter from stack exchange https://stackoverflow.com/questions/48954246/find-sudoku-grid-using-opencv-and-python
if filter:
    print(height, width)

    if height < 400:
        rho_threshold = 20
    else:
        rho_threshold = 40
    theta_threshold = 0.1  # keep below 1.5

    # how many lines are similar to a given one
    similar_lines = {i: [] for i in range(len(lines))}
    for i in range(len(lines)):
        for j in range(len(lines)):
            if i == j:
                continue
# min(abs(theta_i - theta_j), abs(theta_i + 2*np.pi-theta_j), abs(theta_i - 2*np.pi-theta_j))
            rho_i, theta_i = lines[i][0]
            # print(i, theta_i)
            rho_j, theta_j = lines[j][0]
            # pprint(abs(min(np.pi - theta_i, theta_i) -
            #            min(np.pi - theta_j, theta_j)))

            if abs(abs(rho_i) - abs(rho_j)) < rho_threshold and abs(np.sin(theta_i) - np.sin(theta_j)) < theta_threshold:
                similar_lines[i].append(j)

    # ordering the INDECES of the lines by how many are similar to them
    indices = [i for i in range(len(lines))]
    indices.sort(key=lambda x: len(similar_lines[x]))

    # line flags is the base for the filtering
    line_flags = len(lines)*[True]
    for i in range(len(lines) - 1):
        # if we already disregarded the ith element in the ordered list then we don't care (we will not delete anything based on it and we will never reconsider using this line again)
        if not line_flags[indices[i]]:
            continue

        # we are only considering those elements that had less similar line
        for j in range(i + 1, len(lines)):
            # and only if we have not disregarded them already
            if not line_flags[indices[j]]:
                continue

            rho_i, theta_i = lines[indices[i]][0]
            rho_j, theta_j = lines[indices[j]][0]
            if abs(abs(rho_i) - abs(rho_j)) < rho_threshold and abs(np.sin(theta_i) - np.sin(theta_j)) < theta_threshold:
                # if it is similar and have not been disregarded yet then drop it now
                line_flags[indices[j]] = False

print('number of Hough lines:', len(lines))

filtered_lines = []

if filter:
    for i in range(len(lines)):  # filtering
        if line_flags[i]:
            filtered_lines.append(lines[i])

    print('Number of filtered lines:', len(filtered_lines))
else:
    filtered_lines = lines


return_lines = []
temp = 0
for line in filtered_lines:
    rho, theta = line[0]
    a = np.cos(theta)
    b = np.sin(theta)
    x0 = a*rho
    y0 = b*rho
    x1 = int(x0 + 1000*(-b))
    y1 = int(y0 + 1000*(a))
    x2 = int(x0 - 1000*(-b))
    y2 = int(y0 - 1000*(a))
    return_lines.append(((x1, y1), (x2, y2)))

    cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

    temp += 1

plt.imshow(img)
plt.show()


# maps all input lines to a Line object and places into a list
lines = list(map(lambda x: Line(x[0], x[1]), return_lines))

# print(list(map(lambda x: x.slope, lines)))

# pprint(list(map(lambda x: x[0], return_lines)))
