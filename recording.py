import pyaudio
import wave

class AudioRecorder:
    def __init__(self):
        self.is_recording = False
        self.frames = []

    def start_recording(self):
        self.is_recording = True
        self.frames = []
        self._record_audio()

    def stop_recording(self):
        self.is_recording = False
        self.save_audio()

    def _record_audio(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=44100,
                        input=True,
                        frames_per_buffer=1024)
        print("1/16 Запись началась...")
        
        while self.is_recording:
            data = stream.read(1024)
            self.frames.append(data)
        
        stream.stop_stream()
        stream.close()
        p.terminate()

    def save_audio(self):
        print("2/16 Сохранение файла...")
        with wave.open("output.wav", 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(self.frames))
        print("3/16 Запись сохранена в файл 'output.wav'.")