from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
import random
import asyncio

app = FastAPI()
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, app)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store chat history
chat_history = {}

# Sample responses
responses = [
    "I see. That's interesting.",
    "Could you elaborate on that?",
    "That's a great point!",
    "I'm not sure I understand. Can you explain further?",
    "That's fascinating. Tell me more!",
]

@sio.event
async def connect(sid, environ, auth):
    print(f"Client connected: {sid} with auth: {auth}")
    if not auth:
        auth_header = environ.get('HTTP_AUTHORIZATION')
        auth = {}
        if auth_header:
            import json
            auth = json.loads(auth_header)
    chat_id = auth.get('chatId', "default")
    if chat_id:
        await sio.save_session(sid, {'chat_id': chat_id})
        print(f"Client connected: {sid} with chat ID: {chat_id}")
    else:
        return False  # Reject the connection if no chatId is provided

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.event
async def message(sid, data):
    session = await sio.get_session(sid)
    chat_id = session.get('chat_id', None)
    
    if not chat_id or chat_id == "default":
        chat_id = data.get('chatId', "default")
        
    if chat_id not in chat_history:
        chat_history[chat_id] = []
    if type(data) is dict:
        message = data.get("message")
    else : 
        message = data
    chat_history[chat_id].append({"role": "user", "content": message})
    
    await sio.emit('message', {'role': 'assistant', 'content': "Last query was " + message + " for user : " + chat_id}, room=sid)
    await asyncio.sleep(1)
    # Simulate multiple intermediary responses
    for _ in range(random.randint(2, 5)):
        response = random.choice(responses)
        chat_history[chat_id].append({"role": "assistant", "content": response})
        await sio.emit('message', {'role': 'assistant', 'content': response}, room=sid)
        await asyncio.sleep(2)  # Simulate thinking time
    await sio.emit('message', {'role': 'assistant', 'content': "Answer complete. Let's move on! Your turn!"}, room=sid)
@app.get("/chat/{chat_id}")
async def get_chat_history(chat_id: str):
    return chat_history.get(chat_id, [])

app = socket_app