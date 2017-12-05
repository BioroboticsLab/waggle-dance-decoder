#Script to compute angle for all waggle runs in a day directory
#The directory has to follow the WDD structure "...YYYYMMDD/YYYYMMDD_HHmm_C/WR/*.png"
#The angle is stored in a ForList.csv for each waggle run
#When done with all the waggle runs it writes down all results under 'Data/%Y%m%d_%H%M_decoder.csv'
#The output schema is as follows:
#[key] + [length] + [raw_angle] + [x0] + [y0] + [date] + [time] +  [cam_angle]
#Example:
#20160814_1001_1/1,29,-5.78629923147,60.0,70.6,2016/08/14,10:01:42:582,5.78629923147

import os
import datetime
import glob
import cv2
import csv
import sys
import math
sys.path.append('Utils/')
from file_manager import File_manager
from math import ceil
from scipy.stats import multivariate_normal
from scipy import stats
import numpy as np

radi = 180/np.pi

class DoG:
    '''
    Prepares the given Data to create a DoG kernel
    '''
    def get_dog_kernel(self, angle, dist_mean, sigma, kernel_width, cov_matrix):
        kernel = np.zeros(shape=(kernel_width, kernel_width))

        center = [int((kernel_width) / 2), int((kernel_width) / 2)]

        angle = np.radians(angle) #angle * pi / 180
        avg_route = (dist_mean / 2)    #Length

        rotation_vec = np.transpose([np.cos(angle), np.sin(angle)])

        rotation_matrix = np.matrix([[np.cos(angle), np.sin(angle)],[-np.sin(angle), np.cos(angle)]])

        cov_matrix =  rotation_matrix * cov_matrix * np.transpose(rotation_matrix)

        rotation_vec = avg_route * np.transpose([rotation_vec[1], rotation_vec[0]]) #Multiply with half of the distance
        invert_rotation_vec = -rotation_vec #negate the vector to get the mirrored point

        point_one = rotation_vec + center #add to center to move in the right direction
        point_two = center + invert_rotation_vec #add to center to move in the right direction

        for i in range(kernel_width):
            for j in range(kernel_width):
                kernel[j,i] =  multivariate_normal.pdf(point_one, mean=[i,j], cov=cov_matrix) \
                                        -  multivariate_normal.pdf(point_two, mean=[i,j], cov=cov_matrix)

        return kernel

    def mexican_head_kernel(self, kernel_size, mean1, cov1, mean2, cov2):
        dog = np.zeros(shape=(kernel_size, kernel_size))

        for x in range(kernel_size):
            for y in range(kernel_size):
                dog[y,x] = multivariate_normal.pdf([x, y], mean=mean1, cov=cov1) - multivariate_normal.pdf([x, y], mean=mean1, cov=cov2);

        return dog


def create_diff_images(path):
    diff_img = []
    #Bluring matrix
    smothing = np.matrix([[1,1,1],[1,1,1],[1,1,1]]) / 9    
    #Array with the images path
    listing = glob.glob(path + '/' + 'image*.png')
    #Initializes the variables
    frame_counter = 0
    last_frame   = None
    image_array = []                     
    #Iterates through the images
    for frame_path in listing:        
        frame = cv2.imread(frame_path)
        #The png file is a 50x50x3 array, we only need one layer
        frame = frame[:,:,1]        
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
            if (diff_img is None):
                diff_img = [frame_diff]
            #If not, it add it 
            else:
                diff_img.append(frame_diff)

            
        last_frame = frame
    return diff_img
        
def calc_accumulator(diff_img):
    #Output array
    FDI = None            
    #Iterates through the diff_images
    for img in diff_img:
        #fast fourier transformation + shift to center
        tmp = np.fft.fftshift(abs(np.fft.fft2(img)))
        #If it is the first
        if FDI is None:
            FDI = tmp
        #From the second on
        else:
            FDI += tmp
    #Resulting image is returned as FDI    
    return FDI

def filter_with_kernel(FDI):
    #Kernel definition
    dog = DoG().mexican_head_kernel
    cov1 = 30 * np.eye(2)
    cov2 = 4 * np.eye(2)
    Kern = abs(np.fft.fftshift(np.fft.fft2(dog(50, [25,25], cov1, [25,25], cov2))))
    #Restuls array    
    FDI_filt = np.power(np.multiply(FDI, Kern), 5)
    return FDI_filt

def calc_angle(FDI_filt):
    #Radian    
    #FDI_filt moments
    moment = cv2.moments(FDI_filt)
    #Image covariance
    img_cov = np.array([[moment['nu20'], moment['nu11']], [moment['nu11'], moment['nu02']]])
    #Eigenvalues
    w, v = np.linalg.eig(img_cov)
    #According to image convention    
    angle = -np.arctan2(v[1][np.argmin(w)], v[0][np.argmin(w)])
    return angle

def read_DD(path):    
    #path to the waggle run
    split_path = path.split("\\")
    
    fm_csv = File_manager(path).read_csv
    #reads the csv file containing coordinates of dancing bee
    detections = fm_csv(path + '/' + split_path[-2] + "_" + split_path[-1] + '.csv')
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
    #average orientation of peaks in histogram (also not sure why this)!!!!!!!!!
    avgHist = stats.circmean(c[np.argwhere(n == np.amax(n))])
    #Feature 4: 
    feat4 = (m2-m1) + [math.cos(avgHist), math.sin(avgHist)]
    
    #returned angle correspond to the vector pointing from m1 towards m2            
    dd_angle = -np.arctan2(feat4[1],feat4[0])

    return dd_angle
    
def def_orientation(fft_angle, dd_angle):    
    #Angles are converted to vectors
    v1 = [math.cos(fft_angle),math.sin(fft_angle)]
    v2 = [math.cos(dd_angle),math.sin(dd_angle)]    
    #If the dot product is negative, the angles differ in more than 90°
    if np.dot(v1,v2) < 0:
        adj_angle = fft_angle - np.pi
    else :
        adj_angle = fft_angle    
    return adj_angle
    
def List_file(path, raw_angle, cam_angle):
    #path to the waggle run
    split_path = path.split("\\")
    folder = split_path[-2]
    run = split_path[-1]
    year = folder[:4]
    month = folder[4:6]
    day = folder [6:8]
    date = year + '/' + month + '/' + day
        
    with open(path + '/' + split_path[-2] + "_" + split_path[-1] + '.csv', 'rt') as in_file:
        csv_in = csv.reader(in_file, delimiter=' ', quotechar='|')
        [x0, y0, dummy] = next(csv_in)    
        [time, length] = next(csv_in)          
    
    with open(path + '/' + 'ForList.csv', 'w', newline='', encoding='utf-8-sig') as out_file:
        csv_out = csv.writer(out_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csv_out.writerow([folder + '/' + run] + [length] + [raw_angle] + [x0] + [y0] + [date] + [time] + [cam_angle] )
    
def main():
    argv = sys.argv
         
    if (len(argv) == 1):
        path = input("Please enter WaggleDance Path")

    if (len(argv) == 2):
        path = argv[1]
    
    #Filters all minute-camera subdirectories
    folders = filter(lambda x: os.path.isdir(os.path.join(path, x)), os.listdir(path))
    #Iterates through all the minute-camera directories
    for folder in folders:
        #Sets the path to the current minute-camera directory
        tmp_path = os.path.join(path,folder)
        #List of waggle runs
        wd_runs = os.listdir(tmp_path)
        #Iterates through the waggle runs
        for run in wd_runs:
            #Path to next run
            key = os.path.join(tmp_path,run)
            print(key)
            #calculates the waggle run's angle
            diff_img = create_diff_images(key)
            FDI = calc_accumulator(diff_img)
            FDI_filt = filter_with_kernel(FDI)
            angle = calc_angle(FDI_filt)            
            #Orientation corrected fftfilt angles
            dd_angle = read_DD(key)            
            raw_angle = def_orientation(angle, dd_angle)
            #Angle is adjusted to a value within the range [0,2pi]
            raw_angle = raw_angle % (2*np.pi)
            #The angles are converted to match the camera orientation for 2016 and the convention: 
            # 0° should point upwards, positive should turn clockwise.
            #Camera 0 recorded the right side of the hive and was rotated 90° clockwise
            if folder.endswith('_0'):
                cam_angle=-1*raw_angle + np.pi
            #Camera 1 recorded the left side of the hive and was rotated 90° counterclockwise
            else:
                cam_angle=-1*raw_angle            
            #Writes results in a ForList.csv file
            print (cam_angle)
            List_file(key, raw_angle, cam_angle)
    
    # FROM HERE
    #Iterates through all the dances
    #Filters all dance subdirectories
    folders = filter(lambda x: os.path.isdir(os.path.join(path, x)), os.listdir(path))
    i = datetime.datetime.now()
    #prints the header
    with open(str(i.strftime('%Y%m%d_%H%M')) + '_decoder.csv', 'at', newline='') as out_file:            
        writer = csv.writer(out_file, delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)        
        writer.writerow(['key, length, raw_angle, x0, y0, date, time, cam_angle'])
    for folder in folders:
        #Sets the path to the current dance
        tmp_path = os.path.join(path,folder)        
        #Filters list of waggle runs
        wd_runs = os.listdir(tmp_path)
        #Iterates through the waggle runs
        for run in wd_runs:
            #Path to next run
            key = os.path.join(tmp_path,run)
            #Reading
        
            with open(key + '/' + 'ForList.csv', 'rt', encoding='utf-8-sig') as in_file:
                reader = csv.reader(in_file, delimiter=',', quotechar='|')
                row = next(reader)                
                        
            with open(str(i.strftime('%Y%m%d_%H%M')) + '_decoder.csv', 'at', newline='') as out_file:            
                writer = csv.writer(out_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)                
                writer.writerow(row)    
    # TO HERE
    print ('Your data has been propertly saved in ' + str(i.strftime('%Y%m%d_%H%M')) + '_decoder.csv')
if __name__ == "__main__":
    main()
