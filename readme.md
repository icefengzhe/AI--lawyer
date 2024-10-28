# AI Lawyer

AI Lawyer is a web-based application that provides quick legal consultation and advice through a chat interface. It uses a Retrieval-Augmented Generation (RAG) model to provide accurate and context-aware responses.

## Features

- User registration and login
- Chat interface for legal consultations
- History of past conversations
- Automatic generation of chat titles
- Feedback system for conversations
- Chat content search
- Paginated loading of chat messages

## Technology Stack

### Backend
- Python 3.10
- FastAPI
- SQLAlchemy
- Langchain
- ChatTongyi (Tongyi AI model)
- FAISS (Vector Store)

### Frontend
- HTML5
- CSS3
- JavaScript (ES6+)
- WebSocket (for real-time communication)

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ai-lawyer.git
   cd ai-lawyer
   ```

2. Set up a virtual environment:
   ```
   python -m venv env
   source env/bin/activate  # On Windows use `env\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory and add the following:
   ```
   DASHSCOPE_API_KEY=your_api_key_here
   DATABASE_URL=sqlite:///./test.db
   SECRET_KEY=your_secret_key_here
   VECTOR_DB_PATH=./vector_db
   ```

5. Initialize the database:
   ```
   python init_db.py
   ```

6. Run the backend server:
   ```
   uvicorn app.main:app --reload
   ```

7. Open `frontend/login.html` in a web browser to use the application.

## Usage

1. Register a new account or log in to an existing one on the login page.
2. Start a new conversation by typing your legal question in the chat interface on the main page.
3. View your conversation history in the sidebar on the left, click to switch between different conversations.
4. Use the search function to find specific chat content.
5. Provide feedback on the AI's responses if needed.

## Project Structure

```
ai-lawyer/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── main.py
│   │   ├── config.py
│   │   └── database.py
│   └── requirements.txt
├── frontend/
│   ├── css/
│   ├── js/
│   ├── index.html
│   └── login.html
├── .env
├── .gitignore
├── README.md
└── README-cn.md
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an Issue to discuss new features and improvements.

## License

This project is licensed under the MIT License.
