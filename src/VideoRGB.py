import cv2
import numpy as np


class VideoRGB:
    def __init__(self, rgb_path, fps, width, height):
        self.rgb_path = rgb_path
        self.images = None
        self.frame_count = None
        self.fps = fps
        self.width = width
        self.height = height
        self.duration = None
        self.frame_size = (self.width, self.height)
        self.__get_video()

    def __get_video(self):
        data = np.fromfile(self.rgb_path, dtype='uint8')
        self.frame_count = int(len(data) / (self.width * self.height * 3))
        self.duration = self.frame_count / self.fps
        self.images = np.reshape(data, (self.frame_count, self.height, self.width, 3))[..., ::-1]

    def show_frame(self, frame_number):
        cv2.imshow('frame', self.images[frame_number])
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def play_video_original(self):
        for frame in self.images:
            cv2.imshow('frame', frame)
            if cv2.waitKey(1000 // self.fps) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()

    def save_into_mp4(self, output_path):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, self.fps, self.frame_size)
        for frame in self.images:
            out.write(frame)
        out.release()

    def get_frame(self, frame_number):
        return self.images[frame_number]

    def get_frame_count(self):
        return self.frame_count

    def get_fps(self):
        return self.fps

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_duration(self):
        return self.duration

    def get_frame_size(self):
        return self.frame_size

    def get_frame_number_from_time(self, time):
        return int(time * self.fps)

    def get_time_from_frame_number(self, frame_number):
        return frame_number / self.fps

    def get_frame_number_from_percent(self, percent):
        return int(percent * self.frame_count)

    def get_percent_from_frame_number(self, frame_number):
        return frame_number / self.frame_count

    def get_time_from_percent(self, percent):
        return percent * self.duration

    def get_percent_from_time(self, time):
        return time / self.duration

    def get_frame_from_percent(self, percent):
        frame_number = self.get_frame_number_from_percent(percent)
        return self.get_frame(frame_number)


if __name__ == "__main__":
    video = VideoRGB('../data/video/The_Long_Dark_rgb/InputVideo.rgb', 6276, 30, 480, 270)
    video.play_video_original()
    video.save_into_mp4('../data/video/The_Long_Dark_rgb/OutputVideo.mp4')
