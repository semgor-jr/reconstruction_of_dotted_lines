import cv2
import numpy as np

def straight_contour_length(contour):
    min_dist = float('inf')
    max_dist = -float('inf')
    min_point = None
    max_point = None
    for i in range(len(contour) - 1):
        dist = np.linalg.norm(contour[i] - 0)
        if dist < min_dist:
            min_dist = dist
            min_point = contour[i]
        if dist > max_dist:
            max_dist = dist
            max_point = contour[i]
    return np.linalg.norm(max_point - min_point)


def merge_contours(contour1, contour2):
    new_contour = np.concatenate((contour1, contour2))
    new_contour = cv2.convexHull(new_contour)
    return new_contour

def reconstruction(filepath):
# Загрузка изображения
    image = cv2.imread(filepath)

    # Бинаризация
    img_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(img_grey, 90, 255, cv2.THRESH_BINARY)
    # Нахождение контуров
    edges = cv2.Canny(thresh, 50, 150)
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # Новые холсты
    img_contours = [image.copy(), image.copy(), image.copy()]

    # Находим центры контуров, направляющие векторы
    contours_data = []
    for i, contour in enumerate(contours):
        # Ищем центры
        M = cv2.moments(contour)
        if M['m00'] != 0:
            cx = M['m10'] / M['m00']
            cy = M['m01'] / M['m00']
            center = np.array([cx, cy])
            # Создаем наборы направляющих векторов
            angle_step = 0.1  # Шаг в градусах
            angles = np.arange(0, 180, angle_step)
            direction_vectors = [[np.cos(np.deg2rad(angle)), np.sin(np.deg2rad(angle))] for angle in angles]

            approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)
            if len(approx) == 4:  # Прямоугольник
                x, y, w, h = cv2.boundingRect(contour)
                # Определение оси через середины сторон
                if (w > h):
                    optimal_vector = np.array([x, y + h / 2]) - np.array([center[0], center[1]])
                else:
                    optimal_vector = np.array([x + w / 2, y]) - np.array([center[0], center[1]])
                optimal_vector = optimal_vector / np.linalg.norm(optimal_vector)
            else:
                min_distance_sum = float('inf')
                optimal_vector = None
                for direction_vector in direction_vectors:
                    line_equation = np.array([direction_vector[1],
                                              -direction_vector[0],
                                              center[1] * direction_vector[0] - center[0] * direction_vector[1]])
                    distance_sum = 0
                    for point in contour:
                        distance = abs(line_equation[0] * point[0][0] + line_equation[1] * point[0][1]
                                       + line_equation[2]) / np.linalg.norm(line_equation[:2])
                        distance_sum += distance

                    if distance_sum < min_distance_sum:
                        min_distance_sum = distance_sum
                        optimal_vector = direction_vector
            k = optimal_vector[1] / optimal_vector[0]
            b = center[1] - k * center[0]

            length = straight_contour_length(contour)
            contours_data.append([contour, center, k, b, length])
            cv2.line(img_contours[1], (int(cx), int(cy)), (int(cx), int(cy)), (255, 255, 0), 6)

            cv2.line(img_contours[1],
                     tuple(np.int32(np.array([center[0] - length,
                                              k * (center[0] - length) + b]))),
                     tuple(np.int32(np.array([center[0] + length,
                                              k * (center[0] + length) + b]))),
                     (0, 0, 255), 1)
            cv2.drawContours(img_contours[1], contour, -1, (255, 0, 0), 1)

    connected_contours = []
    for i, contour1 in enumerate(contours_data):
        for j, contour2 in enumerate(contours_data):
            if i != j:
                # Проверка расстояния между ближайшими точками контуров
                length1 = straight_contour_length(contour1[0])
                length2 = straight_contour_length(contour2[0])
                center_dist = np.linalg.norm(contour1[1] - contour2[1])
                if (center_dist <= 1.5 * length1 or center_dist <= 1.5 * length2) and (j, i) not in connected_contours:
                    connected_contours.extend([(i, j)])

    for i, j in connected_contours:
        flag = 0
        for k in contours[i]:
            point = k[0][1] - (contours_data[j][2] * k[0][0] + contours_data[j][3])
            if abs(point) < 7.5 and \
                    np.linalg.norm((k[0][0], k[0][1]) - contours_data[j][1]) < 2 * contours_data[j][4]:
                flag = 1
                break
        # print("ok", flag)
        if flag == 0:
            for k in contours[j]:
                point = k[0][1] - (contours_data[i][2] * k[0][0] + contours_data[i][3])
                if abs(point) < 7.5 and \
                        np.linalg.norm((k[0][0], k[0][1]) - contours_data[i][1]) < 2 * contours_data[i][4]:
                    flag = 1
                    break
        # print("ok2", i, j)
        if flag == 1:
            new_contour = merge_contours(contours[i], contours[j])
            # Рисуем и заполняем новый контур
            cv2.fillPoly(img_contours[2], [new_contour], (0, 0, 0))
    return img_contours