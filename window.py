import functools
import os
import sys
import matplotlib
matplotlib.use('QtAgg')
from typing import *
import re
import time
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem , QLineEdit, QDialog, QMessageBox, QFileDialog
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QPixmap
from PyQt6 import uic, QtCore, QtWidgets
import mysql.connector
from Verify import scanthrough
from PyQt6.QtCore import Qt, QTimer, QDateTime
import firebase_admin
from firebase_admin import credentials, db
import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import numpy as np
from Allclass import myMessBox, StandardItem
global user, passw
import csv
import pandas as pd
path = r"C:\Users\TUNG\Documents\FF_GUI_Drone\new-world-22236-firebase-adminsdk-mgqvn-8f111c14b5.json"

# cred = credentials.Certificate(path)
# confirm = firebase_admin.initialize_app(cred, {
#     "databaseURL": "https://new-world-22236-default-rtdb.asia-southeast1.firebasedatabase.app/"
# })
# print(confirm)
# ref = db.reference("/User")
#
# result = ref.get()


mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="tungpro2k11",
    database="test123"
)
mycursor = mydb.cursor()




class myAni(FigureCanvas):
    def __init__(self, x_len: int, y_range: list, parent=None):
        FigureCanvas.__init__(self, plt.Figure())
        self._x_len = x_len
        self.fig_ax = self.figure.subplots()
        self.fig_ax.set_ylim(ymin=y_range[0], ymax=y_range[1])
        self.xs = list(range(0,     self._x_len))
        self.ys = [0] * x_len
        self.setpoint_= [0] * x_len
        self.line_p_, = self.fig_ax.plot(self.xs, self.ys, lw=1, color='blue')
        self.fig_ax.grid()
        self.setpoint_p_l, = self.fig_ax.plot(self.xs, self.setpoint_, lw=1, color='r')

def find_all(a_str, sub):
    start = 0
    i = 0
    occur = []
    while True:
        start = a_str.find(sub, start)
        if start !=-1:
            i += 1
            occur[i-1] = start
        if start ==-1:
           return occur










class Droneview(QMainWindow):
    def __init__(self, parent=None):
        super(Droneview, self).__init__(parent)
        uic.loadUi("DroneView.ui", self)
        self.actionExit.triggered.connect(self.actionexit)
        self.timer = QTimer()
        self.timer.timeout.connect(self.showtime)
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append(port.name)
        print(ports)
        self.comboBox.addItems(ports)
        self.options = ('Plot Pitch', 'Plot Roll', 'Plot Yaw', 'Plot Error', 'Plot XY')
        self.subPlot.addItems(self.options)
        self.subPlot.activated.connect(self.plotting)
        self.comboBox.currentIndexChanged.connect(self.current)
        self.comboBox.activated.connect(self.activated)
        self.ConnectP.clicked.connect(self.connect)
        self.SubmitP.clicked.connect(self.submit)
        self.DisconP.clicked.connect(self.disconnect)
        self.Capture.clicked.connect(self.capture)
        self.PlotState.clicked.connect(self.toggle_ani)
        self.Throttle.valueChanged[int].connect(self.throttle_change)
        self.Throttle.sliderReleased.connect(self.throttle_submit)
        self.data = self.comboBox.currentText()
        self.buffers = bytearray()
        self.y_position = None
        self.roll = None
        self.yaw = None
        self.seriallob = None
        self.pitch= None
        self.indices = None
        self.is_animation_running = True
        self.y_axis = [0] * 5000
        self.ani = None
        self.Px = [0.0] * 50
        self.Py = [0.0] * 50
        self.xs = list(range(0, 5000))
        self.ys = [0] * len(self.xs)
        self.ysp = [0] * len(self.xs)
        self.ysw = [0] * len(self.xs)
        self.errors = [0] * len(self.xs)
        self.setpoint_ = [0] * len(self.xs)
        self.setpoint_p_ = [0] * len(self.xs)
        self.setpoint_p_2 = [0] * len(self.xs)
        self.setpoint_p_3 = [0] * len(self.xs)
        self.fig, self.fig_ax = plt.subplots()  #for roll
        self.fig_2, self.fig_2_ax = plt.subplots()  #for pitch
        self.error, self.error_ax = plt.subplots() #for error
        self.fig_3, self.fig_3_ax = plt.subplots() #xx
        self.fig_4, self.fig_4_ax = plt.subplots()
        self.fig_5, self.fig_5_ax = plt.subplots()
        self.fig_ax.set_ylim(ymin=-20, ymax=20)
        self.fig_2_ax.set_ylim(ymin=-20, ymax=20)
        self.fig_3_ax.set_ylim(ymin=-20, ymax=20)
        self.fig_4_ax.set_ylim(ymin=-50, ymax=50)
        self.error_ax.set_ylim(ymin=-10, ymax=10)
        self.fig_5_ax.set_xlim(xmin=-1, xmax=5)
        self.fig_5_ax.set_ylim(ymin=-1, ymax=5)
        self.fig_5_ax.set_xlabel('Oy')
        self.fig_5_ax.set_ylabel('Ox')
        self.fig_2_ax.set_xlabel('Degree ')
        self.fig_2_ax.set_ylabel('Time (s)')
        self.fig_2_ax.grid()
        self.fig_2_ax.set_title('Roll', fontsize = 12)
        self.fig_3_ax.grid()
        self.fig_3_ax.set_title('Pitch', fontsize = 12)
        self.fig_4_ax.grid()
        self.fig_4_ax.set_title('Yaw', fontsize = 12)
        self.fig_5_ax.grid()
        self.fig_ax.grid()
        self.line_, = self.fig_ax.plot(self.xs, self.ys, lw=1, color='blue')
        self.line_p_, = self.fig_2_ax.plot(self.xs, self.ys, lw=1, color='blue')
        self.line_p2_p, = self.fig_3_ax.plot(self.xs, self.ysp, lw=1, color='blue')
        self.line_p3_p, = self.fig_4_ax.plot(self.xs, self.ysw, lw=1, color='blue')
        self.setpoint_l, = self.fig_ax.plot(self.xs, self.setpoint_, lw=1, color='r')
        self.setpoint_p_l, = self.fig_2_ax.plot(self.xs, self.setpoint_p_, lw=1, color='r')
        self.setpoint_p_l_2, = self.fig_3_ax.plot(self.xs, self.setpoint_p_2, lw=1, color='r')
        self.setpoint_p_l_3, = self.fig_4_ax.plot(self.xs, self.setpoint_p_3, lw=1, color='r')
        self.error_p_, = self.error_ax.plot(self.xs, self.errors, lw=1, color='b')
        self.localize, = self.fig_5_ax.plot(self.Px, self.Py, lw=2, color='blue', marker='.')
        self.neu = 0
        self.select = None
        self.textfile = None
        self.Clear.clicked.connect(self.clear)
        self.Pxx = None
        self.Pyy = None
#for Kp=2.95; Ki=0.085; Kd = 1.4;


#2.72,0.025,0.95
    def throttle_submit(self):
        if self.timer.isActive():
            transfer ="T"+str(self.Throttle.sliderPosition())+"\\n"
            print(transfer)
            self.seriallob.write(transfer.encode('utf-8'))
            self.seriallob.reset_output_buffer()
            # self.seriallob.reset_input_buffer()
        else:
            print("nothing")

    def throttle_change(self,value):
            self.Throt_val.setText(str(value))

    def update_xy(self, frames):
        try:
            self.Px.append(self.Pxx)
            self.Px = self.Px[-50:]
            self.Py.append(self.Pyy)
            self.Py = self.Py[-50:]
            self.localize.set_ydata(self.Py)
            self.localize.set_xdata(self.Px)
            return self.localize,
        except Exception as error:
            print(error)
    def update_roll(self, frames, ):
        try:
            self.ys.append(self.roll)
            self.ys = self.ys[-len(self.xs):]
            self.line_p_.set_ydata(self.ys)
            self.setpoint_.append(self.neu)
            self.setpoint_ = self.setpoint_[-len(self.xs):]
            self.setpoint_p_l.set_ydata(self.setpoint_)
            return [self.line_p_, self.setpoint_p_l,]
        except Exception as error:
            print(error)
            self.line_p_.set_ydata(self.ys)
            self.setpoint_l.set_ydata(self.ys)
            return [self.line_p_, self.setpoint_p_l, ]
    def clear(self):
        self.textfile = open('DataSave.txt', mode='w')
        self.textfile.truncate()
        self.textfile.close()
    def error_update(self, frames):
        try:
            error = self.neu - self.roll
            self.errors.append(error)
            self.errors = self.errors[-len(self.xs):]
            self.error_p_.set_ydata(self.errors)
            return [self.error_p_,]
        except Exception as error:
            print(error)
            self.error_p_.set_ydata(self.errors)
            return [self.error_p_,]

    def update_pitch(self, frames):
        try:
            self.ysp.append(self.pitch)
            self.ysp = self.ysp[-len(self.xs):]
            self.line_p2_p.set_ydata(self.ysp)
            self.setpoint_p_2.append(self.neu)
            self.setpoint_p_2 = self.setpoint_p_2[-len(self.xs):]
            self.setpoint_p_l_2.set_ydata(self.setpoint_p_2)
            return [self.line_p2_p, self.setpoint_p_l_2,]
        except Exception as error:
            print(error)
            self.line_p2_p.set_ydata(self.ysp)
            self.setpoint_p_l_2.set_ydata(self.setpoint_p_2)
            return [self.line_p2_p, self.setpoint_p_l_2, ]

    def update_yaw(self, frames):
        try:
            self.ysw.append(self.yaw)
            self.ysw = self.ysw[-len(self.xs):]
            self.line_p3_p.set_ydata(self.ysw)
            self.setpoint_p_3.append(self.neu)
            self.setpoint_p_3 = self.setpoint_p_3[-len(self.xs):]
            self.setpoint_p_l_3.set_ydata(self.setpoint_p_3)
            return [self.line_p3_p, self.setpoint_p_l_3,]
        except Exception as error:
            print(error)
            self.line_p3_p.set_ydata(self.ysw)
            self.setpoint_p_l_3.set_ydata(self.setpoint_p_3)
            return [self.line_p3_p, self.setpoint_p_l_3, ]

    def plotting(self):
        try:
            self.select = self.options.index(self.subPlot.currentText())
            if self.select == 0:
                self.pitch_canvas = FuncAnimation(self.fig_3, self.update_pitch, frames=1000, interval=1, blit=True)
                self.fig_3.show()
            elif self.select == 1:
                self.roll_canvas = FuncAnimation(self.fig, self.update_roll,frames=1000, interval=1, blit=True)
                self.fig_2.show()
            elif self.select == 2:
                self.yaw_canvas = FuncAnimation(self.fig_4, self.update_yaw, frames=1000, interval=1, blit=True)
                self.fig_4.show()
            elif self.select == 3:
                self.error_canvas = FuncAnimation(self.error, self.error_update, frames=1000, interval=1, blit=True)
                self.error.show()
            elif self.select == 4:
                self.xy_canvas = FuncAnimation(self.fig_5, self.update_xy, frames=1000, interval=1, blit=True)
                self.fig_5.show()
            else:
                myMessBox(txt="Nothing", title="Warning", icon="Warning")
        except Exception as error:
            myMessBox(txt=str(error), title="Warning", icon="Warning")

    def activated(self, index):
        self.data = self.comboBox.currentText()

    def capture(self):
        # file_filter = 'Images (*.png*.jpg*.jpeg);;All Files(*.*)'
        # name = QFileDialog.getSaveFileName(
        #     self,
        #     caption="Name file",
        #     directory='E:/UNIVERSITY/Final_Project/Images',
        #     filter=file_filter,
        # )
        # replace = name[0].replace("/","\\")
        # if name[0] !="":
        #     self.fig.savefig(replace)
        read_file = pd.read_csv(r'C:\Users\TUNG\Documents\FF_GUI_Drone\DataSave.txt')
        read_file.to_csv(r'D:\UNIVERSITY\Final_Project\Matlab\DataSave.csv')

    def toggle_ani(self):
        if self.is_animation_running:
            if self.select == 0:
                self.pitch_canvas.event_source.stop()
            elif self.select == 1:
                self.roll_canvas.event_source.stop()
            elif self.select == 2:
                self.yaw_canvas.event_source.stop()
            elif self.select == 3:
                self.error_canvas.event_source.stop()
            elif self.select == 4:
                self.xy_canvas.event_source.stop()
            self.PlotState.setText("Resume")
        else:
            if self.select == 0:
                self.pitch_canvas.event_source.start()
            elif self.select == 1:
                self.roll_canvas.event_source.start()
            elif self.select == 2:
                self.yaw_canvas.event_source.start()
            elif self.select == 3:
                self.error_canvas.event_source.start()
            elif self.select == 4:
                self.xy_canvas.event_source.start()
            self.PlotState.setText("Pause")
        self.is_animation_running = not self.is_animation_running

    def init(self):
        self.line_.set_ydata(self.ys)
        return self.line_,

    def disconnect(self):
        if self.seriallob.isOpen() == True:
            self.timer.stop()
            self.seriallob.flushOutput()
            self.seriallob.flushInput()
            self.seriallob.close()
            self.textfile.close()
        else:
            print("no")

    def submit(self):
        try:
            transfer = self.Command.text()
            transfer = str(transfer)
            if(transfer[:2] == "SE"):
                # self.setpoint_p_ = [int(transfer[2:])] * len(self.xs)
                self.neu = int(transfer[3:])
                print(transfer[3:])

            if self.seriallob.isOpen():
                # transfer = bytes(transfer, 'utf-8')
                # self.seriallob.write(transfer)
                transfer = bytes(transfer, encoding='utf-8')
                print(transfer)
                self.seriallob.write(transfer)
                # self.seriallob.reset_output_buffer()
                # self.seriallob.reset_input_buffer()
                # self.seriallob.reset_input_buffer()
                self.Command.clear()
                if not self.timer.isActive():
                    self.timer.start(1)
                else:
                    pass
            else:
                myMessBox(txt="submit failed", title="Warning", icon="Warning")
        except Exception as error:
            print(error)


    def connect(self):
        try:
            self.seriallob = serial.Serial(self.data, baudrate=115200, timeout=0.1)

            self.textfile = open('DataSave.txt', mode='w')
            # self.writer = csv.writer(self.textfile)
            # fields = ['Command', 'Command', 'Pitch', 'Roll', 'Yaw', 'Height', 'Distance 1', 'Distance 2', 'Px', 'Py',
            #           'OutPx', 'Outpy']
            # self.writer.writerow(fields)
        except Exception as error:
            myMessBox(txt=str(error), title="Warning", icon="Information")



    def current(self):
        print("zz")

    def actionexit(self):
        self.close()

    def showtime(self):
        try:
            dataz = self.seriallob.readline().decode('utf-8')
            self.indices = [i for i, x in enumerate(dataz) if x == ","]
            self.textfile.write(dataz)
            # self.writer.writerows(dataz)
            # command = dataz.find(",")
            # x_position = dataz.find(",", command+1)
            # self.y_position = dataz.find(",", x_position+1)
            # heading = dataz.find(",", self.y_position+1)
            # alitude = dataz.find(",", heading+1)
            self.pitch = float(dataz[self.indices[1]+1:self.indices[2]])
            self.roll = float(dataz[self.indices[0]+1:self.indices[1]])
            self.yaw = float(dataz[self.indices[2]+1:self.indices[3]])

            # self.Gyro.setText(dataz[self.indices[0]+1:self.indices[2]])
            # print(self.indices)
            self.Pxx = float(dataz[self.indices[7]+1:self.indices[8]])
            self.Pyy = float(dataz[self.indices[8]+1:self.indices[9]])

            # self.Motors.setText(dataz[alitude:])
            # self.Command_2.setText(dataz[:self.indices[0]])
        except Exception as error:
            pass



class Package(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("PackageDetails.ui", self)
        self.actionExit.triggered.connect(self.exit)
        self.treeView.setHeaderHidden(True)

        ref = db.reference("/User")
        result = ref.get()
        Keys = list(result.keys())
        zz = list(result.values())
        nope = result.values()
        z = list(zz[0].values())
        print(z)
        # for sth in range(len(z[0].keys())):
        #     print(sth)

        stop = zz.index('')

        treeModel = QStandardItemModel()
        rootnode = treeModel.invisibleRootItem()
        treeModel.setColumnCount(2)

        for keys in range(len(Keys)):
            keyss = StandardItem(Keys[keys])
            rootnode.appendRow(keyss)
            if keys < stop:
                xic = StandardItem(list(zz[keys].keys())[0])
                keyss.appendRow(xic)
                bro = list(zz[keys].values())
                for sth in range(len(bro[0].keys())):
                    comb = QStandardItem(list(bro[0].keys())[sth] + list(bro[0].values())[sth])
                    xic.appendRow(comb)
        self.treeView.setModel(treeModel)
        self.treeView.resizeColumnToContents(0)


    def exit(self):
        self.close()

    def mousePressEvent(self,e):
        print("ss")


class UserAdd(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("AddUser.ui", self)
        self.setWindowTitle("Add User Block")
        self.AddUserB.clicked.connect(self.pushconnect)

    def pushconnect(self):
        new_username = self.UserN_add.text()
        new_password = self.UserP_add.text()
        new_level = self.UserL_add.text()
        # new_username = "tung"
        # new_password = "12345"
        # new_level = "1"
        command1 = "SELECT UserName FROM LoginDB WHERE EXISTS (LoginDB.UserName = \''+new_usename+\' )"
        if new_username == "" and new_password == "":
            print("username and pass can't be empty")
        else:
            print(new_username)
            print(new_password)
            mycursor.execute("INSERT INTO LoginDB (UserName, Password, Level) VALUES (%s,%s,%s)",
                             (new_username, new_password, new_level))
            mydb.commit()



class UserRemove(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("RemoveUser.ui", self)
        self.setWindowTitle("Remove User Block")
        self.Psearch.clicked.connect(self.searchbutton)
        self.Premove.clicked.connect(self.removebutton)
        self.update()

    def searchbutton(self):
        usernameR = self.Username_R.text()
        mycursor.execute('SELECT Id,Password from LogInDB WHERE UserName =\''+usernameR+"\'")
        result = mycursor.fetchall()
        if result !=[]:
            self.Id_rev.setText(str(result[0][0]))
            self.Pass_rev.setText(result[0][1])
        else:
            print('zzz')

    def removebutton(self):
        acc_id = self.Id_rev.text()
        if self.Pass_rev.text() and self.Id_rev.text() != "":
            mycursor.execute('DELETE FROM LoginDB WHERE Id =\''+acc_id+"\'")
            mydb.commit()
            self.update()
        else:
            print("No UserName is found , Can't delete")


class UserEdit(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("EditUser.ui", self)
        self.setWindowTitle("Edit User Block")
        self.EditP.clicked.connect(self.editbutton)

    def editbutton(self):
        if self.UserE.text() and self.PassE.text() and self.LevelE.text() != "":
            usere = self.UserE.text()
            passe = self.PassE.text()
            levele = self.LevelE.text()
            mycursor.execute('SELECT UserName, Id FROM LoginDB WHERE UserName LIKE %s LIMIT 1', ("%" + usere + "%",))
            result = mycursor.fetchall()
            print(result[0][1])
            if result[0][0] == self.UserE.text():
                print("good")
                mycursor.execute('UPDATE LoginDB SET UserName=%s, Password=%s, Level=%s WHERE Id =%s',(usere,passe,levele,result[0][1]))
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Error Box")
            msg.setText("Edit Variables can't be blank")
            x = msg.exec()


class menu(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("MainScreen.ui", self)
        self.actionExit.triggered.connect(self.actionexit)
        self.actionUser_List.triggered.connect(self.actionuserlist)
        self.window1 = None
        self.dateTimeEdit.setDateTime(QtCore.QDateTime.currentDateTime())
        self.actionPackageDetails.triggered.connect(self.packagedetail)
        self.actionDroneView.triggered.connect(self.drone)
        self.timer = QTimer()
        self.timer.start(1000)
        self.timer.timeout.connect(self.timeupdate)
        self.ima = QPixmap("D:/UNIVERSITY/Final_Project/Images/1300,Kp=2.8,Kd=0.6,Ki=0.038.png")
        self.change = self.ima.scaled(450, 450,aspectRatioMode=QtCore.Qt.AspectRatioMode(1))
        self.label_9.setPixmap(self.change)
    def actionexit(self):
        self.close()

    def actionuserlist(self):
        try:
            self.window2 = userlist(self)
            self.window2.show()
        except:
            print("yep")

    def packagedetail(self):
        self.window3 = Package(self)
        self.window3.show()

    def drone(self):
        self.window4 = Droneview(self)
        self.window4.show()

    def timeupdate(self):
        self.dateTimeEdit.setDateTime(QtCore.QDateTime.currentDateTime())
        self.dateTimeEdit.setDisplayFormat("dd/MM/yyyy hh:mm:ss")


class userlist(QMainWindow):
    def __init__(self, parent=None):
        super(userlist, self).__init__(parent)
        uic.loadUi("UserList.ui", self)
        self.window2 = None
        self.tableUser.setColumnWidth(0, 200)
        self.tableUser.setColumnWidth(1, 200)
        self.tableUser.setColumnWidth(2, 200)
        self.tableUser.setColumnWidth(3, 200)
        # self.tableUser.setHorizontalHeaderLabels(["Id", "Username", "Password", "Level" ])
        self.loaddata()
        self.pushAddUser.clicked.connect(self.AddUserClick)
        self.pushRemoveUser.clicked.connect(self.RemoveUserClick)
        self.pushEditUser.clicked.connect(self.EditUserClick)
        self.action_it.triggered.connect(self.exitclick)
        self.window3 = UserAdd()

    def exitclick(self):
        self.close()

    def AddUserClick(self):
        try:
            self.window3 = UserAdd()
            self.window3.show()
        except:
            print("Bad")

    def RemoveUserClick(self):
        self.window4 = UserRemove()
        self.window4.show()

    def EditUserClick(self):
        self.window5 = UserEdit()
        self.window5.show()

    def loaddata(self):
        print(mydb)
        Q3 = "SELECT * FROM logindb"
        mycursor.execute(Q3)
        result = mycursor.fetchall()
        tablerow = 0
        columnc = len(result)
        #len result = 2 rows
        self.tableUser.setRowCount(columnc)

        # len result = 4 columns
        for row in result:
            self.tableUser.setItem(tablerow, 0, QTableWidgetItem(row[1]))
            self.tableUser.setItem(tablerow, 1, QTableWidgetItem(row[2]))
            self.tableUser.setItem(tablerow, 2, QTableWidgetItem(str(row[3])))
            tablerow = tablerow + 1


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.window = None
        uic.loadUi("LogIn.ui", self)
        self.LogInPush.clicked.connect(self.onclicked)
        self.checkBox.stateChanged.connect(self.clickbox)
        self.actionquit.triggered.connect(self.softexit)
        self.window1 = None
        State = False

    def softexit(self):
        self.close()

    def clickbox(self):
        state = self.checkBox.checkState()
        if state == Qt.CheckState.Checked:
            self.Password.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.Password.setEchoMode(QLineEdit.EchoMode.Password)


    def onclicked(self):
        try:
            user = self.Email.text()
            passw = self.Password.text()
            scanthrough(user, passw)
        except:
            print("ERROR")
            self.Password.clear()
        else:
            try:
                Q1 = 'SELECT * from LogInDB WHERE UserName = \''+user+"\'"
                mycursor.execute(Q1)
                result = mycursor.fetchone()
                if passw == result[2]:
                    print("OK")
                    self.window1 = menu()
                    self.window1.show()
                    self.window1.Userdis.setText(self.Email.text())
                    self.window1.LevelDis.setText(str(result[3]))
                else:
                    print("Wrong password or Username")
            except Exception as error:
                myMessBox(txt=str(error), title="Warning", icon="Warning")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Droneview()
    window.show()
    sys.exit(app.exec())

