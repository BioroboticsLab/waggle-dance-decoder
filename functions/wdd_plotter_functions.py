# coding=utf-8

import os
import glob
import cv2
import math
import datetime
import pysolar
import pytz
import numpy as np
from DoG import DoG
from scipy import stats
from file_manager import File_manager

#Radian
radi = 180/np.pi

#arguments:
#YYYY: Year.
#MM: Month.
#DD: Day.
#HH: Hour.
#mm: Minute.
#DiffUTC: Difference to UTC.
#La: Latitude.
#Lo: Longitude.

#returns:
#Az: Azimuth.
#Al: Altitude.

def SolarAzEl(YYYY, MM, DD, HH, mm, DiffUTC, La, Lo):
    #Time with UTC awarenes
    time = datetime.datetime(YYYY, MM, DD, HH-DiffUTC, mm, 0, 0, pytz.UTC)    
    #Calculates the solar azimuth
    Az = pysolar.solar.get_azimuth(La, Lo, time)*-1-180
    #Calculates the solar altitude
    Al = pysolar.solar.get_altitude(La, Lo, time)
    return Az, Al
 
#arguments:
#DanceAngle: Dance angle in the hive reference system (North to East)
#YYYY: Year.
#MM: Month.
#DD: Day.
#HH: Hour.
#mm: Minute.
#DiffUTC: Difference to UTC.
#La: Latitude.
#Lo: Longitude.

#returns:
#MapAngle: Angle in the map reference system (North to East)
#NHAngle: Angle in the normal handedness (counterclockwise turning and 0° in the x axis)

def translateToRelativeSunDirection(DanceAngle, YYYY, MM, DD, HH, mm, DiffUTC, La, Lo):
    #Time with UTC awarenes
    [Az, Al] = SolarAzEl(YYYY,MM,DD,HH,mm,DiffUTC,La,Lo)
    #Angle in the map reference system (North to East)
    MapAngle = Az/radi + DanceAngle
    #Angle in the normal handedness (counterclockwise turning and 0° in the x axis)
    NHAngle = 2*np.pi - MapAngle + np.pi/2;
    return MapAngle, NHAngle