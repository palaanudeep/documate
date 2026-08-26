from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
import traceback
import time
import uuid
import json
import logging

from app.main.utils import extract_lcdocs_from_file

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

RAG_CHAIN = None
RETRIEVER = None
chatModel = ChatOpenAI(model_name="gpt-3.5-turbo-0125", temperature=0)

def initialize_qa_rag_chain(docs):
    global RAG_CHAIN, RETRIEVER

    RETRIEVER = create_doc_retriever(docs)
    qa_system_prompt = """You are an assistant for question-answering tasks. \
Use the following pieces of retrieved context to answer the question. \
If you don't know the answer, just say that you don't know. \
Use three sentences maximum and keep the answer concise.\

{context}"""
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )
    def get_contextualized_question(input: dict):
        if input.get("chat_history"):
            return create_contextualized_q_chain()
        else:
            return input["question"]
        
    def format_docs(rdocs):
        return "\n\n".join(rdoc.page_content for rdoc in rdocs)
    
    RAG_CHAIN = (
        RunnablePassthrough.assign(
            context=get_contextualized_question | RETRIEVER | format_docs,
            source_documents=get_contextualized_question | RETRIEVER
        )
        | qa_prompt
        | chatModel
        | StrOutputParser()
    )
    return RAG_CHAIN

def create_doc_retriever(docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200, 
        add_start_index=True,
        separators=["\n\n", "\n", " ", ""]
    )
    splits = text_splitter.split_documents(docs)
    
    # Enrich metadata with chunk information for better citations
    for idx, split in enumerate(splits):
        split.metadata['chunk_id'] = idx
        
    vectorstore = Chroma.from_documents(
        documents=splits, 
        embedding=OpenAIEmbeddings(model="text-embedding-3-small")
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    return retriever

def create_contextualized_q_chain():
    contextualize_q_system_prompt = """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is."""

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )
    contextualize_q_chain = contextualize_q_prompt | chatModel | StrOutputParser()
    return contextualize_q_chain

def create_rag_input_dict(question, chat_history):
    chat_history = [HumanMessage(content=msg_obj['message']) if len(msg_obj['user'])>0 else AIMessage(content=msg_obj['message']) for msg_obj in chat_history]
    rag_input_dict = {
        "question": question,
        "chat_history": chat_history,
    }
    return rag_input_dict



def log_request_trace(request_id, question, answer, citations, token_usage, latency_ms, retrieval_count):
    """Log structured trace data for observability"""
    trace = {
        "request_id": request_id,
        "timestamp": time.time(),
        "question": question,
        "answer": answer,
        "citations": citations,
        "token_usage": token_usage,
        "latency_ms": latency_ms,
        "retrieval_count": retrieval_count,
        "model": "gpt-3.5-turbo-0125"
    }
    logger.info(json.dumps(trace))
    return trace


def format_citations(source_docs):
    """Format retrieved documents into citation objects"""
    citations = []
    seen_chunks = set()
    
    for doc in source_docs:
        chunk_key = (doc.metadata.get('page', 'N/A'), doc.metadata.get('chunk_id', 'N/A'))
        if chunk_key not in seen_chunks:
            citations.append({
                'page': doc.metadata.get('page', 'N/A'),
                'chunk_id': doc.metadata.get('chunk_id', 'N/A'),
                'text': doc.page_content[:200] + '...' if len(doc.page_content) > 200 else doc.page_content,
                'source': doc.metadata.get('source', 'Unknown')
            })
            seen_chunks.add(chunk_key)
    
    return citations


def extract_and_load_document(file):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        docs = extract_lcdocs_from_file(file)
        if docs is None:
            raise ValueError("Failed to extract documents from file")
            
        initialize_qa_rag_chain(docs)
        
        # Get summary with retrieval tracking
        question = 'Provide a detailed summary of the document'
        rag_input = create_rag_input_dict(question, [])
        
        # Manually retrieve documents for citations
        retrieved_docs = RETRIEVER.invoke(question)
        
        # Get answer
        result = RAG_CHAIN.invoke(rag_input)
        
        # Calculate metrics
        latency_ms = (time.time() - start_time) * 1000
        
        # Estimate token usage (rough approximation)
        prompt_tokens = sum(len(doc.page_content.split()) for doc in retrieved_docs) + len(question.split())
        completion_tokens = len(result.split())
        token_usage = {
            "prompt_tokens": prompt_tokens * 1.3,  # rough estimate
            "completion_tokens": completion_tokens * 1.3,
            "total_tokens": (prompt_tokens + completion_tokens) * 1.3
        }
        
        citations = format_citations(retrieved_docs)
        
        # Log trace
        log_request_trace(
            request_id=request_id,
            question=question,
            answer=result,
            citations=citations,
            token_usage=token_usage,
            latency_ms=latency_ms,
            retrieval_count=len(retrieved_docs)
        )
        
        return {
            'answer': result,
            'citations': citations,
            'request_id': request_id,
            'latency_ms': latency_ms,
            'token_usage': token_usage
        }
        
    except Exception as e:
        logger.error(f"Request {request_id} failed: {str(e)}")
        logger.error(traceback.format_exc())
        raise e

def get_answer_from_rag(question, chat_history):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        rag_input_dict = create_rag_input_dict(question, chat_history)
        
        # Manually retrieve documents for citations
        retrieved_docs = RETRIEVER.invoke(question)
        
        # Get answer
        result = RAG_CHAIN.invoke(rag_input_dict)
        
        # Calculate metrics
        latency_ms = (time.time() - start_time) * 1000
        
        # Estimate token usage
        prompt_tokens = sum(len(doc.page_content.split()) for doc in retrieved_docs) + len(question.split())
        completion_tokens = len(result.split())
        token_usage = {
            "prompt_tokens": prompt_tokens * 1.3,
            "completion_tokens": completion_tokens * 1.3,
            "total_tokens": (prompt_tokens + completion_tokens) * 1.3
        }
        
        citations = format_citations(retrieved_docs)
        
        # Log trace
        log_request_trace(
            request_id=request_id,
            question=question,
            answer=result,
            citations=citations,
            token_usage=token_usage,
            latency_ms=latency_ms,
            retrieval_count=len(retrieved_docs)
        )
        
        return {
            'answer': result,
            'citations': citations,
            'request_id': request_id,
            'latency_ms': latency_ms,
            'token_usage': token_usage
        }
        
    except Exception as e:
        logger.error(f"Request {request_id} failed: {str(e)}")
        logger.error(traceback.format_exc())
        raise e

def get_answer_from_rag_stream(question, chat_history):
    """Stream RAG response with citations"""
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        rag_input_dict = create_rag_input_dict(question, chat_history)
        
        # Retrieve documents for citations
        retrieved_docs = RETRIEVER.invoke(question)
        citations = format_citations(retrieved_docs)
        
        # Yield citations first
        yield json.dumps({
            'type': 'citations',
            'data': citations,
            'request_id': request_id
        }) + '\n'
        
        # Stream answer
        full_answer = ""
        for chunk in RAG_CHAIN.stream(rag_input_dict):
            if chunk:
                full_answer += chunk
                yield json.dumps({
                    'type': 'token',
                    'data': chunk
                }) + '\n'
        
        # Calculate final metrics
        latency_ms = (time.time() - start_time) * 1000
        prompt_tokens = sum(len(doc.page_content.split()) for doc in retrieved_docs) + len(question.split())
        completion_tokens = len(full_answer.split())
        token_usage = {
            "prompt_tokens": prompt_tokens * 1.3,
            "completion_tokens": completion_tokens * 1.3,
            "total_tokens": (prompt_tokens + completion_tokens) * 1.3
        }
        
        # Log trace
        log_request_trace(
            request_id=request_id,
            question=question,
            answer=full_answer,
            citations=citations,
            token_usage=token_usage,
            latency_ms=latency_ms,
            retrieval_count=len(retrieved_docs)
        )
        
        # Yield final metrics
        yield json.dumps({
            'type': 'metrics',
            'data': {
                'latency_ms': latency_ms,
                'token_usage': token_usage
            }
        }) + '\n'
        
    except Exception as e:
        logger.error(f"Stream request {request_id} failed: {str(e)}")
        logger.error(traceback.format_exc())
        yield json.dumps({
            'type': 'error',
            'data': str(e)
        }) + '\n'
