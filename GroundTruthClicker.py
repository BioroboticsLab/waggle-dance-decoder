#Software to generate GroundTruth data for the dance decoder
#The data is stored in each waggle run directory under resutls.csv
#The output format is as follows:
#[key] + [x0,y0] + [xf,yf] + [raw_angle]
#Example:
#20160814_1001_1/1,"(125, 125)","(189, 69)",41.1859251657

import cv2
import numpy as np
import os
import datetime
import csv
import sys
from math import ceil
from ast import literal_eval as make_tuple

#200 Waggle runs
#vector and angle stored as csv
#Format of the name '%Y%m%d_%H%M.csv' stored in Data/GTData/

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
            #size_x, size_y, colors = image.shape            
            size_x = 250
            size_y = 250
            self.refernce_point = [(ceil(size_x/2), ceil(size_y/2))]
            self.refernce_point.append((x, y))

            self.drawn = True
            self.draw_line()

    def draw_line(self, image):
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
    _vid_direction = 'right'
    _vid_dance = 10

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
            
    def set_vid_dance(self, dance):
        self._vid_dance = dance

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
        
    def get_vid_dance(self):
        return self._vid_dance

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
                
        elif key == ord("n") or key == ord("N"):
            self._vid_running = False            
            self._vid_dance = 0
            self._vid_direction = 'right'
            
        elif key == ord("y") or key == ord("Y"):
            self._vid_running = False
            self._vid_dance = 1
            self._vid_direction = 'right'       
            
        elif key == ord("v") or key == ord("V"):
            self._vid_running = False            
            self._vid_dance = 2
            self._vid_direction = 'right'

        elif key == ord("c") or key == ord("C"):
            self._vid_running = False
            
        elif key == 27:
            self._vid_running = False            
            self._vid_dance = -1

    def vid_restart(self):
        self._vid_capture = cv2.VideoCapture(self._vid_path)
        return self._vid_capture


def main():
    argv = sys.argv
    if (len(argv) == 1):
        path = input("Please enter WaggleDance Path")

    if (len(argv) == 2):
        path = argv[1]


    vp = VidPlayer()
    folders = os.listdir(path)
    folders.sort()
    draw = Draw()

    cv2.namedWindow("Click and Draw")
    cv2.setMouseCallback("Click and Draw", draw.draw_line_from_center)

    counter = 0
    first_frame = True

    for folder in folders:
        tmp_path = os.path.join(path,folder)        
        wd_runs = os.listdir(tmp_path)
        
        if vp.get_vid_dance() < 0:
                break

        for run in wd_runs:
            vp.set_vid_dance(10)
            vp.set_vid_path(tmp_path + '/' + run + '/' + 'image_%03d.png')
            capture = vp.get_vid_capture()                                    

            while(vp.get_vid_running()):
                ret, image = capture.read()                
                if (ret == True):
                    image = cv2.resize(image, None, fx = 5, fy = 5, interpolation = cv2.INTER_CUBIC)
                    draw.draw_line(image)
                    cv2.imshow("Click and Draw", image)
                    vp.vid_player_controlls()

                else:
                    capture = vp.vid_restart()

            if (vp.get_vid_dance() < 0):
                break
                
            draw.calc_angle()

            if (vp.get_vid_dance() == 0):
                with open(tmp_path + '/' + run + '/' + 'gt.csv', 'w', newline='', encoding='utf-8-sig') as out:
                    csv_out = csv.writer(out)                    
                    csv_out.writerow('n')
                    print('Not a dance!')
                
            elif (1 <= vp.get_vid_dance() <= 2):
                with open(tmp_path + '/' + run + '/' + 'gt.csv', 'w', newline='', encoding='utf-8-sig') as out:
                    csv_out = csv.writer(out)                    
                    if (vp.get_vid_dance() == 1):
                        csv_out.writerow('j')
                        print('It is a dance!')
                    else:
                        csv_out.writerow('v')
                        print('Probably a dance--')
                    
                if (draw.get_drawn()):
                    with open(tmp_path + '/' + run + '/' + 'result.csv', 'w', newline='', encoding='utf-8-sig') as out:
                        csv_out = csv.writer(out)
                        csv_out.writerow(['Key'] + ['Start Point'] + ['End Point'] + ['Angle'])
                        csv_out.writerow( [folder + '/' + run] + [draw.get_refernce_points()[0]] + [draw.get_refernce_points()[1]] + [draw.get_angle()])
                        print('Angle: ' + str(draw.get_angle()))
                    
            counter += 1
            print(counter)
            draw.reset_drawing()
            first_frame = True

    capture.release()
    cv2.destroyAllWindows()
        
    # FROM HERE
    i = datetime.datetime.now()            
    #Iterates through all the dances
    for folder in folders:
        #Sets the path to the current dance
        tmp_path = os.path.join(path,folder)
        #Filters list of waggle runs
        wd_runs = os.listdir(tmp_path)
        #Iterates through the waggle runs
        for run in wd_runs:
            #Path to next run
            key = os.path.join(tmp_path,run)
            
            if os.path.isfile(key + '/' + 'result.csv'):                
                #Reading        
                with open(key + '/' + 'result.csv', 'rt', encoding='utf-8-sig') as in_file:
                    reader = csv.reader(in_file, delimiter=',', quotechar='|')
                    row = next(reader)
                    row = next(reader)                
                            
                with open('Data/GTData/' + str(i.strftime('%Y%m%d_%H%M')) + '.csv', 'at', newline='') as out_file:            
                    writer = csv.writer(out_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)                
                    writer.writerow(row)    
    # TO HERE
    print ('Your data has been correctly saved in Data/GTData/' + str(i.strftime('%Y%m%d_%H%M')) + '.csv')
if __name__ == "__main__":
    main()
