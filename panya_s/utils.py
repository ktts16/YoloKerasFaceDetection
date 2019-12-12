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

from utils import scale_and_recenter_points
from math import floor

def align_with_margin(img, output_image_size=112, m=0.4, return_box=False):
    '''
    Scale src (points) to include margin
    BEFORE using it to transform detected landmarks from image
    > Arguments:
    m: margin ratio : margin length = m * original image length
    '''
    debug = False
    # debug = True

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

    if return_box:
        old_l = 112.0
        # bounding box of landmark points (source)
        sbox = np.array([
          [0., 0.],
          [old_l, 0.],
          [0., old_l],
          [old_l, old_l]], dtype=np.float32 )
        sbox = sbox/old_l*output_image_size

    ## note:  l = (1 + (2*m)) * s
    l = output_image_size
    s = floor(l / (1 + (2*m)))
    if debug:
        print(l, s)
        print(s/l)

    newsrc = scale_and_recenter_points(src, old_size=(l,l), new_size=(s,s))
    if debug:
        print(src)
        print(newsrc)

    newbox = None
    if return_box:
        newbox = scale_and_recenter_points(sbox, old_size=(l,l), new_size=(s,s))
        if debug: print('newbox',newbox)

    landmark = np.array([np.array(key['left_eye']),
                np.array(key['right_eye']),
                np.array(key['nose']),
                np.array(key['mouth_left']),
                np.array(key['mouth_right'])]).astype('float')
    dst = landmark.astype(np.float32)

    tform = trans.SimilarityTransform()
    tform.estimate(dst, newsrc)
    M = tform.params[0:2,:]

    return (cv2.warpAffine(img,M,(output_image_size,output_image_size), borderValue = 0.0),
    newsrc, newbox)
