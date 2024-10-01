
import cv2
import numpy as np
import face_recognition
from datetime import datetime
import os

path = 'attendance_images'
images_list = []
image_names = []
my_list = os.listdir(path)
print(my_list)
for file in my_list:
    current_image = cv2.imread(f'{path}/{file}')
    images_list.append(current_image)
    image_names.append(os.path.splitext(file)[0])
print(image_names)

def find_encodings(images):
    encode_list = []
    for image in images:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(image)[0]
        encode_list.append(encode)
    return encode_list

encode_known_list = find_encodings(images_list)
print("Encoding Complete")

def mark_attendance(person_name):
    with open('Attendance.csv', 'r+') as f:
        my_data_list = f.readlines()
        name_list = []
        for line in my_data_list:
            entry = line.split(',')
            name_list.append(entry[0])
        if person_name not in name_list:
            now = datetime.now()
            date_string = now.strftime('%H:%M:%S')
            f.writelines(f'\n{person_name},{date_string}')

webcam_feed = cv2.VideoCapture(0)

while True:
    success, frame = webcam_feed.read()
    frame_resized = cv2.resize(frame,(0,0),None,0.25,0.25)
    frame_resized = cv2.cvtColor(frame_resized,cv2.COLOR_BGR2RGB)

    faces_in_current_frame = face_recognition.face_locations(frame_resized)
    encodes_current_frame = face_recognition.face_encodings(frame_resized,faces_in_current_frame)

    for encode_the_face,location_of_face in zip(encodes_current_frame,faces_in_current_frame):
        matches = face_recognition.compare_faces(encode_known_list,encode_the_face)
        similarity_score = face_recognition.face_distance(encode_known_list,encode_the_face)
        print(similarity_score)
        match_index = np.argmin(similarity_score)

        if matches[match_index]:
            name = image_names[match_index].upper()
            print(name)
            y1,x2,y2,x1 = location_of_face
            y1,x2,y2,x1 = y1*4,x2*4,y2*4,x1*4
            cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
            cv2.rectangle(frame,(x1, y2-35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(frame,name,(x1+6, y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
            mark_attendance(name)

    cv2.imshow('Webcam',frame)
    cv2.waitKey(1)