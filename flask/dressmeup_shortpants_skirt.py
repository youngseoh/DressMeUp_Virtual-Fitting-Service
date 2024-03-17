# -*- coding: utf-8 -*-
"""dressmeup_shortpants,shortskirt.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PMq0m-BpGOVNclMeH_octDmpkZ5iFFy_
"""

import cv2
import numpy as np
# from google.colab.patches import cv2_imshow


# image_path ="/content/drive/MyDrive/dressmeup/human-pose-estimation-opencv/달리남자2.webp"
# cloth_path = "/content/drive/MyDrive/dressmeup/cloth-segmentation/output/cloth_final.png"


def shortpants_skirt(image_path, cloth_path):
    # 이미지와 옷 불러오기
    image = cv2.imread(image_path)
    cloth = cv2.imread(cloth_path)

    # POSE_PAIRS와 BODY_PARTS 정의
    BODY_PARTS = { "Nose": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4,
               "LShoulder": 5, "LElbow": 6, "LWrist": 7, "RHip": 8, "RKnee": 9,
               "RAnkle": 10, "LHip": 11, "LKnee": 12, "LAnkle": 13, "REye": 14,
               "LEye": 15, "REar": 16, "LEar": 17, "Background": 18 }

    POSE_PAIRS = [ ["Neck", "RShoulder"], ["Neck", "LShoulder"], ["RShoulder", "RElbow"],
               ["RElbow", "RWrist"], ["LShoulder", "LElbow"], ["LElbow", "LWrist"],
               ["Neck", "RHip"], ["RHip", "RKnee"], ["RKnee", "RAnkle"], ["Neck", "LHip"],
               ["LHip", "LKnee"], ["LKnee", "LAnkle"], ["Neck", "Nose"], ["Nose", "REye"],
               ["REye", "REar"], ["Nose", "LEye"], ["LEye", "LEar"] ]

    width = 368
    height = 368
    inWidth = width
    inHeight = height


    net = cv2.dnn.readNetFromTensorflow("graph_opt.pb")
    thr = 0.2

    def poseDetector(frame):
        processed_frame = frame.copy()

        frameWidth = frame.shape[1]
        frameHeight = frame.shape[0]

        net.setInput(cv2.dnn.blobFromImage(frame, 1.0, (inWidth, inHeight), (127.5, 127.5, 127.5), swapRB=True, crop=False))
        out = net.forward()
        out = out[:, :19, :, :]
        assert(len(BODY_PARTS) == out.shape[1])

        points = []
        for i in range(len(BODY_PARTS)):
            heatMap = out[0, i, :, :]

            _, conf, _, point = cv2.minMaxLoc(heatMap)
            x = (frameWidth * point[0]) / out.shape[3]
            y = (frameHeight * point[1]) / out.shape[2]
            points.append((int(x), int(y)) if conf > thr else None)

        for pair in POSE_PAIRS:
            partFrom = pair[0]
            partTo = pair[1]
            assert(partFrom in BODY_PARTS)
            assert(partTo in BODY_PARTS)

            idFrom = BODY_PARTS[partFrom]
            idTo = BODY_PARTS[partTo]

            if points[idFrom] and points[idTo]:
                cv2.line(processed_frame, points[idFrom], points[idTo], (0, 255, 0), 3)
                cv2.ellipse(processed_frame, points[idFrom], (3, 3), 0, 0, 360, (0, 0, 255), cv2.FILLED)
                cv2.ellipse(processed_frame, points[idTo], (3, 3), 0, 0, 360, (0, 0, 255), cv2.FILLED)

        t, _ = net.getPerfProfile()
        LHip = points[BODY_PARTS["LHip"]]
        RHip = points[BODY_PARTS["RHip"]]
        RKnee = points[BODY_PARTS["RKnee"]]
        LKnee = points[BODY_PARTS["LKnee"]]

        return LHip, RHip, RKnee, LKnee, frame

    # poseDetector 함수를 사용하여 이미지 처리
    LHip, RHip, RKnee, LKnee, image = poseDetector(image)

    # x 값 차이 계산
    x_diffhip = (RHip[0] - LHip[0]) * 0.8
    x_diffknee= (RKnee[0] -LKnee[0]) * 0.8

    # y 값 차이 계산
    y_left = (LHip[1]-LKnee[1]) * 0.1
    y_right= (RHip[1]-RKnee[1]) * 0.1

    HIP0=int((LHip[0]+RHip[0])/2)
    HIP1= int((LHip[1]+RHip[1])/2)

    LHip1 = (LHip[0] - int(x_diffhip), HIP1+int(y_left))
    RHip1 = (RHip[0] + int(x_diffhip), HIP1+int(y_right))
    LKnee1 = (LKnee[0] - int(x_diffknee), LKnee[1]-int(y_left))
    RKnee1 = (RKnee[0] + int(x_diffknee), RKnee[1]-int(y_right))

    # 변환 행렬 계산
    pts_src = np.float32([[0, 0], [cloth.shape[1], 0], [cloth.shape[1], cloth.shape[0]], [0, cloth.shape[0]]])
    pts_dst = np.float32([LHip1, RHip1, RKnee1, LKnee1])
    matrix = cv2.getPerspectiveTransform(pts_src, pts_dst)

    # 옷 이미지를 메인 이미지에 변환하여 오버레이
    cloth_warped = cv2.warpPerspective(cloth, matrix, (image.shape[1], image.shape[0]))

    # 메인 이미지 위에 옷 이미지를 올바르게 적용
    result = image.copy()
    for y in range(cloth_warped.shape[0]):
        for x in range(cloth_warped.shape[1]):
            if np.all(cloth_warped[y, x] != [0, 0, 0]):
                result[y, x] = cloth_warped[y, x]

    return result

# result_image = longpants_skirt(image_path, cloth_path)