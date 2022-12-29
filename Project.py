from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, QDate, QTimer
from PyQt5.QtGui import QImage, QPixmap
import datetime
from PyQt5.uic import loadUi
import cv2
from PyQt5.QtWidgets import QDialog, QMessageBox
import face_recognition as fr
import numpy as np
import os


class Console(QDialog):
    def __init__(self):
        super(Console, self).__init__()
        loadUi("./design.ui", self)
        curr = QDate.currentDate()
        currDate = curr.toString('ddd dd MMM yyyy')
        currTime = datetime.datetime.now().strftime("%I:%M %p")
        self.insertDate.setText(currDate)
        self.insertTime.setText(currTime)
        self.image = None

    @pyqtSlot()
    def beginDetection(self):

        self.imageTaken = cv2.VideoCapture(0)
        self.timer = QTimer(self)  # Create Timer

        path = 'Images\Face'
        if not os.path.exists(path):
            os.mkdir(path)

        # known face encoding and known face name list
        images = []
        self.imageNames = []
        self.encode_list = []

        attendance_list = os.listdir(path)

        for tasweer in attendance_list:
            cur_img = cv2.imread(f'{path}/{tasweer}')
            images.append(cur_img)
            self.imageNames.append(os.path.splitext(tasweer)[0])  # separates name from .jpg

        for img in images:

            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # converting into RGB form default BGR
            boxes = fr.face_locations(img)
            encodes_cur_frame = fr.face_encodings(img, boxes)[0]
            self.encode_list.append(encodes_cur_frame)

        self.timer.timeout.connect(self.update_frame)  # Connect timeout to the output function
        self.timer.start(40)  # emit the timeout() signal at x=40ms

    def detectFaces(self, currentFace, encodedFaces, imageNames):

        def mark_attendance(name):

            if self.Present.isChecked():
                self.results.hide()
                self.Present.setEnabled(False)  # if person has checked in then don't allow again
                with open('Attendance.csv', 'a') as file:
                    if name != 'unknown':  # if a registered person is found
                        box = QMessageBox.question(self, 'Welcome ' + name, 'Do you want to Mark your Attendance ?',
                                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                        if box == QMessageBox.Yes:
                            # if person says yes
                            timeDate = datetime.datetime.now().strftime("%y/%m/%d %H:%M:%S")
                            file.writelines(f'\n{name},{timeDate},Marked')  # write name and mark attendance
                            self.Present.setChecked(False)
                            """
                            Showing status on console window
                            """
                            self.name1.setText(name)
                            self.status1.setText('Marked')
                            self.Time2 = datetime.datetime.now()
                            self.Present.setEnabled(True)

                        else:
                            self.Present.setEnabled(True)

            elif self.Absent.isChecked():
                self.results.hide()
                self.Absent.setEnabled(False)  # if person has checked in then don't allow again
                with open('Attendance.csv', 'a') as file:
                    if name != 'unknown':  # if a registered person is found

                        box = QMessageBox.question(self, 'Warning!!' + name, 'Do you want to UnMark your Attendance ?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)  # default No

                        if box == QMessageBox.Yes:  # if person says yes

                            timeDate = datetime.datetime.now().strftime("%y/%m/%d %H:%M:%S")
                            file.writelines(f'\n{name},{timeDate}, UnMarked')
                            self.Absent.setChecked(False)
                            self.name1.setText(name)
                            self.status1.setText('UnMarked')
                            self.Absent.setEnabled(True)

                        else:
                            self.Absent.setEnabled(True)

            elif self.saveface.isChecked() and name == 'unknown':
                """
                Saving face
                """
                self.saveface.setEnabled(False)
                person, check = QtWidgets.QInputDialog.getText(self, 'Input Dialog', 'Enter your Name: ')  # creates a dialog box
                if check:

                    cv2.imwrite(f'Images/Face/{person}.jpg', self.image)  # adding image into the dataset folder with his name
                    self.saveface.setEnabled(True)
                    self.results.setText(person + 'Your Record is Saved Successfully')
                    self.saveface.setChecked(False)

            elif self.saveface.isChecked() and name != 'unknown':

                self.results.setText('Your Record is Already Present!')
                self.saveface.setChecked(False)

        currface = fr.face_locations(currentFace)
        currencode = fr.face_encodings(currentFace, currface)

        for eface, loc in zip(currencode, currface):
            match = fr.compare_faces(encodedFaces, eface, tolerance=0.50)
            distance = fr.face_distance(encodedFaces, eface)
            name = "unknown"
            index = np.argmin(distance)

            if match[index] < 0.50:
                # name = imageNames[index].upper()
                mark_attendance(name)
                y1, x2, y2, x1 = loc
                cv2.rectangle(currentFace, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(currentFace, (x1, y2 - 20), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(currentFace, f'{name} {round(distance[index], 3)}', (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            else:
                name = imageNames[index].upper()
                mark_attendance(name)
                y1, x2, y2, x1 = loc
                cv2.rectangle(currentFace, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(currentFace, (x1, y2 - 20), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(currentFace, f'{name} {round(distance[index], 3)}', (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        return currentFace

    def update_frame(self):
        """
        to check the image and display it on the output window
        :return:
        """
        ret, self.image = self.imageTaken.read()
        window = 1
        image = cv2.resize(self.image, (640, 480))
        try:
            image = self.detectFaces(image, self.encode_list, self.imageNames)
        except Exception as e:
            print(e)

        newImage = QImage.Format_Indexed8

        if len(image.shape) == 3:

            if image.shape[2] == 4:

                newImage = QImage.Format_RGBA8888  #The image is stored using a 32-bit byte-ordered RGBA format (8-8-8-8).

            else:
                newImage = QImage.Format_RGB888  # The image is stored using a 24-bit RGB format (8-8-8).

        outImage = QImage(image, image.shape[1], image.shape[0], image.strides[0], newImage)  # image data, height, width, steps
        outImage = outImage.rgbSwapped()

        if window == 1:
            """
            Shows image on the screen
            """
            self.imgLabel.setPixmap(QPixmap.fromImage(outImage))  # displays image on screen
            self.imgLabel.setScaledContents(True)
