import logging
from multiprocessing import Process, Manager
import numpy as np
import cv2
import face_recognition
from picamera.array import PiRGBArray
from picamera import PiCamera
from time import perf_counter, sleep
from AI.db.config import conn, cursor
import pickle
import psycopg2.extras


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s;%(message)s", datefmt="%Y.%m.%d %H:%M:%S"
)

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
raw_capture = PiRGBArray(camera, size=(640, 480))

sleep(0.01)

start = perf_counter()
cursor.execute("SELECT * FROM Employee")
data = cursor.fetchall()
encoded_face_train = [pickle.loads(el[4]) for el in data]
class_names = [el[2] for el in data]
logging.info(f"LOADING DATA: {perf_counter() - start}")


def worker(procnum, return_dict, resized_image, face):
    return_dict[procnum] = face_recognition.face_encodings(resized_image, face)


for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
    start_foo = perf_counter()
    img = frame.array
    resized_image = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    faces_in_frame = face_recognition.face_locations(resized_image)

    manager = Manager()
    return_dict = manager.dict()
    procs = []

    start = perf_counter()
    for el in enumerate(faces_in_frame):
        proc = Process(
            target=worker,
            args=(
                el[0],
                return_dict,
                resized_image,
                [
                    el[1],
                ],
            ),
        )
        procs.append(proc)
        proc.start()

    for proc in procs:
        proc.join()
    finish = perf_counter()
    encoded_faces = [el[1][0] for el in return_dict.items()]
    logging.info(f"Find_encodings_in_loop: {finish - start} + {len(faces_in_frame)} people")
    bulk_records = []
    for encoded_face, faceloc in zip(encoded_faces, faces_in_frame):
        start = perf_counter()
        matches = face_recognition.compare_faces(encoded_face_train, encoded_face)
        finish = perf_counter()
        logging.info(f"Compare_faces: {finish - start}")
        start = perf_counter()
        face_dist = face_recognition.face_distance(encoded_face_train, encoded_face)
        finish = perf_counter()
        logging.info(f"Face_distance: {finish - start}")
        start = perf_counter()
        match_index = np.argmin(face_dist)
        finish = perf_counter()
        logging.info(f"Argmin: {finish - start}")
        name = None
        if matches[match_index]:
            name = data[match_index][0]
            person_name = class_names[match_index].upper().lower()
            y1, x2, y2, x1 = faceloc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(
                img,
                person_name,
                (x1 + 6, y2 - 5),
                cv2.FONT_HERSHEY_COMPLEX,
                1,
                (255, 255, 255),
                2,
            )
        bulk_records.append((name, True))
    psycopg2.extras.execute_batch(
        cursor,
        """INSERT INTO LOG(employee_id, last_seen, status) VALUES(%s, CURRENT_TIMESTAMP, CAST(%s AS BOOLEAN))""",
        bulk_records,
    )
    conn.commit()
    finish_foo = perf_counter()
    logging.info(f"WHOLE EPOCH: {finish_foo - start_foo}")
    cv2.imshow("Frame", img)
    raw_capture.truncate(0)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
