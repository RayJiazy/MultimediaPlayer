import time
import wave
import librosa
import librosa.display
from spleeter.separator import Separator
import os
from pyannote.audio import Pipeline
import simpleaudio as sa

INACTIVE_SPEECH_GAP = 5

def time_from_sample_number(sample_number, sr):
    return sample_number / sr


def sample_number_from_time(time, sr):
    return int(time * sr)


class AudioWav:
    def __init__(self, audio_path):
        self.audio_path = audio_path
        self.wave_read = None
        self.data_original = None
        self.sample_rate = None  # Hz
        self.num_channels = None
        self.y = None
        self.sr = None
        self.length = None  # seconds
        self.sample_format = None
        self.bytes_per_sample = None
        self.dia = None
        self.pipeline = None
        self.speaker_intervals = []  # (speaker, start_time, end_time) speaker is a string, start_time and end_time are in seconds
        self.bgm_intervals = []  # (start_time, end_time) start_time and end_time are in seconds
        self.__get_audio()

    def __get_audio(self):
        # self.rate, self.data_original = wavfile.read(self.audio_path)
        self.y, self.sr = librosa.load(self.audio_path)
        self.wave_read = wave.open(self.audio_path, 'rb')
        self.data_original = self.wave_read.readframes(self.wave_read.getnframes())
        self.num_channels = self.wave_read.getnchannels()
        self.bytes_per_sample = self.wave_read.getsampwidth()
        self.sample_rate = self.wave_read.getframerate()

    def player_start_from_frame(self, idx, fps):
        # idx = 0 means start from the beginning
        frame = idx * 1.0 / fps * self.sample_rate
        self.wave_read.setpos(int(frame))
        audio_data = self.wave_read.readframes(self.wave_read.getnframes())
        wave_obj = sa.WaveObject(audio_data, self.num_channels, self.bytes_per_sample, self.sample_rate)
        return wave_obj.play()

    def player_start_from_frame_to_frame(self, idx_b, idx_e, fps):
        # idx = 0 means start from the beginning
        frame_b = idx_b * 1.0 / fps * self.sample_rate
        frame_e = idx_e * 1.0 / fps * self.sample_rate
        self.wave_read.setpos(int(frame_b))
        audio_data = self.wave_read.readframes(int(frame_e - frame_b) + 1)
        wave_obj = sa.WaveObject(audio_data, self.num_channels, self.bytes_per_sample, self.sample_rate)
        return wave_obj.play()

    def pause(self, sa_obj):
        sa_obj.pause()

    def resume(self, sa_obj):
        sa_obj.resume()

    def stop(self, sa_obj):
        sa_obj.stop()

    def wait_done(self, sa_obj):
        sa_obj.wait_done()

    def find_speaker_changes_within(self, start=0, end=None):  # [start, end) are in seconds
        if end is None:
            end = self.length
        self.speaker_diarization('./InputAudio/vocals.wav')
        speech_turn, track, speaker = next(self.dia.itertracks(yield_label=True))
        self.speaker_intervals.append((speaker, speech_turn.start, speech_turn.end))
        for speech_turn, track, speaker in self.dia.itertracks(yield_label=True):
            if speech_turn and track and speaker:
                if len(self.speaker_intervals) > 0:
                    if speaker != self.speaker_intervals[-1][0]:
                        if self.speaker_intervals[-1][2] - self.speaker_intervals[-1][1] < 1:
                                self.speaker_intervals.pop()
                        if len(self.speaker_intervals) > 0 and abs(speech_turn.start - self.speaker_intervals[-1][2]) < 0.0001:
                            self.speaker_intervals[-1] = (speaker, self.speaker_intervals[-1][1], speech_turn.end)
                        else:
                            self.speaker_intervals.append((speaker, speech_turn.start, speech_turn.end))
                    else:
                        if speech_turn.start - self.speaker_intervals[-1][2] > 4:
                            if self.speaker_intervals[-1][2] - self.speaker_intervals[-1][1] < 1:
                                    self.speaker_intervals.pop()
                            self.speaker_intervals.append((speaker, speech_turn.start, speech_turn.end))
                        else:
                            self.speaker_intervals[-1] = (speaker, self.speaker_intervals[-1][1], speech_turn.end)
                else:
                    self.speaker_intervals.append((speaker, speech_turn.start, speech_turn.end))
        return self.speaker_intervals

    def find_bgm_start_end(self):
        # load audio files with librosa
        y, sr = librosa.load('./InputAudio/accompaniment.wav')
        # split silence
        intervals = librosa.effects.split(y, top_db=20)
        # y_trimmed, index = librosa.effects.trim(y, top_db=20)
        intervals_after = []
        for s, e in intervals:
            ts = librosa.samples_to_time(s, sr=sr)
            te = librosa.samples_to_time(e, sr=sr)
            if te - ts >= 1.2:
                intervals_after.append((ts, te))
        prev_start_t, prev_end_t = intervals_after[0][0], intervals_after[0][1]
        flag = 0
        for s, e in intervals_after[1:]:
            if s - prev_end_t >= 1.2:
                self.bgm_intervals.append((prev_start_t, prev_end_t))
                prev_start_t, prev_end_t = s, e
                flag = 0
            else:
                prev_end_t = e
                flag = 1
        if flag:
            self.bgm_intervals.append((prev_start_t, prev_end_t))
        return self.bgm_intervals

    def vocal_bg_seperation(self):
        if not os.path.exists('./InputAudio'):
            separator = Separator('spleeter:2stems')
            separator.separate_to_file(self.audio_path, '.')

    def speaker_diarization(self, path):
        self.pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization@develop")
        self.pipeline.to(0)
        self.dia = self.pipeline(path, min_speakers=2, max_speakers=5)


if __name__ == "__main__":
    from VideoRGB import VideoRGB
    # video = VideoRGB("../data/video/Ready_Player_One_rgb/InputVideo.rgb", 8682, 30, 480, 270)
    audio = AudioWav('InputAudio.wav')
    # audio.play_audio_all()
    # audio.find_speaker_changes_within()
    # audio.find_bgm_start_end()
    # for ss, s, e in audio.speaker_intervals:
    #     ts = video.get_frame_number_from_time(s)
    #     te = video.get_frame_number_from_time(e)
    #     video.show_frame(ts)
    #     video.show_frame(te)
    #     print(f"speaker: {ss}, start: {s}, end: {e}, start_frame: {ts}, end_frame: {te}")
        # print(f"speaker: {ss}, start: {s}, end: {e}, start_frame: {ts}")
    # audio.play_audio()
    # for s, e in audio.bgm_intervals:
    #     ts = video.get_frame_number_from_time(s)
    #     te = video.get_frame_number_from_time(e)
    #     video.show_frame(ts)
    #     video.show_frame(te)
    #     print(f"start: {s}, end: {e}, start_frame: {ts}, end_frame: {te}")
    player = audio.player_start_from_frame(100, 30)
    time.sleep(5)
    audio.pause(player)
    time.sleep(5)
    audio.resume(player)
    time.sleep(5)
    audio.stop(player)
    # player = audio.player_start_from_frame_to_frame(0, 30, 30)
    # time.sleep(5)
    # audio.pause(player)
    # time.sleep(5)
    # audio.resume(player)
    # audio.wait_done(player)