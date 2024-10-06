import cv2


def steerable_morphology_filter(image, kernel_size, theta, iterations, mode="open"):
  kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
  angle = 0
  for _ in range(iterations):
    angle += theta
    M = cv2.getRotationMatrix2D((kernel_size // 2, kernel_size // 2), angle, 1)
    kernel = cv2.warpAffine(kernel, M, (kernel_size, kernel_size))
    if mode == "close":
      image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    elif mode == "open":
      image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
  return image


def open_do_give(filepath, kernel_size=17, angle=10, iterations=18):
  image = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)

  thresh = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 13, 2)
  image = thresh

  image = cv2.medianBlur(image, 5)

  filtered_image = steerable_morphology_filter(image, kernel_size, angle, iterations)

  imgs = [image, filtered_image]
  return imgs
