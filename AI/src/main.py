import asyncio
import time
import RPi.GPIO as GPIO
import datetime
import cv2
import os
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
from multiprocessing import Process, Manager
import json
import logging
import face_recognition
from time import perf_counter, sleep
from AI.db.config import conn, cursor
import pickle
import psycopg2.extras
import aiohttp
import websockets


def setup_GPIO():
    try:
        logging.info("STARTING SETUP GPIO")
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        TRIGGER = 35
        ECHO = 37
        GPIO.setup(TRIGGER, GPIO.OUT)
        GPIO.setup(ECHO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        logging.info("ENDED SETUP GPIO")
        return TRIGGER, ECHO
    except Exception as e:
        logging.error(f"CHECKING DISTANCE: {e}")


def ultrasonic_detection(TRIGGER, ECHO):
    try:
        GPIO.output(TRIGGER, GPIO.HIGH)
        sleep(0.00001)
        GPIO.output(TRIGGER, GPIO.LOW)
        start = time.time()
        end = time.time()
        while GPIO.input(ECHO) == 0:
            if time.time() - start > 0.1:
                break
            start = time.time()
        while GPIO.input(ECHO) == 1:
            end = time.time()
        signal_duration = end - start
        distance = round(signal_duration * 17150, 2)
        return distance
    except Exception as e:
        logging.error(f"ULTRASONIC DETECTING: {e}")


def start_worker(procnum, return_dict, resized_image, face):
    return_dict[procnum] = face_recognition.face_encodings(resized_image, face)


async def send_message(camera, raw_capture, data, encoded_face_train, class_names):
    async with aiohttp.ClientSession() as session:
        url = f"http://{os.environ.get('HOST')}/auth/signin/"
        response = await session.post(
            url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(
                {
                    "username": f"{os.environ.get('MODERATOR_NAME')}",
                    "password": f"{os.environ.get('MODERATOR_PWD')}",
                }
            ),
        )
        if response.status == 200:
            user_data = await response.json()
            access_token = user_data["access"]
            ws_url = (
                f"ws://{os.environ.get('HOST')}/ws/log/?access_token={access_token}"
            )

            async with websockets.connect(ws_url, ping_interval=None) as websocket:
                logging.info("START SHOOTING")
                for frame in camera.capture_continuous(
                    raw_capture, format="bgr", use_video_port=True, resize=(640, 480)
                ):
                    frame_date = datetime.datetime.now()
                    start_foo = perf_counter()
                    img = frame.array
                    resized_image = cv2.resize(img, (0, 0), None, 0.25, 0.25)
                    faces_in_frame = face_recognition.face_locations(resized_image)
                    logging.info(f"FACES IN FRAME {len(faces_in_frame)}")

                    manager = Manager()
                    return_dict = manager.dict()
                    procs = []

                    start = perf_counter()
                    for el in enumerate(faces_in_frame):
                        proc = Process(
                            target=start_worker,
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
                    logging.info(
                        f"Find_encodings_in_loop: {finish - start} + {len(faces_in_frame)} people"
                    )

                    bulk_records = []
                    for encoded_face, faceloc in zip(encoded_faces, faces_in_frame):
                        start = perf_counter()
                        matches = face_recognition.compare_faces(
                            encoded_face_train, encoded_face
                        )
                        finish = perf_counter()
                        logging.info(f"Compare_faces: {finish - start}")
                        start = perf_counter()
                        face_dist = face_recognition.face_distance(
                            encoded_face_train, encoded_face
                        )
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
                            cv2.rectangle(
                                img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED
                            )
                            cv2.putText(
                                img,
                                person_name,
                                (x1 + 6, y2 - 5),
                                cv2.FONT_HERSHEY_COMPLEX,
                                1,
                                (255, 255, 255),
                                2,
                            )
                            logging.info(f"DETECTED {person_name}")
                        bulk_records.append((name, frame_date, True))
                    psycopg2.extras.execute_batch(
                        cursor,
                        """INSERT INTO LOG(employee_id, last_seen, status) VALUES(%s, CAST(%s AS TIMESTAMP), CAST(%s AS BOOLEAN))""",
                        bulk_records,
                    )
                    conn.commit()
                    finish_foo = perf_counter()
                    logging.info(f"WHOLE EPOCH: {finish_foo - start_foo}")

                    await show_img(img)
                    raw_capture.truncate(0)

                    if faces_in_frame:
                        message = {"frame_date": f"{frame_date}"}
                        await websocket.send(json.dumps(message))

                    await asyncio.sleep(0.0000001)
        else:
            raise ValueError("Failed to establish connection with the server")


async def control_display(off=False):
    if off:
        os.system("vcgencmd display_power 1")
    else:
        os.system("vcgencmd display_power 0")


async def check_distance(TRIGGER, ECHO):
    try:
        logging.info("START CHECKING")
        while True:
            distance = ultrasonic_detection(TRIGGER, ECHO)
            logging.info("CHECKING....")
            if distance <= 10:
                await control_display(True)
                logging.info("obj detected")
                await asyncio.sleep(1)
            else:
                await control_display()
    except Exception as e:
        logging.error(f"CHECKING DISTANCE: {e}")


async def show_img(img):
    cv2.imshow("Frame", img)
    cv2.waitKey(1)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s;%(message)s",
        datefmt="%Y.%m.%d %H:%M:%S",
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
    class_names = [el[1] for el in data]
    logging.info(f"LOADING DATA: {perf_counter() - start}")

    TRIGGER, ECHO = setup_GPIO()
    task1 = asyncio.create_task(check_distance(TRIGGER, ECHO))
    task2 = asyncio.create_task(
        send_message(camera, raw_capture, data, encoded_face_train, class_names)
    )
    await asyncio.gather(task1, task2)
    camera.close()
    GPIO.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
