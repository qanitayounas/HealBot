import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MentalHealthRetriever:
    """Handles retrieval of relevant mental health information from ChromaDB."""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize the retriever.
        
        Args:
            persist_directory (str): Directory where ChromaDB data is stored
        """
        self.persist_directory = persist_directory
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get the collection
        self.collection = self.client.get_collection("mental_health_knowledge")
    
    def retrieve_relevant_chunks(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks based on the user's query.
        
        Args:
            query (str): The user's query/question
            n_results (int): Number of relevant chunks to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of relevant chunks with their metadata
        """
        try:
            # Query the collection
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            chunks = []
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    chunks.append({
                        'content': doc,
                        'metadata': metadata,
                        'distance': distance,
                        'relevance_score': 1 - distance  # Convert distance to relevance score
                    })
            
            logger.info(f"Retrieved {len(chunks)} relevant chunks for query: {query}")
            return chunks
            
        except Exception as e:
            logger.error(f"Error retrieving chunks for query '{query}': {e}")
            return []
    
    def get_mental_health_context(self, user_message: str) -> str:
        """
        Get relevant mental health context for the user's message.
        
        Args:
            user_message (str): The user's message
            
        Returns:
            str: Formatted context from relevant chunks
        """
        chunks = self.retrieve_relevant_chunks(user_message, n_results=3)
        
        if not chunks:
            return "I'm here to help with mental health support. How can I assist you today?"
        
        # Format context from retrieved chunks
        context_parts = []
        for chunk in chunks:
            if chunk['relevance_score'] > 0.5:  # Only include highly relevant chunks
                context_parts.append(chunk['content'])
        
        if context_parts:
            context = "\n\n".join(context_parts)
            return f"Based on mental health knowledge:\n{context}"
        else:
            return "I'm here to provide mental health support. How can I help you today?"
    
    def get_therapeutic_suggestions(self, user_message: str) -> List[str]:
        """
        Get therapeutic suggestions based on the user's message.
        
        Args:
            user_message (str): The user's message
            
        Returns:
            List[str]: List of therapeutic suggestions
        """
        chunks = self.retrieve_relevant_chunks(user_message, n_results=5)
        
        suggestions = []
        for chunk in chunks:
            if chunk['relevance_score'] > 0.6:
                # Extract actionable suggestions from the content
                content = chunk['content']
                if any(keyword in content.lower() for keyword in ['try', 'practice', 'exercise', 'technique', 'method']):
                    suggestions.append(content)
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def get_emergency_resources(self) -> Dict[str, str]:
        """
        Get emergency mental health resources.
        
        Returns:
            Dict[str, str]: Dictionary of emergency resources
        """
        return {
            "National Suicide Prevention Lifeline": "1-800-273-8255",
            "Crisis Text Line": "Text HOME to 741741",
            "Emergency Services": "911",
            "Mental Health America": "1-800-969-6642"
        }
    
    def check_emergency_keywords(self, user_message: str) -> bool:
        """
        Check if the user's message contains emergency keywords.
        
        Args:
            user_message (str): The user's message
            
        Returns:
            bool: True if emergency keywords are detected
        """
        emergency_keywords = [
            'suicide', 'kill myself', 'end my life', 'want to die',
            'self-harm', 'hurt myself', 'no reason to live',
            'everyone would be better off', 'can\'t take it anymore'
        ]
        
        message_lower = user_message.lower()
        return any(keyword in message_lower for keyword in emergency_keywords)

if __name__ == "__main__":
    # Test the retriever
    retriever = MentalHealthRetriever()
    
    # Test queries
    test_queries = [
        "I'm feeling anxious",
        "How can I practice mindfulness?",
        "I'm having trouble sleeping"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        chunks = retriever.retrieve_relevant_chunks(query)
        print(f"Found {len(chunks)} relevant chunks")
        for chunk in chunks:
            print(f"- {chunk['content'][:100]}...") 