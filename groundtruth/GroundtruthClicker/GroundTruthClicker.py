import cv2
import numpy as np
import os
import csv
from math import ceil
from ast import literal_eval as make_tuple

#100 Schwänzelläufe
#punkte raus spiechern
#csv

'''
Class to Draw Stuff on Images or Frames with OpenCV
'''
class Draw:
    refernce_point = []
    angle = 0
    drawn = False

    '''
    CALLBACKS FOR MOUSE INTEACTION
    '''
    '''
    Define the two refernce_points for the line and draw the line
    If the left button down event is triggered the start point is saved
    By releasing it the end point is saved
    At last the Line will be drawn
    '''
    def click_and_draw_line(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.refernce_point = [(x, y)]

        elif event == cv2.EVENT_LBUTTONUP:
            self.refernce_point.append((x, y))

            self.draw_line()

    def draw_line_from_center(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONUP:
            size_x, size_y, colors = image.shape
            self.refernce_point = [(ceil(size_x/2), ceil(size_y/2))]
            self.refernce_point.append((x, y))

            self.drawn = True
            self.draw_line()

    def draw_line(self):
        if len(self.refernce_point) > 0:
            cv2.line(image, self.refernce_point[0], self.refernce_point[1], (0, 255, 0), 1)
            cv2.imshow("Click and Draw", image)

    def calc_angle(self):
        if len(self.refernce_point) > 0:
            y = self.refernce_point[1][1] - self.refernce_point[0][1]
            x = self.refernce_point[1][0] - self.refernce_point[0][0]

            self.angle = (np.arctan2(y, x) * 180 / np.pi) * -1

    def set_refernce_points(self, start_point, end_point):
        self.refernce_point = [start_point]
        self.refernce_point.append(end_point)

    def get_angle(self):
        return self.angle

    def get_refernce_points(self):
        return self.refernce_point

    def get_drawn(self):
        return self.drawn

    def reset_drawing(self):
        self.refernce_point = []
        self.angle = 0
        self.drawn = False

class VidPlayer:
    _vid_path = ''
    _vid_capture = None
    _vid_speed = 50
    _vid_paused = False
    _vid_running = True

    def __init__(self, path = None):
        self._vid_path    = path
        self._vid_capture = cv2.VideoCapture(path)

    def set_vid_path(self, path):
        self._vid_path    = path
        self._vid_capture = cv2.VideoCapture(path)
        self._vid_running = True

    def set_play_speed(self, number):
        if number < 10:
            self._vid_speed = 10
        else:
            self._vid_speed = number

    '''
    Returns the actual path of the video source
    '''
    def get_vid_path(self):
        return self._vid_path

    '''
    Returns the speed in wich the video is played
    '''
    def get_play_speed(self):
        return self._vid_speed

    '''
    Returns the capture Object
    '''
    def get_vid_capture(self):
        return self._vid_capture

    '''
    Returns a boolen wich is true if the vid is running
    '''
    def get_vid_running(self):
        return self._vid_running

    '''
    Some Controlls
    '''
    def vid_player_controlls(self):
        key = cv2.waitKey(self._vid_speed) & 0xFF

        if key == ord("-"):
            if (self._vid_speed > 10):
                self._vid_speed += 10

        elif key == ord("+"):
            self._vid_speed -= 10

        elif key == ord("p"):
            if self._vid_paused == False:
                self._vid_paused = True
                self._vid_speed = 0
            else:
                self._vid_paused = False
                self._vid_speed = 50

        elif key == ord("c"):
            self._vid_running = False

    def vid_restart(self):
        self._vid_capture = cv2.VideoCapture(self._vid_path)
        return self._vid_capture

#image = cv2.imread('/home/sascwitt/Projects/test/testPics/Lauf1/image_001.png')
#vc = cv2.VideoCapture('/home/sascwitt/Projects/test/testPics/kurz/image_%3d.png')

path = '/home/sascwitt/Projects/test/WDs/'

vp = VidPlayer()

folders = os.listdir(path)
folders.sort()
draw = Draw()

cv2.namedWindow("Click and Draw")
cv2.setMouseCallback("Click and Draw", draw.draw_line_from_center)

counter = 0
first_frame = True

for folder in folders:
    tmp_path = path + folder
    wd_runs = os.listdir(tmp_path)

    for run in wd_runs:
        vp.set_vid_path(tmp_path + '/' +  run + '/' +'image_%3d.png')
        capture = vp.get_vid_capture()

        while(vp.get_vid_running()):
            ret, image = capture.read()
            if (ret == True):
                image = cv2.resize(image, None, fx = 3, fy = 3, interpolation = cv2.INTER_CUBIC)

                if (os.path.isfile(tmp_path + '/' +  run + '/' + "result.csv") and first_frame):
                    start = 0
                    end  = 0

                    with open(tmp_path + '/' +  run + '/' + "result.csv") as csvfile:
                        reader = csv.DictReader(csvfile)
                        for row in reader:
                            start = make_tuple(row['\ufeffStart Point'])
                            end   = make_tuple(row['End Point'])

                    draw.set_refernce_points(start, end)
                    first_frame = False

                draw.draw_line()
                cv2.imshow("Click and Draw", image)
                vp.vid_player_controlls()

            else:
                capture = vp.vid_restart()

        draw.calc_angle()

        if (draw.get_drawn()):
            with open(tmp_path + '/' + run + '/' + 'result.csv', 'w', newline='', encoding='utf-8-sig') as out:
                csv_out = csv.writer(out)
                csv_out.writerow(['Start Point'] + ['End Point'] + ['Angle'])
                csv_out.writerow([draw.get_refernce_points()[0]] + [draw.get_refernce_points()[1]] + [draw.get_angle()])
                counter += 1

        print(counter)
        draw.reset_drawing()
        first_frame = True

capture.release()
cv2.destroyAllWindows()
