import os
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from time import perf_counter
import face_recognition
import cv2
import psycopg2.extras
import pickle

from AI.db.config import cursor, conn

path = "static"

images = []


def append_img(img):
    cur_img = cv2.imread(f"{path}/{img}")
    images.append(
        [
            cv2.cvtColor(cur_img, cv2.COLOR_BGR2RGB),
            os.path.splitext(img)[0],
            f"{path}/{img}",
        ]
    )


def find_encodings(img):
    return face_recognition.face_encodings(img[0])[0]


if __name__ == "__main__":
    start = perf_counter()
    with ThreadPoolExecutor() as executor:
        executor.map(append_img, os.listdir(path))
    finish = perf_counter()

    print(f"Append_img: {finish - start}")

    start = perf_counter()
    with ProcessPoolExecutor() as executor:
        encoded_face_train = list(executor.map(find_encodings, images))
    finish = perf_counter()
    print(f"find_encodings: {finish - start}")
    bulk_records = [
        (
            el[1].split()[0],
            el[1].split()[1],
            el[2],
            pickle.dumps(encoded_face_train[index]),
        )
        for index, el in enumerate(images)
    ]
    try:
        psycopg2.extras.execute_batch(
            cursor,
            """INSERT INTO EMPLOYEE(first_name, last_name, img_path, encoded_img) VALUES(%s, %s, %s, %s);""",
            bulk_records,
        )
        conn.commit()
    except Exception as err:
        print(err)
