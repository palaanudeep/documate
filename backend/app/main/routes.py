from flask import Blueprint, jsonify, request, Response
from werkzeug.utils import secure_filename
from flask_jwt_extended import current_user, jwt_required
import json
from app import db
from app.models import Chat, Message
from app.main.llm.document_rag import extract_and_load_document, get_answer_from_rag, get_answer_from_rag_stream
from app.main.utils import extract_lcdocs_from_source

main = Blueprint('main', __name__)

@main.route('/')
def home():
    if current_user:
        return jsonify({'message': f'Hello {current_user.email}, this is Documate!'})
    return jsonify({'message': 'Hello, Please login to Documate!'})

@main.route('/api/load_doc', methods=['POST'])
@jwt_required()
def load_document():
    """Load a document from file upload or URL"""
    try:
        if current_user is None:
            return jsonify({'message': 'Please login to Documate!'}), 401
        
        # Check if it's a URL or file upload
        data = request.get_json() if request.is_json else {}
        url = data.get('url', '').strip() if data else None
        
        if url:
            # URL-based ingest
            print('URL: ', url)
            from app.main.llm.document_rag import extract_and_load_source
            result = extract_and_load_source(url, source_type='url')
            user_id = current_user.id
            doc_name = f"Web: {url[:100]}"  # Truncate long URLs
            chat = Chat(user_id, doc_name, result['answer'])
            db.session.add(chat)
            db.session.commit()
            return jsonify({
                'summary': result['answer'],
                'citations': result['citations'],
                'chat_id': chat.id,
                'request_id': result['request_id'],
                'latency_ms': result['latency_ms'],
                'token_usage': result['token_usage'],
                'source_type': 'url'
            })
        elif 'file' in request.files:
            # File-based ingest
            file = request.files['file']
            filename = secure_filename(file.filename)
            print('FILENAME: ', filename)
            result = extract_and_load_document(file)
            user_id = current_user.id
            doc_name = filename
            chat = Chat(user_id, doc_name, result['answer'])
            db.session.add(chat)
            db.session.commit()
            return jsonify({
                'summary': result['answer'],
                'citations': result['citations'],
                'chat_id': chat.id,
                'request_id': result['request_id'],
                'latency_ms': result['latency_ms'],
                'token_usage': result['token_usage'],
                'source_type': 'file'
            })
        else:
            return jsonify({'message': 'No file or URL provided in request'}), 400
    except ValueError as e:
        # User-facing errors (bad URLs, fetch failures, etc.)
        print(f"ValueError: {e}")
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        print(f"Server error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Server Error: {str(e)}'}), 500


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
        result = get_answer_from_rag(question, chat_history)
        user_id = current_user.id
        user_message = Message(chat_id=chat_id, user_id=user_id, message=question, is_user=True)
        db.session.add(user_message)
        db.session.commit()
        bot_message = Message(chat_id=chat_id, user_id=None, message=result['answer'], is_user=False)
        db.session.add(bot_message)
        db.session.commit()
        return jsonify({
            'answer': result['answer'],
            'citations': result['citations'],
            'request_id': result['request_id'],
            'latency_ms': result['latency_ms'],
            'token_usage': result['token_usage']
        })
    except Exception as e:
        print(e)
        return jsonify({'message': 'Server Error'}), 500

@main.route('/api/get_answer_stream', methods=['POST'])
@jwt_required()
def get_answer_stream():
    """Streaming endpoint for RAG responses"""
    try:
        if current_user is None:
            return jsonify({'message': 'Please login to Documate!'}), 401
        data = request.get_json()
        question = data.get('question', '')
        chat_history = data.get('chat_history', [])
        chat_id = data.get('chat_id', '')
        
        def generate():
            try:
                for chunk in get_answer_from_rag_stream(question, chat_history):
                    yield chunk
            except Exception as e:
                yield json.dumps({'type': 'error', 'data': str(e)}) + '\n'
        
        # Store messages after stream completes (in a real system, use a callback)
        user_id = current_user.id
        user_message = Message(chat_id=chat_id, user_id=user_id, message=question, is_user=True)
        db.session.add(user_message)
        db.session.commit()
        
        return Response(generate(), mimetype='application/x-ndjson')
    except Exception as e:
        print(e)
        return jsonify({'message': 'Server Error'}), 500
