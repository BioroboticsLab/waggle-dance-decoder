import os
import cv2

class VidPlayer:
    
    '''
    The class to display video from images in folder
    '''

    _vid_path = ''
    _vid_capture = None
    _vid_speed = 50
    _vid_paused = False
    _vid_running = True
    _vid_direction = True
    _vid_dance = ''    

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
    
    def set_vid_direction(self, direction):
        self._vid_direction = direction

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
        
    def get_vid_direction(self):
        return self._vid_direction

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

        elif key == ord("y") or key == ord("Y"):
            self._vid_running = False            
            self._vid_dance = 0
            self._vid_direction = True
        
        elif key == ord("n") or key == ord("N"):
            self._vid_running = False            
            self._vid_dance = 1
            self._vid_direction = True
        
        #Up arrow key 
        elif key == ord("w") or key == ord("W"):
            self._vid_running = False            
            self._vid_direction = False
        #Down arrow key
        elif key == ord("s") or key == ord("S"):
            self._vid_running = False            
            self._vid_direction = True        
        #Left arrow key 
        elif key == ord("a") or key == ord("A"):
            self._vid_running = False            
            self._vid_direction = False
        #Right arrow key
        elif key == ord("d") or key == ord("D"):            
            self._vid_running = False            
            self._vid_direction = True
        
        
        elif key == 27:
            self._vid_running = False            
            self._vid_dance = -1

    def vid_restart(self):
        self._vid_capture = cv2.VideoCapture(self._vid_path)
        return self._vid_capture