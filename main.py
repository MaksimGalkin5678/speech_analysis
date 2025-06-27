import tkinter as tk
from tkinter import ttk
from threading import Thread
import asyncio
from pymorphy2 import MorphAnalyzer
from recording import AudioRecorder
from transcription import AudioAnalytics
from analyze import Analyzer
from analyze import analyze_lexical_variety
from db import init_db, get_all_count_words, get_latest_tip, get_all_new_words, get_latest_convincingness_score

class RecorderApp(tk.Tk):
    def __init__(self, recorder, analytics, analyzer):
        super().__init__()
        self.title('Аналитика речи')
        self.geometry('700x500')
        self.configure(bg='#F8F9FA')
        self.resizable(False,False)

        self.recorder = recorder
        self.analytics = analytics
        self.analyzer = analyzer
        self.morph = MorphAnalyzer()

        self.main_frame = tk.Frame(self, bg='#F8F9FA')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


        # Аналитика (лево)
        self.analytics_frame = tk.Frame(self.main_frame, width=335, height=340, bg='#CCE5FF')
        self.analytics_frame.place(x=0, y=0)
        self.analytics_label = tk.Label(self.analytics_frame, text='Аналитика', font=('Inter', 14, 'bold'), bg='#CCE5FF', justify='center')
        self.analytics_label.place(x=10, y=5, width=305, height=30)

        self.TOP5_label = tk.Label(self.analytics_frame, text='5 самых часто используемых слов:', font=('Inter', 12, 'bold'), bg='#CCE5FF', justify='left', anchor='nw')
        self.TOP5_label.place(x=10, y=35)
        self.words_label = tk.Label(self.analytics_frame, text='', font=('Inter', 11), bg='#CCE5FF', justify='left', anchor='nw', wraplength=300)
        self.words_label.place(x=10, y=60, width=320, height=90)

        # # Убедительность
        # # # Заголовок
        self.convincing_title_label = tk.Label(self.analytics_frame, text='Убедительность речи', font=('Inter', 12, 'bold'), bg='#CCE5FF')
        self.convincing_title_label.place(x=10, y=160)
        # # # Оценка
        self.convincing_score_label = tk.Label(self.analytics_frame, text='', font=('Inter', 11), bg='#CCE5FF', justify='left')
        self.convincing_score_label.place(x=10, y=185)
        # # # Комментарий
        self.convincing_comment_label = tk.Label(self.analytics_frame, text='', font=('Inter', 10), bg='#CCE5FF', wraplength=300, justify='left', anchor='nw')
        self.convincing_comment_label.place(x=10, y=205, width=300, height=50)

        # # Оценка лексического разнообразия
        # # # Заголовок
        self.variety_label_title = tk.Label(self.analytics_frame, text='Лексическое разнообразие', font=('Inter', 12, 'bold'), bg='#CCE5FF')
        self.variety_label_title.place(x=10, y=260)
        # # # Вывод описания/пояснения
        self.variety_label = tk.Label(self.analytics_frame, text='', font=('Inter', 11), bg='#CCE5FF', justify='left', wraplength=300)
        self.variety_label.place(x=10, y=285)
        # # # Слово Оценка:
        self.variety_level_text_label = tk.Label(self.analytics_frame, text='Богатство лексики:', font=('Inter', 11), bg='#CCE5FF', justify='left', wraplength=300)
        self.variety_level_text_label.place(x=10, y=310)
        # # # Вывод оценки раскрашенной
        self.variety_level_label = tk.Label(self.analytics_frame, text='', font=('Inter', 11, 'underline'), bg='#CCE5FF', justify='left', wraplength=300)
        self.variety_level_label.place(x=145, y=310)


        # Советы (право верх)
        self.tips_frame = tk.Frame(self.main_frame, width=335, height=165, bg='#FFF3CD')
        self.tips_frame.place(x=345, y=0)
        self.tips_label = tk.Label(self.tips_frame, text='Совет по улучшению речи', font=('Inter', 16, 'bold'), bg='#FFF3CD', justify='center')
        self.tips_label.place(x=10, y=5, width=305, height=32)
        self.tip_text_label = tk.Label(self.tips_frame, text='', font=('Inter', 11), bg='#FFF3CD', wraplength=310, justify='left', anchor='nw')
        self.tip_text_label.place(x=10, y=37, width=310, height=120)


        # Задания (право низ)
        self.tasks_frame = tk.Frame(self.main_frame, width=335, height=165, bg='#D4EDDA')
        self.tasks_frame.place(x=345, y=175)
        self.tasks_label = tk.Label(self.tasks_frame, text='Изучите новые слова', font=('Inter', 16, 'bold'), bg='#D4EDDA', justify='center')
        self.tasks_label.place(x=10, y=5, width=305, height=32)
        # # 1-е слово и его значение
        self.task_word1_label = tk.Label(self.tasks_frame, text='', font=('Inter', 11, 'underline'), bg='#D4EDDA')
        self.task_word1_label.place(x=10, y=40)
        self.task_meaning1_label = tk.Label(self.tasks_frame, text='', font=('Inter', 10), bg='#D4EDDA', wraplength=310, justify='left')
        self.task_meaning1_label.place(x=10, y=60)
        # # 2-е слово и его значение
        self.task_word2_label = tk.Label(self.tasks_frame, text='', font=('Inter', 11, 'underline'), bg='#D4EDDA')
        self.task_word2_label.place(x=10, y=100)
        self.task_meaning2_label = tk.Label(self.tasks_frame, text='', font=('Inter', 10), bg='#D4EDDA', wraplength=310, justify='left')
        self.task_meaning2_label.place(x=10, y=120)


        # Блок записи (внизу)
        self.record_frame = tk.Frame(self.main_frame, height=130, width=680, bg="#E9ECEF")
        self.record_frame.place(x=0, y=350)

        self.status_label = tk.Label(self.record_frame, text='Готов к записи', font=('Inter', 10), bg='#E9ECEF', fg='gray')
        self.status_label.place(x=290, y=0)
        self.record_button = tk.Canvas(self.record_frame, width=103, height=103, bg="#E9ECEF", highlightthickness=0)
        self.record_circle = self.record_button.create_oval(2, 2, 98, 98, fill='#8CE99A')
        self.record_icon = self.record_button.create_text(49, 45, text='▶', font=('Inter', 20), anchor='center')
        self.record_text = self.record_button.create_text(49, 70, text='Начать', font=('Inter', 11, 'bold'), fill='black')
        self.record_button.bind('<Button-1>', self.toggle_recording)
        self.record_button.place(x=285, y=20)

        self.progress = ttk.Progressbar(self.record_frame, orient='horizontal', mode='determinate', length=660)
        self.progress_label = tk.Label(self.record_frame, text='', font=('Inter', 10), bg='#A3B18A')
        self.progress.place_forget()
        self.progress_label.place_forget()


        # Необходимые переменные
        # # Для комментария убедительности
        self.full_convincing_comment = ''
        self.is_comment_expanded = False

        # # Для совета
        self.full_tip_text = ''
        self.short_tip_text = ''
        self.is_tip_expanded = False

        # # Для новых слов
        self.expanded_task_word = None
        self.task_meaning1_label.bind('<Button-1>', lambda e: self.toggle_task_meaning('word1'))
        self.task_meaning2_label.bind('<Button-1>', lambda e: self.toggle_task_meaning('word2'))
        self.task_meaning1_label.config(cursor='hand2')
        self.task_meaning2_label.config(cursor='hand2')

        # # Для записи
        self.pulse_active = False
        self.pulse_state = 0  # от 0 до 1 (увеличивается и уменьшается)

        # Обновление интерфейса
        self.refresh_count_words_display()
        self.refresh_tip_display()
        self.refresh_task_words_display()
        self.refresh_variety_display()
        self.refresh_convincingness_display() 


    # Обработка нажатия кнопки записи
    def toggle_recording(self, event=None):
        if self.recorder.is_recording:
            self.recorder.stop_recording()
            self.record_button.itemconfig(self.record_circle, fill='#7AE28B')
            self.record_button.itemconfig(self.record_icon, text='⏸')
            self.record_button.itemconfig(self.record_text, text='', fill='black')
            self.status_label.config(text='Анализ аудио...', fg='#FFA500')
            self.start_full_analysis("output.wav") 
            self.pulse_active = False
            self.record_button.coords(self.record_circle, 2, 2, 98, 98)
            
        else:
            self.record_button.itemconfig(self.record_circle, fill='#69DB7C')
            self.record_button.itemconfig(self.record_icon, text='🎤')
            self.record_button.itemconfig(self.record_text, text='Слушаю', fill='black')
            self.status_label.config(text='Идёт запись...', fg='green')
            thread = Thread(target=self.recorder.start_recording)
            thread.daemon = True
            thread.start()
            self.pulse_active = True
            self.animate_record_button()


    # Обработка нажатия на комментарий убедительности
    def toggle_comment_display(self, event=None):
        if self.is_comment_expanded:
            # # Свернутое
            self.convincing_comment_label.config(text=self.short_comment_text)
            self.convincing_comment_label.place(x=10, y=205, width=300, height=50)
            # # Вывод блоков
            self.variety_label_title.place(x=10, y=260)
            self.variety_label.place(x=10, y=285)
            self.variety_level_text_label.place(x=10, y=310)
            self.variety_level_label.place(x=145, y=310)
            self.is_comment_expanded = False
        else:
            # # Развернутое
            self.convincing_comment_label.config(text=self.full_convincing_comment + '  ← скрыть', anchor='nw')
            self.convincing_comment_label.place(x=10, y=205, width=300, height=130)
            # # Сворачивание блоков
            self.variety_label_title.place_forget()
            self.variety_label.place_forget()
            self.variety_level_label.place_forget()
            self.variety_level_text_label.place_forget()
            self.is_comment_expanded = True
    

    # Обработка нажатия на совет
    def toggle_tip_display(self, event=None):
        if self.is_tip_expanded:
            self.tip_text_label.config(text=self.short_tip_text, font=('Inter', 11))
            self.is_tip_expanded = False
        else:
            self.tip_text_label.config(text=self.full_tip_text + '  ← скрыть', font=('Inter', 10))
            self.is_tip_expanded = True


    # Функция обработки нажатия на значение слова
    def toggle_task_meaning(self, which):
        if which == self.expanded_task_word:
            # Свернуть обратно
            self.refresh_task_words_display()
            self.expanded_task_word = None
            return
        # Очистка
        self.task_word1_label.place_forget()
        self.task_meaning1_label.place_forget()
        self.task_word2_label.place_forget()
        self.task_meaning2_label.place_forget()
        if which == 'word1' and self.word1_data:
            word, meaning = self.word1_data
            self.task_word1_label.config(text=word.capitalize() + '  ← скрыть')
            self.task_meaning1_label.config(text=meaning)
            self.task_word1_label.place(x=10, y=40)
            self.task_meaning1_label.place(x=10, y=60, height=80)
            self.expanded_task_word = 'word1'
        elif which == 'word2' and self.word2_data:
            word, meaning = self.word2_data
            self.task_word2_label.config(text=word.capitalize() + '  ← скрыть')
            self.task_meaning2_label.config(text=meaning)
            # Переместить на позицию word1
            self.task_word2_label.place(x=10, y=40)
            self.task_meaning2_label.place(x=10, y=60, height=80)
            self.expanded_task_word = 'word2'
    

    # Функция начала анализа + данные для апдейта прогресс бара
    def start_full_analysis(self, audio_file_path):
        def run_async_workflow():
            self.update_progress(10, 'Обработка аудио...')
            asyncio.run(self.analytics.full_analysis_workflow(audio_file_path, self.analyzer))
            self.update_progress(50, 'Обновление базы данных...')
            self.update_progress(90, 'Обновление интерфейса...')
            self.refresh_count_words_display()
            self.refresh_tip_display()
            self.refresh_task_words_display()
            self.refresh_variety_display()
            self.refresh_convincingness_display()
            self.update_progress(100, 'Анализ завершён.')
            self.record_button.itemconfig(self.record_circle, fill='#8CE99A')
            self.record_button.itemconfig(self.record_icon, text='▶')
            self.record_button.itemconfig(self.record_text, text='Начать', fill='black')
        thread = Thread(target=run_async_workflow)
        thread.daemon = True
        thread.start()

    # # апдейт Прогресс бар
    def update_progress(self, value, text):
        self.progress.place(x=10, y=120)
        self.progress_label.place(x=10, y=100)
        self.progress['value'] = value
        self.progress_label.config(text=text)
        self.update_idletasks()
        if value >= 100:
            self.after(1000, self.hide_progress)
    # # Скрытие прогресс бара
    def hide_progress(self):
        self.progress.place_forget()
        self.progress_label.place_forget()
        self.status_label.config(text='Готов к записи', fg='gray')


    # Обновление ТОП-5 слов
    def refresh_count_words_display(self):
        words = get_all_count_words()[:5]
        label_text = '\n'.join(f"{i+1}. {word} — {count}" for i, (word, count) in enumerate(words))
        self.words_label.config(text=label_text)


    # Обновление лексического разнообразия
    def refresh_variety_display(self):
        try:
            with open("output.txt", "r", encoding="utf-8") as f:
                text = f.read()
            stats, level = analyze_lexical_variety(text)
            color = {'Низкое': '#DC3545', 'Среднее': '#FFC107', 'Высокое': "#00CE30"}.get(level, 'black')
            self.variety_label.config(text=f"{stats}")
            self.variety_level_label.config(text=level, fg=color)
        except Exception as e:
            self.variety_label.config(text=f"Ошибка анализа: {e}")


    # Обновление убедительности
    def refresh_convincingness_display(self):
        score_data = get_latest_convincingness_score()
        if score_data:
            score, explanation = score_data
            self.full_convincing_comment = explanation
            self.is_comment_expanded = False
            self.convincing_score_label.config(text=f"Оценка: {score}/10")
            max_len = 90
            if len(explanation) > max_len:
                short_comment = explanation[:max_len].rsplit(' ', 1)[0].strip() + '... → Читать далее'
            else:
                short_comment = explanation
            self.short_comment_text = short_comment
            self.convincing_comment_label.config(text=self.short_comment_text, fg='#212529')
            self.convincing_comment_label.bind('<Button-1>', self.toggle_comment_display)
            self.convincing_comment_label.config(cursor='hand2')
        else:
            self.convincing_score_label.config(text='')
            self.convincing_comment_label.config(text='')


    # Обновление совета
    def refresh_tip_display(self):
        tip = get_latest_tip()
        self.full_tip_text = tip
        self.is_tip_expanded = False
        max_len = 240
        if len(tip) > max_len:
            self.short_tip_text = tip[:max_len].rsplit(' ', 1)[0].strip() + '... → далее'
        else:
            self.short_tip_text = tip
        self.tip_text_label.config(text=self.short_tip_text)
        self.tip_text_label.bind('<Button-1>', self.toggle_tip_display)
        self.tip_text_label.config(cursor='hand2')


    # Обновление заданий (новых слов для изучения)
    def refresh_task_words_display(self):
        self.expanded_task_word = None
        new_words = get_all_new_words()[:2]
        self.word1_data = new_words[0] if len(new_words) > 0 else None
        self.word2_data = new_words[1] if len(new_words) > 1 else None
        if self.word1_data:
            word, meaning = self.word1_data
            self.task_word1_label.config(text=word.capitalize())
            self.task_meaning1_label.config(text=self._shorten_meaning(meaning))
            self.task_word1_label.place(x=10, y=40)
            self.task_meaning1_label.place(x=10, y=60, height=40)

        if self.word2_data:
            word, meaning = self.word2_data
            self.task_word2_label.config(text=word.capitalize())
            self.task_meaning2_label.config(text=self._shorten_meaning(meaning))
            self.task_word2_label.place(x=10, y=100)
            self.task_meaning2_label.place(x=10, y=120, height=40)

    # # Функция вывода короткого значения слова
    def _shorten_meaning(self, text, max_len=70):
        return text[:max_len].rsplit(' ', 1)[0].strip() + '... → развернуть' if len(text) > max_len else text
    

    # Для анимации кнопки записи
    def animate_record_button(self):
        if not self.pulse_active:
            return
        offset = 1.5 if self.pulse_state == 0 else 0
        self.record_button.coords(self.record_circle, 2 - offset, 2 - offset, 98 + offset, 98 + offset)
        self.pulse_state = 1 - self.pulse_state
        self.after(500, self.animate_record_button)


    

if __name__ == '__main__':
    api_key = '' # API для AssemblyAI
    oauth_token = ''
    folder_id = ''

    init_db()
    recorder = AudioRecorder()
    analytics = AudioAnalytics(api_key)
    analyzer = Analyzer(oauth_token, folder_id)
    app = RecorderApp(recorder, analytics, analyzer)
    app.mainloop()
