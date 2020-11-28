# -*- coding:utf-8 -*-
from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton, QPlainTextEdit, QMessageBox
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from cap import *
from rasr import *
from faceapi import *
from ctypes import *
from wav2pcm import *
from audio_record import *
from tcp import *
import threading
import socket
import time
import re

pcm_file = 'C://Users//yuncai//Desktop//input.pcm'
wav_file = 'C://Users//yuncai//Desktop//input.wav'
audio_record_file = 'C://Users//yuncai//Desktop//input.wav'
runflag = 0

resource = [""]
recv = ["init"]


def tcpClient():
    global recv
    global resource

    MaxBytes = 8096 * 8096
    host = '127.0.0.1'
    port = 3000

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(30)
    client.connect((host, port))
    while True:
        inputData = str(resource)  # 等待输入数据
        client.send(inputData.encode())

        recvData = client.recv(MaxBytes)

        localTime = time.asctime(time.localtime(time.time()))
        print(localTime, ' 接收到数据字节数:', len(recvData))

        print(recvData.decode())

        recv = recvData.decode()


class Stats:
    def __init__(self):
        # 从文件中加载UI定义
        # 从 UI 定义中动态 创建一个相应的窗口对象
        # 注意：里面的控件对象也成为窗口对象的属性了
        # 比如 self.ui.button , self.ui.textEdit
        global resource
        global recv

        self.flag = '识别成功'
        self.text = ''

        self.dataflag = 0
        self.baseflag = 0

        self.ui = QUiLoader().load('main.ui')
        self.capture_file = 'C://Users//yuncai//Desktop//cap'
        self.img_file = 'C://Users//yuncai//Desktop//ai.jpg'

        self.ui.compareButton.clicked.connect(self.compareface)
        self.ui.audioButton.clicked.connect(self.audiocmd)

        self.ui.startButton.clicked.connect(self.compareface)
        self.ui.exitButton.clicked.connect(self.exit)
        self.ui.connectButton.clicked.connect(self.connect)

        self.ui.singleRunButton.clicked.connect(self.singlerun)
        self.ui.continueRunButton.clicked.connect(self.continuerun)

        self.ui.baseButton.clicked.connect(self.changeto_base)
        self.ui.dataButton.clicked.connect(self.changeto_data)

        self.ui.searchButton.clicked.connect(self.searchdata)
        self.ui.addButton.clicked.connect(self.adddata)
        self.ui.delButton.clicked.connect(self.deldata)

    def exit(self):
        exit()

    def connect(self):
        thread_tcp = threading.Thread(target=tcpClient)
        thread_tcp.start()

    def audiocmd(self):
        if self.flag == "识别成功":
            self.ui.PlainText.appendPlainText("语音识别")
            self.text = audio2text(audio_record_file, 5)[0]
            self.ui.textBrowser.append(self.text)
            if self.text == "退出系统":
                exit()
            else:
                self.ui.textBrowser.clear()
                self.ui.textBrowser.append("未识别到指令")
        else:
            self.ui.PlainText.appendPlainText("请先认证")

    def compareface(self):

        self.flag = face_compare(self.capture_file)
        self.ui.PlainText.appendPlainText(self.flag)

    def singlerun(self):
        global resource
        global recv
        if self.flag == "识别成功":
            self.ui.PlainText.appendPlainText("单次运行")
            result = re.match('detected', str(recv))
            if result.group() == 'detected':
                fapi = face(userid, password, region)
                resource = fapi.modelarts_api(self.img_file)
                self.ui.PlainText.appendPlainText(resource)

                self.ui.PlainText.appendPlainText("运行完成")
            else:
                self.ui.PlainText.appendPlainText("未检测到物体")

        else:
            self.ui.PlainText.appendPlainText("请先认证")

    def continuerun(self):
        global resource
        global recv
        if self.flag == "识别成功":
            self.ui.PlainText.appendPlainText("连续运行")

            while True:
                result = re.match('detected', str(recv))
                if result.group() == 'detected':
                    fapi = face(userid, password, region)
                    resource = fapi.modelarts_api(self.img_file)
                    self.ui.PlainText.appendPlainText(resource)

                    self.ui.PlainText.appendPlainText("运行完成")
                result = re.match('q', str(recv))
                if result.group() == 'q':
                    break
                else:
                    self.ui.PlainText.appendPlainText("未检测到物体")

        else:
            self.ui.PlainText.appendPlainText("请先认证")

    def changeto_data(self):
        if self.flag == "识别成功":
            self.ui.PlainText.appendPlainText("人脸数据操作")
            self.dataflag = 1
            self.baseflag = 0
        else:
            self.ui.PlainText.appendPlainText("请先认证")

    def changeto_base(self):
        if self.flag == "识别成功":
            self.ui.PlainText.appendPlainText("人脸库操作")
            self.dataflag = 0
            self.baseflag = 1
        else:
            self.ui.PlainText.appendPlainText("请先认证")

    def searchdata(self):
        if self.flag == "识别成功":
            self.ui.PlainText.appendPlainText("搜索数据")
            fapi = face(userid, password, region)
            if self.dataflag:
                self.ui.textBrowser.clear()
                self.ui.textBrowser.append(fapi.search_face_data(0, 10))
                self.ui.PlainText.appendPlainText("人脸数据查询完成")
            else:
                self.ui.textBrowser.clear()
                self.ui.textBrowser.append(fapi.search_face_database())
                self.ui.PlainText.appendPlainText("人脸库数据查询完成")
        else:
            self.ui.PlainText.appendPlainText("请先认证/输入信息")

    def adddata(self):
        if self.flag == "识别成功" and self.ui.lineEdit.text():
            self.ui.PlainText.appendPlainText("添加数据")
            fapi = face(userid, password, region)

            if self.dataflag:
                self.ui.textBrowser.clear()
                self.ui.textBrowser.append(fapi.add_face_data(self.ui.lineEdit.text()))
                self.ui.PlainText.appendPlainText("人脸数据添加完成")
            else:
                self.ui.textBrowser.clear()
                self.ui.textBrowser.append(fapi.new_face_database(self.ui.lineEdit.text()))
                self.ui.PlainText.appendPlainText("人脸库添加完成")
        else:
            self.ui.PlainText.appendPlainText("请先认证/输入信息")

    def deldata(self):
        if self.flag == "识别成功" and self.ui.lineEdit.text():
            self.ui.PlainText.appendPlainText("删除数据")
            fapi = face(userid, password, region)

            if self.dataflag:
                self.ui.textBrowser.clear()
                self.ui.textBrowser.append(fapi.delete_face_data(self.ui.lineEdit.text()))
                self.ui.PlainText.appendPlainText("人脸数据删除完成")
            else:
                self.ui.textBrowser.clear()
                self.ui.textBrowser.append(fapi.delete_face_database(self.ui.lineEdit.text()))
                self.ui.PlainText.appendPlainText("人脸库删除完成")
        else:
            self.ui.PlainText.appendPlainText("请先认证/输入信息")
