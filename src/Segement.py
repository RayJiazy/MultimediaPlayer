from VideoRGB import VideoRGB
# from AudioWav import AudioWav
from ShotDetector import ShotDetector
from SceneDetector import SceneDetector


class SubShot:
    def __init__(self, start_frame, end_frame):
        self.start_frame = start_frame
        self.end_frame = end_frame


class Shot:
    def __init__(self, start_frame, end_frame):
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.subshots = []

    def add_subshot(self, subshot):
        self.subshots.append(subshot)


class Scene:
    def __init__(self, start_frame, end_frame):
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.shots = []

    def add_shot(self, shot):
        self.shots.append(shot)


def seg_shot(start_scene, end_scene, idx_shots):
    # # seg scene
    shots = []
    for i in range(len(idx_shots)):
        shot = idx_shots[i]
        if shot[0] >= start_scene and shot[1] <= end_scene:
            shots.append([shot[0], shot[1]])
    return shots


def seg_subshot(start_shot, end_shot, idx_subshots):
    # # seg shot
    subshots = []
    for i in range(len(idx_subshots)):
        shot = idx_subshots[i]
        if shot[0] >= start_shot and shot[1] <= end_shot:
            subshots.append([shot[0], shot[1]])
    return subshots


def segmentation(video_name, audio_name):
    video_width = 480
    video_height = 270
    video_fps = 30
    video = VideoRGB(video_name, video_fps, video_width, video_height)
    video_framenum = video.frame_count
    # audio = AudioWav(audio_name)
    video.save_into_mp4("InputVideo.mp4")
    detector = ShotDetector(video)
    detector_scene = SceneDetector(video)
    index_shot, index_subshot = detector.find_shots()
    index_scene = detector_scene.get_sence_index(index_shot,[])
    index_scene.insert(0, 0)
    # audio.vocal_bg_seperation()
    # audio.find_speaker_changes_within()
    # audio.find_bgm_start_end()

    # ----------Scene Merge----------- #
    # scene_i, bgm_i = 0, 0
    # bgm_b = 0
    # while scene_i < len(index_scene) and bgm_i < len(audio.bgm_intervals):
    #     scene_b = index_scene[scene_i]
    #     if scene_i == len(index_scene) - 1:
    #         scene_e = video_framenum - 1
    #     else:
    #         scene_e = index_scene[scene_i + 1] - 1
    #     while bgm_i < len(audio.bgm_intervals):
    #         bgm_b, _ = audio.bgm_intervals[bgm_i]
    #         bgm_b = int(bgm_b * video_fps)
    #         if scene_b < bgm_b < scene_e:
    #             if scene_e - bgm_b > 1 * video_fps and bgm_b - scene_b > 2 * video_fps:
    #                 index_scene.insert(scene_i + 1, bgm_b)
    #                 scene_i += 1
    #         else:
    #             break
    #         bgm_i += 1
    #     if bgm_b >= scene_e:
    #         scene_i += 1
    #     else:
    #         bgm_i += 1
    # -------------------------------- #

    # ----------Sub-shot Merge-------- #
    # subshot_i, speaker_i = 0, 0
    # speaker_b = 0
    # while subshot_i < len(index_subshot) and speaker_i < len(audio.speaker_intervals):
    #     subshot_b = index_subshot[subshot_i]
    #     if subshot_i == len(index_subshot) - 1:
    #         subshot_e = video_framenum - 1
    #     else:
    #         subshot_e = index_subshot[subshot_i + 1] - 1
    #     while speaker_i < len(audio.speaker_intervals):
    #         _, speaker_b, _ = audio.speaker_intervals[speaker_i]
    #         speaker_b = int(speaker_b * video_fps)
    #         if subshot_b < speaker_b < subshot_e:
    #             if subshot_e - speaker_b > 0.1 * video_fps and speaker_b - subshot_b > 0.1 * video_fps:
    #                 index_subshot.insert(subshot_i + 1, speaker_b)
    #                 subshot_i += 1
    #         else:
    #             break
    #         speaker_i += 1
    #     if speaker_b < subshot_b:
    #         index_subshot.insert(subshot_i, speaker_b)
    #         speaker_i += 1
    #         continue
    #     subshot_i += 1

    # -------------------------------- #

    n_scene = len(index_scene)
    n_shot = len(index_shot)
    n_subshot = len(index_subshot)

    idx_scenes = []
    index_shots = []
    idx_subshots = []
    for k in range(n_scene - 1):
        idx_scenes.append([index_scene[k], index_scene[k + 1] - 1])
    idx_scenes.append([index_scene[n_scene - 1], video_framenum - 1])
    for k in range(n_shot - 1):
        index_shots.append([index_shot[k], index_shot[k + 1] - 1])
    index_shots.append([index_shot[n_shot - 1], video_framenum - 1])
    for k in range(n_subshot - 1):
        idx_subshots.append([index_subshot[k], index_subshot[k + 1] - 1])
    idx_subshots.append([index_subshot[n_subshot - 1], video_framenum - 1])
    Scenes = []
    for i in range(n_scene):
        start_scene, end_scene = idx_scenes[i][0], idx_scenes[i][1]
        scene = Scene(start_scene, end_scene)
        Scenes.append(scene)
        idx_shots = seg_shot(start_scene, end_scene, index_shots)
        # print(idx_shots)
        n_shot = len(idx_shots)
        for j in range(n_shot):
            start_shot, end_shot = idx_shots[j][0], idx_shots[j][1]
            shot = Shot(start_shot, end_shot)
            scene.add_shot(shot)
            indx_subshots = seg_subshot(start_shot, end_shot, idx_subshots)
            # print(idx_subshots)
            n_subshots = len(indx_subshots)
            for r in range(n_subshots):
                start_subshot, end_subshot = indx_subshots[r][0], indx_subshots[r][1]
                # if start_subshot - start_shot < 0.5 * video_fps:
                #     continue
                subshot = SubShot(start_subshot, end_subshot)
                shot.add_subshot(subshot)
    return Scenes,video_framenum-1
