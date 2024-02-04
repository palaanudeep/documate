from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

from dotenv import load_dotenv
load_dotenv()

from llm.document_rag import extract_and_load_document, get_answer_from_rag



app = Flask(__name__)
CORS(app)


@app.route('/load_doc', methods=['POST'])
def load_document():
    if 'file' in request.files:
        file = request.files['file']
        filename = secure_filename(file.filename)
        print('FILENAME: ', filename)
        message = extract_and_load_document(file)
        return jsonify({'message': message})


@app.route('/get_answer', methods=['POST'])
def get_answer():
    data = request.get_json()
    question = data.get('question', '')
    chat_history = data.get('chat_history', '')
    answer = get_answer_from_rag(question, chat_history)
    return jsonify({'answer': answer})




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

