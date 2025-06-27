import asyncio
import assemblyai as aai

class AudioAnalytics:
    def __init__(self, api_key):
        #  API для AssemblyAI
        aai.settings.api_key = api_key

    async def transcribe_audio(self, audio_file_path):
        transcriber = aai.Transcriber(config=aai.TranscriptionConfig(
            speech_model=aai.SpeechModel.best,
            language_detection=False, 
            language_code='ru'  
        ))
        transcript = await asyncio.to_thread(transcriber.transcribe, audio_file_path)
        if transcript.status == aai.TranscriptStatus.error:
            print(f"❌Ошибка транскрипции: {transcript.error}")
        else:
            print("4/16 ✅ Транскрипция завершена!")
            await self.save_transcription(transcript.text)

    async def save_transcription(self, text):
        with open('output.txt', 'w', encoding='utf-8') as f:
            f.write(text)
        print("5/16 ✅ Транскрипция сохранена в файл 'output.txt' с кодировкой UTF-8.")

    async def full_analysis_workflow(self, audio_file_path, analyzer):
        await self.transcribe_audio(audio_file_path)
        analyzer.run_analysis_from_file()