#!/usr/bin/env python3
"""
Helper script to add questions to questions.json for GitHub Pages deployment.
Usage: python add_question.py
"""
import json
import os
import hashlib
from datetime import datetime

QUESTIONS_FILE = 'questions.json'

def load_questions():
    """Load existing questions from file."""
    if os.path.exists(QUESTIONS_FILE):
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_questions(data):
    """Save questions to file."""
    with open(QUESTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def generate_id(question_text):
    """Generate MD5 hash-based ID from question text."""
    return hashlib.md5(question_text.encode('utf-8')).hexdigest()

def main():
    print("=== Добавление вопроса в questions.json ===\n")
    
    # Get question details
    question = input("Введите вопрос: ").strip()
    if not question:
        print("Ошибка: вопрос не может быть пустым")
        return
    
    answer = input("Введите правильный ответ: ").strip()
    if not answer:
        print("Ошибка: ответ не может быть пустым")
        return
    
    # Generate ID
    question_id = input("Введите ID вопроса (или нажмите Enter для автогенерации на основе MD5): ").strip()
    if not question_id:
        question_id = generate_id(question)
        print(f"Сгенерирован MD5 ID: {question_id}")
    
    # Load existing data
    data = load_questions()
    
    # Check if ID already exists
    existing_question = next((q for q in data if q.get('id') == question_id), None)
    if existing_question:
        overwrite = input(f"Вопрос с ID '{question_id}' уже существует. Перезаписать? (y/n): ")
        if overwrite.lower() != 'y':
            print("Отменено")
            return
        # Remove the existing question
        data = [q for q in data if q.get('id') != question_id]
    
    # Add question
    new_question = {
        'id': question_id,
        'question': question,
        'answer': answer.lower(),
        'created_at': datetime.now().isoformat()
    }
    data.append(new_question)
    
    # Save
    save_questions(data)
    
    print(f"\n✓ Вопрос успешно добавлен!")
    print(f"\nУникальная ссылка для GitHub Pages:")
    print(f"https://<username>.github.io/chgk/question.html?id={question_id}")
    print(f"\nНе забудьте сделать commit и push изменений!")

if __name__ == '__main__':
    main()
