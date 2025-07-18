import cv2
import mediapipe as mp
import time
from BodyModule import PostureDetector
import math
from scipy.signal import savgol_filter
import matplotlib. pyplot as plt
from scipy.signal import find_peaks
VISIBILITY = 0.1
class ExerciseAnalyzer():
    def __init__(self):
        self.detector = PostureDetector()
    def analyzeVideo(self, video_path):
        cap = cv2.VideoCapture(video_path)
        l_angles=[]
        r_angles=[]
        while True:
            succes, img = cap.read()
            if not succes:
                print("End of video or failed to read frame.")
                break 
            img = self.detector.findPose(img, draw=True)
            self.lmlist = self.detector.getPosition(img, draw=False)
            if len(self.lmlist) != 0:
                l_angles.append(self.getLeftArm())
                r_angles.append(self.getRightArm())


            cv2.imshow("Image", img)
            cv2.waitKey(1)
        
        # mark, not_low_l, not_high_l, not_low_r, not_high_r = self.checkBicepCurl(l_angles, r_angles)
        # if not not_low_l and not not_high_l and not not_low_r and not not_high_r:
        #     message = "Good job."
        # elif (not_low_l or not_low_r) and (not_high_l or not_high_r):
        #     message = "You didn't curl fully. Also you need to extend the arm."
        # elif not_high_l or not_high_r:
        #     message = "You didn't curl fully."
        # elif not_low_l or not_low_r:
        #     message = "You need to extend the arm."
        # else:
        #     message = "No arm movement detected."

        # left_wrist_visibility = self.lmlist[15][3] 
        # right_wrist_visibility = self.lmlist[16][3]

        # if left_wrist_visibility < VISIBILITY:
        #     message += "Left arm detection issue."

        # if right_wrist_visibility < VISIBILITY:
        #     message += "Right arm detection issue."
        mark, low, high= self.checkBicepCurl(l_angles, r_angles)
        return mark, "."


    def findAngle(self, a, b, c):
        x1, y1 = a
        x2, y2 = b
        x3, y3 = c

        ba = (x1 - x2, y1 - y2)
        bc = (x3 - x2, y3 - y2)


        dot_product = ba[0]*bc[0] + ba[1]*bc[1]

        mag_ba = math.hypot(ba[0], ba[1])
        mag_bc = math.hypot(bc[0], bc[1])

        cos_angle = dot_product / (mag_ba * mag_bc + 1e-8)  # ca să nu împărți la 0
        angle = math.acos(cos_angle)

        return math.degrees(angle)
    


    def checkBicepCurl(self, left_arm_angles, right_arm_angles):

        filtered_left_angles = savgol_filter(left_arm_angles, window_length=20, polyorder=2, mode= "nearest")
        filtered_right_angles = savgol_filter(right_arm_angles, window_length=20, polyorder=2,  mode= "nearest")

        max_left_id = find_peaks(filtered_left_angles)[0]
        max_right_id = find_peaks(filtered_right_angles)[0]

        min_left_id = find_peaks(-filtered_left_angles)[0]
        min_right_id = find_peaks(-filtered_right_angles)[0]


        # plt.figure(figsize=(12, 6))
        # plt.plot(left_arm_angles, label='Unghi Dreapta Brut', alpha=0.7, color = 'blue')
        # plt.plot(filtered_left_angles, label='Unghi Dreapta Prelucrat', alpha=0.7, color = 'red')
        # # plt.plot(right_arm_angles, label='Unghi Dreapta Brut', alpha=0.7, color = 'blue')
        # # plt.plot(filtered_right_angles, label='Unghi Dreapta Prelucrat', alpha=0.7, color = 'red')
        # plt.show()

        left_wrist_visibility = self.lmlist[13][3] 
        right_wrist_visibility = self.lmlist[14][3]

        not_low_enough_l = 0
        not_high_enough_l = 0

        not_low_enough_r = 0
        not_high_enough_r = 0

        mark_l = -1
        mark_r = -1

        print(left_wrist_visibility)
        print(right_wrist_visibility)

        if len(min_left_id) <= len(max_left_id):
            rep_capture_error = 0
            index_number_l = len(min_left_id)
        else:
            rep_capture_error = 1
            index_number_l = len(max_left_id)

        for i in range(index_number_l):
            if filtered_left_angles[max_left_id[i]] < 150:
                not_low_enough_l += 1
            if filtered_left_angles[min_left_id[i + rep_capture_error]] > 70:
                not_high_enough_l += 1

        # number_of_reps_l = index_number_l - max(not_low_enough_l, not_high_enough_l)
        number_of_mistakes_l = not_high_enough_l + not_low_enough_l
        mark_l = 10 - 5 * number_of_mistakes_l / index_number_l
        return mark_l, not_low_enough_l, not_high_enough_l
        # if len(min_right_id) <= len(max_right_id):
        #     rep_capture_error = 0
        #     index_number_r = len(min_right_id)
        # else:
        #     rep_capture_error = 1
        #     index_number_r = len(max_right_id)

        # for i in range(index_number_r):
        #     if filtered_right_angles[max_right_id[i]] < 150:
        #         not_low_enough_r += 1
        #     if filtered_right_angles[min_right_id[i + rep_capture_error]] > 70:
        #         not_high_enough_r += 1
        # number_of_mistakes_r = not_high_enough_r + not_low_enough_r
        # mark_r = 10 - 5 * number_of_mistakes_r / index_number_r

        # if right_wrist_visibility >= VISIBILITY and left_wrist_visibility < VISIBILITY:
        #     return mark_r, 0, 0, not_low_enough_r, not_high_enough_r
        # elif right_wrist_visibility < VISIBILITY and left_wrist_visibility >= VISIBILITY:
        #     return mark_r, not_low_enough_l, not_high_enough_l, 0, 0
        # elif right_wrist_visibility < VISIBILITY and left_wrist_visibility < VISIBILITY:
        #     return 0,0,0,0,0
        # else:
        #     mark = (mark_r+mark_l)/2
            # return mark, not_low_enough_l, not_high_enough_l, not_low_enough_r, not_high_enough_r

        

    def getRightArm(self):

        right_shoulder = self.lmlist[12][1:3]
        right_elbow = self.lmlist[14][1:3]
        right_wrist = self.lmlist[16][1:3]
        right_arm_angle = self.findAngle(right_shoulder, right_elbow, right_wrist)
        return right_arm_angle
    
    def getLeftArm(self):

        left_shoulder = self.lmlist[11][1:3]
        left_elbow = self.lmlist[13][1:3]
        left_wrist = self.lmlist[15][1:3]
        left_arm_angle = self.findAngle(left_shoulder, left_elbow, left_wrist)
        return left_arm_angle

        