from PIL import Image, ImageDraw
import cv2
import numpy as np
from matplotlib import pyplot as plt
import itertools
from Line import Line


class SudokuImage():
    def __init__(self, PATH):
        self.image_path = PATH

    def get_lines(self):
        img = cv2.imread(self.image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 90, 150, apertureSize=3)
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)
        kernel = np.ones((5, 5), np.uint8)
        edges = cv2.erode(edges, kernel, iterations=1)

        lines = cv2.HoughLines(edges, 1, np.pi/180, 150)

        if not lines.any():
            print('No lines were found')
            exit()

        if filter:
            rho_threshold = 15
            theta_threshold = 0.1

            # how many lines are similar to a given one
            similar_lines = {i: [] for i in range(len(lines))}
            for i in range(len(lines)):
                for j in range(len(lines)):
                    if i == j:
                        continue

                    rho_i, theta_i = lines[i][0]
                    rho_j, theta_j = lines[j][0]
                    if abs(rho_i - rho_j) < rho_threshold and abs(theta_i - theta_j) < theta_threshold:
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
                    if abs(rho_i - rho_j) < rho_threshold and abs(theta_i - theta_j) < theta_threshold:
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
        return return_lines

    def get_inters(self, input_lines):
        # maps all input lines to a Line object and places into a list
        lines = list(map(lambda x: Line(x[0], x[1]), input_lines))
        # sort lines by slope, taking first half will isolate horizontal lines
        lines.sort(key=lambda x: x.slope)

        # find the intersections of all possible combinations of two lines
        intersections = list(map(lambda x: x[0].find_intersection(
            x[1]), list(itertools.combinations(lines, 2))))
        # removing vlaues where no intersection, can be combined with previous step
        intersections = [inter for inter in intersections if inter]

        intersections_by_line = {0: [], 1: [], 2: [],
                                 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: []}

        # group intersections by line, can be combined with above
        for inter in intersections:
            for line_num, line in enumerate(lines[:len(lines)//2]):
                if line.point_on_line(inter):
                    intersections_by_line[line_num].append(inter)
                    break

        # sorting points left to right
        for i in range(9):
            intersections_by_line[i].sort(key=lambda x: x[0])

        # loops over each line and the one above and adds the points as one grid, points are added as bottom left, bottom righ, top right then top left
        grids = []
        for i in range(9):
            for j in range(9):
                grids.append((tuple(map(lambda x: round(x), intersections_by_line[i][j])), tuple(map(lambda x: round(x), intersections_by_line[i][j+1])),
                              tuple(map(lambda x: round(x), intersections_by_line[i+1][j+1])), tuple(map(lambda x: round(x), intersections_by_line[i+1][j]))))
        return grids


if __name__ == "__main__":
    Su = SudokuImage("fuzzy_sudoku.jpg")
    # print(Su.get_lines())
    print(Su.get_inters(Su.get_lines()))
