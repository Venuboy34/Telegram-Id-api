from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Telegram Bot Token (you'll need to create a bot via @BotFather)
BOT_TOKEN = "8535781652:AAFVr1uwapaB_Lok4THScbav7JHoTpgIjZk"
BASE_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'

@app.route('/')
def home():
    return jsonify({
        "status": "active",
        "name": "Telegram Info Finder API",
        "version": "2.0",
        "endpoints": {
            "/api/user": "Get user info by user_id",
            "/api/chat": "Get chat/channel/group info by chat_id or @username",
            "/api/check": "Check if user is premium"
        },
        "usage": {
            "user": "/api/user?id=123456789",
            "chat": "/api/chat?id=@username or -100123456789",
            "check": "/api/check?id=123456789"
        }
    })

@app.route('/api/user', methods=['GET'])
def get_user():
    """Get user information by user_id"""
    try:
        user_id = request.args.get('id')
        
        if not user_id:
            return jsonify({
                "error": "Missing 'id' parameter",
                "usage": "/api/user?id=123456789"
            }), 400
        
        # Use getChat method
        url = f'{BASE_URL}/getChat'
        response = requests.get(url, params={'chat_id': user_id})
        data = response.json()
        
        if not data.get('ok'):
            return jsonify({
                "success": False,
                "error": data.get('description', 'Unknown error')
            }), 400
        
        result = data['result']
        
        user_info = {
            "success": True,
            "type": result.get('type'),
            "id": result.get('id'),
            "first_name": result.get('first_name'),
            "last_name": result.get('last_name'),
            "username": result.get('username'),
            "bio": result.get('bio'),
            "has_private_forwards": result.get('has_private_forwards'),
            "has_restricted_voice_and_video_messages": result.get('has_restricted_voice_and_video_messages')
        }
        
        return jsonify(user_info)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['GET'])
def get_chat():
    """Get chat/channel/group information"""
    try:
        chat_id = request.args.get('id')
        
        if not chat_id:
            return jsonify({
                "error": "Missing 'id' parameter",
                "usage": "/api/chat?id=@username or -100123456789"
            }), 400
        
        url = f'{BASE_URL}/getChat'
        response = requests.get(url, params={'chat_id': chat_id})
        data = response.json()
        
        if not data.get('ok'):
            return jsonify({
                "success": False,
                "error": data.get('description', 'Unknown error')
            }), 400
        
        result = data['result']
        
        chat_info = {
            "success": True,
            "type": result.get('type'),
            "id": result.get('id'),
            "title": result.get('title'),
            "username": result.get('username'),
            "description": result.get('description'),
            "invite_link": result.get('invite_link'),
            "member_count": result.get('member_count') if result.get('type') != 'private' else None,
            "photo": result.get('photo')
        }
        
        return jsonify(chat_info)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/check', methods=['GET'])
def check_premium():
    """Check if a user has Telegram Premium"""
    try:
        user_id = request.args.get('id')
        
        if not user_id:
            return jsonify({
                "error": "Missing 'id' parameter",
                "usage": "/api/check?id=123456789"
            }), 400
        
        url = f'{BASE_URL}/getChat'
        response = requests.get(url, params={'chat_id': user_id})
        data = response.json()
        
        if not data.get('ok'):
            return jsonify({
                "success": False,
                "error": data.get('description', 'Unknown error')
            }), 400
        
        result = data['result']
        
        # Note: Premium status might not be available via Bot API
        premium_info = {
            "success": True,
            "user_id": result.get('id'),
            "username": result.get('username'),
            "first_name": result.get('first_name'),
            "premium": result.get('is_premium', False),
            "note": "Premium status detection is limited via Bot API"
        }
        
        return jsonify(premium_info)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/members', methods=['GET'])
def get_member_count():
    """Get chat member count"""
    try:
        chat_id = request.args.get('id')
        
        if not chat_id:
            return jsonify({
                "error": "Missing 'id' parameter",
                "usage": "/api/members?id=@username"
            }), 400
        
        url = f'{BASE_URL}/getChatMemberCount'
        response = requests.get(url, params={'chat_id': chat_id})
        data = response.json()
        
        if not data.get('ok'):
            return jsonify({
                "success": False,
                "error": data.get('description', 'Unknown error')
            }), 400
        
        return jsonify({
            "success": True,
            "chat_id": chat_id,
            "member_count": data['result']
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel handler
def handler(environ, start_response):
    return app(environ, start_response)
