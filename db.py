import sqlite3
import re

DB_NAME = 'analytics.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS CountWords (
            word TEXT PRIMARY KEY,
            count INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SpeechTips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tip TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS NewWords (
            word TEXT PRIMARY KEY,
            meaning TEXT
        )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS SpeechScores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        score INTEGER,
        explanation TEXT
    )
    ''')
    conn.commit()
    print('База данных работает')
    conn.close()

# Обработка для слов
def update_count_words_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        match = re.search(r'1\.\s*Топ-5.*?:\s*(.*?)\n\s*\d', content, re.DOTALL)
        if not match:
            print("❌Не удалось найти список слов.")
            return
        words_block = match.group(1)
        lines = words_block.strip().split('\n')
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM CountWords')
        for line in lines:
            parts = line.strip().split('—')
            if len(parts) == 2:
                raw_word = parts[0]
                word = re.sub(r'^[^а-яА-Яa-zA-Z0-9]+|[^а-яА-Яa-zA-Z0-9]+$', '', raw_word)
                count_str = parts[1].strip().replace('.', '').replace(',', '')
                try:
                    count = int(re.search(r'\d+', count_str).group())
                    cursor.execute(
                        'INSERT OR REPLACE INTO CountWords (word, count) VALUES (?, ?)',
                        (word, count)
                    )
                    print('8-12/16 ✅База данных обновлена')
                except Exception as e:
                    print(f"❌Ошибка при обработке строки '{line}': {e}")
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌Ошибка при обновлении базы данных: {e}")

# Выборка всех слов
def get_all_count_words():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT word, count FROM CountWords ORDER BY count DESC')
    results = cursor.fetchall()
    conn.close()
    return results


# Обработка для советов
def update_tip_from_file(filename):
    import re
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()
    # # '2. Совет:' до точки с запятой
    match = re.search(r'Совет:([^3]+)', text)
    if match:
        cursor.execute('DELETE FROM SpeechTips')
        tip = match.group(1).strip()
        if tip:
            tip = tip[0].upper() + tip[1:]
            cursor.execute('INSERT INTO SpeechTips (tip) VALUES (?)', (tip,))
            print('13/16 ✅Совет сохранён в БД:', tip)
    conn.commit()
    conn.close()

def get_latest_tip():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT tip FROM SpeechTips ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else "Совет не найден."
    except Exception as e:
        print(f"❌Ошибка при получении совета: {e}")
        return "❌Ошибка при загрузке совета."
    
    
# Обработка НОВОГО слова
def update_new_words_from_file(file_path):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    # # '3. Слова — значения:'
    match = re.search(r'3\.\s*Слова\s*—\s*значения:\s*(.*)', content, re.DOTALL)
    if not match:
        print("❌Не найден блок '3. Слова — значения'")
        conn.close()
        return
    cursor.execute('DELETE FROM NewWords')
    block = match.group(1).strip()
    lines = block.split('\n')
    for line in lines:
        # Удаление маркеров *, -, пробелы и точки с запятой с начала строки
        cleaned_line = re.sub(r'^[\*\-\s]+', '', line).strip()
        parts = re.split(r'\s*[—-]\s*', cleaned_line, maxsplit=1)      
        if len(parts) == 2:
            word = parts[0].strip(' «»"').capitalize()
            meaning = parts[1].strip(' ;.»"\n')
            if word and meaning:
                cursor.execute(
                    'INSERT OR REPLACE INTO NewWords (word, meaning) VALUES (?, ?)',
                    (word, meaning)
                )
    conn.commit()
    conn.close()
    print("14/16 ✅ Новые слова успешно добавлены в базу данных.")

def get_all_new_words():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT word, meaning FROM NewWords')
    results = cursor.fetchall()
    conn.close()
    return results


# Обработка Убедительности речи
# # Сохранение в БД
def update_convincingness_score(score: int, explanation: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM SpeechScores')
    cursor.execute(
        'INSERT INTO SpeechScores (score, explanation) VALUES (?, ?)',
        (score, explanation)
    )
    print('16/16 ✅Убедительность успешно сохранена')
    conn.commit()
    conn.close()

# # Вывод информации по убедительности речи
def get_latest_convincingness_score():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT score, explanation FROM SpeechScores ORDER BY id DESC LIMIT 1')
    row = cursor.fetchone()
    conn.close()
    return row if row else (None, '')
