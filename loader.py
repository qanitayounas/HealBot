import os
from typing import List, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredURLLoader
)
from langchain.schema import Document
import chromadb
from chromadb.config import Settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentLoader:
    """Handles loading and processing of documents for the mental health chatbot."""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize the document loader.
        
        Args:
            persist_directory (str): Directory to persist ChromaDB data
        """
        self.persist_directory = persist_directory
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="mental_health_knowledge",
            metadata={"hnsw:space": "cosine"}
        )
    
    def load_text_file(self, file_path: str) -> List[Document]:
        """Load a text file and return documents."""
        try:
            loader = TextLoader(file_path)
            documents = loader.load()
            logger.info(f"Loaded text file: {file_path}")
            return documents
        except Exception as e:
            logger.error(f"Error loading text file {file_path}: {e}")
            return []
    
    def load_pdf_file(self, file_path: str) -> List[Document]:
        """Load a PDF file and return documents."""
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            logger.info(f"Loaded PDF file: {file_path}")
            return documents
        except Exception as e:
            logger.error(f"Error loading PDF file {file_path}: {e}")
            return []
    
    def load_docx_file(self, file_path: str) -> List[Document]:
        """Load a DOCX file and return documents."""
        try:
            loader = Docx2txtLoader(file_path)
            documents = loader.load()
            logger.info(f"Loaded DOCX file: {file_path}")
            return documents
        except Exception as e:
            logger.error(f"Error loading DOCX file {file_path}: {e}")
            return []
    
    def load_url(self, url: str) -> List[Document]:
        """Load content from a URL and return documents."""
        try:
            loader = UnstructuredURLLoader([url])
            documents = loader.load()
            logger.info(f"Loaded URL: {url}")
            return documents
        except Exception as e:
            logger.error(f"Error loading URL {url}: {e}")
            return []
    
    def load_documents_from_directory(self, directory_path: str) -> List[Document]:
        """Load all supported documents from a directory."""
        documents = []
        
        if not os.path.exists(directory_path):
            logger.error(f"Directory does not exist: {directory_path}")
            return documents
        
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            
            if filename.endswith('.txt'):
                documents.extend(self.load_text_file(file_path))
            elif filename.endswith('.pdf'):
                documents.extend(self.load_pdf_file(file_path))
            elif filename.endswith('.docx'):
                documents.extend(self.load_docx_file(file_path))
        
        logger.info(f"Loaded {len(documents)} documents from directory: {directory_path}")
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks."""
        if not documents:
            return []
        
        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"Split {len(documents)} documents into {len(chunks)} chunks")
        return chunks
    
    def add_documents_to_chroma(self, documents: List[Document], metadata: Optional[dict] = None):
        """Add documents to ChromaDB collection."""
        if not documents:
            logger.warning("No documents to add to ChromaDB")
            return
        
        # Prepare data for ChromaDB
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        ids = [f"doc_{i}" for i in range(len(documents))]
        
        # Add to collection
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Added {len(documents)} documents to ChromaDB")
    
    def create_sample_mental_health_data(self):
        """Create sample mental health data for testing."""
        sample_data = [
            {
                "content": "Cognitive Behavioral Therapy (CBT) is a form of psychotherapy that focuses on identifying and changing negative thought patterns and behaviors. It's effective for treating depression, anxiety, and other mental health conditions.",
                "metadata": {"source": "mental_health_therapy", "topic": "CBT"}
            },
            {
                "content": "Mindfulness meditation involves focusing on the present moment without judgment. Regular practice can reduce stress, anxiety, and improve overall mental well-being.",
                "metadata": {"source": "mental_health_therapy", "topic": "mindfulness"}
            },
            {
                "content": "Deep breathing exercises can help calm the nervous system. Try inhaling for 4 counts, holding for 4, and exhaling for 6 counts to activate the parasympathetic nervous system.",
                "metadata": {"source": "mental_health_therapy", "topic": "breathing_exercises"}
            },
            {
                "content": "Regular exercise releases endorphins, natural mood lifters. Even 30 minutes of moderate exercise can significantly improve mood and reduce symptoms of depression and anxiety.",
                "metadata": {"source": "mental_health_therapy", "topic": "exercise"}
            },
            {
                "content": "Maintaining a consistent sleep schedule is crucial for mental health. Aim for 7-9 hours of quality sleep per night to support emotional regulation and cognitive function.",
                "metadata": {"source": "mental_health_therapy", "topic": "sleep_hygiene"}
            }
        ]
        
        # Add sample data to ChromaDB
        texts = [item["content"] for item in sample_data]
        metadatas = [item["metadata"] for item in sample_data]
        ids = [f"sample_{i}" for i in range(len(sample_data))]
        
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info("Added sample mental health data to ChromaDB")

if __name__ == "__main__":
    # Test the loader
    loader = DocumentLoader()
    loader.create_sample_mental_health_data()
    print("Sample mental health data loaded successfully!") 