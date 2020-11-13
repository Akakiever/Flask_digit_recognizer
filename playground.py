import cv2

from recognize import recognize

img = cv2.imread('meter.png')
string = recognize(img)
if len(string) > 0:
    print(string)
else:
    print('NOT RECOGNIZED')
