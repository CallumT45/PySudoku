import matplotlib.pyplot as plt
import re
import cv2
import pytesseract
import numpy as np
# from pytesseract import Output
from statistics import mode
import string


class OCR():
    def __init__(self, image):
        self.image = image

    def get_grayscale(self, image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # noise removal

    def remove_noise(self, image):
        return cv2.medianBlur(image, 5)

    # thresholding

    def thresholding(self, image):
        # threshold the image, setting all foreground pixels to
        # 255 and all background pixels to 0
        return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # dilation

    def dilate(self, image):
        kernel = np.ones((5, 5), np.uint8)
        return cv2.dilate(image, kernel, iterations=1)

    # erosion

    def erode(self, image):
        kernel = np.ones((5, 5), np.uint8)
        return cv2.erode(image, kernel, iterations=1)

    # opening - erosion followed by dilation

    def opening(self, image):
        kernel = np.ones((5, 5), np.uint8)
        return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

    # canny edge detection

    def canny(self, image):
        return cv2.Canny(image, 100, 200)

    # skew correction

    def deskew(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.bitwise_not(gray)
        thresh = cv2.threshold(gray, 0, 255,
                               cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        coords = np.column_stack(np.where(thresh > 0))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h),
                                 flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated

    def process_image(self):

        deskew = self.deskew(self.image)
        gray = self.get_grayscale(deskew)
        thresh = self.thresholding(gray)
        rnoise = self.remove_noise(gray)
        # erode = self.erode(gray)
        # opening = self.opening(gray)
        canny = self.canny(gray)

        self.images = [gray, rnoise, deskew, canny,
                       thresh]  # erode, thresh, opening

    def show_images(self, cols=1, titles=None):

        n_images = len(self.images)
        if titles is None:
            titles = ['Image (%d)' % i for i in range(1, n_images + 1)]
        fig = plt.figure()
        for n, (image, title) in enumerate(zip(self.images, titles)):
            a = fig.add_subplot(cols, np.ceil(n_images/float(cols)), n + 1)
            if image.ndim == 2:
                plt.gray()
            plt.imshow(image)
            a.set_title(title)
        # fig.set_size_inches(np.array(fig.get_size_inches()) * n_images)
        plt.show()

    def main(self):
        # self.show_images()
        custom_config = r'--oem 3 --psm 10 outputbase digits tessedit_char_whitelist=0123456789'
        output = []

        for image in self.images:
            guess = pytesseract.image_to_string(
                image, config=custom_config)
            guess = guess.replace("\x0c", "").replace("\n", "")
            guess = guess.translate(str.maketrans('', '', string.punctuation))
            output.append(guess)
        return self.find_valid_mode(output)

    def find_valid_mode(self, l):
        # print(l)
        valid_list = [item for item in l if item and int(item) < 10]
        if not valid_list:
            return 0
        return mode(valid_list)


if __name__ == "__main__":
    ocr = OCR('out.png')
    ocr.process_image()
    ocr.main()
