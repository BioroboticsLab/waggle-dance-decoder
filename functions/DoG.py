import numpy as np
from math import ceil
from scipy.stats import multivariate_normal


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
