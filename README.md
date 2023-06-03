# MultimediaPlayer
A multimedia player, which can divide the video and audio according to the scene,shot and subshot. 

Users can play or pause the specified segment through interaction.

For the projects developed by the team, the contributors are not only me but also :

[@ChengweiZhou](https://github.com/ChengwZhou)

[@JasonGuojz](https://github.com/JasonGuojz)

[@PeijieXu](https://github.com/PeijieXu)

## Introduction
**Scene**: a group of shots with a context eg, all shots in the “apartment” room, or all shots in the “garden” scene. All the shots in a scene 
(sequence) are continuous and have common elements – background environment, actors. When a scene changes, the background environment,properties of sound levels all change.

**Shot**: Within a scene, shots are demarcated by an abrupt discontinuous change.

**Subshot**: If the shot has varying properties of interest(motion, noise levels), then the shot should be broken into subshots. For example,
a shot may consists of times when the motion or slow or no motion, and times when the motion is high - these could serve as separate subshots.

## Interaction
**Selective Segment**: Select the specified segment, the selected segment will be highlighted

**Play Button**: Play from the selected segment

**Pause Button**: Pause the video

**Stop Button**: Stop the video and go back to the first frame of the specified segment

*As the video plays continuously, the highlighted segment selection (scene, sequence, shot) should correspondingly update.*

## Demo

![image](https://github.com/RayJiazy/MultimediaPlayer/blob/main/images/demo.gif))   

## Instruction
```
python playvideo.py InputVideo.rgb InputAudio.wav
```
*InputVideo.rgb*: the input video

*InputAudio.wav*: the input audio

## Environment
* Pytorch
* PyQt5
* Scipy
* OpenCV
* Huggingface
* dotenv
* matplotlib

## Reference
[1] A. Massoudi, F. Lefebvre, C. . -h. Demarty, L. Oisel and B. Chupeau, "A Video Fingerprint Based on Visual Digest and Local Fingerprints," 2006 International Conference on Image Processing, Atlanta, GA, USA, 2006, pp. 2297-2300, doi: 10.1109/ICIP.2006.312834.

[2] [https://blog.csdn.net/wjpwjpwjp0831/article/details/118424311](https://blog.csdn.net/wjpwjpwjp0831/article/details/118424311)

[3] [https://github.com/Greedysky/TTKWidgetTools](https://github.com/Greedysky/TTKWidgetTools)
