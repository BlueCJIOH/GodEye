import os
import cv2
import numpy as np
import face_recognition
from datetime import datetime
from picamera.array import PiRGBArray
from picamera import PiCamera
import time

path = 'imgs'

images = []
class_names = []
staff_list = os.listdir(path)
for cl in staff_list:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    class_names.append(os.path.splitext(cl)[0])


def find_encodings(images):
    encoded_list = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encoded_face = face_recognition.face_encodings(img)[0]
        encoded_list.append(encoded_face)
    return encoded_list


encoded_face_train = find_encodings(images)


def mark_attendance(name):
    with open('Attendance.csv', 'r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in nameList:
            now = datetime.now()
            time_stamp = now.strftime('%I:%M:%S:%p')
            date = now.strftime('%d-%B-%Y')
            f.writelines(f'{name}, {time_stamp}, {date}\n')


camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
raw_capture = PiRGBArray(camera, size=(640, 480))

time.sleep(0.01)

for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
    img = frame.array
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    faces_in_frame = face_recognition.face_locations(imgS)
    encoded_faces = face_recognition.face_encodings(imgS, faces_in_frame)
    for encode_face, faceloc in zip(encoded_faces, faces_in_frame):
        matches = face_recognition.compare_faces(encoded_face_train, encode_face)
        face_dist = face_recognition.face_distance(encoded_face_train, encode_face)
        match_index = np.argmin(face_dist)
        if matches[match_index]:
            name = class_names[match_index].upper().lower()
            y1, x2, y2, x1 = faceloc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 5), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            mark_attendance(name)

    cv2.imshow('Frame', img)
    raw_capture.truncate(0)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
