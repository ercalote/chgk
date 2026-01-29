#!/usr/bin/env python3
"""
Helper script to add questions to questions.json for GitHub Pages deployment.
Usage: python add_question.py
"""
import json
import os
from datetime import datetime

QUESTIONS_FILE = 'questions.json'

def load_questions():
    """Load existing questions from file."""
    if os.path.exists(QUESTIONS_FILE):
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'questions': {}}

def save_questions(data):
    """Save questions to file."""
    with open(QUESTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def generate_id(question_text):
    """Generate a readable ID from question text."""
    # Take first few words and make them URL-friendly
    words = question_text.lower().split()[:3]
    base_id = '_'.join(''.join(c for c in word if c.isalnum()) for word in words)
    
    # Add timestamp to ensure uniqueness
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{base_id}_{timestamp}"

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
    question_id = input("Введите ID вопроса (или нажмите Enter для автогенерации): ").strip()
    if not question_id:
        question_id = generate_id(question)
        print(f"Сгенерирован ID: {question_id}")
    
    # Load existing data
    data = load_questions()
    
    # Check if ID already exists
    if question_id in data['questions']:
        overwrite = input(f"Вопрос с ID '{question_id}' уже существует. Перезаписать? (y/n): ")
        if overwrite.lower() != 'y':
            print("Отменено")
            return
    
    # Add question
    data['questions'][question_id] = {
        'question': question,
        'answer': answer.lower(),
        'created_at': datetime.now().isoformat()
    }
    
    # Save
    save_questions(data)
    
    print(f"\n✓ Вопрос успешно добавлен!")
    print(f"\nУникальная ссылка для GitHub Pages:")
    print(f"https://<username>.github.io/chgk/question.html?id={question_id}")
    print(f"\nНе забудьте сделать commit и push изменений!")

if __name__ == '__main__':
    main()
