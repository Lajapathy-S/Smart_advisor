"""
RAG (Retrieval-Augmented Generation) Engine
Handles document retrieval and context augmentation for the chatbot.
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import yaml


class RAGEngine:
    """RAG Engine for retrieving relevant information from JSOM catalog."""
    
    def __init__(self, config_path: str = None):
        """Initialize RAG Engine with configuration."""
        if config_path is None:
            # Default to project root config
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "config.yaml"
        else:
            config_path = Path(config_path)
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.llm_config = self.config['llm']
        self.rag_config = self.config['rag']
        self.vector_db_config = self.config['vector_db']
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model=self.llm_config['embedding_model'],
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        
        # Initialize vector store
        self.vector_store = self._initialize_vector_store()
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.rag_config['chunk_size'],
            chunk_overlap=self.rag_config['chunk_overlap']
        )
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model_name=self.llm_config['model'],
            temperature=self.llm_config['temperature'],
            max_tokens=self.llm_config['max_tokens'],
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        
        # Initialize retrieval chain
        self.qa_chain = self._create_qa_chain()
    
    def _initialize_vector_store(self):
        """Initialize vector store based on configuration."""
        db_type = self.vector_db_config['type'].lower()
        
        if db_type == 'pinecone':
            try:
                from langchain_community.vectorstores import Pinecone
                import pinecone
                pinecone.init(
                    api_key=os.getenv('PINECONE_API_KEY'),
                    environment=os.getenv('PINECONE_ENVIRONMENT')
                )
                return Pinecone.from_existing_index(
                    index_name=self.vector_db_config['pinecone']['index_name'],
                    embedding=self.embeddings
                )
            except ImportError:
                print("Pinecone not available, falling back to ChromaDB")
                db_type = 'chroma'
        
        # Default to ChromaDB (create dir if needed for Streamlit Cloud)
        persist_dir = self.vector_db_config['chroma']['persist_directory']
        if not os.path.isabs(persist_dir):
            project_root = Path(__file__).resolve().parent.parent.parent
            persist_dir = str(project_root / persist_dir.lstrip("./"))
        os.makedirs(persist_dir, exist_ok=True)
        return Chroma(
            persist_directory=persist_dir,
            embedding_function=self.embeddings,
            collection_name=self.vector_db_config['chroma']['collection_name']
        )
    
    def _create_qa_chain(self):
        """Create QA chain with custom prompt."""
        prompt_template = """You are an AI Smart Advisor helping students with degree planning, 
        career mentorship, and skills gap analysis. Use the following context from the official 
        JSOM catalog (which is the source of truth) to answer questions accurately. If you don't 
        know the answer based on the context, say so rather than making up information.

        Context: {context}

        Question: {question}

        Answer:"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        retriever = self.vector_store.as_retriever(
            search_kwargs={"k": self.rag_config['top_k_results']}
        )
        
        return RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Query the RAG system with a question.
        
        Args:
            question: User's question
            
        Returns:
            Dictionary with answer and source documents
        """
        result = self.qa_chain({"query": question})
        return {
            "answer": result["result"],
            "source_documents": result.get("source_documents", [])
        }
    
    def add_documents(self, documents: List[str], metadatas: Optional[List[Dict]] = None):
        """
        Add documents to the vector store.
        
        Args:
            documents: List of document texts
            metadatas: Optional list of metadata dictionaries
        """
        texts = self.text_splitter.create_documents(documents, metadatas=metadatas)
        self.vector_store.add_documents(texts)
        # Persist if ChromaDB
        if hasattr(self.vector_store, 'persist'):
            self.vector_store.persist()
    
    def similarity_search(self, query: str, k: int = None) -> List[Dict]:
        """
        Perform similarity search in the vector store.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of similar documents with scores
        """
        k = k or self.rag_config['top_k_results']
        results = self.vector_store.similarity_search_with_score(query, k=k)
        
        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": score
            }
            for doc, score in results
            if score >= self.rag_config['similarity_threshold']
        ]
