from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
from flask_jwt_extended import current_user, jwt_required
from app.main.llm.document_rag import extract_and_load_document, get_answer_from_rag

main = Blueprint('main', __name__)

@main.route('/')
@jwt_required()
def home():
    if current_user:
        return jsonify({'message': f'Hello {current_user.email}, this is Documate!'})
    return jsonify({'message': 'Hello, Please login to Documate!'})

@main.route('/api/load_doc', methods=['POST'])
@jwt_required()
def load_document():
    if current_user is None:
        return jsonify({'message': 'Please login to Documate!'}), 401
    if 'file' in request.files:
        file = request.files['file']
        filename = secure_filename(file.filename)
        print('FILENAME: ', filename)
        message = extract_and_load_document(file)
        return jsonify({'message': message})


@main.route('/api/get_answer', methods=['POST'])
@jwt_required()
def get_answer():
    if current_user is None:
        return jsonify({'message': 'Please login to Documate!'}), 401
    data = request.get_json()
    question = data.get('question', '')
    chat_history = data.get('chat_history', '')
    answer = get_answer_from_rag(question, chat_history)
    return jsonify({'answer': answer})