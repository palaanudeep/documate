from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
from flask_jwt_extended import current_user, jwt_required
from app import db
from app.models import Chat, Message
from app.main.llm.document_rag import extract_and_load_document, get_answer_from_rag

main = Blueprint('main', __name__)

@main.route('/')
def home():
    if current_user:
        return jsonify({'message': f'Hello {current_user.email}, this is Documate!'})
    return jsonify({'message': 'Hello, Please login to Documate!'})

@main.route('/api/load_doc', methods=['POST'])
@jwt_required()
def load_document():
    try:
        if current_user is None:
            return jsonify({'message': 'Please login to Documate!'}), 401
        if 'file' in request.files:
            file = request.files['file']
            filename = secure_filename(file.filename)
            print('FILENAME: ', filename)
            summary = extract_and_load_document(file)
            user_id = current_user.id
            doc_name = filename
            chat = Chat(user_id, doc_name, summary)
            db.session.add(chat)
            db.session.commit()
            return jsonify({'summary': summary, 'chat_id': chat.id})
        return jsonify({'message': 'No file found in request'}), 400
    except Exception as e:
        print(e)
        return jsonify({'message': 'Server Error'}), 500


@main.route('/api/get_answer', methods=['POST'])
@jwt_required()
def get_answer():
    try:
        if current_user is None:
            return jsonify({'message': 'Please login to Documate!'}), 401
        data = request.get_json()
        question = data.get('question', '')
        chat_history = data.get('chat_history', [])
        chat_id = data.get('chat_id', '')
        answer = get_answer_from_rag(question, chat_history)
        user_id = current_user.id
        user_message = Message(chat_id=chat_id, user_id=user_id, message=question, is_user=True)
        db.session.add(user_message)
        db.session.commit()
        bot_message = Message(chat_id=chat_id, user_id=None, message=answer, is_user=False)
        db.session.add(bot_message)
        db.session.commit()
        return jsonify({'answer': answer})
    except Exception as e:
        print(e)
        return jsonify({'message': 'Server Error'}), 500