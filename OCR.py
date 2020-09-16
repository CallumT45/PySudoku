import matplotlib.pyplot as plt
import re
import cv2
import pytesseract
import numpy as np
from statistics import mode
import string
import time


class OCR():
    def __init__(self, image, accuracy):
        height, width, channels = image.shape
        self.image = image[int(height*0.1):int(height*0.9),
                           int(width*0.1):int(width*0.9)]
        self.accuracy = accuracy

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

    def morph(self, image):
        cv_img = cv2.medianBlur(image, 5)

        ret, th1 = cv2.threshold(cv_img, 127, 255, cv2.THRESH_BINARY)
        th2 = cv2.adaptiveThreshold(
            cv_img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
        th3 = cv2.adaptiveThreshold(
            cv_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

        kernel_erosion = np.ones((3, 3), np.uint8)
        kernel_dilation = np.ones((1, 1), np.uint8)
        erosion = cv2.erode(th2, kernel_erosion, iterations=1)
        dilation = cv2.dilate(erosion, kernel_dilation, iterations=1)
        return dilation

    def process_image(self):

        deskew = self.deskew(self.image)
        basegray = self.get_grayscale(self.image)
        gray = self.get_grayscale(deskew)
        thresh = self.thresholding(gray)
        morph = self.morph(gray)

        if self.accuracy == 0:
            self.images = [basegray]
        else:
            self.images = [morph, thresh, basegray]

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
        # plt.savefig(f'testing/{time.time()}.png')
        # plt.close()

        plt.show()

    def main(self):
        self.process_image()
        custom_config = r'--oem 3 --psm 10 outputbase digits tessedit_char_whitelist=123456789'
        output = []
        # self.show_images()
        for image in self.images:
            guess = pytesseract.image_to_string(
                image, config=custom_config)
            if not guess:
                return 0
            guess = guess.replace("\x0c", "").replace("\n", "")
            guess = guess.translate(str.maketrans('', '', string.punctuation))
            output.append(guess)
        return self.find_valid_mode(output)

    def find_valid_mode(self, l):
        valid_list = [item for item in l if item and int(item) < 10]
        if not valid_list:
            return 0

        try:
            return mode(valid_list)
        except:
            return 0


if __name__ == "__main__":

    ocr = OCR(cv2.imread('out.PNG'))
    ocr.process_image()
    print(ocr.main())
