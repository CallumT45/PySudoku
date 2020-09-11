from PIL import Image, ImageDraw, ImageGrab
import cv2
import numpy as np
from matplotlib import pyplot as plt
import itertools
from Line import Line
from OCR import OCR

from pprint import pprint
from multiprocessing import Process
import time


class SudokuImage():
    def __init__(self, clipboard=False, PATH=""):
        self.clipboard = clipboard
        if clipboard:
            stall = input("Take a screenshot, then press enter")
            self.image = ImageGrab.grabclipboard().convert('RGB')
            self.image = np.array(self.image)
            # Convert RGB to BGR
            self.image = self.image[:, :, ::-1].copy()
        else:
            self.image = cv2.imread(PATH)

    def get_lines(self):
        height, width, channels = self.image.shape
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 90, 180, apertureSize=3)
        # kernel = np.ones((3, 3), np.uint8)
        # edges = cv2.dilate(edges, kernel, iterations=1)
        # kernel = np.ones((5, 5), np.uint8)
        # edges = cv2.erode(edges, kernel, iterations=1)

        lines = cv2.HoughLines(edges, 1, np.pi/180, 150)

        if not lines.any():
            print('No lines were found')
            exit()

        if filter:
            if height < 400:
                rho_threshold = 20
            else:
                rho_threshold = 40
            theta_threshold = 0.1

            # how many lines are similar to a given one
            similar_lines = {i: [] for i in range(len(lines))}
            for i in range(len(lines)):
                for j in range(len(lines)):
                    if i == j:
                        continue

                    rho_i, theta_i = lines[i][0]
                    rho_j, theta_j = lines[j][0]
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
            # cv2.line(self.image, (x1, y1), (x2, y2), (0, 0, 255), 2)
        # plt.imshow(self.image)
        # plt.show()
        return return_lines

    def get_inters(self, input_lines):
        # maps all input lines to a Line object and places into a list
        lines = list(map(lambda x: Line(x[0], x[1]), input_lines))
        # sort lines by slope, taking first half will isolate horizontal lines
        lines.sort(key=lambda x: abs(x.slope))
        # print(list(map(lambda x: x.slope, lines)))

        hori_lines = lines[:10]
        hori_lines.sort(key=lambda x: x.point[1])
        verti_lines = lines[10:]
        # find all the intersections for each horizontal line and sort by left to right
        intersections_by_line = {0: [], 1: [], 2: [],
                                 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: []}
        for i, hline in enumerate(hori_lines):
            intersections_by_line[i] = sorted(list(
                map(lambda x: hline.find_intersection(x), lines[10:])), key=lambda x: x[0])

        # loops over each line and the one above and adds the points as one grid, points are added as bottom left, bottom right, top right then top left
        cells = []
        for i in range(9):
            for j in range(9):
                cells.append((tuple(map(lambda x: round(x), intersections_by_line[i][j])), tuple(map(lambda x: round(x), intersections_by_line[i][j+1])),
                              tuple(map(lambda x: round(x), intersections_by_line[i+1][j+1])), tuple(map(lambda x: round(x), intersections_by_line[i+1][j]))))
        return cells

    def get_crop(self, cell):

        # move outside function
        if self.clipboard:
            pil_image = ImageGrab.grabclipboard().convert("RGBA")

        else:
            image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(image).convert("RGBA")

        imArray = np.asarray(pil_image)

        # create mask
        polygon = cell
        maskIm = Image.new('L', (imArray.shape[1], imArray.shape[0]), 0)
        ImageDraw.Draw(maskIm).polygon(polygon, outline=1, fill=1)
        mask = np.array(maskIm)

        # assemble new image (uint8: 0-255)
        newImArray = np.empty(imArray.shape, dtype='uint8')

        # colors (three first columns, RGB)
        newImArray[:, :, :3] = imArray[:, :, :3]

        # transparency (4th column)
        newImArray[:, :, 3] = mask*255

        # back to Image from numpy
        newIm = Image.fromarray(newImArray, "RGBA")
        newIm = newIm.crop(newIm.getbbox())
        return newIm
        # newIm.save("out.png")

    def get_OCR(self, image):
        opcr = OCR(image)
        opcr.process_image()
        return opcr.main()

    def pop_board(self, cells, indexes, board):
        for i in indexes:
            im = self.get_crop(cells[i])

            pil_image = im.convert('RGB')
            open_cv_image = np.array(pil_image)
            # Convert RGB to BGR
            open_cv_image = open_cv_image[:, :, ::-1].copy()
            num = self.get_OCR(open_cv_image)
            board[i//9].append(int(num))


if __name__ == "__main__":
    Su = SudokuImage(False, "images\web_sudoku.PNG")
    lines = Su.get_lines()
    cells = Su.get_inters(lines)

    def draw_board(board):
        for i, line in enumerate(board):
            if i % 3 == 0:
                print("-"*27)
            print(
                f"{line[0]}  {line[1]}  {line[2]} | {line[3]}  {line[4]}  {line[5]} | {line[6]}  {line[7]}  {line[8]}")

    # for i in range(81):
    #     pop_board(i, board)

    print(cells[0])
    Su.get_crop(cells[73])

    # pil_image = im.convert('RGB')
    # open_cv_image = np.array(pil_image)
    # # Convert RGB to BGR
    # open_cv_image = open_cv_image[:, :, ::-1].copy()
    # Su.get_OCR(open_cv_image)
