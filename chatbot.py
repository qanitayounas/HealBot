import os
import openai
from dotenv import load_dotenv
from retriever import MentalHealthRetriever
from loader import DocumentLoader
import logging
from colorama import init, Fore, Style
import time

# Initialize colorama for colored output
init(autoreset=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MentalHealthChatbot:
    """A mental health chatbot that provides therapeutic support using OpenAI."""
    
    def __init__(self):
        """Initialize the chatbot with OpenAI API and retriever."""
        # Load environment variables
        load_dotenv()
        
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables. Please set it in your .env file.")
        
        self.client = openai.OpenAI(api_key=api_key)
        
        # Initialize retriever
        self.retriever = MentalHealthRetriever()
        
        # Initialize loader for adding new documents
        self.loader = DocumentLoader()
        
        # System prompt for mental health support
        self.system_prompt = """You are a compassionate mental health support chatbot. Your role is to:

1. Provide empathetic and supportive responses to users experiencing mental health challenges
2. Offer evidence-based therapeutic techniques and coping strategies
3. Encourage healthy habits and positive thinking patterns
4. Recognize when professional help is needed and provide appropriate resources
5. Never give medical advice or diagnose conditions
6. Always prioritize user safety and well-being

Key guidelines:
- Be warm, understanding, and non-judgmental
- Use therapeutic techniques like CBT, mindfulness, and breathing exercises
- Encourage self-care and healthy lifestyle choices
- Provide practical, actionable advice
- Know when to refer to mental health professionals
- Maintain appropriate boundaries while being supportive

Remember: You are a support tool, not a replacement for professional mental health care."""

    def get_ai_response(self, user_message: str, context: str = "") -> str:
        """
        Get response from OpenAI API.
        
        Args:
            user_message (str): The user's message
            context (str): Relevant context from retriever
            
        Returns:
            str: AI-generated response
        """
        try:
            # Check for emergency keywords first
            if self.retriever.check_emergency_keywords(user_message):
                return self._get_emergency_response()
            
            # Prepare the conversation
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Context: {context}\n\nUser message: {user_message}"}
            ]
            
            # Get response from OpenAI
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7,
                top_p=0.9
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error getting AI response: {e}")
            return "I'm having trouble processing your message right now. Please try again in a moment."

    def _get_emergency_response(self) -> str:
        """Get emergency response for crisis situations."""
        resources = self.retriever.get_emergency_resources()
        
        response = f"""{Fore.RED}I'm concerned about what you're sharing. Your safety is important.

{Fore.YELLOW}Please consider reaching out to one of these resources immediately:

{Fore.CYAN}National Suicide Prevention Lifeline: {resources['National Suicide Prevention Lifeline']}
Crisis Text Line: {resources['Crisis Text Line']}
Emergency Services: {resources['Emergency Services']}

{Fore.GREEN}You don't have to go through this alone. Professional help is available and can make a real difference.

{Fore.WHITE}Would you like to talk about what's going on, or would you prefer to connect with one of these resources right now?"""
        
        return response

    def get_context_for_message(self, user_message: str) -> str:
        """
        Get relevant context for the user's message.
        
        Args:
            user_message (str): The user's message
            
        Returns:
            str: Relevant context
        """
        return self.retriever.get_mental_health_context(user_message)

    def chat(self):
        """Main chat loop for the mental health chatbot."""
        print(f"{Fore.CYAN}🤖 Mental Health Support Chatbot")
        print(f"{Fore.CYAN}=" * 50)
        print(f"{Fore.WHITE}Hello! I'm here to provide mental health support and guidance.")
        print(f"{Fore.WHITE}I can help with anxiety, depression, stress, and other mental health concerns.")
        print(f"{Fore.WHITE}Type 'quit' or 'exit' to end our conversation.")
        print(f"{Fore.YELLOW}Note: I'm a support tool, not a replacement for professional mental health care.")
        print(f"{Fore.CYAN}=" * 50)
        
        conversation_history = []
        
        while True:
            try:
                # Get user input
                user_input = input(f"\n{Fore.GREEN}You: {Style.RESET_ALL}").strip()
                
                # Check for exit command
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print(f"\n{Fore.CYAN}Thank you for talking with me. Take care of yourself! 💙")
                    break
                
                if not user_input:
                    print(f"{Fore.YELLOW}Please type something so I can help you.")
                    continue
                
                # Get relevant context
                context = self.get_context_for_message(user_input)
                
                # Show thinking indicator
                print(f"{Fore.BLUE}🤔 Thinking...", end="", flush=True)
                
                # Get AI response
                response = self.get_ai_response(user_input, context)
                
                # Clear thinking indicator
                print("\r" + " " * 20 + "\r", end="", flush=True)
                
                # Display response
                print(f"\n{Fore.MAGENTA}Chatbot: {Style.RESET_ALL}{response}")
                
                # Store conversation
                conversation_history.append({
                    "user": user_input,
                    "bot": response,
                    "timestamp": time.time()
                })
                
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Goodbye! Take care! 💙")
                break
            except Exception as e:
                logger.error(f"Error in chat loop: {e}")
                print(f"{Fore.RED}I'm experiencing some technical difficulties. Please try again.")

    def add_knowledge_base(self, file_path: str = None, directory_path: str = None):
        """
        Add documents to the knowledge base.
        
        Args:
            file_path (str): Path to a specific file
            directory_path (str): Path to a directory containing documents
        """
        try:
            if file_path:
                if file_path.endswith('.txt'):
                    documents = self.loader.load_text_file(file_path)
                elif file_path.endswith('.pdf'):
                    documents = self.loader.load_pdf_file(file_path)
                elif file_path.endswith('.docx'):
                    documents = self.loader.load_docx_file(file_path)
                else:
                    print(f"{Fore.RED}Unsupported file type: {file_path}")
                    return
                
                chunks = self.loader.split_documents(documents)
                self.loader.add_documents_to_chroma(chunks)
                print(f"{Fore.GREEN}Successfully added {file_path} to knowledge base!")
                
            elif directory_path:
                documents = self.loader.load_documents_from_directory(directory_path)
                chunks = self.loader.split_documents(documents)
                self.loader.add_documents_to_chroma(chunks)
                print(f"{Fore.GREEN}Successfully added documents from {directory_path} to knowledge base!")
                
        except Exception as e:
            logger.error(f"Error adding to knowledge base: {e}")
            print(f"{Fore.RED}Error adding to knowledge base: {e}")

def main():
    """Main function to run the chatbot."""
    try:
        # Initialize chatbot
        chatbot = MentalHealthChatbot()
        
        # Add sample data if no existing data
        print(f"{Fore.YELLOW}Initializing knowledge base...")
        chatbot.loader.create_sample_mental_health_data()
        
        # Start chat
        chatbot.chat()
        
    except ValueError as e:
        print(f"{Fore.RED}Configuration Error: {e}")
        print(f"{Fore.YELLOW}Please make sure to:")
        print(f"1. Create a .env file with your OPENAI_API_KEY")
        print(f"2. Install all required packages: pip install -r requirements.txt")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"{Fore.RED}An unexpected error occurred: {e}")

if __name__ == "__main__":
    main() 