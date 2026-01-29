#!/usr/bin/env python3
"""
Simple Flask application for Russian quiz "Что? Где? Когда?"
No database required - uses JSON file for storage.
"""
import os
import json
import uuid
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
DATA_FILE = 'data.json'

def load_data():
    """Load questions and attempt data from JSON file."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # If JSON is corrupted, backup and start fresh
            if os.path.exists(DATA_FILE):
                os.rename(DATA_FILE, f'{DATA_FILE}.corrupt.{int(datetime.now().timestamp())}')
            return {'questions': {}, 'attempts': {}}
    return {'questions': {}, 'attempts': {}}

def save_data(data):
    """Save questions and attempt data to JSON file."""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    """Admin page to create questions."""
    return render_template('admin.html')

@app.route('/api/question', methods=['POST'])
def create_question():
    """Create a new question with a unique ID."""
    data_obj = load_data()
    
    question_text = request.json.get('question', '').strip()
    answer = request.json.get('answer', '').strip()
    
    if not question_text or not answer:
        return jsonify({'error': 'Вопрос и ответ обязательны'}), 400
    
    # Validate input lengths
    if len(question_text) > 5000:
        return jsonify({'error': 'Вопрос слишком длинный (максимум 5000 символов)'}), 400
    
    if len(answer) > 500:
        return jsonify({'error': 'Ответ слишком длинный (максимум 500 символов)'}), 400
    
    question_id = str(uuid.uuid4())
    data_obj['questions'][question_id] = {
        'question': question_text,
        'answer': answer.lower(),
        'created_at': datetime.now().isoformat()
    }
    
    save_data(data_obj)
    
    return jsonify({
        'id': question_id,
        'url': f'/q/{question_id}'
    })

@app.route('/q/<question_id>')
def question_page(question_id):
    """Display the question page for visitors."""
    data_obj = load_data()
    
    if question_id not in data_obj['questions']:
        return "Вопрос не найден", 404
    
    return render_template('question.html', question_id=question_id)

@app.route('/api/question/<question_id>', methods=['GET'])
def get_question(question_id):
    """Get question details (without answer)."""
    data_obj = load_data()
    
    if question_id not in data_obj['questions']:
        return jsonify({'error': 'Вопрос не найден'}), 404
    
    question_data = data_obj['questions'][question_id]
    return jsonify({
        'question': question_data['question']
    })

@app.route('/api/answer/<question_id>', methods=['POST'])
def check_answer(question_id):
    """Check if the answer is correct."""
    data_obj = load_data()
    
    if question_id not in data_obj['questions']:
        return jsonify({'error': 'Вопрос не найден'}), 404
    
    user_answer = request.json.get('answer', '').strip().lower()
    client_id = request.json.get('client_id', '')
    
    if not client_id:
        return jsonify({'error': 'Требуется идентификатор клиента'}), 400
    
    # Check for timeout
    attempt_key = f"{question_id}:{client_id}"
    if 'attempts' not in data_obj:
        data_obj['attempts'] = {}
    
    if attempt_key in data_obj['attempts']:
        last_attempt = datetime.fromisoformat(data_obj['attempts'][attempt_key])
        time_since = datetime.now() - last_attempt
        
        if time_since < timedelta(seconds=30):
            remaining = 30 - int(time_since.total_seconds())
            return jsonify({
                'correct': False,
                'timeout': True,
                'remaining_seconds': remaining,
                'message': f'Подождите {remaining} секунд перед следующей попыткой'
            })
    
    correct_answer = data_obj['questions'][question_id]['answer']
    is_correct = user_answer == correct_answer
    
    if not is_correct:
        # Record failed attempt
        data_obj['attempts'][attempt_key] = datetime.now().isoformat()
        save_data(data_obj)
        
        return jsonify({
            'correct': False,
            'timeout': False,
            'message': 'Неправильный ответ. Попробуйте снова через 30 секунд.'
        })
    
    # Correct answer - clear the attempt record
    if attempt_key in data_obj['attempts']:
        del data_obj['attempts'][attempt_key]
        save_data(data_obj)
    
    return jsonify({
        'correct': True,
        'message': 'Поздравляем! Ответ правильный!'
    })

if __name__ == '__main__':
    # Get debug mode from environment variable, default to False for production
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
