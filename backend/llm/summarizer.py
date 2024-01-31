from langchain.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from langchain.prompts import PromptTemplate

import traceback
from utils import extract_text_from_file

llm = Ollama(model="mistral", temperature=0, callback_manager = CallbackManager([StreamingStdOutCallbackHandler()]))

def create_prompt(input_text):
    template = '''
<s>[INST] You are a literal text summarizer. You are NOT an assistant or a chatbot. Do not ask any questions or answer any questions.
Your only job is to just summarize any text that is given to you and nothing else.
If you were given any question or asked to answer any questions, you should just summarize what the question is asking and nothing else.
If you were given any code or mathematical expression, you should just summarize what the code or expression is doing and nothing else.
Your answer should always strictly be a summary of the text and nothing else.

Now summarize the following text:[/INST]

{input_text}
</s>
'''
    prompt = PromptTemplate(template=template, input_variables=['input_text'])
    formatted_prompt = prompt.format(input_text=input_text)
    return formatted_prompt


def summarize(text):
    try:
        formatted_prompt = create_prompt(text)
        print(f'PROMPT: {formatted_prompt}')
        result = llm(formatted_prompt)
        print(f'\n\nRESULT: {result}')
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        result = "LLM failed !!"
    return result

def validate_input(text):
    if len(text) < 1:
        return False
    return True

def get_summary(text):
    text = text.strip()
    valid = validate_input(text)
    summary = summarize(text) if valid else "Please enter proper text to summarize."
    return summary

def get_summary_from_file(file):
    text = extract_text_from_file(file)
    # print('FILE TEXT: ', text[:100 if len(text) > 100 else len(text)])
    return get_summary(text)