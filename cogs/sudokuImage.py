from PIL import Image, ImageDraw, ImageGrab
import cv2
import numpy as np
from cogs.Line import Line
from cogs.OCR import OCR


class SudokuImage():
    def __init__(self, PATH="", accuracy=0, clipboard=False):
        self.clipboard = clipboard
        self.accuracy = accuracy
        if clipboard:
            stall = input("Take a screenshot, then press enter")
            self.image = ImageGrab.grabclipboard().convert('RGB')
            self.image = np.array(self.image)
            # Convert RGB to BGR
            self.image = self.image[:, :, ::-1].copy()
        else:
            self.image = cv2.imread(PATH)

    def get_lines(self):
        """[First processes image then uses Houghlines to find all the lines in the image, these lines are then filtered to remove any similar lines, i.e. lines with a 
        similar slope and in a similar place on the image]

        Returns:
            [list]: [list of tuples of start and end points for the lines]
        """
        height, width, channels = self.image.shape
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 90, 180, apertureSize=3)

        lines = cv2.HoughLines(edges, 1, np.pi/180, 150)

        if not lines.any():
            print('No lines were found')
            exit()

        # filter function improved version from https://stackoverflow.com/questions/48954246/find-sudoku-grid-using-opencv-and-python,
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

        filtered_lines = []

        for i in range(len(lines)):  # filtering
            if line_flags[i]:
                filtered_lines.append(lines[i])

        if len(filtered_lines) != 20:
            print('Lines could not be determined\nTry using a photo with just the sudoku leaving some space for the outisde border')
            exit()

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
        """[Reads in the l;ist of points and converts each element to a line object, these are sorted by slope, to separate horizontal lines from vertical.
            Horizontal lines are then sorted by y value of point, to ensure top to bottom. Then intersections are calculated for each horizontal line with each vertical line.
            These intersections are then grouped to a cell by bottom left, bottom right, top right and then top left.]

        Args:
            input_lines ([list]): [list of start and end points of lines]

        Returns:
            [list]: [cells a list of points to describe each cell within the sudoku game]
        """
        # maps all input lines to a Line object and places into a list
        lines = list(map(lambda x: Line(x[0], x[1]), input_lines))
        # sort lines by slope, taking first half will isolate horizontal lines
        lines.sort(key=lambda x: abs(x.slope))

        hori_lines = lines[:10]
        hori_lines.sort(key=lambda x: x.point[1])
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
        """[Given 4 points, will open the image and crop to fit the shape defined by the 4 points]

        Args:
            cell ([tuple]): [4 points describing a cell]

        Returns:
            [image]: 
        """

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

    def get_OCR(self, image):
        opcr = OCR(image, self.accuracy)
        return opcr.main()

    def pop_board(self, cell):
        """Cropping this way is not supported with Open CV2 and so is done with pillow, but the image needs to be converted back to open cv for OCR"""
        im = self.get_crop(cell)

        pil_image = im.convert('RGB')
        open_cv_image = np.array(pil_image)
        # Convert RGB to BGR
        open_cv_image = open_cv_image[:, :, ::-1].copy()
        num = self.get_OCR(open_cv_image)
        return int(num)
