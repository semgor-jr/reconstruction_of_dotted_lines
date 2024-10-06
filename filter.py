import cv2
import numpy as np


def merge_contours(contour1, contour2, threshold):
  merged_contour = []
  for j in range(len(contour2) - 1):
    distance = cv2.pointPolygonTest(contour1, (int(contour2[j][0][0]), int(contour2[j][0][1])), measureDist=True)
    if abs(distance) <= threshold:
      merged_contour.append(contour2[j])
  for j in range(len(contour1) - 1):
    distance = cv2.pointPolygonTest(contour2, (int(contour1[j][0][0]), int(contour1[j][0][1])), measureDist=True)
    if abs(distance) <= threshold:
      merged_contour.append(contour1[j])
  return np.array([merged_contour], dtype=np.int32)


def min_distance(contour1, contour2):
  min_dist = float('inf')
  closest_point1 = None
  closest_point2 = None
  for i in range(len(contour1) - 1):
    for j in range(len(contour2) - 1):
      dist = np.linalg.norm(contour1[i] - contour2[j])
      if dist < min_dist:
        min_dist = dist
        closest_point1 = contour1[i]
        closest_point2 = contour2[j]
  return min_dist, closest_point1, closest_point2


def open_do_give(filepath, threshold):
  image = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
  pairs = []

  thresh = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 13, 2)

  image = thresh
  image = cv2.medianBlur(image, 5)

  edges = cv2.Canny(image, 0, 200)
  contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

  res = np.uint8(np.zeros((image.shape[0], image.shape[1], 3), dtype='uint8'))
  cv2.drawContours(res, contours, -1, (255, 255, 255), 1, cv2.LINE_AA, hierarchy, 1)
  prom = res.copy()
  new = []
  cv2.fillPoly(image, contours, (0, 0, 0))
  for i, contour1 in enumerate(contours):
      for j, contour2 in enumerate(contours):
        if i != j and [j, i] not in pairs:
          pairs.append([i, j])
          dist, p1, p2 = min_distance(contour1, contour2)

          if dist < threshold:
            flag = 0
            cv2.line(prom, (p1[0][0], p1[0][1]), (p2[0][0], p2[0][1]), (255, 255, 255), 2)
            cv2.circle(prom, (p1[0][0], p1[0][1]), int(1.5 * dist), (255, 255, 255), 1)
            count = 0
            for k in range(len(contour2) - 1):
              rng = (contour2[k][0][0] - p2[0][1])**2 + (contour2[k][0][1] - p2[0][0])**2
              if abs(rng - (1.5 * dist)**2) < 0.3 * threshold:
                count += 1
                if count >= 3:
                  flag = 1
                  break
            if (flag != 1):
              count = 0
              for k in range(len(contour1) - 1):
                rng = (contour1[k][0][0] - p1[0][1])**2 + (contour1[k][0][1] - p1[0][0])**2
                if abs(rng - (1.5 * dist)**2) < 0.3 * threshold:
                  count += 1
                  if count >= 3:
                    flag = 1
                    break
            if (flag == 1):
              continue

            merged_contour = merge_contours(contour1, contour2, threshold)
            hull = cv2.convexHull(merged_contour[0])
            v = cv2.approxPolyDP(hull, 10, True)
            if (len(v) == 2 or len(v) == 4):
              cv2.fillPoly(image, [hull], (0, 0, 0))
            new.append(hull)
  for i, c  in enumerate(new):
    new_contour = c
    cv2.drawContours(res, [new_contour], -1, (255, 255, 255), 1, cv2.LINE_AA, hierarchy, 1)
    cv2.fillPoly(res, [new_contour], (255, 255, 255))
  imgs = [image, res, prom]
  return  imgs
