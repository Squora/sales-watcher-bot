from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
import joblib
import os
from data.train_data import TRAIN_DATA

# Функция для загрузки диалогов из файла
def load_dialogues(file_path="dialogues.txt"):
    dialogues = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f.readlines():
                question, answer = line.strip().split("|")
                dialogues.append((question, answer))
    except FileNotFoundError:
        print(f"Файл {file_path} не найден.")
    return dialogues

# Обновленные данные для обучения
def load_and_update_training_data(file_path="data/dialogues.txt"):
    # Загрузка диалогов
    dialogues = load_dialogues(file_path)

    # Добавляем новые диалоги из файла
    additional_data = [(dialogue[0], "product") for dialogue in dialogues]  # Категория "product", можно изменить
    return TRAIN_DATA + additional_data  # Объединяем старые и новые данные

def train_and_save_model(model_path="data/intent_model.pkl"):
    # Создаем папку, если ее нет
    os.makedirs(os.path.dirname(model_path), exist_ok=True)

    TRAIN_DATA = load_and_update_training_data()  # Загружаем данные
    texts, labels = zip(*TRAIN_DATA)

    # Разделяем данные на обучающую и тестовую выборки
    X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)

    # Используем TfidfVectorizer вместо CountVectorizer
    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    clf = MultinomialNB()
    clf.fit(X_train_tfidf, y_train)

    # Оцениваем модель на тестовых данных
    y_pred = clf.predict(X_test_tfidf)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Точность модели: {accuracy * 100:.2f}%")

    # Сохраняем модель и векторизатор
    joblib.dump((clf, vectorizer), model_path)
    print("Модель обучена и сохранена.")

def load_model(model_path="data/intent_model.pkl"):
    if not os.path.exists(model_path):
        train_and_save_model(model_path)

    model, vectorizer = joblib.load(model_path)
    return model, vectorizer
