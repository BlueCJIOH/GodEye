import json
import os
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from time import perf_counter
import face_recognition

import cv2

path = 'imgs'

images = []
class_names = []
staff_list = os.listdir(path)


def append_img(img):
    cur_img = cv2.imread(f'{path}/{img}')
    images.append(cv2.cvtColor(cur_img, cv2.COLOR_BGR2RGB))
    class_names.append(os.path.splitext(img)[0])


def find_encodings(img):
    return face_recognition.face_encodings(img)[0]


if __name__ == '__main__':
    start = perf_counter()
    with ThreadPoolExecutor() as executor:
        executor.map(append_img, staff_list)
    finish = perf_counter()

    print(f"Append_img: {finish - start}")

    start = perf_counter()
    with ProcessPoolExecutor() as executor:
        encoded_face_train = list(executor.map(find_encodings, images))
    finish = perf_counter()
    print(f"find_encodings: {finish - start}")
    dict_ = {
        'class_names': class_names,
        'encoded_face_train': encoded_face_train
    }
    with open("data.json", 'w') as data:
        data.write(dumps(dict_, indent=4))
