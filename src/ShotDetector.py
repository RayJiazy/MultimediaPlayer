from VideoRGB import VideoRGB
import numpy as np
import cv2

class ShotDetector:
  def __init__(self, video: VideoRGB):
    self.video = video
    self.frame_cnt = video.get_frame_count()
    self.orb = cv2.ORB_create(nfeatures = int(1e3))
    self.bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    self.shots = [0]
    self.subshots = []
    self.cache = (-1, None, (None, None))
    self.data = []
    self.video_brightness = 0

  def pHash(self, img):
    """get image pHash fingerprint of 32*32 gray image
    Input: numpy.ndarray
    Ouput: String
    """
    h, w = img.shape[:2]
    vis0 = np.zeros((h, w), np.float32)
    vis0[:h, :w] = img
    # DCT transformation
    vis1 = cv2.dct(cv2.dct(vis0))
    vis1 = cv2.resize(vis1,(32, 32))
    img_list = vis1.flatten()
    #average
    avg = sum(img_list) * 1. / len(img_list)
    avg_list = ['0' if i < avg else '1' for i in img_list]
    
    return ''.join(['%x' % int(''.join(avg_list[x:x + 4]), 2) for x in range(0, 32 * 32, 4)])
  
  def hammingDist(self, s1, s2):
    """
    method-1 comparing hamming distance
    """
    return 1 - sum([ch1 != ch2 for ch1, ch2 in zip(s1, s2)]) * 1. / (32 * 32 / 4)
  
  def calculate_diff(self, frame1_idx: int, frame2_idx: int) :

    if self.cache[0] != frame1_idx:
      gray1 = cv2.cvtColor(self.video.get_frame(frame1_idx), cv2.COLOR_BGR2GRAY)
      # sharpen the images
      lap1 = cv2.convertScaleAbs(cv2.Laplacian(gray1, cv2.CV_16S, ksize=3))
      kps1, des1 = self.orb.detectAndCompute(lap1, None)
    else:
      gray1 = self.cache[1]
      kps1, des1 = self.cache[2]
     
    gray2 = cv2.cvtColor(self.video.get_frame(frame2_idx), cv2.COLOR_BGR2GRAY)
    # sharpen the images
    lap2 = cv2.convertScaleAbs(cv2.Laplacian(gray2, cv2.CV_16S, ksize=3))
    kps2, des2 = self.orb.detectAndCompute(lap2, None)
    self.cache = (frame2_idx, gray2, (kps2, des2))
    
    hamming_dist = self.hammingDist(self.pHash(gray1), self.pHash(gray2))
    
    if min(len(kps1), len(kps2)) < 100:
      self.data.append((frame2_idx, 0, 0, 0, 0))
      return
      
    matches = self.bf.match(des1, des2)
    # matches = sorted(matches, key=lambda x:x.distance)

    brightness = np.mean(gray2)
    self.video_brightness += brightness

    match_cnt = len(matches)    
    
    match_ratio = match_cnt/min(len(kps1), len(kps2))*100
    
    self.data.append((frame2_idx, hamming_dist, match_cnt, brightness, match_ratio))
    
    
  def pick_shots(self, step_size, 
    orb_th_low:int = 50, orb_th_high:int = 100, 
    bright_th_low:int = 10, bright_th_high:int = 30):
    self.video_brightness /= len(self.data)

    for i in range(1, len(self.data)):
      _, hamming_dist_last, match_cnt_last, brightness_last, match_ratio_last = self.data[i-1]
      frame_idx, hamming_dist, match_cnt, brightness, match_ratio = self.data[i]
      
      time = frame_idx / self.video.get_fps()
      mins = int(time/60)
      secs = float(time%60)
      time_f = '{}:{} {} '.format(mins, "%2.1f"%secs, "%.1f"%time)
      
      if hamming_dist == 0:
        # print('  \t{}\t: {}\t{}\t{}\t{} '.format(time_f, '%.2f' % 0 , '%.1f' % 0, 0, '%.1f'%(0)))
        continue
      
      brightness_diff = abs(brightness_last - brightness)

      res = 0
      
      if brightness > 15:
        if match_cnt > 3 * orb_th_high or match_ratio > 50 or hamming_dist > 0.96:
          res = 0
        elif ((hamming_dist < 0.5 or hamming_dist_last - hamming_dist > 0.2) and brightness > 24) or brightness_diff > bright_th_high:
          res = 2
        elif abs(match_ratio_last - match_ratio) > 10 or abs(match_ratio_last - match_ratio) * 2 + brightness_diff >  40 :
          if match_cnt >=150 and brightness_diff > 5:
            res = 2
          else: res = 3
        elif match_ratio - brightness_diff < 20  and brightness > 35:
          if brightness_diff <10 and match_cnt < 200:
            res = 3
          elif hamming_dist < 0.85:
            res = 1
        elif match_cnt_last - match_cnt > 200:
          res = 1
      else:  # dark scene
        if hamming_dist_last == 0:
          res = 2
        if hamming_dist < 0.4 or hamming_dist_last - hamming_dist > 0.2 or brightness_diff > bright_th_high:
          res = 2

      # if abs(time -(60*2+58)) < 2 and res!=2:
      #   print('->\t{}\t: {}\t{}\t{}\t{} %'.format(time_f, '%.2f' % hamming_dist , '%.1f' % brightness, match_cnt, '%.1f'%(match_ratio)))
      
      
      if res == 2:
        # print('++\t{}\t: {}\t{}\t{}\t{} \t%'.format(time_f, '%.2f' % hamming_dist , '%.1f' % brightness, match_cnt, '%.1f'%(match_ratio)))
        if self.shots[-1] < frame_idx - step_size:
          self.shots.append(frame_idx)
      elif res == 1:
        # print(' +\t{}\t: {}\t{}\t{}\t{} \t%'.format(time_f, '%.2f' % hamming_dist , '%.1f' % brightness, match_cnt, '%.1f'%(match_ratio)))
        if self.shots[-1] < frame_idx - step_size:
          self.shots.append(frame_idx)
      elif res == 3:
        self.subshots.append(frame_idx)
        # print(' s\t{}\t: {}\t{}\t{}\t{} %'.format(time_f, '%.2f' % hamming_dist , '%.1f' % brightness, match_cnt, '%.1f'%(match_ratio)))
      # else:
        # print('  \t{}\t: {}\t{}\t{}\t{} '.format('%.1f' %time, '%.2f' % hamming_dist , '%.1f' % brightness_diff, match_cnt, '%.1f'%(match_ratio)))
        
    
  def find_shots(self, step_size:int = 9):
    
    
    for frame_idx in range(step_size, self.frame_cnt, step_size):
      self.calculate_diff(frame_idx - step_size, frame_idx)
      
    self.pick_shots(step_size)

    
    return self.shots, self.subshots
