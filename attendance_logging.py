# Will serve as the security gate in order for the user to access the program they created
# The user is first noticed to upload their images within a file for program's reference. For instance, the "attendance_images" file
# The program then logs the name and time, the user appeared in the program
# The csv file generated here will be used by another program in order for the user to access the main body of information they inputted
# Not yet official, add a functionality to let the user upload his/her own picture

import cv2
import numpy as nps
import face_recognition
from datetime import datetime
import os
from tkinter import filedialog
from tkinter import *
import shutil
import sys


images_list = []
image_names = []

def upload_image():
    file_path = filedialog.askopenfilename(title = "Select image: Make sure it's named accordingly",filetypes = (("jpg files","*jpg"),("all files","*.*")))
    if file_path:
        # Copy the file to the attendance_images directory
        image_name = os.path.basename(file_path)
        new_path = os.path.join("attendance_images", image_name)
        # The idea to use the shutil in copying files to a directory was derived from Stackoverflow: https://stackoverflow.com/questions/71001058/tkinter-upload-image-and-save-it-to-local-directory
        shutil.copy(file_path, new_path)

        # Convert the uploaded image to RGB and save it back
        uploaded_image = cv2.imread(new_path)
        # The code on how to convert an image to RGB format is derived from geeksforgeeks: https://www.geeksforgeeks.org/convert-bgr-and-rgb-with-python-opencv/
        rgb_image = cv2.cvtColor(uploaded_image, cv2.COLOR_BGR2RGB)

        # Use the RGB image directly
        images_list.append(rgb_image)
        image_names.append(os.path.splitext(image_name)[0])
        print(f"Uploaded and processed image: {image_name}")

        user_option = input("Do you want to add more image? (press 'y' to add; any key to exit): ")
        if user_option.lower() == 'y':
            window = Tk()
            window.withdraw()  # Hides the Tkinter window for better visual appearance
            upload_image()
            window.mainloop()
        else:
            print("The program will automatically refresh. Restart the program")
            quit()

def activate_face_recognition():
    print("Face recognition activating...\nPlease wait")
    
    # Encodes each images and convert it into RGB format. Note: RGB is the only type face recognition module can read and process
    def find_encodings(images):
        encode_list = []
        for image in images:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # The idea for the encoding error handling is from stackoverflow: https://stackoverflow.com/questions/59919993/indexerror-list-index-out-of-range-face-recognition
            try:
                encoded_image = face_recognition.face_encodings(image)[0]
                encode_list.append(encoded_image)
            except IndexError:
                print("Warning: No face detected in one of the images.\nSol: use another image")
                continue

        return encode_list

    encode_known_list = find_encodings(images_list)
    print("Encoding Complete")
  
    # Structures and log user information in the CSV file specified
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

    # Processes the webcam feed for identifying person and logging in the CSV file
    while True:
        success, frame = webcam_feed.read()
        # Resizes the images to 25%
        frame_resized = cv2.resize(frame,(0,0),None,0.25,0.25)
        frame_resized = cv2.cvtColor(frame_resized,cv2.COLOR_BGR2RGB)
        faces_in_current_frame = face_recognition.face_locations(frame_resized)
        # Encode the faces found in the current frame into feature vectors for comparison
        encodes_current_frame = face_recognition.face_encodings(frame_resized,faces_in_current_frame)

        for encode_the_face,location_of_face in zip(encodes_current_frame,faces_in_current_frame):
            # Compares the detected face encoding with the known encodings, then calculate its similarity score (lower value = more similar)
            matches = face_recognition.compare_faces(encode_known_list,encode_the_face)
            similarity_score = face_recognition.face_distance(encode_known_list,encode_the_face)
            print(similarity_score)
            match_index = nps.argmin(similarity_score)
            
            # Frames the camera feed when the person matched an existing image within the program's directory
            if matches[match_index]:
                name = image_names[match_index].upper()
                print(name)
                # Dimensions for formatting the square and name while the program is recognizing the person in camera feed
                y1,x2,y2,x1 = location_of_face
                y1,x2,y2,x1 = y1*4,x2*4,y2*4,x1*4
                cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
                cv2.rectangle(frame,(x1, y2-35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(frame,name,(x1+6, y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
                # Mark the attendance of the person in the CSV file
                mark_attendance(name)

        cv2.imshow('Webcam',frame)
        cv2.waitKey(1)

# Coordinates all the functionalities of the program
def main():
    print("WELCOME! THIS IS A FACE RECOGNITION AND SECURITY MANAGEMENT PROGRAM")
    # Reviews the images in the attendance_image directory
    path = 'attendance_images'
    my_list = os.listdir(path)
    for file in my_list:
        current_image = cv2.imread(f'{path}/{file}')
        images_list.append(current_image)
        image_names.append(os.path.splitext(file)[0])
    print(f"Existing image profiles: {image_names}")
    print("If your name isn't on the list please, please add your image; otherwise, proceed to the program")

    user_input = input("Do you want to add your own image (press 'y' to add; any key to proceed in attendance logging): ")
    if user_input.lower() == 'y':
        window = Tk()
        window.withdraw()  # Hides the Tkinter window for better visual appearance
        upload_image()
        window.mainloop()
    else:
        activate_face_recognition()

main()

