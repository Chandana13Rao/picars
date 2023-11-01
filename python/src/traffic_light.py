import cv2
import numpy as np


def detect_color(cv_img):
    # calculate 2D histograms for pairs of channels: GR
    histGR = cv2.calcHist([cv_img], [1, 2], None, [256, 256], [0, 256, 0, 256])

    # histogram is float and counts need to be scale to range 0 to 255
    # histScaled = (
    #     exposure.rescale_intensity(histGR, in_range=(0, 1), out_range=(0, 255))
    #     .clip(0, 255)
    #     .astype(np.uint8)
    # )
    histScaled = (histGR * 255).clip(0, 255).astype(np.uint8)

    # make masks
    ww = 256
    hh = 256
    ww13 = ww // 3
    ww23 = 2 * ww13
    hh13 = hh // 3
    hh23 = 2 * hh13
    black = np.zeros_like(histScaled, dtype=np.uint8)
    # specify points in OpenCV x,y format
    ptsUR = np.array([[[ww13, 0], [ww - 1, hh23], [ww - 1, 0]]], dtype=np.int32)
    redMask = black.copy()
    cv2.fillPoly(redMask, ptsUR, (255, 255, 255))
    ptsBL = np.array([[[0, hh13], [ww23, hh - 1], [0, hh - 1]]], dtype=np.int32)
    greenMask = black.copy()
    cv2.fillPoly(greenMask, ptsBL, (255, 255, 255))

    # Test histogram against masks
    region = cv2.bitwise_and(histScaled, histScaled, mask=redMask)
    redCount = np.count_nonzero(region)
    region = cv2.bitwise_and(histScaled, histScaled, mask=greenMask)
    greenCount = np.count_nonzero(region)
    print("redCount:", redCount)
    print("greenCount:", greenCount)

    # Find color
    threshCount = 100
    if redCount > greenCount and redCount > threshCount:
        color = "red"
    elif greenCount > redCount and greenCount > threshCount:
        color = "green"
    elif redCount < threshCount and greenCount < threshCount:
        color = "yellow"
    else:
        color = "other"

    # view results
    # cv2.imshow("hist", histScaled)
    # cv2.imshow("redMask", redMask)
    # cv2.imshow("greenMask", greenMask)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return color


def detect_traffic_light(cv_img):
    cimg = cv_img
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)

    # hough circle detect
    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        1,
        100,
        param1=100,
        param2=40,
        minRadius=0,
        maxRadius=30,
    )

    # If circles were detected, proceed with color detection
    if circles is not None:
        print(f"{len(circles[0]) = }")
        for circle in circles[0]:
            x, y, r = map(round, circle)
            cv2.circle(cimg, (x, y), r, (0, 255, 0), 2)
            # Extract the region around the circle
            region_around_circle = cv_img[y - r : y + r, x - r : x + r]
            color = detect_color(region_around_circle)

            # Print the detected color for each circle
            print(f"Circle at ({x}, {y}) is {color}")
    else:
        print("No circles detected")
        color = "other"
    # TODO: Major color extraction yet to be done

    return color, cimg


if __name__ == "__main__":
    filenames = [
        "../assests/traffic_light_red",
        "../assests/traffic_light_green",
        "../assests/traffic_light_yellow",
        "../assests/red",
    ]

    for filename in filenames:
        print(filename)
        # read image
        cv_img = cv2.imread(filename + ".jpg")
        print("*****************************************")
        _, cimg = detect_traffic_light(cv_img)
        cv2.imwrite(filename + "_circles.jpg", cimg)
        print("*****************************************")
