import os
import cv2
import numpy as np
from math import ceil

def create_diff_images(path, folders, smothing = np.matrix([[1,1,1],[1,1,1],[1,1,1]]) / 9):
    diff_img = {}


    for folder in folders:
        tmp_path = path + folder
        wd_runs = os.listdir(tmp_path)

        for run in wd_runs:
            cap = cv2.VideoCapture(tmp_path + '/' +  run + '/' + 'image_%3d.png')

            frame_counter = 0
            last_frame   = None
            image_array = []

            run_len = len(os.listdir(tmp_path + '/' +  run + '/'))

            run_end =  run_len - int(run_len * 0.1)

            while(True):
                ret, frame = cap.read()
                frame_counter += 1
                key = str(tmp_path + '/' +  run + '/')

                if (ret == True):
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                    if last_frame is None:
                        last_frame  = frame
                        continue

                    else:
                        frame_diff = last_frame.astype(float) - frame.astype(float)
                        frame_diff = cv2.filter2D(frame_diff, -1, smothing)


                        if (key not in diff_img):
                            diff_img[key] = [frame_diff]

                        else:
                            diff_img[key].append(frame_diff)

                    if frame_counter > run_end:
                        ret = False

                    last_frame = frame

                else:
                    break

    return diff_img

def calculate_image_sum_for_angle(angles, key, img_arrays, kernels):
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

def calculate_image_sum_for_frame(_angles, key, img_arrays, kernels):
    mat = np.zeros((len(img_arrays), ceil(len(_angles) / 2)))

    for index, img in enumerate(img_arrays):
        for idx in range(int(len(_angles) / 2)):
            kernel = kernels[idx]

            mat[index][idx] = np.amax(abs(cv2.filter2D(img, -1, -kernel)))

    return mat, key
