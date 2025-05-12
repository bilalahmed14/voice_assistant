import os
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA

class RAGProcessor:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.llm = ChatOpenAI(temperature=0)
        self.vector_store = None
        self.initialize_knowledge_base()

    def initialize_knowledge_base(self):
        # Create knowledge base directory if it doesn't exist
        os.makedirs('knowledge_base', exist_ok=True)
        
        # Load and process documents
        documents = []
        for filename in os.listdir('knowledge_base'):
            if filename.endswith(('.txt', '.md')):
                with open(os.path.join('knowledge_base', filename), 'r', encoding='utf-8') as f:
                    documents.append(f.read())

        if not documents:
            raise ValueError("No documents found in knowledge_base directory")

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        texts = text_splitter.split_text('\n'.join(documents))

        # Create vector store
        self.vector_store = FAISS.from_texts(
            texts,
            self.embeddings
        )

    def get_answer(self, question: str) -> str:
        if not self.vector_store:
            raise ValueError("Knowledge base not initialized")

        # Create retrieval chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever()
        )

        # Get answer
        result = qa_chain.run(question)
        return result 