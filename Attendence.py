import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime

import mysql.connector


path = 'ImagesBasic'
images = []
classNames = []
myList = os.listdir(path)
print(myList)
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
print(classNames)
 
def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList
 
def markAttendance(name):
    now = datetime.now()
    d2 = now.strftime("%B %d, %Y")
    dtString = now.strftime('%H:%M:%S')
    mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="1234",
  database="mydatabase"
)
    mycursor = mydb.cursor()
    sql1 = "SELECT * FROM student WHERE name = %s"
    adr=(name,)
    mycursor.execute(sql1, adr)
    flag=0;
    myresult = mycursor.fetchall()
    for x in myresult:
        if x[4]=="true":
          flag=1;  
    if flag !=1:
            sql = "INSERT INTO student (name, date,time,flag) VALUES (%s, %s,%s,%s)"
            val = (name, d2,dtString,"true")
            mycursor.execute(sql, val)
            print("1 record inserted")
            mydb.commit()
    


 
encodeListKnown = findEncodings(images)
print('Encoding Complete')
 
cap = cv2.VideoCapture(0)
 
while True:
    success, img = cap.read()

    imgS = cv2.resize(img,(0,0),None,0.25,0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
 
    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS,facesCurFrame)
 
    for encodeFace,faceLoc in zip(encodesCurFrame,facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
#print(faceDis)
        matchIndex = np.argmin(faceDis)
 
        

        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
#print(name)
            y1,x2,y2,x1 = faceLoc
            y1, x2, y2, x1 = y1*4,x2*4,y2*4,x1*4
            cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
            cv2.rectangle(img,(x1,y2-35),(x2,y2),(0,255,0),cv2.FILLED)
            cv2.putText(img,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
            markAttendance(name)
 
    cv2.imshow('Webcam',img)
    cv2.waitKey(1)
    key = cv2.waitKey(10) 
    if key == 27: 
            break
cv2.destroyAllWindows()