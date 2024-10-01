import cv2
import numpy as np
import face_recognition


image_elon = face_recognition.load_image_file('test_images/Elon Musk.jpg')
image_elon = cv2.cvtColor(image_elon,cv2.COLOR_BGR2RGB)
image_test = face_recognition.load_image_file('test_images/Elon Test.jpg')
image_test = cv2.cvtColor(image_test,cv2.COLOR_BGR2RGB)


face_location = face_recognition.face_locations(image_elon)[0]
encode_elon = face_recognition.face_encodings(image_elon)[0]
cv2.rectangle(image_elon,(face_location[3],face_location[0]),(face_location[1],face_location[2]),(255,0,255),2)

face_location_test = face_recognition.face_locations(image_test)[0]
encode_test = face_recognition.face_encodings(image_test)[0]
cv2.rectangle(image_test,(face_location_test[3],face_location_test[0]),(face_location_test[1],face_location_test[2]),(255,0,255),2)


results = face_recognition.compare_faces(([encode_elon]), encode_test)
face_similarity = face_recognition.face_distance([encode_elon], encode_test)
print(results, face_similarity)
cv2.putText(image_test,f'{results}{round(face_similarity[0],2)}',(50,50),cv2.FONT_HERSHEY_COMPLEX,1,(0,0,255),2)


cv2.imshow('Elon Musk',image_elon)
cv2.imshow('Elon Test',image_test)
cv2.waitKey(0)
