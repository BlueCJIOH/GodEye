import os
from multiprocessing import Process, Manager
import numpy as np
import cv2
import face_recognition
from datetime import datetime
from picamera.array import PiRGBArray
from picamera import PiCamera
from time import sleep, perf_counter
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

path = 'imgs'

images = []
class_names = []
staff_list = os.listdir(path)


def append_img(img):
    cur_img = cv2.imread(f'{path}/{img}')
    images.append(cv2.cvtColor(cur_img, cv2.COLOR_BGR2RGB))
    class_names.append(os.path.splitext(img)[0])


start = perf_counter()

with ThreadPoolExecutor() as executor:
    executor.map(append_img, staff_list)

finish = perf_counter()

print(f"Append_img: {finish - start}")


def find_encodings(img):
    return face_recognition.face_encodings(img)[0]


start = perf_counter()
with ProcessPoolExecutor() as executor:
    encoded_face_train = list(executor.map(find_encodings, images))
finish = perf_counter()

print(f"find_encodings: {finish - start}")


def mark_attendance(name):
    with open('Attendance.csv', 'r+') as f:
        data_list = f.readlines()
        name_list = []
        for line in data_list:
            entry = line.split(',')
            name_list.append(entry[0])
            if name not in name_list:
                now = datetime.now()
                time_stamp = now.strftime('%I:%M:%S:%p')
                date = now.strftime('%d-%B-%Y')
                f.writelines(f'{name}, {time_stamp}, {date}\n')


camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
raw_capture = PiRGBArray(camera, size=(640, 480))

sleep(0.01)


def worker(start, procnum, return_dict, resized_image, face):
    return_dict[procnum] = face_recognition.face_encodings(resized_image, face)
    finish = perf_counter()
    print(f'Face encodings in worker {finish-start}')


for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
    img = frame.array
    resized_image = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    faces_in_frame = face_recognition.face_locations(resized_image)
    manager = Manager()
    return_dict = manager.dict()
    procs = []
    start = perf_counter()
    # instantiating process with arguments
    for el in enumerate(faces_in_frame):
        proc = Process(target=worker, args=(start, el[0], return_dict, resized_image, [el[1], ]))
        procs.append(proc)
        proc.start()

    # complete the processes
    for proc in procs:
        proc.join()

    finish = perf_counter()
    encoded_faces = [el[1][0] for el in return_dict.items()]
    print(f"Find_encodings_in_loop: {finish - start} + {len(faces_in_frame)}")

    for encoded_face, faceloc in zip(encoded_faces, faces_in_frame):
        start = perf_counter()
        matches = face_recognition.compare_faces(encoded_face_train, encoded_face)
        finish = perf_counter()
        print(f"Compare_faces: {finish - start}")
        start = perf_counter()
        face_dist = face_recognition.face_distance(encoded_face_train, encoded_face)
        finish = perf_counter()
        print(f"Face_distance: {finish - start}")
        start = perf_counter()
        match_index = np.argmin(face_dist)
        finish = perf_counter()
        print(f"Argmin: {finish - start}")
        if matches[match_index]:
           name = class_names[match_index].upper().lower()
           y1, x2, y2, x1 = faceloc
           y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
           cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
           cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
           cv2.putText(img, name, (x1 + 6, y2 - 5), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
           # mark_attendance(name)

    cv2.imshow('Frame', img)
    raw_capture.truncate(0)
    if cv2.waitKey(1) & 0xFF == ord('q'):
       break