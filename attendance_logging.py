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
import csv
import random
import string
import time

images_list, image_names, profiles_list, file_list  = [], [], [], []

# Idea for this function is from YT and was tailored to the neeeds of the program
def upload_image_security():
    upper_case_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    lower_case_letter = upper_case_letters.lower()
    numbers = "".join(random.choices(string.digits, k=3)) 
    special_symbols = "!@#$%^&*()_-><|/?:."
    # Combine all parts, then shuffles it for maximum randomness
    passcode = upper_case_letters + lower_case_letter + numbers + special_symbols
    passcode_list = list(passcode)
    random.shuffle(passcode_list)
    # Limit the passcode into five characters
    official_passcode = "".join(random.sample(passcode_list, 5))

    available_attempts = 3 
    while available_attempts > 0:
        print(f"Please type in the given passcode: | {official_passcode} | to add your image to the directory")
        user_passcode_attempt = input("Enter the passcode: ")
        if user_passcode_attempt == official_passcode:
            print("Access granted")
            break 
        else:
            available_attempts -= 1
            print(f"Wrong passcode. Attempts remaining: {available_attempts}")

        if available_attempts == 0:
            print("No more attempts left. Try again later.")
            # Added a timer before the user can proceed to try again
            time.sleep(3)
            main()  

    window = Tk()
    window.withdraw()  # Hide Tkinter window for better appearance
    upload_image()
    window.mainloop() 

def upload_image():
    file_path = filedialog.askopenfilename(title = "Select image: Make sure it's named accordingly",filetypes = (("jpg files","*jpg"),("all files","*.*")))
    if file_path:
        # Copy the file to the attendance_images directory
        image_name = os.path.basename(file_path)
        new_path = os.path.join("attendance_images", image_name)
        # The idea to use the shutil in copying files to a directory was derived from Stackoverflow: https://stackoverflow.com/questions/71001058/tkinter-upload-image-and-save-it-to-local-directory
        shutil.copy(file_path, new_path)
        # Convert the uploaded image to RGB and save it back
        # The code on how to convert an image to RGB format is derived from geeksforgeeks: https://www.geeksforgeeks.org/convert-bgr-and-rgb-with-python-opencv/
        uploaded_image = cv2.imread(new_path)
        rgb_image = cv2.cvtColor(uploaded_image, cv2.COLOR_BGR2RGB)
        # Utilizes the RGB image directly
        images_list.append(rgb_image)
        image_names.append(os.path.splitext(image_name)[0])
        print(f"Uploaded and processed image: {image_name}")

        user_option = input("Do you want to add more image?\n Press 'y' to add)\n Press any key to main menu: ").lower()
        if user_option == 'y':
            window = Tk()
            window.withdraw()  # Hides the Tkinter window for better visual appearance
            upload_image()
            window.mainloop()
        else:
            main()

    if not file_path:     
        functionality_option = input("Image upload cancelled\n Do you want to try again? ('y' to proceed; any key to main menu): ").lower()
        if functionality_option.lower() == 'y':
            upload_image()
        else:
            main()

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
  
    # Structures and log user informations in the CSV file specified
    def mark_attendance(person_name):
        header_list = ['Name', 'Time']
        name_list = []
        with open('attendance.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, delimiter=',', fieldnames=header_list)
            writer.writeheader()
            if person_name not in name_list:
                now = datetime.now()
                date_string = now.strftime('%H:%M:%S')
                name_list.append(person_name)
                writer.writerow({'Name': person_name, 'Time': date_string})

    webcam_feed = cv2.VideoCapture(0)

    # Processes the webcam feed for identifying person and logging in the CSV file
    while True:
        success, frame = webcam_feed.read()
        # # Resizes the images to 25%
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
 
        # Terminating feature idea was derived from https://discuss.codingblocks.com/t/program-is-not-terminating/32257/5
        terminate_key = cv2.waitKey(1) & 0xFF
        if terminate_key == ord('q'):
            print("Terminating...")
            break

    # Release the webcam and close any open windows
    cv2.destroyAllWindows()
    webcam_feed.release()

    print("Exited face recogntion. Attendance logged in successfully\n Going back to main menu...")
    main()

# Prompts the user to enter their full name for profiling
def user_full_name():
    while True:
        special_cases = ["-", "'", "."]
        user_name = input("Enter your full name: ")
        user_name = user_name.split()
        name = (''.join(user_name))
        if len(name) >= 2:
            if any(elements in special_cases for elements in name) or name.isalpha():
                    name = (' '.join(user_name))
                    # Makes the first letters of the words capitalized
                    name = name.title()
                    profiles_list.append(name)
                    return name
            else:
                print(f"Name contains invalid characters. Only letters, digits, and {special_cases} are allowed.")
        else:
            print("Enter a valid name")

# Prompts the user to enter their age for profiling
def user_age():
    while True:
        try:
            user_age = int(input("Enter age (input must be realistic): "))
            if 0 < user_age <= 130:
                return user_age
            else:
                print("Please enter a valid age")
        except ValueError:
            print("Enter a numerical input only")

# Formats the input of the user within a txt file
def text_format():
    name = user_full_name()
    age = user_age()
    return f"Name: {name} | Age: {age}"

# Creates a txt file
def create_file_name():
    while True:
        print("The program will automatically convert the name into snake case")
        user_input = input("What do you want to name your txt file?: ")
        if user_input.isdigit():
            print("Please enter a valid name (Pure numerical name is not allowed)")
        else:
            index_list = []
            # Converts the name in a snake_case format if there's no occurrence of a number within the name
            user_input = '_'.join(user_input.lower().split())
            # Checks for the occurrence of a number within the name and stores its index
            if any(num.isdigit() for num in user_input):
                for index, inputs in enumerate(user_input):
                    if inputs.isdigit():
                        index_list.append(index)
                # Adds an underscore in the index of the first number within the name using the smallest index from index_list
                index_of_number = min(index_list)
                for indices in range(len(user_input)):
                    if indices == index_of_number:
                        valid_name = user_input[:index_of_number] + "_" + user_input[index_of_number:]
                        break
            else:
                valid_name = user_input
            
            valid_name = valid_name.replace("__", "_")
            return valid_name

# Coordinates all the functionalities of the txt editing functionality
def txt_editing_functionality():
    print("Please take note that the file and information inputted here can only be...\nACCESSED WHEN THE PROGRAM VALIDATED THE ATTENDANCE OF AN EXISTING PROFILE")
    file_name = create_file_name()
    # Temporarily stores the name of the txt file
    file_list.append(file_name)

    while True:
        with open(f"{file_name}.txt", "a") as file:
            file.write(text_format())

            while True:
                user_option = input("Do you want to add more information?\n Press 'y' to proceed\n Press 'n' to opt not to): ").lower()
                if user_option == 'y':
                    file.write(f"\n{text_format()}")
                elif user_option == 'n':
                    break
                else:
                    print("Please respond using only the specified")
            
        reuse_option = input(f"Do you want to keep using the file '{file_name}.txt' (press 'y' or 'n'); or\nCreate a new one (press any key)? ").lower()
        if reuse_option == 'y':
            continue 
        elif reuse_option == 'n':
            print("Going back to main menu...")
            break
        else:
            file_name = create_file_name()
            file_list.append(file_name) 
            print(f"New file: '{file_name}.txt' will be used.")
    
    main()

# Coordinates all the functionalities of the program
def main():
    print("WELCOME! THIS IS A FACE RECOGNITION AND FILE MANAGEMENT PROGRAM")
    # Reviews the images in the attendance_image directory
    path = 'attendance_images'
    my_list = os.listdir(path)
    for file in my_list:
        current_image = cv2.imread(f'{path}/{file}')
        images_list.append(current_image)
        image_names.append(os.path.splitext(file)[0])
    print(f"Existing image profiles: {image_names}")
    print("Please choose an option:\n"
      "1) If your name isn't on the list: Add your image.\n"
      "2) if your name is on the list: Proceed to face recognition.\n"
      "3) Create and edit a user profile.\n"
      "4) View profiles.\n"
      "5) Exit.")

    while True:
        user_input = input("Press the corresponding number of the option to proceed (1 or 4): ")
        if user_input == '1':
            upload_image_security()
        elif user_input == '2':
            activate_face_recognition()
        elif user_input == '3':
            txt_editing_functionality()
        elif user_input == '4':
            pass
        elif user_input == '5':
            print("User exited the program")
            quit()
        else:
            print("please respond using only the specified")
        
main()

