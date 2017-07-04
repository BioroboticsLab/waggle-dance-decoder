# coding=utf-8
#This function generates an array of diff_images
#Where diff_img is the matrix resulting from the difference between two consecutive frames

import os
import glob
import cv2
import math
import numpy as np
from DoG import DoG
from scipy import stats
from file_manager import File_manager

#Radian
radi = 180/np.pi

def create_diff_images(path):
    #List of dances directories
    folders = os.listdir(path)	
    diff_img = {}
    #Bluring matrix
    smothing = np.matrix([[1,1,1],[1,1,1],[1,1,1]]) / 9
    #Iterates through all the dances
    for folder in folders:
        #Sets the path to the current dance
        tmp_path = path + folder
        #List of waggle runs
        wd_runs = os.listdir(tmp_path)
        #Iterates through the waggle runs
        for run in wd_runs:
            #Array with the images path
            listing = glob.glob(tmp_path + '/' +  run + '/' + 'image*.png')
            #Initializes the variables
            frame_counter = 0
            last_frame   = None
            image_array = []                     
            #Iterates through the images
            for frame_path in listing:
                frame = cv2.imread(frame_path)
                #The png file is a 50x50x3 array, we only need one layer
                frame = frame[:,:,1]                
                #Sets as key a string with the path to the WRun                
                key = str(tmp_path[-15:] + '/' +  run)
                #If it is the first frame
                if last_frame is None:	
                    last_frame  = frame
                    continue
                #Any other frame
                else:
                    #Difference between consecutive frames
                    frame_diff = last_frame.astype(float) - frame.astype(float)
                    frame_diff = cv2.filter2D(frame_diff, -1, smothing)
                    #If it is the first diff in the WRun
                    if (key not in diff_img):
                        diff_img[key] = [frame_diff]
                    #If not, it add it 
                    else:
                        diff_img[key].append(frame_diff)

                    
                last_frame = frame
                
    return diff_img

def calc_image_sum_for_angle(angles, key, img_arrays, kernels):
    sums = []

    for idx, angle in enumerate(angles):
        img_sum = 0
        kernel = kernels[idx]

        for index, img in enumerate(img_arrays):
            if (index < len(img_arrays) - 10):
                filtered_img = np.amax(cv2.filter2D(img, -1, -kernel))

                img_sum += filtered_img
            else:
                break

        sums.append(img_sum)

    return sums, key
    
def calc_image_sum_for_frame(_angles, key, img_arrays, kernels):
    mat = np.zeros((len(img_arrays), math.ceil(len(_angles) / 2)))

    for index, img in enumerate(img_arrays):
        for idx in range(int(len(_angles) / 2)):
            kernel = kernels[idx]

            mat[index][idx] = np.amax(abs(cv2.filter2D(img, -1, -kernel)))

    return mat, key

def calc_accumulator(diff_img):
    #Output array
    FDI = {}    
    #Iterates through the waggle runs
    for key, img_arrays in list(diff_img.items()):        
        image = None
        #Iterates through the diff_images
        for img in img_arrays:
            #fast fourier transformation + shift to center
            tmp = np.fft.fftshift(abs(np.fft.fft2(img)))
            #If it is the first
            if image is None:
                image = tmp
            #From the second on
            else:
                image += tmp
        #Resulting image is stored under key = path to WRun
        FDI[key]=(image)
    return FDI

def filter_with_kernel(FDI):
    #Kernel definition
    dog = DoG().mexican_head_kernel
    cov1 = 30 * np.eye(2)
    cov2 = 4 * np.eye(2)
    Kern = abs(np.fft.fftshift(np.fft.fft2(dog(50, [25,25], cov1, [25,25], cov2))))
    #Restuls array
    FDI_filt = {}
    #Iterates through the FDI
    for key, FDI_img in list(FDI.items()):     
        FDI_filt[key] = np.power(np.multiply(FDI_img, Kern), 5)
    return FDI_filt

def calc_angles(FDI_filt):    
    #Results vector
    angles = {}
    #Iterates through the FDI_filt
    for key, FDI_img in list(FDI_filt.items()):    
        moment = cv2.moments(FDI_img)
        #Image covariance
        img_cov = np.array([[moment['nu20'], moment['nu11']], [moment['nu11'], moment['nu02']]])        
        #Eigenvalues
        w, v = np.linalg.eig(img_cov)
        #According to image convention
        angles[key] = -np.arctan2(v[1][np.argmin(w)], v[0][np.argmin(w)])*radi
    return angles

def read_GT(path):
    fm_csv = File_manager(path).read_csv
    #list of Groung Truth angles
    gt_angles = {}
    folders = os.listdir(path)
    #Iterates through all the dances
    for folder in folders:
        #Sets the path to the current dance
        tmp_path = path + folder
        #List of waggle runs
        wd_runs = os.listdir(tmp_path)
        #Iterates through the waggle runs
        for run in wd_runs:
            key = str(tmp_path[-15:] + '/' +  run)
            gt_angles[key] = float(fm_csv(tmp_path + '/' +  run + '/' + "result.csv")["Angle"])
    return gt_angles
    
#Returns a dictionary with angles in radians based on the dot detector coordinates
def read_DD(path):
    fm_csv = File_manager(path).read_csv
    #list of Groung Truth angles
    dd_angles = {}
    folders = os.listdir(path)
    #Iterates through all the dances
    for folder in folders:
        #Sets the path to the current dance
        tmp_path = path + folder
        #List of waggle runs
        wd_runs = os.listdir(tmp_path)
        #Iterates through the waggle runs
        for run in wd_runs:
            WRPath = str(tmp_path + '/' +  run + '/')
            #path to the waggle run
            split_WR = WRPath.split("/")
            #reads the csv file containing coordinates of dancing bee
            detections = fm_csv(WRPath + split_WR[-3] + "_" + split_WR[-2] + '.csv')
            #Parses last row from csv to vector
            dd_float = np.array(list(detections.values())[0].split(" "))[:-1].astype(float)
            #Filters all -1, no detection
            dd_float = [val for val in dd_float if val != -1]
            
            #Reshape to an [n,2] array
            #dd_float[:,0] = Xcoordinates
            #dd_float[:,1] = Ycoordinates
            DD = np.reshape(dd_float, (int(len(dd_float)/2),2), order = 'C')
            #LOOKING FOR THE SWEET SPOT!!!
            #Half the size of the vector
            Nhalf = int(np.floor(len(DD)/2))            
            #Average coordinates of the first five detections            
            m1 = DD[:5,:].mean(axis=0)
            #Average coordinates of the second half of detections
            m2 = DD[Nhalf+1:,:].mean(axis=0)
            
            #Delta vectors            
            dDD = [[i[0]- m1[0],i[1]- m1[1]] for i in DD[Nhalf+1:,:]]
            dDD = np.reshape(dDD,(len(dDD),2), order = 'C')            
            #Feature 2: angles of the delta vectors
            feat2 = [np.arctan2(i[1],i[0]) for i in dDD]
            #Histogram of delta vectors where:
            #n = number of occurrencies and c = angle values
            [n, c] = np.histogram(feat2, bins = 100)
            #average orientation of peaks in histogram
            avgHist = stats.circmean(c[np.argwhere(n == np.amax(n))])
            #Feature 4: 
            feat4 = (m2-m1) + [math.cos(avgHist), math.sin(avgHist)]
            
            #returned angle correspond to the vector pointing from m1 towards m2            
            dd_angles[tmp_path[-15:] + '/' +  run] = -np.arctan2(feat4[1],feat4[0])*radi
    return dd_angles
    
#Returns DDvector generated by DotDetector
def read_DDvector(WRPath):
    fm_csv = File_manager(path).read_csv
    WRPath = str(WRPath + '/')
    #path to the waggle run
    split_WR = WRPath.split("/")
    #reads the csv file containing coordinates of dancing bee
    detections = fm_csv(WRPath + split_WR[-3] + "_" + split_WR[-2] + '.csv')
    #Parses last row from csv to vector
    dd_float = np.array(list(detections.values())[0].split(" "))[:-1].astype(float)
    #Filters all -1, no detection
    dd_float = [val for val in dd_float if val != -1]
    return dd_float

#Returns an angle with adjusted orientation
#Input parameters:
#fft_angles: A dictionary containing the angles computed using the fft method.
#dd_angles: A dictionary containing the vectors defined using the dot detector coordinates.
#Output:
#adj_angles: A dictionary containing the corrected angles.
def def_orientation(fft_angles, dd_angles):    
    adj_angles = {}
    #Iterates through all the dances
    for key in list(fft_angles):        
        #Angles are converted to vectors
        v1 = [math.cos(fft_angles[key]/radi),math.sin(fft_angles[key]/radi)]
        v2 = [math.cos(dd_angles[key]/radi),math.sin(dd_angles[key]/radi)]       
        #If the dot product is negative, the angles differ in more than 90°        
        if np.dot(v1,v2) < 0:
            adj_angles[key] = (fft_angles[key] - 180) % 360
        else :
            adj_angles[key] = (fft_angles[key]) % 360
    return adj_angles

# It returns the substraction of two angles, angle1-angle2 in an image convention 0° at 3, +/- 180° at 9. 
# arguments: angle1, angle2 in grads
# returns: diffAngle = angle1-angle2
def subst_angles(angle1, angle2):    
    #Angles are converted to vectors
    v1 = [math.cos(angle1/radi),math.sin(angle1/radi)]
    v2 = [math.cos(angle2/radi),math.sin(angle2/radi)]    
    #The magnitude is calculated using dot product
    diffAngle = math.acos(np.dot(v1,v2))*radi
    #The direction is defined using cross product
    if np.cross(v1,v2) < 0:
        diffAngle = -diffAngle    
    return diffAngle