import sys
import cv2
from PyQt5.QtWidgets import QSizePolicy, QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QScrollArea
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QImage
from ClickableLable import ClickableLabel
from Segement import segmentation


def extract_frames(video_path):
    frames = []
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Could not open the video file.")
        exit()
    while True:
        ret,frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()
    return frames

class Main_UI(QMainWindow):
    def __init__(self, video_path,scenes):
        super().__init__()
        self.width = 576
        self.height = 324
        self.scene_idx = -1
        self.shot_idx = -1
        self.subshot_idx = -1
        self.start_frame = -1
        self.end_frame = -1
        self.selected_label = None
        self.video_path = video_path
        self.init_video()
        self.scenes = scenes
        # 主窗口设置
        self.setWindowTitle('Scrollable Video Player')
        self.setGeometry(100, 100, 800, 600)

        # 创建一个 QWidget 作为滚动区域的内容
        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)

        # 向 content_layout 添加多个 QLabel
        self.scenes = scenes
        for i in range(len(self.scenes)):
            label = ClickableLabel(f'Scene {i+1}',None, parent=self)
            content_layout.addWidget(label)
            scene = scenes[i]
            for j in range(len(scene.shots)):
                child_label = ClickableLabel(f'\tShot {j+1}',label, self)
                content_layout.addWidget(child_label)
                shot = scene.shots[j]
                for r in range(len(shot.subshots)):
                    grandchild_label = ClickableLabel(f'\t\tSubShot {r+1}',child_label, self)
                    content_layout.addWidget(grandchild_label)

        # 创建一个 QScrollArea 并设置 content_widget 作为其内容
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.content_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        scroll_area.setFixedSize(300, 600)

        # 创建 QLabel 用于显示视频
        self.video_label = QLabel(self)
        self.video_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.video_label.setFixedSize(600, 350)
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
        self.timer.timeout.connect(self.update_frame)
        self.paused = True
        self.inited = False

    def play_video(self):
        self.paused = False
        if not self.inited:
            self.inited = True
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)
            self.timer.start(30)
        else:
            if not self.timer.isActive():
                self.timer.start(30)

    def pause_video(self):
        if self.timer.isActive():
            self.timer.stop()
            self.paused = True


    def stop_video(self):
        if self.timer.isActive():
            self.timer.stop()
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)
        ret, frame = self.cap.read()
        frame = cv2.resize(frame, (self.width, self.height))
        self.show_frame(frame)
        self.paused = True

    def update_frame(self):
        ret, frame = self.cap.read()
        frame = cv2.resize(frame, (self.width, self.height))
        if not ret or int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) >= self.end_frame:
            self.timer.stop()
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)
            ret, frame = self.cap.read()
            frame = cv2.resize(frame, (self.width, self.height))
            self.paused = True

        if ret and not self.paused:
            self.show_frame(frame)

    def show_frame(self, frame):
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        qimg = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        self.video_label.setPixmap(pixmap)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    video_path = 'test.mp4'
    scenes = segmentation(0)
    player = Main_UI(video_path,scenes)
    player.show()
    sys.exit(app.exec_())
