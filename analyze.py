import requests
import json
from db import update_count_words_from_file, update_tip_from_file, update_new_words_from_file, update_convincingness_score
import re
from pymorphy2 import MorphAnalyzer

# Класс анализа от Яндекс ГПТ
class Analyzer:
    def __init__(self, oauth_token, folder_id):
        self.url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {oauth_token}",
            "x-folder-id": folder_id
        }

# Запросы для ГПТ
    # # Анализ основной
    def analyze_text_with_yandex_cloud(self, text):
        prompt_text = f"""
        Проанализируй текст и ответь:
        1. Выведи топ-5 самых часто повторяющихся слов (без предлогов и местоимений) и количество.
        2. Дай совет для улучшения качества речи.
        3. Предложи 2 слова, которые могут расширить словарный запас человека. Их не должно быть в тексте.
        1 пункт оформи в формате: 1. Топ-5 самых часто повторяющихся слов в тексте:
        -слово - 5
        2 пункт оформи в формате: 2. Совет:
        3 пункт оформи в формате: 3. Слова - значения.

        Текст: {text}
        """
        prompt = {
            "modelUri": "gpt://b1gpe5t8i45qpvvk3dru/yandexgpt-lite",
            "completionOptions": {
                "stream": False,
                "temperature": 0.6,
                "maxTokens": "1000"
            },
            "messages": [{"role": "user", "text": prompt_text}]
        }
        response = requests.post(self.url, headers=self.headers, json=prompt)
        if response.status_code == 200:
            result = response.json().get("result", {}).get("alternatives", [{}])[0].get("message", {}).get("text", "")
            print("6/16 ✅Ответ от YandexGPT получен!")
            self.save_analysis(result)
        else:
            print(f"❌Ошибка при запросе к YandexGPT: {response.status_code}, {response.text}")

    # # Анализ убедительности 
    def analyze_convincingness_with_gpt(self, text):
        prompt_text = f"""
        Оцени, насколько речь ниже убедительна по 10-балльной шкале. Укажи балл и кратко объясни почему:
        
        Дай ответ в форме: х/10 баллов. Комментарий.

        Речь:
        {text}
        """
        prompt = {
            "modelUri": "gpt://b1gpe5t8i45qpvvk3dru/yandexgpt-lite",
            "completionOptions": {
                "stream": False,
                "temperature": 0.4,
                "maxTokens": "1000"
            },
            "messages": [{"role": "user", "text": prompt_text}]
        }
        response = requests.post(self.url, headers=self.headers, json=prompt)
        if response.status_code == 200:
            result = response.json()
            text = result['result']['alternatives'][0]['message']['text']
            print("15/16 ✅ 2 Ответ от YandexGPT получен!")
            match = re.match(r'(\d{1,2})\s*/\s*10\s*балл[а-я]*[.:!\n]*\s*Комментарий:\s*(.*)', text.strip(), re.DOTALL)
            if match:
                score = int(match.group(1))
                explanation = match.group(2).strip()
                explanation = explanation[0].upper() + explanation[1:]
                update_convincingness_score(score, explanation)
        else:
            print(f"❌Ошибка при запросе к YandexGPT: {response.status_code}, {response.text}")


# Сохранение основного анализа
    def save_analysis(self, analysis_text):
        with open('Otvet.txt', 'w', encoding='utf-8') as f:
            f.write(analysis_text)
        update_count_words_from_file("Otvet.txt")
        update_tip_from_file("Otvet.txt")
        update_new_words_from_file("Otvet.txt")
        print("7/16 ✅Результаты анализа сохранены в 'Otvet.txt'.")

# Запуск основного анализа + доп. анализа уверенности речи
    def run_analysis_from_file(self, file_path='output.txt'):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read().strip()
            if text:
                self.analyze_text_with_yandex_cloud(text)
                self.analyze_convincingness_with_gpt(text)
            else:
                print("❌Файл пуст, нечего анализировать.")
        except FileNotFoundError:
            print("❌Файл output.txt не найден.")



########### НЕ В КЛАССЕ ANALYZER ###############
# Анализ лексического разнообразия
def analyze_lexical_variety(text: str) -> tuple[str, str]:
    morph = MorphAnalyzer()
    words = re.findall(r'\b\w+\b', text.lower())
    lemmas = [morph.parse(w)[0].normal_form for w in words]
    total = len(lemmas)
    unique = len(set(lemmas))
    percent = round((unique / total) * 100) if total > 0 else 0
    if percent <= 30:
        level = "Низкое"
    elif percent <= 60:
        level = "Среднее"
    else:
        level = "Высокое"
    stats = f"{unique} уникальных слов из {total} ({percent}%)"
    return stats, level


if __name__ == "__main__":
    oauth_token = ""  # API-ТОКЕН для Яндекса
    folder_id = ""    # FOLDER ID для Яндекса

    analyzer = Analyzer(oauth_token, folder_id)
    analyzer.run_analysis_from_file()  # Отдельный запуск анализа (Можно закомментить)
    