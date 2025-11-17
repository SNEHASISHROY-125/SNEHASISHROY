from flask import Flask, request, jsonify
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import sqlite3
import uvicorn

app = Flask(__name__)

# In-memory storage for messages (you might want to use a database in production)
messages = []

@app.route('/api/messages', methods=['POST'])
def post_message():
	data = request.get_json()
	
	# Validate required fields
	required_fields = ['name', 'email', 'message']
	if not all(field in data for field in required_fields):
		return jsonify({'error': 'Missing required fields'}), 400
	
	# Create message object
	message = {
		'id': len(messages) + 1,
		'name': data['name'],
		'email': data['email'],
		'message': data['message'],
		'timestamp': datetime.now().isoformat()
	}
	
	# Store the message
	messages.append(message)
	
	return jsonify(message), 201

@app.route('/api/messages', methods=['GET'])
def get_messages():
	return jsonify(messages)

if __name__ == '__main__':
	app.run(debug=True)
	app = FastAPI()

	# Create SQLite database and table
	def init_db():
		conn = sqlite3.connect('messages.db')
		c = conn.cursor()
		c.execute('''CREATE TABLE IF NOT EXISTS messages
					 (id INTEGER PRIMARY KEY AUTOINCREMENT,
					  name TEXT NOT NULL,
					  email TEXT NOT NULL,
					  message TEXT NOT NULL,
					  timestamp TEXT NOT NULL)''')
		conn.commit()
		conn.close()

	class Message(BaseModel):
		name: str
		email: str
		message: str

	@app.on_event("startup")
	async def startup():
		init_db()

	@app.post("/api/messages", status_code=201)
	async def create_message(message: Message):
		conn = sqlite3.connect('messages.db')
		c = conn.cursor()
		c.execute("INSERT INTO messages (name, email, message, timestamp) VALUES (?, ?, ?, ?)",
				 (message.name, message.email, message.message, datetime.now().isoformat()))
		conn.commit()
		message_id = c.lastrowid
		conn.close()
		return {"id": message_id, **message.dict(), "timestamp": datetime.now().isoformat()}

	@app.get("/api/messages")
	async def read_messages():
		conn = sqlite3.connect('messages.db')
		c = conn.cursor()
		c.execute("SELECT * FROM messages")
		messages = [{"id": row[0], "name": row[1], "email": row[2], 
					 "message": row[3], "timestamp": row[4]} for row in c.fetchall()]
		conn.close()
		return messages

	if __name__ == "__main__":
		uvicorn.run(app, host="0.0.0.0", port=8000)