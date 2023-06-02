from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt

def find_main_window(widget):
    while widget.parent() is not None:
        widget = widget.parent()
    return widget

class ClickableLabel(QLabel):
    def __init__(self, text, parent_label= None,parent=None):
        super(ClickableLabel, self).__init__(text, parent)
        self.setMouseTracking(True)
        self.isSelected = False
        self.parent_label = parent_label
        self.ui = parent
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.isSelected = not self.isSelected
            main_window = find_main_window(self)
            if self.isSelected:
                if main_window.selected_label:
                    main_window.selected_label.setStyleSheet("")
                    main_window.selected_label.isSelected = not main_window.selected_label.isSelected
                self.setStyleSheet("background-color: blue")
                main_window.selected_label = self
                # main_window.inited = False
                if main_window.paused:
                    main_window.inited = False
                if "Scene" in self.text()[:-1]:
                    # self.ui.pause_video()
                    main_window.state = 0
                    main_window.scene_idx = int(self.text().replace("Scene",""))-1
                    main_window.shot_idx = -1
                    main_window.subshot_idx = -1
                    # self.ui.play_video()
                elif "SubShot" in self.text()[:-1]:
                    # self.ui.pause_video()
                    main_window.state = 1
                    main_window.scene_idx = int(self.parent_label.parent_label.text().replace("Scene","")) - 1
                    main_window.shot_idx = int(self.parent_label.text().replace("Shot","")) - 1
                    main_window.subshot_idx = int(self.text().replace("SubShot","")) - 1
                    # self.ui.play_video()
                else:
                    # self.ui.pause_video()
                    main_window.state = 2
                    main_window.scene_idx = int(self.parent_label.text().replace("Scene","")) - 1
                    main_window.shot_idx = int(self.text().replace("Shot","")) - 1
                    main_window.subshot_idx = -1
                    # self.ui.play_video()
                if main_window.shot_idx == -1 and main_window.subshot_idx == -1:
                    main_window.start_frame,  main_window.end_frame = main_window.scenes[main_window.scene_idx].start_frame, main_window.scenes[
                        main_window.scene_idx].end_frame
                elif main_window.subshot_idx == -1:
                    main_window.start_frame,  main_window.end_frame = main_window.scenes[main_window.scene_idx].shots[main_window.shot_idx].start_frame, \
                        main_window.scenes[main_window.scene_idx].shots[main_window.shot_idx].end_frame
                else:
                    main_window.start_frame,  main_window.end_frame = main_window.scenes[main_window.scene_idx].shots[main_window.shot_idx].subshots[
                        main_window.subshot_idx].start_frame, \
                        main_window.scenes[main_window.scene_idx].shots[main_window.shot_idx].subshots[
                            main_window.subshot_idx].end_frame
                if main_window.inited:
                    main_window.inited = False
                    main_window.play_video()
            else:
                main_window.selected_label = None
                main_window.start_frame = -1
                self.setStyleSheet("")