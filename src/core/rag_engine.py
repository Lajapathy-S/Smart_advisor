"""
RAG (Retrieval-Augmented Generation) Engine
Handles document retrieval and context augmentation for the chatbot.
Uses modern LangChain (no deprecated RetrievalQA).
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
import yaml


class RAGEngine:
    """RAG Engine for retrieving relevant information from JSOM catalog."""

    def __init__(self, config_path: str = None):
        """Initialize RAG Engine with configuration."""
        if config_path is None:
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "config.yaml"
        else:
            config_path = Path(config_path)

        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.llm_config = self.config["llm"]
        self.rag_config = self.config["rag"]
        self.vector_db_config = self.config["vector_db"]

        self.embeddings = OpenAIEmbeddings(
            model=self.llm_config["embedding_model"],
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )

        self.vector_store = self._initialize_vector_store()

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.rag_config["chunk_size"],
            chunk_overlap=self.rag_config["chunk_overlap"],
        )

        self.llm = ChatOpenAI(
            model=self.llm_config["model"],
            temperature=self.llm_config["temperature"],
            max_tokens=self.llm_config["max_tokens"],
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )

        self.retriever = self.vector_store.as_retriever(
            search_kwargs={"k": self.rag_config["top_k_results"]}
        )

        # Prompt for RAG (no deprecated chains)
        self.rag_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an AI Smart Advisor helping students with degree planning, "
                    "career mentorship, and skills gap analysis. Use ONLY the following "
                    "context from the official JSOM catalog (source of truth) to answer. "
                    "If the answer is not in the context, say so. Do not make up information.",
                ),
                ("human", "Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"),
            ]
        )

    def _initialize_vector_store(self):
        """Initialize vector store based on configuration."""
        db_type = self.vector_db_config["type"].lower()

        if db_type == "pinecone":
            try:
                from langchain_community.vectorstores import Pinecone
                import pinecone

                pinecone.init(
                    api_key=os.getenv("PINECONE_API_KEY"),
                    environment=os.getenv("PINECONE_ENVIRONMENT"),
                )
                return Pinecone.from_existing_index(
                    index_name=self.vector_db_config["pinecone"]["index_name"],
                    embedding=self.embeddings,
                )
            except ImportError:
                db_type = "chroma"

        persist_dir = self.vector_db_config["chroma"]["persist_directory"]
        if not os.path.isabs(persist_dir):
            project_root = Path(__file__).resolve().parent.parent.parent
            persist_dir = str(project_root / persist_dir.lstrip("./"))
        os.makedirs(persist_dir, exist_ok=True)
        return Chroma(
            persist_directory=persist_dir,
            embedding_function=self.embeddings,
            collection_name=self.vector_db_config["chroma"]["collection_name"],
        )

    def _format_docs(self, docs: List[Document]) -> str:
        """Format retrieved documents as a single context string."""
        return "\n\n".join(doc.page_content for doc in docs)

    def query(self, question: str) -> Dict[str, Any]:
        """
        Query the RAG system: retrieve docs, then run LLM with context.
        """
        docs = self.retriever.invoke(question)
        context = self._format_docs(docs)

        chain = self.rag_prompt | self.llm | StrOutputParser()
        answer = chain.invoke({"context": context, "question": question})

        return {
            "answer": answer,
            "source_documents": docs,
        }

    def add_documents(
        self, documents: List[str], metadatas: Optional[List[Dict]] = None
    ):
        """Add documents to the vector store (with optional splitting)."""
        docs = self.text_splitter.create_documents(documents, metadatas=metadatas)
        self.vector_store.add_documents(docs)
        if hasattr(self.vector_store, "persist"):
            self.vector_store.persist()

    def similarity_search(self, query: str, k: int = None) -> List[Dict]:
        """Perform similarity search in the vector store."""
        k = k or self.rag_config["top_k_results"]
        results = self.vector_store.similarity_search_with_score(query, k=k)
        threshold = self.rag_config.get("similarity_threshold", 0.0)
        return [
            {"content": doc.page_content, "metadata": doc.metadata, "score": score}
            for doc, score in results
            if score >= threshold
        ]
