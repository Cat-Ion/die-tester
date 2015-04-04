import cv2
import subprocess

class Image:
    def __init__(self, img, num = -1):
        self.img = img
#        self.img = cv2.bilateralFilter(img, 5, 15, 15)
#        self.img = cv2.GaussianBlur(self.img, None, 2)
#        self.img = cv2.Laplacian(self.img, cv2.CV_8U, scale = 3, ksize = 5)
#        self.img = cv2.GaussianBlur(self.img, None, 2)
        self.processed = None
#        self.keypoints, self.descriptors = sift.detectAndCompute(self.img, None)
        self.num = num

def grab_image():
    subprocess.call(["gphoto2", "--no-keep", "--capture-image-and-download", "--force-overwrite", "--quiet"])
    return open_image("capt0000.jpg")

def open_image(path, num = -1):
    return Image(cv2.imread(path), num)

def process(sift, img):
    if img.processed == None:
        img.processed = img.img

    img.processed = cv2.bilateralFilter(img.processed, 5, 15, 15)
    img.processed = cv2.GaussianBlur(img.processed, None, 2)
    img.processed = cv2.Laplacian(img.processed, cv2.CV_8U, scale = 3, ksize = 5)
    img.processed = cv2.GaussianBlur(img.processed, None, 2)
    img.keypoints, img.descriptors = sift.detectAndCompute(img.processed, None)
