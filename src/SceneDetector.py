from VideoRGB import VideoRGB
import numpy as np
from scipy import signal
import cv2


class SceneDetector:
    def __init__(self, video: VideoRGB):
        self.video = video


    def get_dct8(self, img):
        h, w = img.shape[:2]
        vis0 = np.zeros((h, w), np.float32)
        vis0[:h, :w] = img
        # DCT transformation
        vis1 = cv2.dct(cv2.dct(vis0))
        dct8_mat = cv2.resize(vis1, (8, 8))

        # creat 8*8 DCT matrix, by computing average using convolution and then downsampling
        # kernel = np.array([[1. / 16] * 4 for i in range(4)])
        # dct32_mat = signal.convolve2d(vis1, kernel, 'same')
        #
        # dct8_mat = np.zeros((8, 8))
        # for i in range(0, dct32_mat.shape[0], 4):
        #     for j in range(0, dct32_mat.shape[1], 4):
        #         dct8_mat[int(i / 4)][int(j / 4)] = dct32_mat[i, j]
        return dct8_mat

    def get_DCT8_list(self):
        dct_list = list()
        for i in range(self.video.frame_count):
            frame = self.video.get_frame(i)
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            image = cv2.resize(image, (64, 64), interpolation=cv2.INTER_CUBIC)
            dct = self.get_dct8(image)
            dct_list.append(dct)
        return dct_list

    def normalization(self, x):
        max_n = np.max(x)
        min_n = np.min(x)
        res = np.zeros(len(x))
        for i, item in enumerate(x):
            res[i] = (item - min_n) / (max_n - min_n)
        return res


    def get_avg_dct_of_clips(self, index):
        """
        get average DCT value of movie clips between each shot
        """
        dct_list = self.get_DCT8_list()
        shot_avg_dct = []
        for i in range(1, len(index)):
            begin = index[i - 1] + 1
            end = index[i]
            temp = np.zeros((8, 8))  # 8*8
            for ind in (begin, end):
                temp += dct_list[ind]
            temp = temp / (end - begin)
            shot_avg_dct.append(temp.flatten())
        return shot_avg_dct

    def split_scene(self, index_array, slack_variable):
        count = 0
        mark = 0
        find_zero = False
        find_next_oneset = False
        for i, val in enumerate(index_array):
            if val == False:
                find_zero = True
                if count == slack_variable:
                    break
                else:
                    count += 1
            else:
                mark = i
                if find_zero:
                    find_next_oneset = True
                continue
        return mark

    def merge_close_clips(self, index_scene):
        new_index = []
        begin = 0
        end = 0
        last = 0
        while end < (len(index_scene)-1):
            # print(begin, end)
            if (index_scene[end+1] - index_scene[end]) > 100:
                end += 1
                if index_scene[begin] - last > 100:
                    new_index.append(index_scene[begin])
                new_index.append(index_scene[end])
                last = index_scene[end]
                end +=1
                begin = end
            else:
                end += 1
        return new_index

    def get_sence_index(self, index_shot, bgm_intervals):
        """
        get the similarity of each clips, and then select with distance penalty

        """
        dct_clips = self.get_avg_dct_of_clips(index_shot)

        index_scene = []
        i = 0
        while i < len(dct_clips):
            # get the similarity of each clips
            dct_similarity = []
            for j in range(i, len(dct_clips)):
                dct_similarity.append(np.sum(np.abs(dct_clips[i] - dct_clips[j])))

            dct_similarity, index_temp = np.array(dct_similarity), np.array(index_shot)
            dct_similarity = np.abs(dct_similarity)

            # print('\n=========================')
            # print('SCENE INFO')
            # print(f'slack variable:{2}')
            # print(f'similarity threshold:{40}')
            index = np.array(dct_similarity < 40)
            index_split = self.split_scene(index, 2)
            temp = index_temp[i + 1:][index_split]
            # print(f'clips similarity under threshold:{index_temp[i + 1:][dct_similarity < 40]}')
            index_scene.append(temp)
            i = index_shot.index(temp)
            # print(f'final scene index added:{temp}')

        #         #first select
        #         dct_new = dct_similarity[dct_similarity < 40]
        #         index_temp = index_temp[i+1:][dct_similarity < 40]
        #         print('\n=========================')
        #         print('SCENE INFO')
        #         print(i)
        #         print(f'origin clips similarity:{dct_new}')

        #         #select with adding distance penalty
        #         dis_penalty = (index_temp-np.min(index_temp))/1000
        #         dct_new = np.exp(dis_penalty) + dct_new
        #         print(f'clips similarity with distance penalty:{dct_new}')
        #         index_temp = index_temp[dct_new<30]
        #         dct_new = dct_new[dct_new<30]
        #         print(f'according to shot indexes included:{index_temp}')

        #         if index_temp.tolist():
        #             temp = index_temp[-1]
        #             index_scene.append(temp)
        #             i = index_shot.index(temp)
        #         else:
        #             index_scene.append(index_shot[i])
        #             i+=1
        # print(f'origin:{index_scene}')
        print(index_scene)
        index_scene = self.merge_close_clips(index_scene)
        print(index_scene)
        # print(f'after merge:{index_scene}')
        index_scene = np.array(index_scene)
        # if bgm_intervals:
        #     select_index = np.ones(len(index_scene))
        #     for interval in bgm_intervals:
        #         start = interval[0]
        #         end = interval[1]
        #         start_frame = self.video.get_frame_number_from_time(start)
        #         end_frame = self.video.get_frame_number_from_time(end)
        #         for i, frame in enumerate(index_scene):
        #             if (frame > start_frame) and (frame < end_frame):
        #                 select_index[i] = 0
        #     index_scene = index_scene * select_index

        return index_scene.tolist()
