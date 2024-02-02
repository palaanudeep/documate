from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage


RAG_CHAIN = None
chatModel = ChatOpenAI(model_name="gpt-3.5-turbo-0125", temperature=0)

def initialize_qa_rag_chain(docs):
    global RAG_CHAIN

    retriever = create_doc_retriever(docs)
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
        RunnablePassthrough.assign(context=get_contextualized_question | retriever | format_docs)
        | qa_prompt
        | chatModel
        | StrOutputParser()
    )
    return RAG_CHAIN

def create_doc_retriever(docs):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, add_start_index=True)
    splits = text_splitter.split_documents(docs)
    vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings(model="text-embedding-3-small"))
    retriever = vectorstore.as_retriever()
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
    chat_history = [HumanMessage(content=chat_history[i]) if i%2 == 0 else AIMessage(content=chat_history[i]) for i in range(len(chat_history))]
    rag_input_dict = {
        "question": question,
        "chat_history": chat_history,
    }
    return rag_input_dict