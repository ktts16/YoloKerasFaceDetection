from skimage import transform as trans
from mtcnn.mtcnn import MTCNN
import cv2
import numpy as np
import math

detector = MTCNN(min_face_size=12)

def align(img, output_image_size=112):

    A = detector.detect_faces(img)
    highest = 0
    min_size = 30

    for i in range(len(A)):
       box = A[i]['box']
       if box[2]+box[3]>highest:
           bb = box
           c = A[i]['confidence']
           key = A[i]['keypoints']
           highest = box[2]+box[3]

    if not A:
       return 'Cannot_detect_face'
    if c<=.96:
       return 'Confident_percent'
    if bb[2]< min_size or bb[3]<min_size:
       return 'Face image size is too low'
    src = np.array([
      [30.2946, 51.6963],
      [65.5318, 51.5014],
      [48.0252, 71.7366],
      [33.5493, 92.3655],
      [62.7299, 92.2041] ], dtype=np.float32 )

    src[:,0] += 8.0
    src = src/112*output_image_size
    landmark = np.array([np.array(key['left_eye']),
                np.array(key['right_eye']),
                np.array(key['nose']),
                np.array(key['mouth_left']),
                np.array(key['mouth_right'])]).astype('float')
    dst = landmark.astype(np.float32)

    tform = trans.SimilarityTransform()
    tform.estimate(dst, src)
    M = tform.params[0:2,:]

    warped = cv2.warpAffine(img,M,(output_image_size,output_image_size), borderValue = 0.0)

    return warped