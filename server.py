from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import os
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'
PORT = 3891

# Paths
USER_DATA_PATH = 'users.json'
CHAT_DATA_DIR = 'chats'

# Ensure directories and files exist
if not os.path.exists(CHAT_DATA_DIR):
    os.makedirs(CHAT_DATA_DIR)

if not os.path.exists(USER_DATA_PATH):
    with open(USER_DATA_PATH, 'w') as file:
        json.dump({}, file)

# Helper Functions
def load_users():
    with open(USER_DATA_PATH, 'r') as file:
        return json.load(file)

def save_users(users):
    with open(USER_DATA_PATH, 'w') as file:
        json.dump(users, file)

def load_chat_data(user1, user2):
    filename = f"{CHAT_DATA_DIR}/{user1}_{user2}.json" if user1 < user2 else f"{CHAT_DATA_DIR}/{user2}_{user1}.json"
    if not os.path.exists(filename):
        return []
    with open(filename, 'r') as file:
        return json.load(file)

def save_chat_data(user1, user2, messages):
    filename = f"{CHAT_DATA_DIR}/{user1}_{user2}.json" if user1 < user2 else f"{CHAT_DATA_DIR}/{user2}_{user1}.json"
    with open(filename, 'w') as file:
        json.dump(messages, file)

# Routes
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('home'))
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    users = load_users()

    if username in users and users[username] == password:
        session['username'] = username
        app.logger.info(f"User '{username}' logged in successfully.")
        return jsonify({'status': 'success', 'message': 'Login successful'})
    elif username in users:
        app.logger.warning(f"Login failed: Incorrect password for '{username}'.")
        return jsonify({'status': 'error', 'message': 'Incorrect password'})
    else:
        app.logger.warning(f"Login failed: User '{username}' does not exist.")
        return jsonify({'status': 'error', 'message': 'User not found. Please register.'})

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    users = load_users()

    if username in users:
        app.logger.warning(f"Registration failed: Username '{username}' already exists.")
        return jsonify({'status': 'error', 'message': 'Username already exists. Please log in.'})

    users[username] = password
    save_users(users)
    session['username'] = username
    app.logger.info(f"User '{username}' registered successfully.")
    return jsonify({'status': 'success', 'message': 'User registered successfully'})

@app.route('/logout', methods=['GET'])
def logout():
    username = session.pop('username', None)
    if username:
        app.logger.info(f"User '{username}' logged out successfully.")
    return redirect(url_for('index'))

@app.route('/home', methods=['GET'])
def home():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template('home.html')

@app.route('/get_chats', methods=['GET'])
def get_chats():
    username = session.get('username')
    if not username:
        return jsonify({'status': 'error', 'message': 'Not logged in'})

    chat_files = os.listdir(CHAT_DATA_DIR)
    chats = [
        chat.replace('.json', '').replace(f"{username}_", '').replace(f"_{username}", '')
        for chat in chat_files if username in chat
    ]
    app.logger.info(f"Chats retrieved successfully for user '{username}'.")
    return jsonify({'status': 'success', 'chats': chats})

@app.route('/get_messages/<chat_user>', methods=['GET'])
def get_messages(chat_user):
    username = session.get('username')
    if not username:
        return jsonify({'status': 'error', 'message': 'Not logged in'})

    messages = load_chat_data(username, chat_user)
    app.logger.info(f"Messages retrieved successfully between '{username}' and '{chat_user}'.")
    return jsonify({'status': 'success', 'messages': messages})

@app.route('/send_message', methods=['POST'])
def send_message():
    username = session.get('username')
    if not username:
        return jsonify({'status': 'error', 'message': 'Not logged in'})

    chat_user = request.json.get('chat_user')
    message = request.json.get('message')
    if not chat_user or not message:
        return jsonify({'status': 'error', 'message': 'Invalid data'})

    # Load existing messages
    messages = load_chat_data(username, chat_user)
    messages.append({'sender': username, 'message': message})

    # Save chat for both users
    save_chat_data(username, chat_user, messages)
    save_chat_data(chat_user, username, messages)
    app.logger.info(f"Message sent successfully from '{username}' to '{chat_user}'.")
    return jsonify({'status': 'success', 'message': 'Message sent successfully'})

if __name__ == '__main__':
    app.run(host='localhost', port=PORT)
