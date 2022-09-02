import sys
import Model
import win32api
import os
import shutil
import queue
import threading
import numpy as np
from PyQt5.Qt import *
#QUrl
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtMultimedia import QMediaContent
from PyQt5.QtGui import QPalette, QBrush, QPixmap, QColor
from PyQt5 import QtCore, QtWidgets, QtMultimedia, QtMultimediaWidgets
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QDesktopWidget, QLabel, QLineEdit, QComboBox, \
    QColorDialog, QFileDialog, QMessageBox


class PatternDisplayWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):

        super(PatternDisplayWindow, self).__init__(parent)
        self.setWindowTitle("Pattern player")
        self.setGeometry(0, 0, 2560, 1400)
        self.pattern_player = QtMultimedia.QMediaPlayer(None, QtMultimedia.QMediaPlayer.VideoSurface)
        video_widget = QtMultimediaWidgets.QVideoWidget()

        container = QtWidgets.QWidget()
        layer = QtWidgets.QVBoxLayout(container)
        layer.setContentsMargins(0, 0, 0, 0)
        layer.addWidget(video_widget)

        self.play_button = QtWidgets.QPushButton()
        self.play_button.setEnabled(True)
        self.play_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
        self.play_button.clicked.connect(self.play)

        self.position_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self.setPosition)

        sublayer = QtWidgets.QHBoxLayout()
        sublayer.setContentsMargins(0, 0, 0, 0)
        sublayer.addWidget(self.play_button)
        sublayer.addWidget(self.position_slider)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(container)
        layout.addLayout(sublayer)

        wid = QtWidgets.QWidget(self)
        self.setCentralWidget(wid)
        wid.setLayout(layout)

        self.pattern_player.setVideoOutput(video_widget)
        self.pattern_player.stateChanged.connect(self.media_state_control)
        self.pattern_player.positionChanged.connect(self.position_control)
        self.pattern_player.durationChanged.connect(self.duration_control)

    def play(self):
        if self.pattern_player.state() == QtMultimedia.QMediaPlayer.PlayingState:
            self.pattern_player.pause()
        else:
            self.pattern_player.play()

    def media_state_control(self, state):
        if self.pattern_player.state() == QtMultimedia.QMediaPlayer.PlayingState:
            self.play_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPause))
        else:
            self.play_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))

    def position_control(self, position):
        self.position_slider.setValue(position)

    def duration_control(self, duration):
        self.position_slider.setRange(0, duration)

    def setPosition(self, position):
        self.pattern_player.setPosition(position)


class MainQtWindow(QWidget):

    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT):
        super().__init__()

        self.testInterface = PatternDisplayWindow()
        self.combox_content = ['Choose a patient', 'Yang Yu', 'AA CC', 'BB BB']
        setting_data = self.load_setting()

        self.current_patient = []
        self.current_test = []
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT

        self.frame_rate_line_content = str(setting_data[0])
        self.NUMBER_OF_SPOTS_line_content = str(setting_data[1])
        self.test_duration_line_content = str(setting_data[4])
        color_in_txt0 = str(setting_data[2]).split(',')
        color_in_txt1 = str(setting_data[3]).split(',')
        self.defult_spot_color_off = [int(color_in_txt0[0]), int(color_in_txt0[1]), int(color_in_txt0[2])]
        self.defult_spot_color_on = [int(color_in_txt1[0]), int(color_in_txt1[1]), int(color_in_txt1[2])]
        self.spot_size_content = str(setting_data[5])

        #Included New features
        self.upload_paths = []
        self.patient_details =[]
        self.flash_interval_content = str(setting_data[6])
        self.dir_path = os.getcwd()


        self.initUI()

    def initUI(self):
        """Initialize all the UI and put them in a certain place"""

        """This attribute controls the size of the software"""
        self.interface_control_index = 0.8

        """  Start of the key buttons: history_button build_a_new_test_button quit_button"""
        # Home Button
        home_button = QPushButton('Home', self)
        home_button.setStyleSheet("QPushButton{color:white}"
                                     "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      "QPushButton{background-color:rgba(51, 51, 51, 0)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(153 * self.interface_control_index)) + "px}")
        home_button.setMinimumHeight(int(80 * self.interface_control_index))
        home_button.move(0, int(250 * self.interface_control_index))
        home_button.clicked.connect(self.home_on_click)
        self.home_button = home_button


        # History Button
        history_button = QPushButton('History', self)
        history_button.setStyleSheet("QPushButton{color:white}"
                                     "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      # "QPushButton{background-color:rgba(51, 51, 51, 255)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(147 * self.interface_control_index)) + "px}")
        history_button.setMinimumHeight(int(80 * self.interface_control_index))
        history_button.move(0, int(330 * self.interface_control_index))
        history_button.clicked.connect(self.history_on_click)
        self.history_button = history_button

        # Build a new Test Button
        build_a_new_test_button = QPushButton('Build a new test', self)

        build_a_new_test_button.setStyleSheet("QPushButton{color:white}"
                                              "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      # "QPushButton{background-color:rgba(51, 51, 51, 255)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(83 * self.interface_control_index)) + "px}")
        build_a_new_test_button.setMinimumHeight(int(80 * self.interface_control_index))
        build_a_new_test_button.move(0, int(410 * self.interface_control_index))
        build_a_new_test_button.clicked.connect(self.build_test_on_click)
        self.build_a_new_test_button = build_a_new_test_button

        # Build a new Calibration Button
        build_a_calibrate_button = QPushButton('Calibration Test', self)

        build_a_calibrate_button.setStyleSheet("QPushButton{color:white}"
                                               "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      # "QPushButton{background-color:rgba(51, 51, 51, 255)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(83 * self.interface_control_index)) + "px}")
        build_a_calibrate_button.setMinimumHeight(int(80 * self.interface_control_index))
        build_a_calibrate_button.move(0, int(570 * self.interface_control_index))
        build_a_calibrate_button.clicked.connect(self.build_calibrate_on_click)
        self.build_a_calibrate_button = build_a_calibrate_button

        # Build a new analyse Button
        analyse_test_button = QPushButton('Analyse EEG data', self)

        analyse_test_button.setStyleSheet("QPushButton{color:white}"
                                               "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                               # "QPushButton{background-color:rgba(51, 51, 51, 255)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(83 * self.interface_control_index)) + "px}")
        analyse_test_button.setMinimumHeight(int(80 * self.interface_control_index))
        analyse_test_button.move(0, int(650 * self.interface_control_index))
        analyse_test_button.clicked.connect(self.start_analyse_on_click)
        self.analyse_test_button = analyse_test_button

        # Start a Test Button
        start_a_test_button = QPushButton('Start a test', self)

        start_a_test_button.setStyleSheet("QPushButton{color:white}"
                                          "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      "QPushButton{background-color:rgba(51, 51, 51, 0)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(115 * self.interface_control_index)) + "px}")
        start_a_test_button.setMinimumHeight(int(80 * self.interface_control_index))
        start_a_test_button.move(0, int(490 * self.interface_control_index))
        start_a_test_button.clicked.connect(self.start_test_on_click)
        self.start_a_test_button = start_a_test_button

        # Quit Button.
        quit_button = QPushButton('Quit', self)

        quit_button.setStyleSheet("QPushButton{color:white}"
                                  "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      "QPushButton{background-color:rgba(51, 51, 51, 0)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{border-radius:" + str(
            int(60 * self.interface_control_index)) + "px}"
                                                      "QPushButton{padding:0px " + str(
            int(168 * self.interface_control_index)) + "px}")
        quit_button.setMinimumHeight(int(80 * self.interface_control_index))
        quit_button.move(0, int(720 * self.interface_control_index))
        quit_button.clicked.connect(QCoreApplication.quit)
        self.quit_button = quit_button
        """  End of the key buttons  """

        """ - Start of the welcome page - """

        # Label Retina Function Test
        retina_function_test_label = QLabel('Retina Function Test', self)
        retina_function_test_label.setStyleSheet("QLabel{color:white}"
                                                 "QLabel{font-size:" + str(
            int(100 * self.interface_control_index)) + "px;color:rgb(215,215,215);}")
        retina_function_test_label.move(int(560 * self.interface_control_index),
                                        int(340 * self.interface_control_index))
        self.retina_function_test_label = retina_function_test_label

        # Label Welcome
        please_select_a_function_label = QLabel('Please select a function from the left', self)
        please_select_a_function_label.setStyleSheet("QLabel{color:white}"
                                    "QLabel{font-size:" + str(int(55 * self.interface_control_index)) + "px;color:rgb(127,127,127);}")
        please_select_a_function_label.move(int(565 * self.interface_control_index), int(450 * self.interface_control_index))
        self.please_select_a_function_label = please_select_a_function_label

        """ - End of the welcome page - """

        """  -- Start of the history page --  """
        history_pixmap = QPixmap('Images/pyqt5/History.png')

        # history_label1
        history_label1 = QLabel(self)
        history_label1.setPixmap(history_pixmap)
        history_label1.resize(int(1139 * self.interface_control_index), int(243 * self.interface_control_index))
        history_label1.move(int(430 * self.interface_control_index), int(42 * self.interface_control_index))
        history_label1.setScaledContents(True)

        # history_label2
        history_label2 = QLabel(self)
        history_label2.setPixmap(history_pixmap)
        history_label2.resize(int(1139 * self.interface_control_index), int(243 * self.interface_control_index))
        history_label2.move(int(430 * self.interface_control_index), int(328 * self.interface_control_index))
        history_label2.setScaledContents(True)

        # history_label3
        history_label3 = QLabel(self)
        history_label3.setPixmap(history_pixmap)
        history_label3.resize(int(1139 * self.interface_control_index), int(243 * self.interface_control_index))
        history_label3.move(int(430 * self.interface_control_index), int(613 * self.interface_control_index))
        history_label3.setScaledContents(True)

        # info label1
        info_label1 = QLabel('AA 12 34 56 A', self)
        info_label1.setStyleSheet(
            "QLabel{font-size:" + str(int(35 * self.interface_control_index)) + "px; color:rgb(127,127,127);}")
        info_label1.move(int(467 * self.interface_control_index), int(65 * self.interface_control_index))
        info_label1.setVisible(True)

        # info label2
        info_label2 = QLabel('AA 12 34 56 A', self)
        info_label2.setStyleSheet(
            "QLabel{font-size:" + str(int(35 * self.interface_control_index)) + "px; color:rgb(127,127,127);}")
        info_label2.move(int(467 * self.interface_control_index), int(351 * self.interface_control_index))
        info_label2.setVisible(True)

        # info label3
        info_label3 = QLabel('AA 12 34 56 A', self)
        info_label3.setStyleSheet(
            "QLabel{font-size:" + str(int(35 * self.interface_control_index)) + "px; color:rgb(127,127,127);}")
        info_label3.move(int(467 * self.interface_control_index), (636 * self.interface_control_index))
        info_label3.setVisible(True)

        # info label4
        info_label4 = QLabel('Yang Yu', self)
        info_label4.setStyleSheet(
            "QLabel{font-size:" + str(int(55 * self.interface_control_index)) + "px;color:rgb(127,127,127);}")
        info_label4.move(int(900 * self.interface_control_index), int(130 * self.interface_control_index))
        info_label4.setVisible(True)

        # info label5
        info_label5 = QLabel('Yang Yu', self)
        info_label5.setStyleSheet(
            "QLabel{font-size:" + str(int(55 * self.interface_control_index)) + "px;color:rgb(127,127,127);}")
        info_label5.move(int(900 * self.interface_control_index), int(416 * self.interface_control_index))
        info_label5.setVisible(True)

        # info label6
        info_label6 = QLabel('Yang Yu', self)
        info_label6.setStyleSheet(
            "QLabel{font-size:" + str(int(55 * self.interface_control_index)) + "px;color:rgb(127,127,127);}")
        info_label6.move(int(900 * self.interface_control_index), int(701 * self.interface_control_index))
        info_label6.setVisible(True)

        self.history_label1 = history_label1
        self.history_label2 = history_label2
        self.history_label3 = history_label3
        self.info_label1 = info_label1
        self.info_label2 = info_label2
        self.info_label3 = info_label3
        self.info_label4 = info_label4
        self.info_label5 = info_label5
        self.info_label6 = info_label6
        """  -- End of the history page --  """

        """ --- Start of the start test page ---"""
        # for_current_patient_button
        for_current_patient_button = QPushButton('For an existing patient', self)
        for_current_patient_button.setStyleSheet("QPushButton{color:white}"
                                                 "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(85,85,85);}"
                                                      "QPushButton:hover{color:rgb(50,50,50)}"
                                                      "QPushButton{background-color:rgb(215, 215, 215)}"
                                                      "QPushButton{border:" + str(
            int(15 * self.interface_control_index)) + "px}"
                                                      "QPushButton{border-radius:" + str(
            int(7 * self.interface_control_index)) + "px}"
                                                     "QPushButton{padding:0px " + str(
            int(220 * self.interface_control_index)) + "px}")
        for_current_patient_button.setMinimumHeight(int(90 * self.interface_control_index))
        for_current_patient_button.move(int(585 * self.interface_control_index),
                                        int(270 * self.interface_control_index))
        for_current_patient_button.clicked.connect(self.to_choose_current_patient_page)
        self.for_current_patient_button = for_current_patient_button

        # for_new_patient_button
        for_new_patient_button = QPushButton('For a new patient', self)
        for_new_patient_button.setStyleSheet("QPushButton{color:white}"
                                             "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(85,85,85);}"
                                                      "QPushButton:hover{color:rgb(50,50,50)}"
                                                      "QPushButton{background-color:rgb(215, 215, 215)}"
                                                      "QPushButton{border:" + str(
            int(15 * self.interface_control_index)) + "px}"
                                                      "QPushButton{border-radius:" + str(
            int(7 * self.interface_control_index)) + "px}"
                                                     "QPushButton{padding:0px " + str(
            int(256 * self.interface_control_index)) + "px}")
        for_new_patient_button.setMinimumHeight(int(90 * self.interface_control_index))
        for_new_patient_button.move(int(585 * self.interface_control_index), int(550 * self.interface_control_index))
        for_new_patient_button.clicked.connect(self.to_create_patient_page)
        self.for_new_patient_button = for_new_patient_button
        """ --- End of the start test page ---"""

        """ ---- Start of the choose_current_patient_page ---- """
        notes_of_existing_patient_label = QLabel('Test for an existing patient', self)
        notes_of_existing_patient_label.setStyleSheet(
            "QLabel{font-size:" + str(int(76 * self.interface_control_index)) + "px;color:rgb(215,215,215);}")
        notes_of_existing_patient_label.move(int(576 * self.interface_control_index),
                                             int(220 * self.interface_control_index))
        self.notes_of_existing_patient_label = notes_of_existing_patient_label

        choose_a_patient_label = QLabel('Choose a patient', self)
        choose_a_patient_label.setStyleSheet(
            "QLabel{font-size:" + str(int(35 * self.interface_control_index)) + "px;color:rgb(215,215,215);}")
        choose_a_patient_label.move(int(580 * self.interface_control_index), int(430 * self.interface_control_index))
        self.choose_a_patient_label = choose_a_patient_label

        choose_patient_combobox = QComboBox(self)
        choose_patient_combobox.move(int(875 * self.interface_control_index), int(430 * self.interface_control_index))
        choose_patient_combobox.addItems(self.combox_content)
        choose_patient_combobox.setStyleSheet("QComboBox{color:rgb(200,200,200);}"
                                              "QComboBox{background-color:rgb(80,80,80);}"
                                              "QComboBox{border-radius:" + str(
            int(3 * self.interface_control_index)) + "px}"
                                                     "QComboBox{font-size:" + str(
            int(25 * self.interface_control_index)) + "px;}")
        choose_patient_combobox.setFixedHeight(int(44 * self.interface_control_index))
        choose_patient_combobox.setFixedWidth(int(525 * self.interface_control_index))
        self.choose_patient_combobox = choose_patient_combobox

        back_button_1 = QPushButton('Back', self)
        back_button_1.setStyleSheet("QPushButton{color:white}"
                                        "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(85,85,85);}"
                                                      "QPushButton:hover{color:rgb(50,50,50)}"
                                                      "QPushButton{background-color:rgb(215, 215, 215)}"
                                                      "QPushButton{border:" + str(
            int(15 * self.interface_control_index)) + "px}"
                                                      "QPushButton{border-radius:" + str(
            int(7 * self.interface_control_index)) + "px}"
                                                     "QPushButton{padding:0px " + str(
            int(146 * self.interface_control_index)) + "px}")
        back_button_1.setMinimumHeight(int(75 * self.interface_control_index))
        back_button_1.move(int(580 * self.interface_control_index), int(600 * self.interface_control_index))
        back_button_1.clicked.connect(self.back_on_click)
        self.back_button_1 = back_button_1

        continue_button_1 = QPushButton('Continue', self)
        continue_button_1.setStyleSheet("QPushButton{color:white}"
                                        "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(85,85,85);}"
                                                      "QPushButton:hover{color:rgb(50,50,50)}"
                                                      "QPushButton{background-color:rgb(215, 215, 215)}"
                                                      "QPushButton{border:" + str(
            int(15 * self.interface_control_index)) + "px}"
                                                      "QPushButton{border-radius:" + str(
            int(7 * self.interface_control_index)) + "px}"
                                                     "QPushButton{padding:0px " + str(
            int(115 * self.interface_control_index)) + "px}")
        continue_button_1.setMinimumHeight(int(75 * self.interface_control_index))
        continue_button_1.move(int(1032 * self.interface_control_index), int(600 * self.interface_control_index))
        continue_button_1.clicked.connect(self.to_choose_a_pattern)
        self.continue_button_1 = continue_button_1

        """ ---- End of the choose_current_patient_page ---- """

        """ ----- Start of the create_patient_page ----- """
        notes_of_creating_patient_label = QLabel('Test for a new patient', self)
        notes_of_creating_patient_label.setStyleSheet(
            "QLabel{font-size:" + str(int(89 * self.interface_control_index)) + "px;color:rgb(215,215,215);}")
        notes_of_creating_patient_label.move(int(580 * self.interface_control_index),
                                             int(180 * self.interface_control_index))
        self.notes_of_creating_patient_label = notes_of_creating_patient_label

        # full name
        full_name_label = QLabel('Full name', self)
        full_name_label.setStyleSheet(
            "QLabel{font-size:" + str(int(30 * self.interface_control_index)) + "px;color:rgb(215,215,215);}")
        full_name_label.move(int(580 * self.interface_control_index), int(360 * self.interface_control_index))
        self.full_name_label = full_name_label

        full_name_line = QLineEdit(self)
        full_name_line.move(int(717 * self.interface_control_index), int(366 * self.interface_control_index))
        full_name_line.setStyleSheet("QLineEdit{color:rgb(200,200,200);}"
                                     "QLineEdit{background-color:rgb(70,70,70);}"
                                     "QLineEdit{border:" + str(int(5 * self.interface_control_index)) + "px}"
                                                                                                        "QLineEdit{border-radius:" + str(
            int(7 * self.interface_control_index)) + "px}"
                                                     "QLineEdit{font-size:" + str(
            int(25 * self.interface_control_index)) + "px;}")
        full_name_line.setFixedHeight(int(30 * self.interface_control_index))
        full_name_line.setFixedWidth(int(268 * self.interface_control_index))
        self.full_name_line = full_name_line

        # birthday
        birthdate_label = QLabel('Birthdate', self)
        birthdate_label.setStyleSheet(
            "QLabel{font-size:" + str(int(30 * self.interface_control_index)) + "px;color:rgb(215,215,215);}")
        birthdate_label.move(int(997 * self.interface_control_index), int(360 * self.interface_control_index))
        self.birthdate_label = birthdate_label

        birthdate_line = QLineEdit(self)
        birthdate_line.move(int(1120 * self.interface_control_index), int(366 * self.interface_control_index))
        birthdate_line.setStyleSheet("QLineEdit{color:rgb(200,200,200);}"
                                     "QLineEdit{background-color:rgb(70,70,70);}"
                                     "QLineEdit{border:" + str(int(5 * self.interface_control_index)) + "px}"
                                                                                                        "QLineEdit{border-radius:" + str(
            int(7 * self.interface_control_index)) + "px}"
                                                     "QLineEdit{font-size:" + str(
            int(25 * self.interface_control_index)) + "px;}")
        birthdate_line.setFixedHeight(int(30 * self.interface_control_index))
        birthdate_line.setFixedWidth(int(262 * self.interface_control_index))
        self.birthdate_line = birthdate_line

        # national insurance number
        NIN_label = QLabel('National insurance number', self)
        NIN_label.setStyleSheet(
            "QLabel{font-size:" + str(int(30 * self.interface_control_index)) + "px;color:rgb(215,215,215);}")
        NIN_label.move(int(580 * self.interface_control_index), int(470 * self.interface_control_index))
        self.NIN_label = NIN_label

        NIN_line = QLineEdit(self)
        NIN_line.move(int(936 * self.interface_control_index), int(476 * self.interface_control_index))
        NIN_line.setStyleSheet("QLineEdit{color:rgb(200,200,200);}"
                               "QLineEdit{background-color:rgb(70,70,70);}"
                               "QLineEdit{border:" + str(int(5 * self.interface_control_index)) + "px}"
                                                                                                  "QLineEdit{border-radius:" + str(
            int(7 * self.interface_control_index)) + "px}"
                                                     "QLineEdit{font-size:" + str(
            int(25 * self.interface_control_index)) + "px;}")
        NIN_line.setFixedHeight(int(30 * self.interface_control_index))
        NIN_line.setFixedWidth(int(445 * self.interface_control_index))
        self.NIN_line = NIN_line

        back_button_2 = QPushButton('Back', self)
        back_button_2.setStyleSheet("QPushButton{color:white}"
                                    "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(85,85,85);}"
                                                      "QPushButton:hover{color:rgb(50,50,50)}"
                                                      "QPushButton{background-color:rgb(215, 215, 215)}"
                                                      "QPushButton{border:" + str(
            int(15 * self.interface_control_index)) + "px}"
                                                      "QPushButton{border-radius:" + str(
            int(7 * self.interface_control_index)) + "px}"
                                                     "QPushButton{padding:0px " + str(
            int(146 * self.interface_control_index)) + "px}")
        back_button_2.setMinimumHeight(int(75 * self.interface_control_index))
        back_button_2.move(int(580 * self.interface_control_index), int(600 * self.interface_control_index))
        back_button_2.clicked.connect(self.back_on_click)
        self.back_button_2 = back_button_2


        # continue_button_2
        continue_button_2 = QPushButton('Continue', self)
        continue_button_2.setStyleSheet("QPushButton{color:white}"
                                        "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(85,85,85);}"
                                                      "QPushButton:hover{color:rgb(50,50,50)}"
                                                      "QPushButton{background-color:rgb(215, 215, 215)}"
                                                      "QPushButton{border:" + str(
            int(15 * self.interface_control_index)) + "px}"
                                                      "QPushButton{border-radius:" + str(
            int(7 * self.interface_control_index)) + "px}"
                                                     "QPushButton{padding:0px " + str(
            int(115 * self.interface_control_index)) + "px}")
        continue_button_2.setMinimumHeight(int(75 * self.interface_control_index))
        continue_button_2.move(int(1013 * self.interface_control_index), int(600 * self.interface_control_index))
        continue_button_2.clicked.connect(self.to_choose_a_pattern)
        self.continue_button_2 = continue_button_2
        """ ----- End of the create_patient_page ----- """

        """ ----- Start of EEG data analysis page ----- """
        # eeg_upload_1 button
        eeg_upload_1 = QPushButton('Non-Headset', self)
        eeg_upload_1.setStyleSheet("QPushButton{color:white}"
                                        "QPushButton{font-size:" + str(
            int(30 * self.interface_control_index)) + "px;color:rgb(85,85,85);}"
                                                      "QPushButton:hover{color:rgb(50,50,50)}"
                                                      "QPushButton{background-color:rgb(215, 215, 215)}"
                                                      "QPushButton{border:" + str(
            int(15 * self.interface_control_index)) + "px}"
                                                      "QPushButton{border-radius:" + str(
            int(5 * self.interface_control_index)) + "px}"
                                                     "QPushButton{padding:0px " + str(
            int(50 * self.interface_control_index)) + "px}")
        eeg_upload_1.setMinimumHeight(int(60 * self.interface_control_index))
        eeg_upload_1.move(int(400 * self.interface_control_index), int(550 * self.interface_control_index))
        eeg_upload_1.clicked.connect(self.to_set_path_data)
        self.eeg_upload_1 = eeg_upload_1

        # eeg_upload_2 button
        eeg_upload_2 = QPushButton('Only-Headset', self)
        eeg_upload_2.setStyleSheet("QPushButton{color:white}"
                                        "QPushButton{font-size:" + str(
            int(30 * self.interface_control_index)) + "px;color:rgb(85,85,85);}"
                                                      "QPushButton:hover{color:rgb(50,50,50)}"
                                                      "QPushButton{background-color:rgb(215, 215, 215)}"
                                                      "QPushButton{border:" + str(
            int(15 * self.interface_control_index)) + "px}"
                                                      "QPushButton{border-radius:" + str(
            int(5 * self.interface_control_index)) + "px}"
                                                     "QPushButton{padding:0px " + str(
            int(50 * self.interface_control_index)) + "px}")
        eeg_upload_2.setMinimumHeight(int(60 * self.interface_control_index))
        eeg_upload_2.move(int(700 * self.interface_control_index), int(550 * self.interface_control_index))
        eeg_upload_2.clicked.connect(self.to_set_path_data)
        self.eeg_upload_2 = eeg_upload_2

        # eeg_upload_3 button
        eeg_upload_3 = QPushButton('Headset-Test', self)
        eeg_upload_3.setStyleSheet("QPushButton{color:white}"
                                        "QPushButton{font-size:" + str(
            int(30 * self.interface_control_index)) + "px;color:rgb(85,85,85);}"
                                                      "QPushButton:hover{color:rgb(50,50,50)}"
                                                      "QPushButton{background-color:rgb(215, 215, 215)}"
                                                      "QPushButton{border:" + str(
            int(15 * self.interface_control_index)) + "px}"
                                                      "QPushButton{border-radius:" + str(
            int(5 * self.interface_control_index)) + "px}"
                                                     "QPushButton{padding:0px " + str(
            int(50 * self.interface_control_index)) + "px}")
        eeg_upload_3.setMinimumHeight(int(60 * self.interface_control_index))
        eeg_upload_3.move(int(1000 * self.interface_control_index), int(550 * self.interface_control_index))
        eeg_upload_3.clicked.connect(self.to_set_path_data)
        self.eeg_upload_3 = eeg_upload_3

        # calibration_upload button
        calibration_upload = QPushButton('Calibration File', self)
        calibration_upload.setStyleSheet("QPushButton{color:white}"
                                        "QPushButton{font-size:" + str(
            int(30 * self.interface_control_index)) + "px;color:rgb(85,85,85);}"
                                                      "QPushButton:hover{color:rgb(50,50,50)}"
                                                      "QPushButton{background-color:rgb(215, 215, 215)}"
                                                      "QPushButton{border:" + str(
            int(15 * self.interface_control_index)) + "px}"
                                                      "QPushButton{border-radius:" + str(
            int(5 * self.interface_control_index)) + "px}"
                                                     "QPushButton{padding:0px " + str(
            int(50 * self.interface_control_index)) + "px}")
        calibration_upload.setMinimumHeight(int(60 * self.interface_control_index))
        calibration_upload.move(int(1300 * self.interface_control_index), int(550 * self.interface_control_index))
        calibration_upload.clicked.connect(self.to_set_path_data)
        self.calibration_upload = calibration_upload


        notes_of_analyse_EEG_data_label = QLabel('Analyse uploaded EEG data', self)
        notes_of_analyse_EEG_data_label.setStyleSheet(
            "QLabel{font-size:" + str(int(65 * self.interface_control_index)) + "px;color:rgb(215,215,215);}")
        notes_of_analyse_EEG_data_label.move(int(580 * self.interface_control_index),
                                             int(180 * self.interface_control_index))
        self.notes_of_analyse_EEG_data_label = notes_of_analyse_EEG_data_label
        """ ----- End of EEG data analysis page ----- """

        """ ----- Start of the parameters_setting_page ----- """
        notes_of_parameters_setting_label = QLabel('Test parameters settings', self)
        notes_of_parameters_setting_label.setStyleSheet(
            "QLabel{font-size:" + str(int(85 * self.interface_control_index)) + "px;color:rgb(215,215,215);}")
        notes_of_parameters_setting_label.move(int(550 * self.interface_control_index),
                                               int(160 * self.interface_control_index))
        self.notes_of_parameters_setting_label = notes_of_parameters_setting_label

        # frame_rate
        frame_rate_label = QLabel('Frame rate (frames/second)', self)
        frame_rate_label.setStyleSheet(
            "QLabel{font-size:" + str(int(20 * self.interface_control_index)) + "px;color:rgb(215,215,215);}")
        frame_rate_label.move(int(554 * self.interface_control_index), int(350 * self.interface_control_index))
        self.frame_rate_label = frame_rate_label

        frame_rate_line = QLineEdit(self)
        frame_rate_line.move(int(809 * self.interface_control_index), int(353 * self.interface_control_index))
        frame_rate_line.setText(self.frame_rate_line_content)
        frame_rate_line.setStyleSheet("QLineEdit{color:rgb(200,200,200);}"
                                      "QLineEdit{background-color:rgb(70, 70, 70);}"
                                      "QLineEdit{border-radius:" + str(int(3 * self.interface_control_index)) + "px}"
                                                                                                                "QLineEdit{font-size:" + str(
            int(18 * self.interface_control_index)) + "px;}")
        frame_rate_line.setFixedHeight(int(22 * self.interface_control_index))
        frame_rate_line.setFixedWidth(int(160 * self.interface_control_index))
        self.frame_rate_line = frame_rate_line

        #Interval_Rate
        interval_rate_label = QLabel('Flash interval(seconds)', self)
        interval_rate_label.setStyleSheet(
            "QLabel{font-size:" + str(int(20 * self.interface_control_index)) + "px;color:rgb(215,215,215);}")
        interval_rate_label.move(int(986 * self.interface_control_index), int(350 * self.interface_control_index))
        self.interval_rate_label= interval_rate_label

        interval_rate_line = QLineEdit(self)
        interval_rate_line.move(int(1145 * self.interface_control_index), int(353 * self.interface_control_index))
        interval_rate_line.setStyleSheet("QLineEdit{color:rgb(200,200,200);}"
                                           "QLineEdit{background-color:rgb(70, 70, 70);}"
                                           "QLineEdit{border-radius:" + str(
            int(3 * self.interface_control_index)) + "px}"
                                                     "QLineEdit{font-size:" + str(
            int(18 * self.interface_control_index)) + "px;}")
        interval_rate_line.setFixedHeight(int(22 * self.interface_control_index))
        interval_rate_line.setFixedWidth(int(285 * self.interface_control_index))
        interval_rate_line.setText(self.NUMBER_OF_SPOTS_line_content)
        self.interval_rate_line = interval_rate_line

        # NUMBER_OF_SPOTS
        NUMBER_OF_SPOTS_label = QLabel('Number of spots', self)
        NUMBER_OF_SPOTS_label.setStyleSheet(
            "QLabel{font-size:" + str(int(20 * self.interface_control_index)) + "px;color:rgb(215,215,215);}")
        NUMBER_OF_SPOTS_label.move(int(986 * self.interface_control_index), int(350 * self.interface_control_index))
        self.NUMBER_OF_SPOTS_label = NUMBER_OF_SPOTS_label

        NUMBER_OF_SPOTS_line = QLineEdit(self)
        NUMBER_OF_SPOTS_line.move(int(1145 * self.interface_control_index), int(353 * self.interface_control_index))
        NUMBER_OF_SPOTS_line.setStyleSheet("QLineEdit{color:rgb(200,200,200);}"
                                           "QLineEdit{background-color:rgb(70, 70, 70);}"
                                           "QLineEdit{border-radius:" + str(
            int(3 * self.interface_control_index)) + "px}"
                                                     "QLineEdit{font-size:" + str(
            int(18 * self.interface_control_index)) + "px;}")
        NUMBER_OF_SPOTS_line.setFixedHeight(int(22 * self.interface_control_index))
        NUMBER_OF_SPOTS_line.setFixedWidth(int(285 * self.interface_control_index))
        NUMBER_OF_SPOTS_line.setText(self.NUMBER_OF_SPOTS_line_content)
        self.NUMBER_OF_SPOTS_line = NUMBER_OF_SPOTS_line

        # spot_size
        spot_size_label = QLabel('Spot size (pixels)', self)
        spot_size_label.setStyleSheet(
            "QLabel{font-size:" + str(int(20 * self.interface_control_index)) + "px;color:rgb(215,215,215);}")
        spot_size_label.move(int(554 * self.interface_control_index), int(450 * self.interface_control_index))
        self.spot_size_label = spot_size_label

        spot_size_line = QLineEdit(self)
        spot_size_line.move(int(715 * self.interface_control_index), int(452 * self.interface_control_index))
        spot_size_line.setText(self.spot_size_content)
        spot_size_line.setStyleSheet("QLineEdit{color:rgb(200,200,200);}"
                                     "QLineEdit{background-color:rgb(70, 70, 70);}"
                                     "QLineEdit{border-radius:" + str(int(3 * self.interface_control_index)) + "px;}"
                                                                                                               "QLineEdit{font-size:" + str(
            int(18 * self.interface_control_index)) + "px;}")
        spot_size_line.setFixedHeight(int(22 * self.interface_control_index))
        spot_size_line.setFixedWidth(int(254 * self.interface_control_index))
        self.spot_size_line = spot_size_line

        # duration
        test_duration_label = QLabel('Test duration (second)', self)
        test_duration_label.setStyleSheet(
            "QLabel{font-size:" + str(int(20 * self.interface_control_index)) + "px;color:rgb(215,215,215);}")
        test_duration_label.move(int(986 * self.interface_control_index), int(450 * self.interface_control_index))
        self.test_duration_label = test_duration_label

        test_duration_line = QLineEdit(self)
        test_duration_line.move(int(1192 * self.interface_control_index), int(452 * self.interface_control_index))
        test_duration_line.setStyleSheet("QLineEdit{color:rgb(200,200,200);}"
                                         "QLineEdit{background-color:rgb(70, 70, 70);}"
                                         "QLineEdit{border-radius:" + str(int(3 * self.interface_control_index)) + "px}"
                                         "QLineEdit{font-size:" + str(int(18 * self.interface_control_index)) + "px;}")
        test_duration_line.setFixedHeight(int(22 * self.interface_control_index))
        test_duration_line.setFixedWidth(int(233 * self.interface_control_index))
        test_duration_line.setText(self.test_duration_line_content)
        self.test_duration_line = test_duration_line

        # color_select
        spot_color_off_label = QLabel('Spot color off', self)
        spot_color_off_label.setStyleSheet(
            "QLabel{font-size:" + str(int(20 * self.interface_control_index)) + "px;color:rgb(215,215,215);}")
        spot_color_off_label.move(int(554 * self.interface_control_index), int(550 * self.interface_control_index))
        self.spot_color_off_label = spot_color_off_label

        spot_color_on_label = QLabel('Spot color on', self)
        spot_color_on_label.setStyleSheet(
            "QLabel{font-size:" + str(int(20 * self.interface_control_index)) + "px;color:rgb(215,215,215);}")
        spot_color_on_label.move(int(986 * self.interface_control_index), int(550 * self.interface_control_index))
        self.spot_color_on_label = spot_color_on_label

        self.spot_color_off = QColor(self.defult_spot_color_off[0], self.defult_spot_color_off[1],
                                     self.defult_spot_color_off[2])
        spot_color_off_button = QPushButton('Select', self)
        spot_color_off_button.setStyleSheet("QPushButton{color:white}"
                                            "QPushButton{font-size:" + str(
            int(15 * self.interface_control_index)) + "px;color:rgb(95,95,95);}"
                                                      "QPushButton:hover{color:rgb(50,50,50)}"
                                                      "QPushButton{background-color:rgb(215, 215, 215)}"
                                                      "QPushButton{border:" + str(
            int(15 * self.interface_control_index)) + "px}"
                                                      "QPushButton{border-radius:" + str(
            int(3 * self.interface_control_index)) + "px}"
                                                     "QPushButton{padding:0px " + str(
            int(10 * self.interface_control_index)) + "px}")
        spot_color_off_button.setMinimumHeight(int(20 * self.interface_control_index))
        spot_color_off_button.move(int(714 * self.interface_control_index), int(552 * self.interface_control_index))
        spot_color_off_button.clicked.connect(self.showDialog0)

        color_widget0 = QWidget(self)
        color_widget0.setStyleSheet('QWidget{border-radius:' + str(
            int(5 * self.interface_control_index)) + 'px}' 'QWidget{background-color:%s}' % self.spot_color_off.name())

        color_widget0.setGeometry(int(785 * self.interface_control_index), int(552 * self.interface_control_index),
                                  int(180 * self.interface_control_index), int(20 * self.interface_control_index))
        self.spot_color_off_button = spot_color_off_button
        self.color_widget0 = color_widget0

        self.spot_color_on = QColor(self.defult_spot_color_on[0], self.defult_spot_color_on[1],
                                    self.defult_spot_color_on[2])
        spot_color_on_button = QPushButton('Select', self)
        spot_color_on_button.setStyleSheet("QPushButton{color:white}"
                                           "QPushButton{font-size:" + str(
            int(15 * self.interface_control_index)) + "px;color:rgb(95,95,95);}"
                                                      "QPushButton:hover{color:rgb(50,50,50)}"
                                                      "QPushButton{background-color:rgb(215, 215, 215)}"
                                                      "QPushButton{border:" + str(
            int(15 * self.interface_control_index)) + "px}"
                                                      "QPushButton{border-radius:" + str(
            int(3 * self.interface_control_index)) + "px}"
                                                     "QPushButton{padding:0px " + str(
            int(10 * self.interface_control_index)) + "px}")
        spot_color_on_button.setMinimumHeight(int(20 * self.interface_control_index))
        spot_color_on_button.move(int(1155 * self.interface_control_index), int(552 * self.interface_control_index))
        spot_color_on_button.clicked.connect(self.showDialog1)

        color_widget1 = QWidget(self)
        color_widget1.setStyleSheet('QWidget{border-radius:' + str(
            int(7 * self.interface_control_index)) + 'px}' 'QWidget{background-color:%s}' % self.spot_color_on.name())
        color_widget1.setGeometry(int(1225 * self.interface_control_index), int(552 * self.interface_control_index),
                                  int(200 * self.interface_control_index), int(20 * self.interface_control_index))
        self.spot_color_on_button = spot_color_on_button
        self.color_widget1 = color_widget1

        # build_test_button
        build_test_button = QPushButton('Build a new test', self)
        build_test_button.setStyleSheet("QPushButton{color:white}"
                                        "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(85,85,85);}"
                                                      "QPushButton:hover{color:rgb(50,50,50)}"
                                                      "QPushButton{background-color:rgb(215, 215, 215)}"
                                                      "QPushButton{border:" + str(
            int(60 * self.interface_control_index)) + "px}"
                                                      "QPushButton{border-radius:" + str(
            int(10 * self.interface_control_index)) + "px}"
                                                      "QPushButton{padding:0px " + str(
            int(320 * self.interface_control_index)) + "px}")
        build_test_button.setMinimumHeight(int(75 * self.interface_control_index))
        build_test_button.move(int(554 * self.interface_control_index), int(670 * self.interface_control_index))

        build_test_button.clicked.connect(self.ok_on_click)

        self.build_test_button = build_test_button

        # build_calibaration_test_button
        build_calibration_test_button = QPushButton('Build the Calibration test', self)
        build_calibration_test_button.setStyleSheet("QPushButton{color:white}"
                                        "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(85,85,85);}"
                                                      "QPushButton:hover{color:rgb(50,50,50)}"
                                                      "QPushButton{background-color:rgb(215, 215, 215)}"
                                                      "QPushButton{border:" + str(
            int(60 * self.interface_control_index)) + "px}"
                                                      "QPushButton{border-radius:" + str(
            int(10 * self.interface_control_index)) + "px}"
                                                      "QPushButton{padding:0px " + str(
            int(320 * self.interface_control_index)) + "px}")
        build_calibration_test_button.setMinimumHeight(int(75 * self.interface_control_index))
        build_calibration_test_button.move(int(554 * self.interface_control_index), int(670 * self.interface_control_index))

        build_calibration_test_button.clicked.connect(self.calibrate_on_click)

        self.build_calibration_test_button = build_calibration_test_button

        # build_analyse_button
        build_analyse_button = QPushButton('Generate Report', self)
        build_analyse_button.setStyleSheet("QPushButton{color:white}"
                                                    "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(85,85,85);}"
                                                      "QPushButton:hover{color:rgb(50,50,50)}"
                                                      "QPushButton{background-color:rgb(215, 215, 215)}"
                                                      "QPushButton{border:" + str(
            int(60 * self.interface_control_index)) + "px}"
                                                      "QPushButton{border-radius:" + str(
            int(10 * self.interface_control_index)) + "px}"
                                                      "QPushButton{padding:0px " + str(
            int(320 * self.interface_control_index)) + "px}")
        build_analyse_button.setMinimumHeight(int(75 * self.interface_control_index))
        build_analyse_button.move(int(550 * self.interface_control_index),
                                           int(670 * self.interface_control_index))

        build_analyse_button.clicked.connect(self.analyse_on_click)

        self.build_analyse_button = build_analyse_button
        """ ----- End of the parameters_setting_page ----- """

        # other setting
        self.setGeometry(462, 280, int(1600 * self.interface_control_index), int(900 * self.interface_control_index))
        self.setWindowTitle('Retina Test V2.5')
        self.setFixedSize(self.width(), self.height())

        self.set_everything_false()
        self.setWelcomeLabelTrue()

        """Set the background"""
        self.palette1 = QPalette()
        self.pix = QPixmap("Images/pyqt5/BackGround.jpg")
        self.pix = self.pix.scaled(int(1600 * self.interface_control_index), int(900 * self.interface_control_index))
        self.palette1.setBrush(QPalette.Background, QBrush(self.pix))
        self.setPalette(self.palette1)
        self.center()
        self.show()
        pass

    def set_everything_false(self):
        self.setHistoryPageFalse()
        self.set_start_test_page_false()
        self.set_calibration_test_page_false()
        self.set_choose_patient_page_false()
        self.set_create_patient_page_false()
        self.setWelcomeLabelFalse()
        self.set_parameters_setting_page_false()



    def play_video(self):
        pattern_player = PatternDisplayWindow()
        pattern_player.show()
        pass

    def set_parameters_setting_page_false(self):
        self.notes_of_analyse_EEG_data_label.setVisible(False)
        self.notes_of_parameters_setting_label.setVisible(False)
        self.frame_rate_label.setVisible(False)
        self.frame_rate_line.setVisible(False)
        self.NUMBER_OF_SPOTS_line.setVisible(False)
        self.NUMBER_OF_SPOTS_label.setVisible(False)
        self.interval_rate_label.setVisible(False)
        self.interval_rate_line.setVisible(False)
        self.spot_color_on_button.setVisible(False)
        self.spot_color_off_button.setVisible(False)
        self.color_widget0.setVisible(False)
        self.color_widget1.setVisible(False)
        self.test_duration_line.setVisible(False)
        self.test_duration_label.setVisible(False)
        self.spot_color_on_label.setVisible(False)
        self.spot_size_line.setVisible(False)
        self.spot_color_off_label.setVisible(False)
        self.spot_size_label.setVisible(False)
        self.build_test_button.setVisible(False)
        self.build_calibration_test_button.setVisible(False)

    def set_parameters_setting_page_true(self):
        self.notes_of_analyse_EEG_data_label.setVisible(False)
        self.notes_of_parameters_setting_label.setVisible(True)
        self.frame_rate_label.setVisible(True)
        self.frame_rate_line.setVisible(True)
        self.interval_rate_label.setVisible(False)
        self.interval_rate_line.setVisible(False)
        self.NUMBER_OF_SPOTS_line.setVisible(True)
        self.NUMBER_OF_SPOTS_label.setVisible(True)
        self.spot_color_on_button.setVisible(True)
        self.spot_color_off_button.setVisible(True)
        self.color_widget0.setVisible(True)
        self.color_widget1.setVisible(True)
        self.test_duration_line.setVisible(True)
        self.spot_color_on_label.setVisible(True)
        self.spot_size_line.setVisible(True)
        self.spot_color_off_label.setVisible(True)
        self.spot_size_label.setVisible(True)
        self.test_duration_label.setVisible(True)
        self.build_test_button.setVisible(True)
        self.build_calibration_test_button.setVisible(False)

    def set_calibration_setting_page_true(self):
        self.notes_of_analyse_EEG_data_label.setVisible(False)
        self.notes_of_parameters_setting_label.setVisible(True)
        self.frame_rate_label.setVisible(True)
        self.frame_rate_line.setVisible(True)
        self.interval_rate_label.setVisible(True)
        self.interval_rate_line.setVisible(True)
        self.NUMBER_OF_SPOTS_line.setVisible(False)
        self.NUMBER_OF_SPOTS_label.setVisible(False)
        self.spot_color_on_button.setVisible(True)
        self.spot_color_off_button.setVisible(True)
        self.color_widget0.setVisible(True)
        self.color_widget1.setVisible(True)
        self.test_duration_line.setVisible(True)
        self.spot_color_on_label.setVisible(True)
        self.spot_size_line.setVisible(False)
        self.spot_color_off_label.setVisible(True)
        self.spot_size_label.setVisible(False)
        self.test_duration_label.setVisible(True)
        self.build_test_button.setVisible(False)
        self.build_calibration_test_button.setVisible(True)

    def set_analyse_page_true(self):
        self.notes_of_creating_patient_label.setVisible(False)
        self.notes_of_analyse_EEG_data_label.setVisible(True)
        self.full_name_label.setVisible(True)
        self.full_name_line.clear()
        self.full_name_line.setVisible(True)
        self.birthdate_label.setVisible(True)
        self.birthdate_line.setVisible(True)
        self.birthdate_line.clear()
        # self.NIN_label.setVisible(True)
        # self.NIN_line.setVisible(True)
        self.continue_button_2.setVisible(False)
        self.eeg_upload_1.setVisible(True)
        self.eeg_upload_2.setVisible(True)
        self.eeg_upload_3.setVisible(True)
        self.calibration_upload.setVisible(True)
        self.build_analyse_button.setVisible(True)
        self.back_button_2.setVisible(False)


    def set_create_patient_page_false(self):
        self.notes_of_creating_patient_label.setVisible(False)
        self.notes_of_analyse_EEG_data_label.setVisible(False)
        self.full_name_label.setVisible(False)
        self.full_name_line.setVisible(False)
        self.birthdate_label.setVisible(False)
        self.birthdate_line.setVisible(False)
        self.NIN_label.setVisible(False)
        self.NIN_line.setVisible(False)
        self.continue_button_2.setVisible(False)
        self.eeg_upload_1.setVisible(False)
        self.eeg_upload_2.setVisible(False)
        self.eeg_upload_3.setVisible(False)
        self.calibration_upload.setVisible(False)
        self.build_analyse_button.setVisible(False)
        self.back_button_2.setVisible(False)

    def set_create_patient_page_true(self):
        self.notes_of_creating_patient_label.setVisible(True)
        self.notes_of_analyse_EEG_data_label.setVisible(False)
        self.full_name_label.setVisible(True)
        self.full_name_line.setVisible(True)
        self.birthdate_label.setVisible(True)
        self.birthdate_line.setVisible(True)
        self.NIN_label.setVisible(True)
        self.NIN_line.setVisible(True)
        self.continue_button_2.setVisible(True)
        self.eeg_upload_1.setVisible(False)
        self.eeg_upload_2.setVisible(False)
        self.eeg_upload_3.setVisible(False)
        self.calibration_upload.setVisible(False)
        self.build_analyse_button.setVisible(False)
        self.back_button_2.setVisible(True)

    def set_choose_patient_page_false(self):
        self.notes_of_existing_patient_label.setVisible(False)
        self.choose_a_patient_label.setVisible(False)
        self.choose_patient_combobox.setVisible(False)
        self.continue_button_1.setVisible(False)
        self.back_button_1.setVisible(False)

    def set_choose_patient_page_true(self):
        self.notes_of_existing_patient_label.setVisible(True)
        self.choose_a_patient_label.setVisible(True)
        self.choose_patient_combobox.setVisible(True)
        self.continue_button_1.setVisible(True)
        self.back_button_1.setVisible(True)

    def to_choose_a_pattern(self):
        # self.set_everything_false()
        media = QFileDialog.getOpenFileUrl()[0]
        self.testInterface = PatternDisplayWindow()
        self.testInterface.pattern_player.setMedia(QMediaContent(media))
        self.testInterface.show()

    def to_set_path_data(self):
        # self.set_everything_false()
        media = QFileDialog.getOpenFileUrl()[0]
        self.upload_paths.append(media.path()[1:len(media.path())])
        # self.testInterface = PatternDisplayWindow()
        # self.testInterface.pattern_player.setMedia(QMediaContent(media))
        # self.testInterface.show()

    def set_start_test_page_false(self):
        self.for_new_patient_button.setVisible(False)
        self.for_current_patient_button.setVisible(False)

    def set_calibration_test_page_false(self):
        self.for_new_patient_button.setVisible(False)
        self.for_current_patient_button.setVisible(False)

    def set_start_test_page_true(self):
        self.for_new_patient_button.setVisible(True)
        self.for_current_patient_button.setVisible(True)

    def set_start_test_page_true(self):
        self.for_new_patient_button.setVisible(True)
        self.for_current_patient_button.setVisible(True)

    def to_create_patient_page(self):
        self.set_everything_false()
        self.set_create_patient_page_true()

    def to_choose_current_patient_page(self):
        self.set_everything_false()
        self.set_choose_patient_page_true()

    def ok_on_click(self):
        # self.pop_thread = threading.Thread(target=self.pop_dialog())
        #
        # self.generate_thread = threading.Thread(target=self.generate_everything())
        #
        # threads = []
        # threads.append(self.pop_thread)
        # threads.append(self.generate_thread)
        #
        # for t in threads:
        #     t.start()

        self.testInterface = PatternDisplayWindow()
        self.generate_everything()
        self.testInterface.show()

    def calibrate_on_click(self):
        self.testInterface = PatternDisplayWindow()
        self.generate_calibration()
        self.testInterface.show()

    def analyse_on_click(self):
        # self.testInterface = PatternDisplayWindow()
        self.analyse_data()
        # self.testInterface.show()

    def pop_dialog(self):
        msg_box = QMessageBox(QMessageBox.Information, 'Notification', 'Generating pattern now')
        msg_box.exec_()
        pass

    def setInitButtonTrue(self):
        self.history_button.setVisible(True)
        self.start_a_test_button.setVisible(True)
        self.build_a_new_test_button.setVisible(True)
        self.quit_button.setVisible(True)

    def setInitButtonFalse(self):
        self.history_button.setVisible(False)
        self.start_a_test_button.setVisible(False)
        self.build_a_new_test_button.setVisible(False)
        self.quit_button.setVisible(False)

    def setHistoryPageFalse(self):
        self.history_label1.setVisible(False)
        self.history_label2.setVisible(False)
        self.history_label3.setVisible(False)
        self.info_label1.setVisible(False)
        self.info_label2.setVisible(False)
        self.info_label3.setVisible(False)
        self.info_label4.setVisible(False)
        self.info_label5.setVisible(False)
        self.info_label6.setVisible(False)

    def setHistoryPageTrue(self):
        self.history_label1.setVisible(True)
        self.history_label2.setVisible(True)
        self.history_label3.setVisible(True)
        self.info_label1.setVisible(True)
        self.info_label2.setVisible(True)
        self.info_label3.setVisible(True)
        self.info_label4.setVisible(True)
        self.info_label5.setVisible(True)
        self.info_label6.setVisible(True)

    def build_test_on_click(self):
        self.set_everything_false()
        self.set_parameters_setting_page_true()

        self.history_button.setStyleSheet("QPushButton{color:white}"
                                          "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      "QPushButton{background-color:rgba(51, 51, 51, 0)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(147 * self.interface_control_index)) + "px}")
        self.build_a_new_test_button.setStyleSheet("QPushButton{color:white}"
                                                   "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      "QPushButton{background-color:rgba(51, 51, 51, 255)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(83 * self.interface_control_index)) + "px}")

        self.start_a_test_button.setStyleSheet("QPushButton{color:white}"
                                               "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      "QPushButton{background-color:rgba(51, 51, 51, 0)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(83 * self.interface_control_index)) + "px}")

        self.build_a_calibrate_button.setStyleSheet("QPushButton{color:white}"
                                                   "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      "QPushButton{background-color:rgba(51, 51, 51, 0)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(83 * self.interface_control_index)) + "px}")

        self.analyse_test_button.setStyleSheet("QPushButton{color:white}"
                                               "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      "QPushButton{background-color:rgba(51, 51, 51, 0)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(83 * self.interface_control_index)) + "px}")

    def build_calibrate_on_click(self):
        self.set_everything_false()
        self.set_calibration_setting_page_true()

        self.history_button.setStyleSheet("QPushButton{color:white}"
                                          "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      "QPushButton{background-color:rgba(51, 51, 51, 0)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(147 * self.interface_control_index)) + "px}")
        self.build_a_new_test_button.setStyleSheet("QPushButton{color:white}"
                                                   "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      "QPushButton{background-color:rgba(51, 51, 51, 0)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(83 * self.interface_control_index)) + "px}")

        self.start_a_test_button.setStyleSheet("QPushButton{color:white}"
                                               "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      "QPushButton{background-color:rgba(51, 51, 51, 0)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(83 * self.interface_control_index)) + "px}")

        self.build_a_calibrate_button.setStyleSheet("QPushButton{color:white}"
                                                   "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      "QPushButton{background-color:rgba(51, 51, 51, 255)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(83 * self.interface_control_index)) + "px}")

        self.analyse_test_button.setStyleSheet("QPushButton{color:white}"
                                               "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      "QPushButton{background-color:rgba(51, 51, 51, 0)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(83 * self.interface_control_index)) + "px}")

    def home_on_click(self):
        self.set_everything_false()
        self.setWelcomeLabelTrue()
        self.history_button.setStyleSheet("QPushButton{color:white}"
                                          "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      "QPushButton{background-color:rgba(51, 51, 51, 0)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(147 * self.interface_control_index)) + "px}")
        self.build_a_new_test_button.setStyleSheet("QPushButton{color:white}"
                                                   "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      "QPushButton{background-color:rgba(51, 51, 51, 0)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(83 * self.interface_control_index)) + "px}")

        self.start_a_test_button.setStyleSheet("QPushButton{color:white}"
                                               "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      "QPushButton{background-color:rgba(51, 51, 51, 0)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(83 * self.interface_control_index)) + "px}")

        self.build_a_calibrate_button.setStyleSheet("QPushButton{color:white}"
                                                    "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      "QPushButton{background-color:rgba(51, 51, 51, 0)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(83 * self.interface_control_index)) + "px}")

        self.analyse_test_button.setStyleSheet("QPushButton{color:white}"
                                               "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      "QPushButton{background-color:rgba(51, 51, 51, 0)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(83 * self.interface_control_index)) + "px}")

    def back_on_click(self):
        self.set_everything_false()
        self.start_test_on_click()


    def history_on_click(self):
        self.history_button.setStyleSheet("QPushButton{color:white}"
                                          "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      "QPushButton{background-color:rgb(51, 51, 51)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(147 * self.interface_control_index)) + "px}")

        self.build_a_new_test_button.setStyleSheet("QPushButton{color:white}"
                                                   "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      "QPushButton{background-color:rgba(51, 51, 51, 0)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(83 * self.interface_control_index)) + "px}")

        self.build_a_calibrate_button.setStyleSheet("QPushButton{color:white}"
                                                    "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      "QPushButton{background-color:rgba(51, 51, 51, 0)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(83 * self.interface_control_index)) + "px}")

        self.start_a_test_button.setStyleSheet("QPushButton{color:white}"
                                               "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      "QPushButton{background-color:rgba(51, 51, 51, 0)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(83 * self.interface_control_index)) + "px}")

        self.analyse_test_button.setStyleSheet("QPushButton{color:white}"
                                               "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      "QPushButton{background-color:rgba(51, 51, 51, 0)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(83 * self.interface_control_index)) + "px}")

        self.set_everything_false()
        self.setHistoryPageTrue()
        pass

    def start_test_on_click(self):
        self.history_button.setStyleSheet("QPushButton{color:white}"
                                          "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      "QPushButton{background-color:rgba(51, 51, 51, 0)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(147 * self.interface_control_index)) + "px}")
        self.build_a_new_test_button.setStyleSheet("QPushButton{color:white}"
                                                   "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      "QPushButton{background-color:rgba(51, 51, 51, 0)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(83 * self.interface_control_index)) + "px}")

        self.build_a_calibrate_button.setStyleSheet("QPushButton{color:white}"
                                                    "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      "QPushButton{background-color:rgba(51, 51, 51, 0)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(83 * self.interface_control_index)) + "px}")

        self.start_a_test_button.setStyleSheet("QPushButton{color:white}"
                                               "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      "QPushButton{background-color:rgba(51, 51, 51, 255)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(83 * self.interface_control_index)) + "px}")

        self.analyse_test_button.setStyleSheet("QPushButton{color:white}"
                                                    "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      "QPushButton{background-color:rgba(51, 51, 51, 0)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(83 * self.interface_control_index)) + "px}")

        self.set_everything_false()
        self.set_start_test_page_true()

    def start_analyse_on_click(self):
        self.set_everything_false()
        self.set_analyse_page_true()
        self.history_button.setStyleSheet("QPushButton{color:white}"
                                          "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      "QPushButton{background-color:rgba(51, 51, 51, 0)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(147 * self.interface_control_index)) + "px}")
        self.build_a_new_test_button.setStyleSheet("QPushButton{color:white}"
                                                   "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      "QPushButton{background-color:rgba(51, 51, 51, 0)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(83 * self.interface_control_index)) + "px}")

        self.build_a_calibrate_button.setStyleSheet("QPushButton{color:white}"
                                          "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      "QPushButton{background-color:rgba(51, 51, 51, 0)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(147 * self.interface_control_index)) + "px}")

        self.analyse_test_button.setStyleSheet("QPushButton{color:white}"
                                               "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      "QPushButton{background-color:rgba(51, 51, 51, 255)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(83 * self.interface_control_index)) + "px}")

        self.start_a_test_button.setStyleSheet("QPushButton{color:white}"
                                                    "QPushButton{font-size:" + str(
            int(35 * self.interface_control_index)) + "px;color:rgb(242,242,242);}"
                                                      "QPushButton:hover{color:rgb(160,160,160)}"
                                                      "QPushButton{background-color:rgba(51, 51, 51, 0)}"
                                                      "QPushButton{border:0px}"
                                                      "QPushButton{padding:0px " + str(
            int(83 * self.interface_control_index)) + "px}")

    def setWelcomeLabelFalse(self):
        self.please_select_a_function_label.setVisible(False)
        self.retina_function_test_label.setVisible(False)

    def setWelcomeLabelTrue(self):
        self.please_select_a_function_label.setVisible(True)
        self.retina_function_test_label.setVisible(True)

    def center(self):
        geometry = self.frameGeometry()
        center = QDesktopWidget().availableGeometry().center()
        geometry.moveCenter(center)
        self.move(geometry.topLeft())

    def showDialog0(self):
        col = QColorDialog.getColor()
        self.defult_spot_color_off[0], self.defult_spot_color_off[1], self.defult_spot_color_off[2] = col.getRgb()[0], \
                                                                                                      col.getRgb()[1], \
                                                                                                      col.getRgb()[2]

        if col.isValid():
            self.color_widget0.setStyleSheet('QWidget{border-radius:' + str(
                int(7 * self.interface_control_index)) + 'px}' 'QWidget{background-color:%s}' % col.name())

    def showDialog1(self):
        col = QColorDialog.getColor()
        self.defult_spot_color_on[0], self.defult_spot_color_on[1], self.defult_spot_color_on[2] = col.getRgb()[0], \
                                                                                                   col.getRgb()[1], \
                                                                                                   col.getRgb()[2]
        if col.isValid():
            self.color_widget1.setStyleSheet('QWidget{border-radius:' + str(
                int(7 * self.interface_control_index)) + 'px}' 'QWidget{background-color:%s}' % col.name())

    def save_setting(self):
        with open('Setting.txt', 'w') as f:
            f.write(self.frame_rate_line_content)
            f.write("\n")
            f.write(self.NUMBER_OF_SPOTS_line_content)
            f.write("\n")

            f.write(str(self.defult_spot_color_off[0]) + "," + str(self.defult_spot_color_off[1]) + "," + str(
                self.defult_spot_color_off[2]))
            f.write("\n")
            f.write(str(self.defult_spot_color_on[0]) + "," + str(self.defult_spot_color_on[1]) + "," + str(
                self.defult_spot_color_on[2]))
            f.write("\n")

            f.write(self.test_duration_line_content)
            f.write("\n")
            f.write(self.spot_size_content)

            f.write("\n")
            f.write(self.flash_interval_content)


    def save_Calibration_setting(self):
        with open(self.dir_path+"\\"+"Settings.txt", 'w') as f:
            f.write(self.frame_rate_line_content)
            f.write("\n")

            f.write(str(self.defult_spot_color_off[0]) + "," + str(self.defult_spot_color_off[1]) + "," + str(
                self.defult_spot_color_off[2]))
            f.write("\n")
            f.write(str(self.defult_spot_color_on[0]) + "," + str(self.defult_spot_color_on[1]) + "," + str(
                self.defult_spot_color_on[2]))

            f.write("\n")
            f.write(self.test_duration_line_content)

            f.write("\n")
            f.write(self.flash_interval_content)


    def load_setting(self):
        datas = []
        for line in open("Setting.txt", "r"):
            line = line.strip()
            datas.append(line)
        return datas


    """This function generate the elements, frames, and pattern. It will use the algorithm in Model.py"""
    def generate_everything(self):
        self.NUMBER_OF_SPOTS_line_content = self.NUMBER_OF_SPOTS_line.text()
        self.frame_rate_line_content = self.frame_rate_line.text()
        self.test_duration_line_content = self.test_duration_line.text()
        self.spot_size_content = self.spot_size_line.text()
        self.SPOT_SIZE = int(self.spot_size_content)
        self.save_setting()

        QApplication.processEvents()

        GE = Model.Generate_Everything(self)

        """Distribution matrix"""
        GE.DISTRIBUTION_MATRIX = GE.distribute_matrix_generation()


        GE.IMAGE_ROW = len(GE.DISTRIBUTION_MATRIX)
        GE.IMAGE_COLUMN = 2 * GE.IMAGE_ROW

        GE.CIRCLE_RADIUS = self.SPOT_SIZE
        GE.SCREEN_WIDTH = self.SCREEN_WIDTH
        GE.TARGET_WIDTH = self.SCREEN_WIDTH
        GE.TARGET_HEIGHT = int(GE.SCREEN_WIDTH / 2)
        GE.PICS_SIZE = int(GE.TARGET_WIDTH / GE.IMAGE_COLUMN)
        GE.CIRCLE_POSITION = (int(GE.PICS_SIZE / 2), int(GE.PICS_SIZE / 2))

        GE.IMAGE_WIDTH = GE.PICS_SIZE
        GE.IMAGE_HEIGHT = GE.PICS_SIZE

        """Pseudo random sequence"""
        GE.pse_matrix = GE.generate_pse_matrix()

        """Generate element pics, frame pics, and the video"""
        GE.get_elements_and_frame_pics_and_video()

        pattern_path = os.getcwd() + '\\' + GE.video_name
        # media = QUrl.fromLocalFile(pattern_path)
        # self.testInterface.pattern_player.setMedia(QMediaContent(media))
        video_name = GE.video_name.split('.')
        print(pattern_path)
        self.dir_path = os.getcwd() + '\\' + video_name[0]
        print(self.dir_path)
        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)
            # move files into created directory
            shutil.move(pattern_path, self.dir_path)
        else:
            os.remove(self.dir_path + "\\" + GE.video_name)
            shutil.move(pattern_path, self.dir_path)
        media = QUrl.fromLocalFile(self.dir_path + "\\" + GE.video_name)
        self.testInterface.pattern_player.setMedia(QMediaContent(media))

    def analyse_data(self):
        full_name = self.full_name_line.text()
        birthday = self.birthdate_line.text()
        self.patient_details = []
        self.patient_details.append(full_name)
        self.patient_details.append(birthday)

        QApplication.processEvents()

        GE = Model.Generate_Everything(self)
        print(self.upload_paths)
        GE.generate_EEG_analysis_report()

    #"""This function generate the elements, frames, and pattern for the calibration test. It will use the algorithm in Model.py"""
    def generate_calibration(self):
        device = win32api.EnumDisplayDevices()
        settings = win32api.EnumDisplaySettings(device.DeviceName, -1)
        refresh_rate = getattr(settings, 'DisplayFrequency')
        self.spot_size_content = 10000

        # self.NUMBER_OF_SPOTS_line.text()
        self.NUMBER_OF_SPOTS_line_content = '1'
        self.frame_rate_line_content = self.frame_rate_line.text()
        self.flash_interval_content = self.interval_rate_line.text()
        self.test_duration_line_content = self.test_duration_line.text()
        self.spot_size_content = self.spot_size_line.text()
        self.SPOT_SIZE = int(self.spot_size_content)/2
        # self.save_setting()

        QApplication.processEvents()

        GE = Model.Generate_Everything(self)

        GE.SCREEN_WIDTH = self.SCREEN_WIDTH
        GE.SCREEN_HEIGHT = self.SCREEN_HEIGHT

        """Calibration flashing sequence"""
        GE.calibration_matrix = GE.generate_calibration_matrix()

        """Generate element pics, frame pics, and the video"""
        GE.get_elements_and_frame_pics_and_video_calibration()

        pattern_path = os.getcwd() + '\\' + GE.video_name
        video_name = GE.video_name.split('.')
        print(pattern_path)
        self.dir_path = os.getcwd() + '\\' + video_name[0]
        print(self.dir_path)
        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)
            # move files into created directory
            shutil.move(pattern_path, self.dir_path)
        else:
            os.remove(self.dir_path+"\\"+GE.video_name)
            shutil.move(pattern_path, self.dir_path)
        media = QUrl.fromLocalFile(self.dir_path+"\\"+GE.video_name)
        self.testInterface.pattern_player.setMedia(QMediaContent(media))
        self.save_Calibration_setting()

if __name__ == '__main__':
    np.set_printoptions(threshold=np.inf)

    """Generate Front-end"""
    app = QApplication(sys.argv)
    interface = MainQtWindow(app.primaryScreen().size().width(), app.primaryScreen().size().height())
    sys.exit(app.exec_())