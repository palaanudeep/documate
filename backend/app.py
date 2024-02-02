from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

from dotenv import load_dotenv
load_dotenv()

from llm.summarizer import get_summary_from_file, get_answer_from_rag



app = Flask(__name__)
CORS(app)

sample_text = '''
A Large Language Model, as the name implies, refers to a model trained on large datasets to comprehend and generate content. Essentially, it's a transformer model on a large scale. The transformer model itself is a neural network designed to grasp context and meaning through the analysis of relationships within sequential data.


The architecture of transformer model (Source)
Transformers are great for LLMs because they have two important features: positional encodings and self-attention.

Positional encodings help the model understand the order of words in a sequence and include this information in the word embeddings. Here's a bit more about it from Brandon Rohrer’s article "Transformers from Scratch":

“There are several ways that position information could be introduced into our embedded representation of words, but the way it was done in the original transformer was to add a circular wiggle.”


“The position of the word in the embedding space acts as the center of a circle. A perturbation is added to it, depending on where it falls in the order of the sequence of words. For each position, the word is moved the same distance but at a different angle, resulting in a circular pattern as you move through the sequence. Words that are close to each other in the sequence have similar perturbations, but words that are far apart are perturbed in different directions.”

Self-attention allows the words in a sequence to interact with each other and find out who they should pay more attention to. To help you understand this concept better, I’ve borrowed an example from Jay Alammar’s “The Illustrated Transformer” article:

“Say the following sentence is an input sentence we want to translate:”

‘The animal didn’t cross the street because it was too tired’

“What does ‘it’ in this sentence refer to? Is it referring to the street or to the animal? It’s a simple question to a human, but not as simple to an algorithm.”

“When the model is processing the word ‘it,’ self-attention allows it to associate ‘it’ with ‘animal.’”

Transformers utilize a powerful attention mechanism known as multi-head attention. Think of it as combining several self-attentions. This way, we can capture various aspects of language and better understand how different entities relate to each other in a sequence.

If you're interested in a visual guide to understand LLMs and transformers, this resource is worth exploring.
'''

@app.route('/')
def hello_world():
    return get_summary(sample_text)

@app.route('/summarize', methods=['POST'])
def summarize_text():
    if 'file' in request.files:
        file = request.files['file']
        filename = secure_filename(file.filename)
        print('FILENAME: ', filename)
        summary = get_summary_from_file(file)
        return jsonify({'summary': summary})
    else:
        data = request.get_json()
        question = data.get('question', '')
        chat_history = data.get('chat_history', '')
        answer = get_answer_from_rag(question, chat_history)
        return jsonify({'answer': answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

