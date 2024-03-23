from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
from app.auth.routes import current_user
from app.main.llm.document_rag import extract_and_load_document, get_answer_from_rag

main = Blueprint('main', __name__)

@main.route('/')
def home():
    if current_user.is_authenticated():
        return jsonify({'message': f'Hello {current_user.email}, this is Documate!'})
    return jsonify({'message': 'Hello, Please login to Documate!'})

@main.route('/load_doc', methods=['POST'])
def load_document():
    if current_user.is_anonymous():
        return jsonify({'message': 'Please login to Documate!'}), 401
    if 'file' in request.files:
        file = request.files['file']
        filename = secure_filename(file.filename)
        print('FILENAME: ', filename)
        message = extract_and_load_document(file)
        return jsonify({'message': message})


@main.route('/get_answer', methods=['POST'])
def get_answer():
    if current_user.is_anonymous():
        return jsonify({'message': 'Please login to Documate!'}), 401
    data = request.get_json()
    question = data.get('question', '')
    chat_history = data.get('chat_history', '')
    answer = get_answer_from_rag(question, chat_history)
    return jsonify({'answer': answer})