from skimage.metrics import structural_similarity as ssim
import numpy as np
import cv2
import sys

def mse(imageA, imageB):
	res = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
	res /= float(imageA.shape[0] * imageA.shape[1])
	return res

imageA = cv2.imread(sys.argv[1])
imageB = cv2.imread(sys.argv[2])

# convert the images to grayscale
imageAgs = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
imageBgs = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)


if __name__ == "__main__":
	print(f'SSIM: {ssim(imageAgs, imageBgs)}, MSE: {mse(imageA, imageB)}')