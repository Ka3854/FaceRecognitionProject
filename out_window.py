import time
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot, QTimer, QDate, Qt
from PyQt5.QtWidgets import QDialog,QMessageBox
import cv2
import face_recognition
import numpy as np
import datetime
import os
import csv

class Ui_OutputDialog(QDialog):
    def __init__(self):
        super(Ui_OutputDialog, self).__init__()
        loadUi("./outputwindow.ui", self)

        # displaying date,time on output window ui
        now = QDate.currentDate()
        current_date = now.toString('ddd dd MMMM yyyy')
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        self.Date_Label.setText(current_date)
        self.Time_Label.setText(current_time)
        self.image = None

    @pyqtSlot()
    def startVideo(self, camera_name):

        if len(camera_name) == 1:
        	self.capture = cv2.VideoCapture(int(camera_name))
        else:
        	self.capture = cv2.VideoCapture(camera_name)
        self.timer = QTimer(self)  # Create Timer
        path = 'ImagesAttendance'
        if not os.path.exists(path):
            os.mkdir(path)
        # known face encoding and known face name list
        images = []
        self.class_names = []
        self.encode_list = []#creating list for face encodings
        self.TimeList1 = []# creating list for checking in,out times
        self.TimeList2 = []
        attendance_list = os.listdir(path)# creating list for images in imagesattendance folder


        for cl in attendance_list:
            cur_img = cv2.imread(f'{path}/{cl}')#importing images from the folder along with the name
            images.append(cur_img)#appending image
            self.class_names.append(os.path.splitext(cl)[0])#appending name
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(img)
            encodes_cur_frame = face_recognition.face_encodings(img, boxes)[0] #finding encoding of images
            self.encode_list.append(encodes_cur_frame)
        self.timer.timeout.connect(self.update_frame)  # Connect timeout to the output function
        self.timer.start(10)  # emit the timeout() signal at x=10ms

    def face_rec_(self, frame, encode_list_known, class_names):
        """
        :param frame: frame from camera
        :param encode_list_known: known face encoding
        :param class_names: known face names
        :return:
        """
        # csv
        #funtion for marking attendance in csv and output window

        def mark_attendance(name):
            """
            :param name: detected face known or unknown one
            """
            if self.ClockInButton.isChecked():
                self.ClockInButton.setEnabled(False)
                with open('Attendance.csv', 'a') as f:
                        #clocks in employee
                        if (name != 'unknown'):
                            buttonReply = QMessageBox.question(self, 'Welcome ' + name, 'Are you Clocking In?' ,
                                                               QMessageBox.Yes | QMessageBox.No, QMessageBox.No)# clock in confirmation dialogue box opens
                            if buttonReply == QMessageBox.Yes:

                                #name, date , clock in time is entered into csv
                                date_time_string = datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")
                                f.writelines(f'\n{name},{date_time_string},Clock In')
                                self.ClockInButton.setChecked(False)
                                #status is changed to "clocked in" in output window
                                self.NameLabel.setText(name)
                                self.StatusLabel.setText('Clocked In')
                                self.HoursLabel.setText('Measuring')
                                self.MinLabel.setText('')

                                self.Time1 = datetime.datetime.now()
                                self.ClockInButton.setEnabled(True)
                            else:
                                print('Not clicked.')
                                self.ClockInButton.setEnabled(True)
            #clocks out employee
            elif self.ClockOutButton.isChecked():
                self.ClockOutButton.setEnabled(False)
                with open('Attendance.csv', 'a') as f:
                        if (name != 'unknown'):
                            buttonReply = QMessageBox.question(self, 'Cheers ' + name, 'Are you Clocking Out?',
                                                              QMessageBox.Yes | QMessageBox.No, QMessageBox.No)# clock out confirmation dialogue box opens
                            if buttonReply == QMessageBox.Yes:

                              date_time_string = datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S") #reads and stores current date, time in the variable
                              self.ClockOutButton.setChecked(False)

                              self.NameLabel.setText(name)
                              self.StatusLabel.setText('Clocked Out')
                              self.Time2 = datetime.datetime.now()


                              self.ElapseList(name)
                              #calculating clocked time for which employee was present in enterprise
                              self.TimeList2.append(datetime.datetime.now())
                              CheckInTime = self.TimeList1[-1]
                              CheckOutTime = self.TimeList2[-1]
                              self.ElapseHours = (CheckOutTime - CheckInTime)
                              self.MinLabel.setText("{:.0f}".format(abs(self.ElapseHours.total_seconds() / 60)%60)+'m')
                              self.HoursLabel.setText("{:.0f}".format(abs(self.ElapseHours.total_seconds() / 60**2))+'h')
                              #name, clocking out date, time, total time for which employee was present entered into csv
                              f.writelines(f'\n{name},{date_time_string},Clock Out,{self.ElapseHours},total time')
                              self.ClockOutButton.setEnabled(True)
                            else:
                                print('Not clicked.')
                                self.ClockOutButton.setEnabled(True)

        # face recognition
        # finding encodings of webcam image
        faces_cur_frame = face_recognition.face_locations(frame)
        encodes_cur_frame = face_recognition.face_encodings(frame, faces_cur_frame)#creating a list of current face encoding
        # count = 0
        for encodeFace, faceLoc in zip(encodes_cur_frame, faces_cur_frame):
            # matching and finding smallest face distance among stored images(encode list known)
            match = face_recognition.compare_faces(encode_list_known, encodeFace, tolerance=0.50)
            face_dis = face_recognition.face_distance(encode_list_known, encodeFace)
            name = "unknown"
            best_match_index = np.argmin(face_dis)
            # displaying a person's name and a box around face after finding a match
            if match[best_match_index]:
                name = class_names[best_match_index].upper()
                y1, x2, y2, x1 = faceLoc
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(frame, (x1, y2 - 20), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
            mark_attendance(name)# marks attendance in csv file by passing name into the mark_attendance function

        return frame

    def showdialog(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        msg.setText("This is a message box")
        msg.setInformativeText("This is additional information")
        msg.setWindowTitle("MessageBox demo")
        msg.setDetailedText("The details are as follows:")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

    #to retrieve clocked time from csv (of current employee clocking out.)
    def ElapseList(self,name):
        with open('Attendance.csv', "r") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 2

            Time1 = datetime.datetime.now()
            Time2 = datetime.datetime.now()
            for row in csv_reader:
                for field in row:
                    if field in row:
                        if field == 'Clock In':
                            if row[0] == name:
                                Time1 = (datetime.datetime.strptime(row[1], '%d/%m/%y %H:%M:%S')) #reads clock in date, time from csv
                                self.TimeList1.append(Time1) #adds it to time list 1
                        if field == 'Clock Out':
                            if row[0] == name:
                                Time2 = (datetime.datetime.strptime(row[1], '%d/%m/%y %H:%M:%S'))#reads clock in date , time from csv
                                self.TimeList2.append(Time2) #adds it to time list 2






    def update_frame(self):
        ret, self.image = self.capture.read()
        self.displayImage(self.image, self.encode_list, self.class_names, 1)

    def displayImage(self, image, encode_list, class_names, window=1):
        """
        :param image: frame from camera
        :param encode_list: known face encoding list
        :param class_names: known face names
        :param window: number of window
        :return:
        """
        image = cv2.resize(image, (640, 480)) # resizing image captured in camera
        try:
            image = self.face_rec_(image, encode_list, class_names)
        except Exception as e:
            print(e)
        qformat = QImage.Format_Indexed8
        if len(image.shape) == 3:
            if image.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888
        outImage = QImage(image, image.shape[1], image.shape[0], image.strides[0], qformat)
        outImage = outImage.rgbSwapped()

        if window == 1:
            self.imgLabel.setPixmap(QPixmap.fromImage(outImage))
            self.imgLabel.setScaledContents(True)
