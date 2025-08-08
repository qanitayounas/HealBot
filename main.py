from fastapi import FastAPI, HTTPException, Depends, status, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List, Optional
import jwt
import datetime
import os
from datetime import datetime, timedelta
from PyPDF2 import PdfReader
import openai
from dotenv import load_dotenv
from pymongo import MongoClient
from passlib.context import CryptContext
from jose import JWTError, jwt
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request as StarletteRequest
from starlette.responses import RedirectResponse
import re
from starlette.middleware.sessions import SessionMiddleware
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="HealBot API", version="1.0.0")

# Add SessionMiddleware for OAuth
import os
app.add_middleware(
    SessionMiddleware,
    secret_key="supersecretkey"
)

# CORS middleware to allow all origins, methods, and headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
SECRET_KEY = "your_secret_key_here"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

security = HTTPBearer()

client = MongoClient("mongodb://localhost:27017/")
db = client["ment_chat_db"]
users_collection = db["users"]
sessions_collection = db["sessions"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    timestamp: datetime

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class UserProfile(BaseModel):
    name: str
    email: str
    id: str

class Session2Request(BaseModel):
    answers: list
    questions: list

class TherapyStep(BaseModel):
    heading: str
    explanation: str

class Session2Response(BaseModel):
    classification: str
    therapy_plan: List[TherapyStep]

class Session2ChatRequest(BaseModel):
    question: str
    session1Summary: dict
    therapy: dict

class Session2ChatResponse(BaseModel):
    response: str

class UserRegister(BaseModel):
    email: str
    password: str
    name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class SessionData(BaseModel):
    user_id: str
    session_number: int
    data: dict

class OCDSession2Request(BaseModel):
    answers: list
    questions: list

class OCDTherapyStep(BaseModel):
    heading: str
    explanation: str

class OCDSession2Response(BaseModel):
    classification: str
    therapy_plan: List[OCDTherapyStep]


# Mock user database
mock_users = {
    "user@example.com": {
        "id": "1",
        "name": "John Doe",
        "email": "user@example.com",
        "password": "password123"  # In production, use hashed passwords
    }
}

# Mock chat history
chat_history = {}

# Utility functions

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user(email: str):
    return users_collection.find_one({"email": email})

# Auth dependencies
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(email)
    if user is None:
        raise credentials_exception
    return user

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def generate_bot_response(user_message: str) -> str:
    """Generate bot response based on user input"""
    message_lower = user_message.lower()
    
    if any(word in message_lower for word in ['anxious', 'worried', 'anxiety']):
        return (
            "I'm sorry you're feeling anxious. Anxiety can be overwhelming, but you're not alone. "
            "Let's try a simple breathing exercise together: Inhale deeply for 4 seconds, hold your breath for 4 seconds, and exhale slowly for 4 seconds. "
            "If you'd like, I can guide you through more relaxation techniques or help you identify what's making you feel this way. Would you like to talk more about it or try another exercise?"
        )
    
    elif any(word in message_lower for word in ['sad', 'depressed', 'down']):
        return (
            "It's okay to feel sad sometimes. Remember, your feelings are valid and it's important to acknowledge them. "
            "If you'd like, you can share more about what's making you feel this way, or I can suggest some activities that might help lift your mood, such as journaling, listening to music, or taking a short walk. "
            "Would you like to talk more about it or try a mood-boosting activity?"
        )
    
    elif any(word in message_lower for word in ['good', 'happy', 'great']):
        return (
            "That's wonderful to hear! Positive moments are worth celebrating. "
            "What made your day better? Sharing your happy experiences can help reinforce positive feelings. "
            "Is there anything you'd like to talk about or any goals you'd like to set for yourself today?"
        )
    
    elif any(word in message_lower for word in ['sleep', 'insomnia', 'tired']):
        return (
            "Sleep issues can be really challenging and affect many aspects of your life. "
            "Have you tried establishing a regular bedtime routine, limiting screen time before bed, or practicing relaxation techniques? "
            "If you'd like, I can share some sleep hygiene tips or help you track your sleep patterns. Would you like more advice on improving your sleep?"
        )
    
    elif any(word in message_lower for word in ['ocd', 'obsessive', 'compulsive']):
        return (
            "I understand OCD can be very difficult to manage. You're showing strength by reaching out. "
            "Exposure and Response Prevention (ERP) is a proven technique for managing OCD symptoms. "
            "Would you like to learn more about ERP or talk about your experiences? Remember, I'm here to support you every step of the way."
        )
    
    elif any(word in message_lower for word in ['help', 'support']):
        return (
            "I'm here to help you. You can talk to me about your feelings, and I'll do my best to support you. "
            "If you ever feel overwhelmed, it's okay to ask for help from friends, family, or a mental health professional. "
            "Would you like some resources or coping strategies?"
        )
    
    else:
        return (
            "Thank you for sharing that with me. Every feeling and thought you have is important. "
            "Would you like to talk more about what's on your mind, or is there something specific you'd like help with today?"
        )

@app.get("/")
async def root():
    return {"message": "HealBot API is running!"}

@app.post("/api/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """Login endpoint"""
    user = users_collection.find_one({"email": login_data.email})
    if not user or not verify_password(login_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    access_token = create_access_token(data={"sub": user["email"]})
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": str(user.get("_id", "")),
            "name": user.get("name", ""),
            "email": user["email"]
        }
    )

@app.post("/api/register")
def register(user: UserRegister):
    if get_user(user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    user_dict = user.dict()
    user_dict["password"] = hashed_password
    users_collection.insert_one(user_dict)
    # Fetch the user back to get the _id
    new_user = users_collection.find_one({"email": user.email})
    return {
        "msg": "User registered successfully",
        "user": {
            "id": str(new_user.get("_id", "")),
            "name": new_user.get("name", ""),
            "email": new_user["email"]
        }
    }

@app.post("/login")
def login(user: UserLogin):
    db_user = get_user(user.email)
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer", "user": {"email": db_user["email"], "name": db_user.get("name", "")}}

@app.get("/api/user", response_model=UserProfile)
async def get_user_profile(email: str = Depends(verify_token)):
    """Get user profile from MongoDB"""
    user = users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserProfile(
        id=str(user.get("_id", "")),
        name=user.get("name", ""),
        email=user["email"]
    )

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_bot(chat_data: ChatMessage):
    """Chat endpoint for bot responses (no auth)"""
    email = "guest"
    if not chat_data or not chat_data.message:
        raise HTTPException(status_code=400, detail="Message is required")

    user_message = chat_data.message

    # Generate bot response
    bot_response = generate_bot_response(user_message)

    # Store in chat history (optional)
    if email not in chat_history:
        chat_history[email] = []

    chat_history[email].append({
        "user_message": user_message,
        "bot_response": bot_response,
        "timestamp": datetime.utcnow()
    })

    return ChatResponse(
        response=bot_response,
        timestamp=datetime.utcnow()
    )

@app.get("/api/chat/history")
async def get_chat_history():
    """Get chat history for guest user (no auth)"""
    email = "guest"
    return chat_history.get(email, [])

@app.post("/api/session2-therapy", response_model=Session2Response)
async def session2_therapy(data: Session2Request):
    # Read CBT-I guidelines from PDF
    cbt_path = os.path.join(os.path.dirname(__file__), '../documents/CBT-I insomnia dataset.pdf')
    try:
        reader = PdfReader(cbt_path)
        cbt_text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read CBT-I document: {e}")

    # Format user answers
    user_qa = "\n".join([f"Q: {q}\nA: {a}" for q, a in zip(data.questions, data.answers)])

    # Compose OpenAI prompt
    try:
        # Do NOT print the API key for security
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # Reduce the amount of CBT-I PDF text sent
        cbt_excerpt = cbt_text[:800]
        # Improved prompt: use OpenAI's own CBT-I knowledge, use PDF only as reference
        prompt = f"""
You are a compassionate insomnia therapist and expert in Cognitive Behavioral Therapy for Insomnia (CBT-I).

Below are the user's answers from their intake session:
{user_qa}

Your response MUST follow this exact structure and formatting, with NO extra sentences before or after:

Insomnia Classification:
[State the user's insomnia type and a brief explanation. This section must NOT be labeled as a step, and must be visually distinct.]

According to your insomnia classification, follow the below CBT-I therapy steps:

Sleep Education
[In clear, simple language, provide a detailed, step-by-step explanation (at least 5-6 sentences) tailored to the user's answers above. Reference their specific habits, beliefs, and struggles. Do NOT use asterisks or Markdown for bolding. Use clear, plain language and numbered or bulleted lists if needed.]

Sleep Hygiene
[Same as above: detailed, easy-to-understand, and tailored to the user's answers. Do NOT use asterisks or Markdown for bolding.]

Stimulus Control
[Same as above. Do NOT use asterisks or Markdown for bolding.]

Sleep Restriction
[Same as above. Do NOT use asterisks or Markdown for bolding.]

Cognitive Therapy
[Same as above. Do NOT use asterisks or Markdown for bolding.]

Relaxation
[Same as above. Do NOT use asterisks or Markdown for bolding.]

Relapse Prevention
[Same as above. Do NOT use asterisks or Markdown for bolding.]

IMPORTANT:
- Each step must be separated by a blank line.
- The step heading and its explanation must be on separate lines.
- The step heading must be ONLY the exact, short heading from the list above (no 'Step 1:', 'Step 2:', etc.).
- Do NOT merge all step details into one paragraph.
- Do NOT add any extra sentences or summary before or after the steps. Only output the sections and steps as shown above.
- For each step, use the user's answers to make the advice as specific and relevant as possible.
- Each step’s explanation should be at least 5-6 sentences, easy to understand, and include practical examples.
- Do NOT use asterisks or Markdown for bolding anywhere in your response.
"""
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.7
        )
        content = response.choices[0].message.content
        # Post-process to split classification and steps into distinct blocks
        step_headings = [
            "Sleep Education",
            "Sleep Hygiene",
            "Stimulus Control",
            "Sleep Restriction",
            "Cognitive Therapy",
            "Relaxation",
            "Relapse Prevention"
        ]
        step_pattern = r"(?:^|\n)({})\n".format("|".join(re.escape(h) for h in step_headings))
        # Find all step headings and their positions
        matches = list(re.finditer(step_pattern, content))
        steps = []
        def clean_explanation(text):
            return text.replace('**', '').strip()
        for i, match in enumerate(matches):
            start = match.end()
            end = matches[i+1].start() if i+1 < len(matches) else len(content)
            heading = match.group(1)
            explanation = content[start:end].strip()
            explanation = clean_explanation(explanation)  # Remove stars
            steps.append({"heading": heading, "explanation": explanation})
        # Classification is everything before the first heading
        classification = content[:matches[0].start()].strip() if matches else content.strip()
        # Return as structured data (or join for frontend if needed)
        return Session2Response(classification=classification, therapy_plan=steps)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"OpenAI error: {e}\nTraceback: {tb}")

@app.post("/api/session2-therapy-chat", response_model=Session2ChatResponse)
async def session2_therapy_chat(data: Session2ChatRequest):
    # Compose context
    user_qa = "\n".join([f"Q: {q}\nA: {a}" for q, a in zip(data.session1Summary.get('questions', []), data.session1Summary.get('answers', []))])
    therapy_text = f"Insomnia Classification: {data.therapy.get('classification', '')}\nTherapy Plan: {data.therapy.get('therapy_plan', '')}"
    prompt = f"""
You are a compassionate insomnia therapist and expert in Cognitive Behavioral Therapy for Insomnia (CBT-I).

Below are the user's answers from their intake session:
{user_qa}

Here is the personalized CBT-I therapy plan for this user:
{therapy_text}

The user has a follow-up question about their therapy or insomnia:
Q: {data.question}

Please answer as a supportive CBT-I therapist, using the user's answers and therapy plan as context. Be specific, practical, and encouraging. If the question is not about therapy, still answer supportively as an insomnia expert.
"""
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )
        content = response.choices[0].message.content
        return Session2ChatResponse(response=content)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"OpenAI error: {e}\nTraceback: {tb}")

@app.post("/api/ocd-session2-therapy", response_model=OCDSession2Response)
async def ocd_session2_therapy(data: OCDSession2Request):
    # Compose OpenAI prompt for ERP (Exposure and Response Prevention) therapy
    user_qa = "\n".join([f"Q: {q}\nA: {a}" for q, a in zip(data.questions, data.answers)])
    prompt = f"""
You are a compassionate OCD therapist and expert in Exposure and Response Prevention (ERP) therapy.

Below are the user's answers from their intake session:
{user_qa}

Your response MUST follow this exact structure and formatting, with NO extra sentences before or after:

OCD Classification:
[State the user's OCD type and a brief explanation. This section must NOT be labeled as a step, and must be visually distinct.]

According to your OCD classification, follow the below ERP therapy steps:

Psychoeducation
[In clear, simple language, provide a detailed, step-by-step explanation (at least 5-6 sentences) tailored to the user's answers above. Reference their specific obsessions, compulsions, and struggles.]

Exposure Hierarchy
[Same as above: detailed, easy-to-understand, and tailored to the user's answers.]

Exposure Practice
[Same as above.]

Response Prevention
[Same as above.]

Cognitive Restructuring
[Same as above.]

Relapse Prevention
[Same as above.]

IMPORTANT:
- Each step must be separated by a blank line.
- The step heading and its explanation must be on separate lines.
- The step heading must be ONLY the exact, short heading from the list above (no 'Step 1:', 'Step 2:', etc.).
- Do NOT merge all step details into one paragraph.
- Do NOT add any extra sentences or summary before or after the steps. Only output the sections and steps as shown above.
- For each step, use the user's answers to make the advice as specific and relevant as possible.
- Each step’s explanation should be at least 5-6 sentences, easy to understand, and include practical examples.
- Do NOT use asterisks or Markdown for bolding anywhere in your response.
"""
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.7
        )
        content = response.choices[0].message.content
        step_headings = [
            "Psychoeducation",
            "Exposure Hierarchy",
            "Exposure Practice",
            "Response Prevention",
            "Cognitive Restructuring",
            "Relapse Prevention"
        ]
        import re
        step_pattern = r"(?:^|\n)({})\n".format("|".join(re.escape(h) for h in step_headings))
        matches = list(re.finditer(step_pattern, content))
        steps = []
        def clean_explanation(text):
            return text.replace('**', '').strip()
        for i, match in enumerate(matches):
            start = match.end()
            end = matches[i+1].start() if i+1 < len(matches) else len(content)
            heading = match.group(1)
            explanation = content[start:end].strip()
            explanation = clean_explanation(explanation)
            steps.append({"heading": heading, "explanation": explanation})
        classification = content[:matches[0].start()].strip() if matches else content.strip()
        return OCDSession2Response(classification=classification, therapy_plan=steps)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"OpenAI error: {e}\nTraceback: {tb}")

@app.post("/api/journal")
async def save_journal_entry(entry: dict, email: str = Depends(verify_token)):
    """Save journal entry"""
    # In a real app, you'd save to a database
    return {"message": "Journal entry saved successfully", "entry": entry}

@app.post("/session")
def save_session(data: SessionData, user=Depends(get_current_user)):
    print(f"Saving session for user_id={data.user_id}, session_number={data.session_number}")
    print(f"Session data: {data.data}")
    if not data.data or (isinstance(data.data, dict) and not data.data):
        raise HTTPException(status_code=400, detail="Session data is empty; not saving.")
    sessions_collection.update_one(
        {"user_id": data.user_id, "session_number": data.session_number},
        {"$set": {"data": data.data}},
        upsert=True
    )
    return {"msg": "Session data saved"}

@app.get("/session/{user_id}/{session_number}")
def get_session(user_id: str, session_number: int, user=Depends(get_current_user)):
    session = sessions_collection.find_one({"user_id": user_id, "session_number": session_number})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"data": session["data"]}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Hardcoded Google OAuth and session secrets for local development
GOOGLE_CLIENT_ID = "97285599774-63p6e3qn1vqkpovgu458vs7eim5oos1c.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
FRONTEND_URL = "http://localhost:3000"
SESSION_SECRET_KEY = "supersecretkey"

oauth = OAuth()
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

@app.get('/api/auth/google')
async def login_via_google(request: StarletteRequest):
    redirect_uri = request.url_for('auth_google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri, prompt='select_account')

@app.get('/api/auth/google/callback')
async def auth_google_callback(request: StarletteRequest):
    token = await oauth.google.authorize_access_token(request)
    user_info = await oauth.google.userinfo(token=token)
    email = user_info.get('email')
    name = user_info.get('name')
    if not email:
        return RedirectResponse(f"{FRONTEND_URL}/login?error=google_no_email")
    # Find or create user
    user = get_user(email)
    if not user:
        users_collection.insert_one({"email": email, "name": name, "password": None})
    # Issue JWT
    access_token = create_access_token(
        data={"sub": email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    # Redirect to frontend with token in query param
    return RedirectResponse(f"{FRONTEND_URL}/google-auth-success?token={access_token}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 