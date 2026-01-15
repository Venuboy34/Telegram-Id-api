from flask import Flask, request, jsonify
from telethon.sync import TelegramClient
from telethon.tl.types import User, Channel, Chat
import os
import asyncio

app = Flask(__name__)

# Telegram API credentials
API_ID = '20288994'
API_HASH = 'd702614912f1ad370a0d18786002adbf'
PHONE = '+94703993277'

@app.route('/')
def home():
    return jsonify({
        "status": "active",
        "message": "Telegram Info Finder API",
        "endpoints": {
            "/api/find": "Find Telegram user/group/channel/bot info",
            "method": "GET",
            "params": "username or id"
        }
    })

@app.route('/api/find', methods=['GET'])
def find_telegram_entity():
    try:
        query = request.args.get('q')
        
        if not query:
            return jsonify({
                "error": "Missing 'q' parameter",
                "usage": "/api/find?q=username_or_id"
            }), 400
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(get_entity_info(query))
        loop.close()
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

async def get_entity_info(query):
    """Fetch entity information from Telegram"""
    
    if not API_ID or not API_HASH:
        return {"error": "API credentials not configured"}
    
    # Create session
    client = TelegramClient('session', API_ID, API_HASH)
    
    try:
        await client.connect()
        
        if not await client.is_user_authorized():
            return {"error": "Bot not authorized. Please authorize first."}
        
        # Get entity
        entity = await client.get_entity(query)
        
        # Extract information based on entity type
        info = {
            "id": entity.id,
            "access_hash": getattr(entity, 'access_hash', None)
        }
        
        if isinstance(entity, User):
            info.update({
                "type": "bot" if entity.bot else "user",
                "first_name": entity.first_name,
                "last_name": entity.last_name,
                "username": entity.username,
                "phone": entity.phone,
                "premium": getattr(entity, 'premium', False),
                "verified": entity.verified,
                "restricted": entity.restricted,
                "scam": entity.scam,
                "fake": getattr(entity, 'fake', False),
                "bot": entity.bot
            })
        
        elif isinstance(entity, Channel):
            info.update({
                "type": "channel" if entity.broadcast else "supergroup",
                "title": entity.title,
                "username": entity.username,
                "participants_count": getattr(entity, 'participants_count', None),
                "verified": entity.verified,
                "restricted": entity.restricted,
                "scam": entity.scam,
                "fake": getattr(entity, 'fake', False),
                "megagroup": entity.megagroup,
                "broadcast": entity.broadcast
            })
        
        elif isinstance(entity, Chat):
            info.update({
                "type": "group",
                "title": entity.title,
                "participants_count": getattr(entity, 'participants_count', None),
                "migrated_to": getattr(entity, 'migrated_to', None)
            })
        
        return {
            "success": True,
            "data": info
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
    
    finally:
        await client.disconnect()

# Vercel serverless handler
def handler(request):
    with app.request_context(request.environ):
        return app.full_dispatch_request()

if __name__ == '__main__':
    app.run(debug=True)
