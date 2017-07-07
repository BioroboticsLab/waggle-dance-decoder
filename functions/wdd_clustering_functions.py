#Clustering and RANSAC for WDD
#Fernando Wario
#June 2017

import os
import glob
import cv2
import math
import csv
import datetime
import json
import pandas
import sys
import scipy.cluster
import numpy as np

from scipy import stats
#Radian
radi = 180/np.pi


"""
Fit model to data using the RANSAC algorithm
Given:
    inputFile - path to decoder.csv
    camID     - ID of working camera    
Return:
    A         - dictionary A, where:
                key = WRun key
                vector = [length_ms, cam_angle, x0, y0, timeStamp_sec, HH, mm]
"""
def data_format(inputFile, camID, plot = 0):
    A = {}
    with open(inputFile, 'rt', encoding='utf-8-sig') as DecFile:
        reader = csv.reader(DecFile, delimiter = ',')
        next(reader)        
        for row in reader:            
            #Only WRuns from camera camID
            if (row[0][14] == camID):    
                key = row[0]
                #duration of the WRun in ms
                length_ms = float(row[1])*10
                #Time is splitted
                split_time = row[6].split(":")
                #Timestamp to seconds, disregard miliseconds
                time_sec = int(split_time[0])*3600 + int(split_time[1])*60 + int(split_time[2])
                #if plot is true then it returns cam_angle
                if (plot):
                    A[key] = [length_ms, float(row[-1]), float(row[3]), float(row[4]), time_sec, split_time[0], split_time[1]]
                #otherwise raw_angle is returned
                else:
                    A[key] = [length_ms, float(row[2]), float(row[3]), float(row[4]), time_sec, split_time[0], split_time[1]]
    return A


"""
Fit model to data using the RANSAC algorithm
Given:
    A         - dictionary returned by data_format
    max_d     - euclidean distance threshold
Return:
    C         - dictionary C, where:
                key = clusterID
                vector = [WRuns key, camAngles]
"""    
def generate_clusters(A, max_d):
    B = np.array([[A[key][2], A[key][3], A[key][4]/4] for key in A])
    Z = scipy.cluster.hierarchy.linkage(B, 'ward')    
    clusters = scipy.cluster.hierarchy.fcluster(Z, max_d, criterion='distance')
    #Keys of WRuns that have been clustered together
    C={}
    for count, key in enumerate(A):
        if (str(clusters[count]) not in C):
            C[str(clusters[count])] = [[key, A[key][1]]]
        else:
            C[str(clusters[count])].append([key, A[key][1]])
    return C

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

def random_subset(n,n_data):
    #data array indexes
    all_idxs = np.arange(n_data)
    #shuffles the indexes
    np.random.shuffle(all_idxs)
    #the first n are returned
    idxs1 = all_idxs[:n]    
    return idxs1

def get_error(test_points, maybeAngle):
    diffAngle = []
    for count, angle1 in enumerate(test_points):
        #Angles are converted to vectors
        vTest = [math.cos(angle1),math.sin(angle1)]
        vMaybe = [math.cos(maybeAngle),math.sin(maybeAngle)]
        #Difference is calculated using dot product
        escProd = np.dot(vTest,vMaybe)
        #limits the escProd to the range [-1,1]
        escProd = clamp(escProd, -1, 1)
        #
        diffAngle.append(math.acos(escProd))
    return np.array(diffAngle)

"""
Fit model to data using the RANSAC algorithm
Given:
    data - a set of observed data points    
    n - the minimum number of data values required to compute an angle
    k - the maximum number of iterations allowed in the algorithm
    t - a threshold value for determining when a data point fits a model
    d - the number of close data values required to assert that a model fits well to data
Return:
    bestfit          - angle that best fit the data (or nil if no good model is found)
    best_inlier_idxs - indexes of inlier data (or nil if no good model is found)
"""
def ransac_WDD(data, n, k, t, d):
    it = 0
    bestfit = None
    besterr = np.inf
    best_inlier_idxs = None
    while it < k:
        all_idxs = np.arange(data.shape[0])
        #generates a random subset
        maybe_idxs = random_subset(n,data.shape[0])
        maybeinliers = data[maybe_idxs]
        #generates a model out of selected inliers
        maybeAngle = stats.circmean(maybeinliers, high=2*np.pi, low=0)
        #error from all data to generated model
        test_err = get_error(data, maybeAngle)
        # select indices of rows with accepted points
        inl_idxs = all_idxs[test_err < t]
        inliers = data[inl_idxs]
        #if the number of inliers is above threshold
        if len(inliers) > d:
            betterdata = inliers
            bettermodel = maybeAngle
            better_errs = test_err
            thiserr = np.mean(better_errs)
            #if found error is the best so far, the model is updated
            if thiserr < besterr:
                bestfit = bettermodel
                besterr = thiserr
                best_inlier_idxs = inl_idxs
        it+=1
    #returns best model and inliers' indexes
    else:
        return bestfit, best_inlier_idxs

"""
Clean a set of clusters
Given:
    A - dictionary of data returned by data_format
    C - dictionary of clusters returned by generate_clusters
    n - the minimum number of data values required to compute an angle
    k - the maximum number of iterations allowed in the algorithm
    t - a threshold value for determining when a data point fits a model
    d - the number of close data values required to assert that a model fits well to data
Return:
    cleanClusters - dictionary cleanClusters, where:
                    key = clusterID
                    vector = [avg_angle, avg_length, WRuns keys]
"""
#def clean_clusters(A, C, n, k, t, d):
def clean_clusters(A, C, n, t):
    #dictionary for the results
    cleanClusters = {}
    #iterates over all clusters
    for clusterID in C:
        #Only clusters with a minimum of 3 elements are considered as potential dances
        if len(C[clusterID]) > 3:
            #loading the angles
            data = np.array([x[1] for x in C[clusterID]])
            temp_ransac = []
            #maximum number of iterations
            k = 5*len(C[clusterID])
            #minimum number of inliers to be considered a valid model
            d = 0.6*len(C[clusterID])
            #RANSAC is applied to each cluster            
            temp_ransac = ransac_WDD(data, n, k, t, d)
            #clear auxiliary variables
            temp_cluster = []
            accum = 0
            if (temp_ransac[0]):
                for i in temp_ransac[1]:                    
                    temp_cluster.append(C[clusterID][i][0])
                    accum += A[C[clusterID][i][0]][0]
                avg_length = accum/len(temp_ransac[1])
                HH = int(A[C[clusterID][i][0]][5])
                mm = int(A[C[clusterID][i][0]][6])
                #Returns [angle, avg_length, HH, mm, WRuns keys]
                cleanClusters[clusterID] = temp_ransac[0], avg_length, HH, mm, temp_cluster
    return cleanClusters