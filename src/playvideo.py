import sys
import cv2
import time
from PyQt5.QtWidgets import QSizePolicy, QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QScrollArea
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QImage
from ClickableLable import ClickableLabel
from Segement import segmentation
# from AudioWav import AudioWav
# from huggingface_hub import login
# from dotenv import load_dotenv
import os
from PyQt5 import __file__ as pyfile

def extract_frames(video_path):
    frames = []
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        # print("Error: Could not open the video file.")
        exit()
    while True:
        ret,frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()
    return frames

class Main_UI(QMainWindow):
    def __init__(self, video_path,scenes,audio_name,final_frame):
        super().__init__()
        self.fps = 30
        self.width = 480
        self.height = 270
        self.final_frame = final_frame
        self.state = -1
        self.scene_idx = -1
        self.shot_idx = -1
        self.subshot_idx = -1
        self.start_frame = -1
        self.end_frame = -1
        self.selected_label = None
        self.cur = -1
        self.player = None
        self.video_path = video_path
        self.init_video()
        self.scenes = scenes
        # self.audio = AudioWav(audio_name)

        # 主窗口设置
        self.setWindowTitle('Scrollable Video Player')
        self.setGeometry(100, 100, 800, 600)

        # 创建一个 QWidget 作为滚动区域的内容
        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)

        # 向 content_layout 添加多个 QLabel
        self.scene_labels = []
        self.shot_labels = []
        self.subshot_labels = []
        self.scenes = scenes
        for i in range(len(self.scenes)):
            label = ClickableLabel(f'Scene {i+1}',None, parent=self)
            self.scene_labels.append(label)
            content_layout.addWidget(label)
            scene = scenes[i]
            temp_shot = []
            temp_subshots = []
            for j in range(len(scene.shots)):
                child_label = ClickableLabel(f'\tShot {j+1}',label, self)
                temp_shot.append(child_label)
                content_layout.addWidget(child_label)
                shot = scene.shots[j]
                temp_subshot = []
                for r in range(len(shot.subshots)):
                    grandchild_label = ClickableLabel(f'\t\tSubShot {r+1}',child_label, self)
                    temp_subshot.append(grandchild_label)
                    content_layout.addWidget(grandchild_label)
                temp_subshots.append(temp_subshot)
            self.shot_labels.append(temp_shot)
            self.subshot_labels.append(temp_subshots)
        # print(self.shot_labels)
        # 创建一个 QScrollArea 并设置 content_widget 作为其内容
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.content_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        scroll_area.setFixedSize(300, 600)

        # 创建 QLabel 用于显示视频
        self.video_label = QLabel(self)
        self.video_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.video_label.setFixedSize(480, 270)
        self.video_label.setAlignment(Qt.AlignCenter)

        # 播放按钮设置
        self.play_button = QPushButton('Play', self)
        self.play_button.clicked.connect(self.play_video)

        # 暂停按钮设置
        self.pause_button = QPushButton('Pause', self)
        self.pause_button.clicked.connect(self.pause_video)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.clicked.connect(self.stop_video)

        # 右边界面布局
        left_layout = QVBoxLayout()
        video_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        left_layout.addWidget(scroll_area,alignment=Qt.AlignCenter)
        video_layout.addWidget(self.video_label,alignment=Qt.AlignCenter)
        button_layout.addWidget(self.play_button)
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.stop_button)
        right_layout.addLayout(video_layout)
        right_layout.addLayout(button_layout)
        # 主布局设置
        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)


    def init_video(self):
        self.cap = cv2.VideoCapture(self.video_path)
        self.timer = QTimer()
        self.timer.setTimerType(Qt.PreciseTimer)
        self.timer.timeout.connect(self.update_frame)
        self.paused = True
        self.inited = False

    def play_video(self):
        if self.start_frame != -1:
            # if not self.paused:
            #     if self.player:
            #         self.audio.stop(self.player)
            self.paused = False
            if not self.inited:
                self.inited = True
                # self.player = self.audio.player_start_from_frame(self.start_frame, self.fps)
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)
                self.timer.start(1000/(self.fps))
            else:
                if not self.timer.isActive():
                    # self.player = self.audio.player_start_from_frame(self.cur, self.fps)
                    self.timer.start(1000/(self.fps))

    def pause_video(self):
        if self.start_frame != -1:
            if self.timer.isActive():
                self.timer.stop()
                self.paused = True
                # self.audio.stop(self.player)
                # self.player = None


    def stop_video(self):
        if self.start_frame != -1:
            self.inited = False
            if self.timer.isActive():
                self.timer.stop()
                # self.audio.stop(self.player)
                # self.player = None
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)
            ret, frame = self.cap.read()
            frame = cv2.resize(frame, (self.width, self.height))
            self.show_frame(frame)
            self.paused = True


    def update_frame(self):
        ret, frame = self.cap.read()
        frame = cv2.resize(frame, (self.width, self.height))
        if not ret or int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) >= self.final_frame:
            self.timer.stop()
            # self.audio.stop(self.player)
            # self.player = None
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)
            ret, frame = self.cap.read()
            frame = cv2.resize(frame, (self.width, self.height))
            self.paused = True
            self.inited = False

        if ret and not self.paused:
            self.cur = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            # print(self.start_frame,self.end_frame,self.scene_idx,self.shot_idx,self.state)
            self.show_frame(frame)
            if self.state == 0:
                if self.end_frame >= self.cur >= self.start_frame:
                    # if has shot
                    if scenes[self.scene_idx].shots:
                        self.shot_idx = 0
                        self.subshot_idx = -1
                        self.selected_label.isSelected = False
                        self.selected_label.setStyleSheet("")
                        self.selected_label = self.shot_labels[self.scene_idx][self.shot_idx]
                        self.selected_label.isSelected = True
                        self.selected_label.setStyleSheet("background-color: blue")
                        self.start_frame = scenes[self.scene_idx].shots[self.shot_idx].start_frame
                        self.end_frame = scenes[self.scene_idx].shots[self.shot_idx].end_frame
                        self.state = 1
                # if from scene go to next scene
                elif self.cur > self.end_frame:
                    self.scene_idx += 1
                    self.shot_idx = -1
                    self.subshot_idx = -1
                    self.selected_label.isSelected = False
                    self.selected_label.setStyleSheet("")
                    self.selected_label = self.scene_labels[self.scene_idx]
                    self.selected_label.isSelected = True
                    self.selected_label.setStyleSheet("background-color: blue")
                    self.start_frame = scenes[self.scene_idx].start_frame
                    self.end_frame = scenes[self.scene_idx].end_frame

            elif self.state == 1:
                if self.end_frame >= self.cur > self.start_frame:
                    # if has subshot
                    if scenes[self.scene_idx].shots[self.shot_idx].subshots:
                        self.subshot_idx = 0
                        self.selected_label.isSelected = False
                        self.selected_label.setStyleSheet("")
                        self.selected_label = self.subshot_labels[self.scene_idx][self.shot_idx][self.subshot_idx]
                        self.selected_label.isSelected = True
                        self.selected_label.setStyleSheet("background-color: blue")
                        self.start_frame = scenes[self.scene_idx].shots[self.shot_idx].subshots[self.subshot_idx].start_frame
                        self.end_frame = scenes[self.scene_idx].shots[self.shot_idx].subshots[self.subshot_idx].end_frame
                        self.state = 2
                # if from shot go to next shot
                elif self.cur > self.end_frame:
                    # if has next shot
                    if self.shot_idx+1 < len(scenes[self.scene_idx].shots):
                        self.shot_idx += 1
                        self.subshot_idx = -1
                        self.selected_label.isSelected = False
                        self.selected_label.setStyleSheet("")
                        self.selected_label = self.shot_labels[self.scene_idx][self.shot_idx]
                        self.selected_label.isSelected = True
                        self.selected_label.setStyleSheet("background-color: blue")
                        self.start_frame = scenes[self.scene_idx].shots[self.shot_idx].start_frame
                        self.end_frame = scenes[self.scene_idx].shots[self.shot_idx].end_frame
                    # no next shot, go to scene
                    else:
                        self.scene_idx += 1
                        self.subshot_idx = -1
                        self.shot_idx = -1
                        self.selected_label.isSelected = False
                        self.selected_label.setStyleSheet("")
                        self.selected_label = self.scene_labels[self.scene_idx]
                        self.selected_label.isSelected = True
                        self.selected_label.setStyleSheet("background-color: blue")
                        self.start_frame = scenes[self.scene_idx].start_frame
                        self.end_frame = scenes[self.scene_idx].end_frame
                        self.state = 0

            elif self.state == 2:
                if self.cur > self.end_frame:
                    # if has next subshot
                    if self.subshot_idx+1 < len(scenes[self.scene_idx].shots[self.shot_idx].subshots):
                        self.subshot_idx += 1
                        self.selected_label.isSelected = False
                        self.selected_label.setStyleSheet("")
                        self.selected_label = self.subshot_labels[self.scene_idx][self.shot_idx][self.subshot_idx]
                        self.selected_label.isSelected = True
                        self.selected_label.setStyleSheet("background-color: blue")
                        self.start_frame = scenes[self.scene_idx].shots[self.shot_idx].subshots[self.subshot_idx].start_frame
                        self.end_frame = scenes[self.scene_idx].shots[self.shot_idx].subshots[self.subshot_idx].end_frame
                    # no next shot
                    else:
                        # go next shot
                        if self.shot_idx+1 < len(scenes[self.scene_idx].shots):
                            self.shot_idx += 1
                            self.subshot_idx = -1
                            self.selected_label.isSelected = False
                            self.selected_label.setStyleSheet("")
                            self.selected_label = self.shot_labels[self.scene_idx][self.shot_idx]
                            self.selected_label.isSelected = True
                            self.selected_label.setStyleSheet("background-color: blue")
                            self.start_frame = scenes[self.scene_idx].shots[self.shot_idx].start_frame
                            self.end_frame = scenes[self.scene_idx].shots[self.shot_idx].end_frame
                            self.state = 1
                        # next scene
                        elif self.scene_idx + 1 <= len(scenes):
                            self.scene_idx += 1
                            self.shot_idx = -1
                            self.subshot_idx = -1
                            self.selected_label.isSelected = False
                            self.selected_label.setStyleSheet("")
                            self.selected_label = self.scene_labels[self.scene_idx]
                            self.selected_label.isSelected = True
                            self.selected_label.setStyleSheet("background-color: blue")
                            self.start_frame = scenes[self.scene_idx].start_frame
                            self.end_frame = scenes[self.scene_idx].end_frame
                            self.state = 0

    def show_frame(self, frame):
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        qimg = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        self.video_label.setPixmap(pixmap)

if __name__ == '__main__':
    dirname = os.path.dirname(pyfile)
    plugin_path = os.path.join(dirname, 'Qt5','plugins', 'platforms')
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
    app = QApplication(sys.argv)
    video_name = sys.argv[1]
    audio_name = sys.argv[2]
    if "rgb" not in video_name:
        print("The incorrect video format.")
        exit()
    if "wav" not in audio_name:
        print("The incorrect audio format.")
        exit()
    video_path = "InputVideo.mp4"
    # load_dotenv()
    # login(os.getenv('HUGGINGFACE_TOKEN'), True)
    scenes,final_frame = segmentation(video_name, audio_name)
    player = Main_UI(video_path,scenes,audio_name,final_frame)
    player.show()
    sys.exit(app.exec_())
