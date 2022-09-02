import cv2
import math
import random
import threading
from scipy import signal
import numpy as np
import PIL.Image as Image
import moviepy.editor as moviepy
import eeglib
import plotly.graph_objects as go
import  os
# from jinja2 import Environment, FileSystemLoader
# from weasyprint import HTML
from fpdf import FPDF
import kaleido

class Generate_Everything:

    def __init__(self, interface):
        self.IMAGES_PATH = 'Images/elements//'
        self.IMAGES_FORMAT = ['.PNG', '.png']
        self.IMAGE_SAVE_PATH = 'Images/picsForVideo/'

        r0, g0, b0 = interface.defult_spot_color_off[0], interface.defult_spot_color_off[1], \
                     interface.defult_spot_color_off[2]
        r1, g1, b1 = interface.defult_spot_color_on[0], interface.defult_spot_color_on[1], \
                     interface.defult_spot_color_on[2]

        self.spot_color_off = (b0, g0, r0)
        self.spot_color_on = (b1, g1, r1)

        base_r = (r0 + r1) / 3
        base_g = (g0 + g1) / 3
        base_b = (b0 + b1) / 3

        self.BASE_COLOR = (base_r + base_g + base_b) / 3

        self.NUMBER_OF_SPOTS = int(interface.NUMBER_OF_SPOTS_line_content)

        # frame details
        self.FRAME_RATE = int(interface.frame_rate_line_content)
        self.DURATION = int(interface.test_duration_line_content)

        # total frame
        self.TOTAL_FRAME = self.FRAME_RATE * self.DURATION

        #Other Details
        self.FLASH_INTERVAl = interface.flash_interval_content
        self.UPLOAD_PATHS = interface.upload_paths
        self.PATIENT_DETAILS = interface.patient_details


    def calculate_visual_angel(self):
        self.real_size = 0.01858 * self.CIRCLE_RADIUS * 2
        self.visual_angel = math.atan(self.real_size / 50)
        self.str_word = "The visual angel is " + str(self.visual_angel) + ", and is " + str(
            self.visual_angel * 57.3) + "°"
        return self.str_word

    def change_video_to_mp4(self):
        clip = moviepy.VideoFileClip("output.avi")
        clip.write_videofile("output.mp4")

    def get_elements_and_frame_pics_and_video(self):
        """This function is used to generate element pics, frame pics, and the video(pattern)"""

        """Process of color elements"""
        self.elements_generation()

        """Pics combination"""
        # self.generate_frame_image_by_multithread()
        self.image_compose(0, self.TOTAL_FRAME)

        """video generation"""
        self.video_generation()

    def get_elements_and_frame_pics_and_video_calibration(self):
        """This function is used to generate element pics, frame pics, and the video(pattern)"""

        """Process of color elements"""
        self.elements_generation_calibration()

        """Pics combination"""
        # self.generate_frame_image_by_multithread()
        self.calibration_image_compose(0, self.TOTAL_FRAME)

        """video generation"""
        self.calibration_video_generation()

    def generate_pse_matrix(self):
        pse_matrix = np.zeros((self.NUMBER_OF_SPOTS, self.TOTAL_FRAME), dtype=int)

        length = 15 if (self.NUMBER_OF_SPOTS * self.TOTAL_FRAME < 2 * 15 - 1) else 25
        m_poly = [14, 4, 3, 1] if (self.NUMBER_OF_SPOTS * self.TOTAL_FRAME < 2 * 15 - 1) else [24, 5, 4, 3]

        m_xor = [0] * length
        for i in m_poly:
            m_xor[length - 1 - i] = 1
        M_series = [1] * length

        for x in range(self.NUMBER_OF_SPOTS):
            for y in range(self.TOTAL_FRAME):
                temp = 0
                for j in range(length):
                    temp = temp + m_xor[j] * M_series[j]
                M_series.append(temp % 2)
                del M_series[0]
                temp = [str(i) for i in M_series]
                pse_matrix[x][y] = temp[len(temp) - 1]

        print("PSE matrix generates successful")
        return pse_matrix

    """Calibration flashing sequence"""
    def generate_calibration_matrix(self):
        calibration_matrix = []
        if self.FLASH_INTERVAl == 'Auto':
            for t in range(self.DURATION + 1, 1, -1):  # Duration of the test

                # Creating the flashing point of each frame
                intervals = np.arange(1, self.FRAME_RATE, t)
                frames = signal.unit_impulse(self.FRAME_RATE, intervals.tolist())
                calibration_matrix.extend(frames)
        else:
            self.FLASH_INTERVAl = float(self.FLASH_INTERVAl)
            frame_sec = round((1/self.FRAME_RATE), 2) #Seconds
            flash_interval = self.FLASH_INTERVAl/frame_sec #The Frame

            #Equal Interval Calibration matrix
            intervals = np.arange(0, self.FRAME_RATE * self.DURATION, int(flash_interval))
            frames = signal.unit_impulse(self.FRAME_RATE * self.DURATION, intervals.tolist())
            calibration_matrix.extend(frames)

        return calibration_matrix

    def distribute_matrix_generation(self):
        # Depends on the spot number
        length = 4
        for i in range(4, 100000):
            if (2 * i * i >= self.NUMBER_OF_SPOTS):
                length = i
                break
        temp_matrix = np.zeros((length, 2 * length), dtype=int)
        it_number = self.NUMBER_OF_SPOTS

        while (it_number > 0):
            temp_x = random.randint(0, length - 1)
            temp_y = random.randint(0, 2 * length - 1)
            if (temp_matrix[temp_x][temp_y] == 0):
                temp_matrix[temp_x][temp_y] = 1
                it_number = it_number - 1

        print("Distribution matrix generates successful")
        return temp_matrix

    def elements_generation(self):
        # spot_color_off
        # print("Inside elements generation")
        canvas0 = np.ones((self.PICS_SIZE, self.PICS_SIZE, 3), dtype="uint8")
        canvas0 *= int(self.BASE_COLOR)

        cv2.imwrite("Images/elements/base_color.png", canvas0)  # generate base_color
        cv2.circle(canvas0, center=self.CIRCLE_POSITION, radius=self.CIRCLE_RADIUS, color=self.spot_color_off,
                   thickness=-1)
        cv2.imwrite("Images/elements/spot_color_off.png", canvas0)

        # spot_color_on
        canvas1 = np.ones((self.PICS_SIZE, self.PICS_SIZE, 3), dtype="uint8")
        canvas1 *= int(self.BASE_COLOR)

        cv2.circle(canvas1, center=self.CIRCLE_POSITION, radius=self.CIRCLE_RADIUS, color=self.spot_color_on,
                   thickness=-1)
        cv2.imwrite("Images/elements/spot_color_on.png", canvas1)

        # cross
        canvas2 = np.ones((self.PICS_SIZE, self.PICS_SIZE, 4), dtype="uint8")
        canvas2 *= 0


        # Drawing the lines
        cross_width = int(self.PICS_SIZE / 10) if (int(self.PICS_SIZE / 10) >= 1) else 1
        temp_color = int(self.BASE_COLOR * 2)
        cross_color = (temp_color, temp_color, temp_color, 255)
        cv2.line(canvas2, (int(self.PICS_SIZE / 5), int(self.PICS_SIZE / 2)),
                 (int(4 * self.PICS_SIZE / 5), int(self.PICS_SIZE / 2)), cross_color, cross_width)
        cv2.line(canvas2, (int(self.PICS_SIZE / 2), int(self.PICS_SIZE / 5)),
                 (int(self.PICS_SIZE / 2), int(4 * self.PICS_SIZE / 5)), cross_color, cross_width)

        cv2.imwrite("Images/elements/cross.png", canvas2)
        print("Elements generate successful")

    def elements_generation_calibration(self):
        # spot_color_off
        # print("Inside elements generation")
        canvas0 = np.ones((self.SCREEN_HEIGHT, self.SCREEN_WIDTH, 3), dtype="uint8")
        canvas0 *= int(self.BASE_COLOR)
        cv2.imwrite("Images/elements/base_color.png", canvas0)  # generate base_color

        cv2.rectangle(canvas0, (0, 0), (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), self.spot_color_off, thickness=-1)
        cv2.imwrite("Images/elements/spot_color_off.png", canvas0)

        # spot_color_on
        canvas1 = np.ones((self.SCREEN_HEIGHT, self.SCREEN_WIDTH, 3), dtype="uint8")
        canvas1 *= int(self.BASE_COLOR)
        cv2.rectangle(canvas1, (0, 0), (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), self.spot_color_on, thickness=-1)
        cv2.imwrite("Images/elements/spot_color_on.png", canvas1)
        print("Elements generate successful")

    def generate_frame_image_by_multithread(self):
        threads = []
        t1 = threading.Thread(target=self.image_compose(0, int(self.TOTAL_FRAME / 4)))
        t2 = threading.Thread(
            target=self.image_compose(int((self.TOTAL_FRAME / 4) - 1), int((self.TOTAL_FRAME / 4)) * 2))
        t3 = threading.Thread(
            target=self.image_compose(int((self.TOTAL_FRAME / 4) * 2 - 1), int((self.TOTAL_FRAME / 4) * 3)))
        t4 = threading.Thread(target=self.image_compose(int(self.TOTAL_FRAME / 4) * 3 - 1, self.TOTAL_FRAME))

        threads.append(t1)
        threads.append(t2)
        threads.append(t3)
        threads.append(t4)

        for t in threads:
            t.start()

    def video_generation(self):
        # print("Inside video_generation")
        data_path = "Images/picsForVideo/"
        self.VIDEO_SIZE = (self.PICS_SIZE * self.IMAGE_COLUMN, self.PICS_SIZE * int(self.IMAGE_ROW))  # 需要转为视频的图片的尺寸

        self.video_name = "pattern_" + str(self.FRAME_RATE) + "fps_" + str(self.DURATION) + "second_" + str(
            self.NUMBER_OF_SPOTS) + "spots_" + str(self.CIRCLE_RADIUS) + "pixels.mp4"

        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        video = cv2.VideoWriter(self.video_name, fourcc, self.FRAME_RATE, self.VIDEO_SIZE)

        for i in range(self.TOTAL_FRAME):
            image_path = data_path + "frame" + str(i) + ".png"
            img = cv2.imread(image_path)
            video.write(img)
        video.release()

        print("Pattern generates successful")

    def calibration_video_generation(self):
        # print("Inside calibration video_generation")
        data_path = "Images/picsForVideo/"
        self.VIDEO_SIZE = (self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

        self.video_name = "Calibration_" + str(self.FRAME_RATE) + "fps_" + str(self.DURATION) + "second" + ".mp4"

        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        video = cv2.VideoWriter(self.video_name, fourcc, self.FRAME_RATE, self.VIDEO_SIZE)

        for i in range(self.TOTAL_FRAME):
            image_path = data_path + "frame" + str(i) + ".png"
            img = cv2.imread(image_path)
            video.write(img)
        video.release()

        print("Pattern generates successful")

    def image_compose(self, start_frame, end_frame):
        # print("Inside image compose")
        to_image = Image.new('RGB', (self.IMAGE_COLUMN * self.PICS_SIZE, self.IMAGE_ROW * self.PICS_SIZE))

        k = 0

        for i in range(start_frame, end_frame):
            for x in range(0, self.IMAGE_ROW):
                for y in range(0, self.IMAGE_COLUMN):
                    if (self.DISTRIBUTION_MATRIX[x][y] == 1):
                        if (self.pse_matrix[k][i] == 0):
                            cur_path = self.IMAGES_PATH + "spot_color_off.png"
                        else:
                            cur_path = self.IMAGES_PATH + "spot_color_on.png"
                        k = (k + 1) % self.NUMBER_OF_SPOTS
                        from_image = Image.open(cur_path).resize((self.IMAGE_WIDTH, self.IMAGE_HEIGHT), Image.ANTIALIAS)
                    else:
                        from_image = Image.open(self.IMAGES_PATH + "base_color.png").resize(
                            (self.IMAGE_WIDTH, self.IMAGE_HEIGHT), Image.ANTIALIAS)
                    to_image.paste(from_image, (y * self.IMAGE_HEIGHT, x * self.IMAGE_WIDTH))

            # draw the cross
            cross_image = Image.open(self.IMAGES_PATH + "cross.png").resize((self.IMAGE_WIDTH, self.IMAGE_HEIGHT),
                                                                            Image.ANTIALIAS)
            r, g, b, a = cross_image.split()
            to_image.paste(cross_image, (int(self.IMAGE_COLUMN * self.PICS_SIZE / 2) - int(self.PICS_SIZE / 2),
                                         int(self.IMAGE_ROW * self.PICS_SIZE / 2) - int(self.PICS_SIZE / 2)), mask=a)

            target_path = self.IMAGE_SAVE_PATH + "frame" + str(i) + ".png"
            to_image.save(target_path)

        print("Frame images generate successful")

    def calibration_image_compose(self, start_frame, end_frame):
        # print("Inside image compose")
        to_image = Image.new('RGB', (self.SCREEN_WIDTH,self.SCREEN_HEIGHT))


        for i in range(start_frame, end_frame):
            if self.calibration_matrix[i] == 0.0:
                cur_path = self.IMAGES_PATH + "spot_color_off.png"
            else:
                cur_path = self.IMAGES_PATH + "spot_color_on.png"
            from_image = Image.open(cur_path).resize((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), Image.ANTIALIAS)
            to_image.paste(from_image)

            target_path = self.IMAGE_SAVE_PATH + "frame" + str(i) + ".png"
            to_image.save(target_path)

        print("Frame images generate successful")

    """Analysing EEG data from EEG channels 6(PO7) and 8(PO8) since it represents the channels for left and and right visual cortex in Unicorn biofeedback amplifier"""
    def analyse_EEG_data(self,datapath):
        #Loading, normalizing and filtering data before analysis.
        # windowSize = 250
        helper = eeglib.helpers.CSVHelper(datapath,
                                          lowpass=30, highpass=1, normalize=True, sampleRate=250)

        # Setting the window size to 1 seconds
        helper.prepareEEG(helper.sampleRate)

        helper.selectSignals(["EEG 6", "EEG 8"])
        helper.eeg.outputMode = "dict"
        # ,segmentation=[(("0","30"),0),(("15","60"),1)]
        wrap = eeglib.wrapper.Wrapper(helper)

        wrap.addFeature.bandPower(hideArgs=True, spectrumFrom='DFT')
        data = wrap.getAllFeatures()

        data = data.iloc[0:self.DURATION, :]
        return data

    def read_calibration_file(self):
        settings = []
        window_frames = []
        for line in open(self.UPLOAD_PATHS[3], "r"):
            line = line.strip()
            settings.append(line)

        self.FRAME_RATE = int(settings[0])
        self.DURATION = int(settings[3])
        self.FLASH_INTERVAl = settings[4]
        calibration_matrix =  self.generate_calibration_matrix()

        for i in range(0, len(calibration_matrix),  self.FRAME_RATE):
            window_frames.append(np.mean([calibration_matrix[i:i +  self.FRAME_RATE]]))
        return window_frames

    def generate_EEG_analysis_report(self):
        if len(self.UPLOAD_PATHS) == 4 and self.PATIENT_DETAILS[0] != '' and self.PATIENT_DETAILS[1] != '':
            if os.path.exists(os.getcwd() + '\\' + 'Plots\\'):
                windowed_calibration_matrix = self.read_calibration_file()

                #Filtering and Normalizing all EEG data
                without_headset = self.analyse_EEG_data(self.UPLOAD_PATHS[0])
                with_headset = self.analyse_EEG_data(self.UPLOAD_PATHS[1])
                with_test = self.analyse_EEG_data(self.UPLOAD_PATHS[2])

                #Calculating electrical Interference because of the VR Headset and and removing it for Channels 6 and 8
                interference_6 = with_headset['bandPower_EEG 6_beta'] - without_headset['bandPower_EEG 6_beta']
                interference_8 = with_headset['bandPower_EEG 8_beta'] - without_headset['bandPower_EEG 8_beta']
                with_test['bandPower_EEG 8_beta'] = with_test['bandPower_EEG 8_beta'] - interference_8
                with_test['bandPower_EEG 6_beta'] = with_test['bandPower_EEG 6_beta'] - interference_6

                #Plotting all graphs based on the sampling rate of the biofeedback amplifier(250Hz)
                fig = go.Figure(layout=dict(xaxis=dict(title='Time'), yaxis=dict(title='Amplitude')))
                fig.add_scatter(x=np.arange(0, self.DURATION), y=without_headset['bandPower_EEG 8_beta'])
                fig.update_layout(height=500,title_text='EEG Channel 8 Data Without Headset')
                fig.write_image("Plots/4.png")
                # fig.show()

                fig = go.Figure(layout=dict(xaxis=dict(title='Time'), yaxis=dict(title='Amplitude')))
                fig.add_scatter(x=np.arange(0, self.DURATION), y=with_headset['bandPower_EEG 8_beta'])
                fig.update_layout(height=500,title_text='EEG Channel 8 Data With Headset Without Test')
                fig.write_image("Plots/3.png")

                fig = go.Figure(layout=dict(xaxis=dict(title='Time'), yaxis=dict(title='Amplitude')))
                fig.add_scatter(x=np.arange(0, self.DURATION), y=with_test['bandPower_EEG 8_beta'])
                fig.update_layout(height=500,title_text='EEG Channel 8 Data With Headset With Test')
                fig.write_image("Plots/2.png")

                fig = go.Figure(layout=dict(xaxis=dict(title='Time'), yaxis=dict(title='Amplitude')))
                fig.add_scatter(x=np.arange(0, self.DURATION), y=windowed_calibration_matrix)
                fig.update_layout(height=500,title_text='Calibration Pulse Train')
                fig.write_image("Plots/1.png")

                fig = go.Figure(layout=dict(xaxis=dict(title='Time'), yaxis=dict(title='Amplitude')))
                fig.add_scatter(x=np.arange(0, self.DURATION), y=without_headset['bandPower_EEG 6_beta'])
                fig.update_layout(height=500, title_text='EEG Channel 6 Data Without Headset')
                fig.write_image("Plots/7.png")
                # fig.show()

                fig = go.Figure(layout=dict(xaxis=dict(title='Time'), yaxis=dict(title='Amplitude')))
                fig.add_scatter(x=np.arange(0, self.DURATION), y=with_headset['bandPower_EEG 6_beta'])
                fig.update_layout(height=500, title_text='EEG Channel 6 Data With Headset Without Test')
                fig.write_image("Plots/6.png")

                fig = go.Figure(layout=dict(xaxis=dict(title='Time'), yaxis=dict(title='Amplitude')))
                fig.add_scatter(x=np.arange(0, self.DURATION), y=with_test['bandPower_EEG 6_beta'])
                fig.update_layout(height=500, title_text='EEG Channel 6 Data With Headset With Test')
                fig.write_image("Plots/5.png")

                #Generate the report
                output_file = self.PATIENT_DETAILS[0]+'.pdf'
                filenames = [next(os.walk(os.getcwd() + '\\' + 'Plots\\'), (None, None, []))[2] ] # [] if no file
                pdf = PDF()
                for elem in filenames:
                    pdf.print_page(elem,self.PATIENT_DETAILS)

                pdf.output(output_file, 'F')
                print("Report generation successful!")
            else:
                print("Folder \Plots not found. Please create folder.")
        else:
            print("All file paths not found or Patient details missing. Upload all files or insert patient details.")

class Patient:
    patient_count = 0
    def __init__(self, NIN_number, name, birthday):
        self.NIN_number = NIN_number
        self.birthday = birthday
        self.name = name
        self.test_list = []
        Patient.patient_count += 1


class Test:
    def __init__(self, test_id, patient_name, test_time):
        self.patient_name = patient_name
        self.test_time = test_time
        self.test_id = test_id


class PDF(FPDF):
    def __init__(self):
        super().__init__()
        # Setting the height and width of the A4 sheet
        self.WIDTH = 210
        self.HEIGHT = 297

    def header(self,):
        self.set_font('Arial', 'B', 11)

    def footer(self):
        # Adding Page no.'s in the footer section
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

    def page_body(self, images=None,patient=None):
      #For printing patient details
        if patient != None:
            self.cell(5)
            self.cell(60, 1, 'Name:'+ patient[0], 0, 0, 'R')
            self.cell(5)
            self.cell(60, 1, 'Birthday:' + patient[1], 0, 0, 'R')
        if len(images) == 2:
            self.image(os.getcwd()+"\\Plots\\"+images[0], 5, 15, self.WIDTH-10)
            self.image(os.getcwd()+"\\Plots\\"+images[1], 5, 150, self.WIDTH-10)
        elif len(images) == 1:
            self.image(os.getcwd() + "\\Plots\\" + images[0], 5, 15, self.WIDTH - 10)
        else:
            self.cell(5)
            self.cell(60, 50, 'Images Not Found', 0, 0, 'R')

    def print_page(self, images,patient):
        # Generates the report
        self.add_page()
        self.page_body(images[0:2], patient)
        self.add_page()
        self.page_body(images[2:4])
        self.add_page()
        self.page_body(images[4:6])
        self.add_page()
        self.page_body(images[6:7])


