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

def seg_scene(frames):
    # # seg video
    scenes = []
    for i in range(10):
        scenes.append([i*120,(i+1)*120-1])
    return scenes

def seg_shot(start_scene,end_scene):
    # # seg scene
    shots = []
    for i in range(3):
        shots.append([start_scene+(i*40),start_scene+((i+1)*40)-1])
    return shots

def seg_subshot(start_shot,end_shot):
    # # seg shot
    subshots = []
    for i in range(2):
        subshots.append([start_shot+(i*20),start_shot+((i+1)*20)-1])
    return subshots

def segmentation(frames):
    idx_scenes = seg_scene(frames)
    n_scene = len(idx_scenes)
    Scenes = []
    for i in range(n_scene):
        start_scene,end_scene = idx_scenes[i][0], idx_scenes[i][1]
        scene = Scene(start_scene, end_scene)
        Scenes.append(scene)
        idx_shots = seg_shot(start_scene,end_scene)
        n_shot = len(idx_shots)
        for j in range(n_shot):
            start_shot,end_shot = idx_shots[j][0],idx_shots[j][1]
            shot = Shot(start_shot,end_shot)
            scene.add_shot(shot)
            idx_subshots = seg_subshot(start_shot,end_shot)
            n_subshots = len(idx_subshots)
            for r in range(n_subshots):
                start_subshot, end_subshot = idx_subshots[r][0], idx_subshots[r][1]
                subshot = SubShot(start_subshot, end_subshot)
                shot.add_subshot(subshot)
    return Scenes

scenes = segmentation([10])
