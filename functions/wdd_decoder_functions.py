#This function generates an array of diff_images
#Where diff_img is the matrix resulting from the difference between two consecutive frames

import os
import glob
import cv2
import numpy as np
from math import ceil
from file_manager import File_manager

#input parameters
#path     - Path to the dances

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
            #WRun length
            run_len = len(listing)          
            #Iterates through the images
            for frame_path in listing:
                frame = cv2.imread(frame_path)
                #The png file is a 50x50x3 array, we only need one layer
                frame = frame[:,:,1]                
                #Sets as key a string with the path to the WRun
                key = str(tmp_path + '/' +  run + '/')
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
    mat = np.zeros((len(img_arrays), ceil(len(_angles) / 2)))

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

def filter_with_kernel(FDI, Kern):
    #Restuls array
    FDI_filt = {}
    #Iterates through the FDI
    for key, FDI_img in list(FDI.items()):     
        FDI_filt[key] = np.power(np.multiply(FDI_img, Kern), 5)
    return FDI_filt

def calc_angles(FDI_filt):
    #Radian
    radi = 180/np.pi
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
            key = str(tmp_path + '/' +  run + '/')
            gt_angles[key] = float(fm_csv(key + "result.csv")["Angle"])
    return gt_angles
    
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
            key = str(tmp_path + '/' +  run + '/')
            #path to the waggle run
            split_keys = key.split("/")
            #reads the csv file containing coordinates of dancing bee
            detections = fm_csv(key + split_keys[-3] + "_" + split_keys[-2] + '.csv')
            #Angle from DotDetector
            angle_rad = np.array(list(detections.keys())[0].split(" "))[:3].astype(float)            
            dd_angles[key] = float(angle_rad[2]*180/np.pi)
    return dd_angles
    
def def_orientation(fft_angles, dd_angles):    
    ct_angles = {}
    #Iterates through all the dances
    for key in list(fft_angles):
        #If the difference between fft_angle and dd_angle is more than 90° orientation has to be flipped
        if abs(dd_angles[key]-fft_angles[key]) > 90:
            if fft_angles[key] < 0:
                ct_angles[key] = fft_angles[key] + 180
            else:
                ct_angles[key] = fft_angles[key] - 180
        else:
            ct_angles[key] = fft_angles[key]
    return ct_angles