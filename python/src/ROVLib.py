import math
from collections import deque

import cv2
import imutils
import numpy as np


def motor_values_from_input(left_vector, right_vector, vertical_vector, deadzone=0.1):
    """motor_values_from_input(left_vector, right_vector, deadzone=0.1)
    Takes two vectors representing motor speeds
    for left and right sides of an ROV where every motor is angled 45 degrees. Returns a dictionary of motor values."""

    # To prevent a divide by zero error, put the joystick angle at zero
    if right_vector[1] == 0:
        if right_vector[0] >= 0:
            right_joystick_angle = 0
        else:
            right_joystick_angle = 180 * math.pi / 180.0
    else:
        right_joystick_angle = math.atan(right_vector[0] / right_vector[1])

    right_motor_angle = right_joystick_angle + (45.0 * math.pi / 180.0)

    # If the joystick does not properly recenter, set it to 0
    if (abs(right_vector[0]) < deadzone) and (abs(right_vector[1]) < deadzone):
        right_raw_motor_x = 0
        right_raw_motor_y = 0
    else:
        right_raw_motor_x = math.sin(right_motor_angle)
        right_raw_motor_y = math.cos(right_motor_angle)

    if right_vector[1] < 0.0:
        right_raw_motor_y = right_raw_motor_y * -1
        right_raw_motor_x = right_raw_motor_x * -1

    try:
        right_scale = max(abs(right_vector[0]), abs(right_vector[1])) / max(abs(right_raw_motor_x),
                                                                            abs(right_raw_motor_y))
    except ZeroDivisionError:
        right_scale = 0

    scaled_right_motor_x = right_scale * right_raw_motor_x

    if scaled_right_motor_x > 1.0:
        scaled_right_motor_x = 1.0
    elif scaled_right_motor_x < -1.0:
        scaled_right_motor_x = -1.0

    if (scaled_right_motor_x > 0) and (scaled_right_motor_x < 0.40):
        scaled_right_motor_x = scaled_right_motor_x / 2
    elif (scaled_right_motor_x >= 0.40) and (scaled_right_motor_x < 0.70):
        scaled_right_motor_x = scaled_right_motor_x - 0.20
    elif (scaled_right_motor_x >= 0.70) and (scaled_right_motor_x == 1):
        scaled_right_motor_x = (5 / 3) * scaled_right_motor_x - 2 / 3

    if (scaled_right_motor_x > -0.40) and (scaled_right_motor_x < 0):
        scaled_right_motor_x = scaled_right_motor_x / 2
    elif -0.40 >= scaled_right_motor_x > -0.70:
        scaled_right_motor_x = scaled_right_motor_x + 0.20
    elif scaled_right_motor_x <= 0.70 and scaled_right_motor_x == -1:
        scaled_right_motor_x = (5 / 3) * scaled_right_motor_x + 2 / 3

    scaled_right_motor_y = right_scale * right_raw_motor_y

    if scaled_right_motor_y > 1.0:
        scaled_right_motor_y = 1.0
    elif scaled_right_motor_y < -1.0:
        scaled_right_motor_y = -1.0

    if (scaled_right_motor_y > 0) and (scaled_right_motor_y < 0.40):
        scaled_right_motor_y = scaled_right_motor_y / 2
    elif (scaled_right_motor_y >= 0.40) and (scaled_right_motor_y < 0.70):
        scaled_right_motor_y = scaled_right_motor_y - 0.20
    elif (scaled_right_motor_y >= 0.70) and (scaled_right_motor_y == 1):
        scaled_right_motor_y = (5 / 3) * scaled_right_motor_y - 2 / 3

    if (scaled_right_motor_y > -0.40) and (scaled_right_motor_y < 0):
        scaled_right_motor_y = scaled_right_motor_y / 2
    elif -0.40 >= scaled_right_motor_y > -0.70:
        scaled_right_motor_y = scaled_right_motor_y + 0.20
    elif scaled_right_motor_y <= 0.70 and scaled_right_motor_y == -1:
        scaled_right_motor_y = (5 / 3) * scaled_right_motor_y + 2 / 3

    if left_vector[1] == 0:
        if left_vector[0] >= 0:
            left_joystick_angle = 0
        else:
            left_joystick_angle = 180 * math.pi / 180.0
    else:
        left_joystick_angle = math.atan(left_vector[0] / left_vector[1])

    left_motor_angle = left_joystick_angle + (45.0 * math.pi / 180.0)

    if (abs(left_vector[0]) < deadzone) and (abs(left_vector[1]) < deadzone):
        left_raw_motor_x = 0
        left_raw_motor_y = 0
    else:
        left_raw_motor_x = math.sin(left_motor_angle)
        left_raw_motor_y = math.cos(left_motor_angle)

    if left_vector[1] < 0.0:
        left_raw_motor_y = left_raw_motor_y * -1
        left_raw_motor_x = left_raw_motor_x * -1
    try:
        left_scale = max(abs(left_vector[0]), abs(left_vector[1])) / max(abs(left_raw_motor_x), abs(left_raw_motor_y))
    except ZeroDivisionError:
        left_scale = 0
    scaled_left_motor_x = left_scale * left_raw_motor_x

    # Limit the power to 1 for left x
    if scaled_left_motor_x > 1.0:
        scaled_left_motor_x = 1.0
    elif scaled_left_motor_x < -1.0:
        scaled_left_motor_x = -1.0

    # Scale left x motor when positive
    if (scaled_left_motor_x > 0) and (scaled_left_motor_x < 0.40):
        scaled_left_motor_x = scaled_left_motor_x / 2
    elif (scaled_left_motor_x >= 0.40) and (scaled_left_motor_x < 0.70):
        scaled_left_motor_x = scaled_left_motor_x - 0.20
    elif (scaled_left_motor_x >= 0.70) and (scaled_left_motor_x == 1):
        scaled_left_motor_x = (5 / 3) * scaled_left_motor_x - 2 / 3
    # Scale left x motor when negative
    if (scaled_left_motor_x > -0.40) and (scaled_left_motor_x < 0):
        scaled_left_motor_x = scaled_left_motor_x / 2
    elif -0.40 >= scaled_left_motor_x > -0.70:
        scaled_left_motor_x = scaled_left_motor_x + 0.20
    elif scaled_left_motor_x <= 0.70 and scaled_left_motor_x == -1:
        scaled_left_motor_x = (5 / 3) * scaled_left_motor_x + 2 / 3

    # Limit the power to 1 for left y
    scaled_left_motor_y = left_scale * left_raw_motor_y

    if scaled_left_motor_y > 1.0:
        scaled_left_motor_y = 1.0
    elif scaled_left_motor_y < -1.0:
        scaled_left_motor_y = -1.0

    # Scale left y when positive
    if (scaled_left_motor_y > 0) and (scaled_left_motor_y < 0.40):
        scaled_left_motor_y = scaled_left_motor_y / 2
    elif (scaled_left_motor_y >= 0.40) and (scaled_left_motor_y < 0.70):
        scaled_left_motor_y = scaled_left_motor_y - 0.20
    elif (scaled_left_motor_y >= 0.70) and (scaled_left_motor_y == 1):
        scaled_left_motor_y = (5 / 3) * scaled_left_motor_y - 2 / 3
    # Scale left y when negative
    if (scaled_left_motor_y > -0.40) and (scaled_left_motor_y < 0):
        scaled_left_motor_y = scaled_left_motor_y / 2
    elif -0.40 >= scaled_left_motor_y > -0.70:
        scaled_left_motor_y = scaled_left_motor_y + 0.20
    elif scaled_left_motor_y <= 0.70 and scaled_left_motor_y == -1:
        scaled_left_motor_y = (5 / 3) * scaled_left_motor_y + 2 / 3

    return {"top_left": scaled_left_motor_x, "top_right": scaled_right_motor_y, "bottom_left": scaled_left_motor_y,
            "bottom_right": scaled_right_motor_x, "vertical_left": vertical_vector[0],
            "vertical_right": vertical_vector[1]}


def transect_line(image, lower_color_bound=(127, 127, 127), upper_color_bound=(255, 255, 255), lower_canny_bound=0,
                  upper_canny_bound=255, aperture_size=3, hough_lines_threshold=175, target_line_distance=10,
                  line_distance_multiplier=1 / 100, line_offset_multiplier=1 / 100):
    """transect_line(image, target_line_distance) Takes an image represented as a numpy array, thresholds it to allow
    only colors within the lower and upper bounds provided, uses Canny edge detection on it, gets lines in the image
    using HoughLines, filters out all but the shortest 2 lines, averages those lines' angles, gets the difference
    between the averaged angle and forward, uses that difference to get 2 vectors for motor_values_from_input, gets the offset from the center of the 2 detected lines and the actual center, combines all the vectors to make a new, final vector, passes that in chunks to motor_values_from_input, and returns the result.

    Returns a dictionary of motor values."""

    grayscale = cv2.inRange(image, lower_color_bound, upper_color_bound)  # Filter out all pixels that can't be lines
    # we're looking for
    edges = cv2.Canny(grayscale, lower_canny_bound, upper_canny_bound, apertureSize=aperture_size)  # Find edges with
    # Canny edge detection

    try:
        lines = cv2.HoughLines(edges, 1, np.pi / 180, hough_lines_threshold)[0]  # Get lines from the edges
    except TypeError:  # This error could be caused by a white background; invert the image and recalculate everything
        grayscale = cv2.bitwise_not(grayscale)
        edges = cv2.Canny(grayscale, lower_canny_bound, upper_canny_bound, apertureSize=aperture_size)  # Find edges
        # with Canny edge detection
        lines = cv2.HoughLines(edges, 1, np.pi / 180, hough_lines_threshold)[0]  # Try to get lines from the edges again

    longest_lines = deque([(0.0, 0.0, 0.0)], 2)  # Limited deque of tuples in the form (line length, angle, center x)

    print(len(lines))

    for rho, theta in lines:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 + 1000 * (-b))
        y1 = int(y0 + 1000 * (a))
        x2 = int(x0 - 1000 * (-b))
        y2 = int(y0 - 1000 * (a))

        try:
            m = (y2 - y1) / (x2 - x1)
        except ZeroDivisionError:
            center_x = image.shape[0] / 2
        else:
            center_x = 1 / m * (-b) + (1 / m) * (image.shape[0] / 2)

        length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        if length > min(longest_lines, key=lambda x: x[0])[0]:  # If the smallest line in longest_lines is smaller
            # than this new length, replace it with the new line's angle and line length
            longest_lines.append((length, theta, center_x))

    heading = (longest_lines[0][1] + longest_lines[1][1]) / 2  # Average the remaining 2 angles to get the final heading
    heading -= 1.57  # We want to go forward, so subtract 90 degrees (in radians) from the calculated heading
    rotation_heading_vectors = ((0, math.sin(heading)), (0, -math.sin(heading)))  # Calculate the heading vectors
    # from the heading angle

    distance = abs(longest_lines[0][2] - longest_lines[1][2]) - target_line_distance  # Calculate the distance
    # between the midpoints of the lines and the target line distance
    vertical_power = max(min(distance * line_distance_multiplier, 1.0), -1.0)  # Multiply the distance by the distance
    # multiplier and clip the result to the maximum motor power (1)

    print(longest_lines)
    average_center_x = (longest_lines[0][2] + longest_lines[1][2]) / 2  # Average the centers of the lines
    center_offset = max(min((average_center_x - image.shape[1] / 2) * line_offset_multiplier, 1.0), -1.0)  # Subtract
    # the averaged center from the actual center x of the image, multiply that offset by the offset multiplier,
    # and clip the result to the maximum motor power (1)

    strafe_heading_vectors = ((center_offset, 0), (center_offset, 0))
    print(average_center_x, image.shape[1] / 2)

    final_heading_vectors = ((strafe_heading_vectors[0][0], rotation_heading_vectors[0][1]),
                             (strafe_heading_vectors[1][0], rotation_heading_vectors[1][1]))  # Calculate the final
    # heading vectors as a combination of the x and y values of the pre calculated heading vectors

    return motor_values_from_input(*final_heading_vectors, (vertical_power,) * 2)  # Finally, calculate the actual
    # motor values from the new combined heading and return them


def coral_detection_circle(image_1, image_2, threshold_min=175, threshold_max=255, max_features=50000, match_threshold=0.15, display=False):
    grayscale_1 = cv2.cvtColor(image_1, cv2.COLOR_BGR2GRAY)  # Convert images to grayscale
    grayscale_2 = cv2.cvtColor(image_2, cv2.COLOR_BGR2GRAY)

    if display:
        cv2.imshow("Image 1 Grayscale", grayscale_1)
        cv2.imshow("Image 2 Grayscale", grayscale_2)

    blurred_1 = cv2.GaussianBlur(grayscale_1, (5, 5), 0)  # Blur the images
    blurred_2 = cv2.GaussianBlur(grayscale_2, (5, 5), 0)

    if display:
        cv2.imshow("Image 1 Blurred", blurred_1)
        cv2.imshow("Image 2 Blurred", blurred_2)

    thresholded_1 = cv2.threshold(blurred_1, threshold_min, threshold_max, cv2.THRESH_BINARY)[1]  # Threshold the images
    thresholded_2 = cv2.threshold(blurred_2, threshold_min, threshold_max, cv2.THRESH_BINARY)[1]

    if display:
        cv2.imshow("Image 1 Thresholded", thresholded_1)
        cv2.imshow("Image 2 Thresholded", thresholded_2)

    contours_1 = imutils.grab_contours(cv2.findContours(thresholded_1.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE))
    contours_2 = imutils.grab_contours(cv2.findContours(thresholded_2.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE))

    # Detect ORB features and compute descriptors
    orb = cv2.ORB_create(max_features)
    keypoints_1, descriptors_1 = orb.detectAndCompute(grayscale_1, None)
    keypoints_2, descriptors_2 = orb.detectAndCompute(grayscale_2, None)

    # Match features.
    matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
    matches = matcher.match(descriptors_1, descriptors_2, None)

    # Sort matches by score
    matches.sort(key=lambda x: x.distance, reverse=False)

    # Remove matches that don't meet the threshold
    good_matches_number = int(len(matches) * match_threshold)
    matches = matches[:good_matches_number]

    if display:
        # Draw top matches
        image_matches = cv2.drawMatches(image_1, keypoints_1, image_2, keypoints_2, matches, None)
        cv2.imshow("Matches", image_matches)
        # cv2.imwrite("matches.jpg", image_matches)

    # Extract location of good matches
    points_1 = np.zeros((len(matches), 2), dtype=np.float32)
    points_2 = np.zeros((len(matches), 2), dtype=np.float32)

    for i, match in enumerate(matches):
        points_1[i, :] = keypoints_1[match.queryIdx].pt
        points_2[i, :] = keypoints_2[match.trainIdx].pt

    # Get the homography matrix
    homography, mask = cv2.findHomography(points_1, points_2, cv2.RANSAC)

    # Apply it to the first image
    height, width, channels = image_1.shape
    transformed_image_1 = cv2.warpPerspective(image_1, homography, (width, height))

    if display:
        print(transformed_image_1.shape[:2][::-1])
        cv2.imshow("Image 1 Transformed", transformed_image_1)
        overlayed = cv2.addWeighted(transformed_image_1, 0.5, cv2.resize(image_2, transformed_image_1.shape[:2][::-1]), 0.5, 0.0)
        cv2.imshow("Overlayed", overlayed)


if __name__ == "__main__":
    #  TEST
    image = cv2.imread("parralel_lines.png", cv2.IMREAD_COLOR)
    print(transect_line(image))

    coral_detection_circle(cv2.imread("test_coral_image_1.png"), cv2.imread("test_coral_image_2.png"), display=True)

    while True:
        cv2.waitKey(1)