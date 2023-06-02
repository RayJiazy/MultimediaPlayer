# MultimediaPlayer
A multimedia player, which can divide the video and audio according to the scene,shot and subshot.

## Introduction
**Scene**: a group of shots with a context eg, all shots in the “apartment” room, or all shots in the “garden” scene. All the shots in a scene 
(sequence) are continuous and have common elements – background environment, actors. When a scene changes, the background environment,properties of sound levels all change.

**Shot**: Within a scene, shots are demarcated by an abrupt discontinuous change.

**Subshot**: If the shot has varying properties of interest(motion, noise levels), then the shot should be broken into subshots. For example,
a shot may consists of times when the motion or slow or no motion, and times when the motion is high - these could serve as separate subshots.

## Interaction
**Selective Segment**: Select the specified segment
**Play Button**: Play the selected segment
**Paus Button**: Pause the video
**Stop Button**: Stop the video and go back to the first frame of the specified segment

## Demo
![image](https://github.com/RayJiazy/MultimediaPlayer/blob/main/src/Effect.gif)   
