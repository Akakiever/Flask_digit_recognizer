import re

import cv2
import pytesseract
from pytesseract import Output


def recognize(cv_img, return_boxes=False, threshold=185):
    cv_img = 255 - cv_img
    cv_img = cv2.threshold(cv_img, threshold, 255, cv2.THRESH_BINARY)[1]
    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    # cv_img = cv2.morphologyEx(cv_img, cv2.MORPH_CLOSE, kernel)

    string = pytesseract.image_to_string(cv_img, config='--psm 6')
    string = re.sub('\D', '', string)
    # print(string)
    if return_boxes:
        if len(string) > 0:
            boxes = pytesseract.image_to_boxes(cv_img, output_type=Output.DICT)
            for box in zip(boxes['left'], boxes['bottom'], boxes['right'], boxes['top'], boxes['char']):
                cv2.rectangle(
                    cv_img,
                    (box[0], box[1]),
                    (box[2], box[3]),
                    (255, 0, 0),
                    2
                )
                cv2.putText(
                    cv_img, box[4],
                    (box[0], box[1]),
                    cv2.FONT_HERSHEY_COMPLEX, 1,
                    (255, 0, 0)
                )
        return string, cv_img
    return string
