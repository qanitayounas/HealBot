# HealBot 

A terminal-based mental health support chatbot powered by OpenAI GPT-3.5-turbo and ChromaDB for knowledge retrieval. This chatbot provides therapeutic support, coping strategies, and mental health guidance for users.

## Features

- 🤖 **AI-Powered Responses**: Uses OpenAI GPT-3.5-turbo for intelligent, empathetic responses
- 📚 **Knowledge Base**: ChromaDB integration for storing and retrieving mental health information
- 🧠 **Mental Health Focus**: Specialized for mental health support and therapeutic guidance
- 🔒 **Secure**: Environment variables for API key management
- 📁 **Document Loading**: Support for PDF, DOCX, and TXT files
- 🚨 **Emergency Detection**: Recognizes crisis situations and provides appropriate resources
- 💬 **Interactive Terminal Interface**: Color-coded, user-friendly terminal interface

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Internet connection for API calls

## Installation

1. **Clone or download the project files**

2. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your OpenAI API key**:
   - Create a `.env` file in the project root
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     ```

## Usage

### Basic Usage

Run the chatbot:
```bash
python chatbot.py
```

### Adding Knowledge Base

You can add your own mental health documents to enhance the chatbot's knowledge:

```python
from chatbot import MentalHealthChatbot

chatbot = MentalHealthChatbot()

# Add a single file
chatbot.add_knowledge_base(file_path="path/to/your/document.pdf")

# Add all documents from a directory
chatbot.add_knowledge_base(directory_path="path/to/your/documents/")
```

### Supported File Types

- **PDF files** (.pdf)
- **Word documents** (.docx)
- **Text files** (.txt)

## Project Structure

```
ment_chat/
├── chatbot.py          # Main chatbot logic and OpenAI integration
├── retriever.py        # ChromaDB retrieval functionality
├── loader.py           # Document loading and processing
├── requirements.txt    # Python dependencies
├── env_template.txt    # Environment variables template
├── README.md          # This file
└── chroma_db/         # ChromaDB data storage (created automatically)
```

## Key Components

### 1. `chatbot.py`
- Main chatbot interface
- OpenAI API integration
- Emergency keyword detection
- Terminal-based chat interface

### 2. `retriever.py`
- ChromaDB query functionality
- Relevant chunk retrieval
- Emergency resource management
- Therapeutic suggestion generation

### 3. `loader.py`
- Document processing and chunking
- Multiple file format support
- ChromaDB integration
- Sample mental health data creation

## Mental Health Focus

This chatbot is specifically designed for mental health support and includes:

- **Therapeutic Techniques**: CBT, mindfulness, breathing exercises
- **Coping Strategies**: Stress management, anxiety reduction
- **Emergency Resources**: Crisis hotlines and emergency contacts
- **Professional Referral**: Guidance on when to seek professional help
- **Safety Monitoring**: Detection of crisis situations

## Safety Features

- **Emergency Detection**: Recognizes crisis keywords and provides immediate resources
- **Professional Boundaries**: Clear about limitations and when to seek professional help
- **Resource Provision**: Provides contact information for mental health professionals
- **Crisis Response**: Immediate access to suicide prevention and crisis resources

## Important Notes

⚠️ **Disclaimer**: This chatbot is a support tool and should not replace professional mental health care. Always consult with qualified mental health professionals for serious concerns.

🔒 **Privacy**: Conversations are not stored permanently, but API calls are processed by OpenAI. Review their privacy policy for details.

🚨 **Crisis Situations**: If you're experiencing a mental health crisis, please contact emergency services or a crisis hotline immediately.

## Customization

### Adding Custom Knowledge

1. Prepare your mental health documents (PDF, DOCX, or TXT)
2. Use the `add_knowledge_base()` method to load them
3. The chatbot will automatically use this information in responses

### Modifying System Prompt

Edit the `system_prompt` in `chatbot.py` to customize the chatbot's personality and approach.

### Adjusting Retrieval Parameters

Modify the `n_results` parameter in `retriever.py` to change how many relevant chunks are retrieved.

## Troubleshooting

### Common Issues

1. **API Key Error**: Ensure your `.env` file contains the correct OpenAI API key
2. **Import Errors**: Make sure all dependencies are installed with `pip install -r requirements.txt`
3. **ChromaDB Issues**: Delete the `chroma_db` folder to reset the knowledge base

### Getting Help

- Check that all required packages are installed
- Verify your OpenAI API key is valid and has sufficient credits
- Ensure you have proper internet connectivity for API calls

## Contributing

Feel free to enhance this chatbot by:
- Adding more therapeutic techniques
- Expanding the knowledge base
- Improving emergency detection
- Adding new file format support

## License


This project is for educational and support purposes. Please use responsibly and in accordance with mental health best practices. 
