from time import time
from fastapi import logger
from app.route.websocket_router import last_ping
from app.utils.active_connections import active_connections
import asyncio


async def disconnect_inactive_users():
    while True:
        now = time()
        for user_id in list(active_connections.keys()):
            for session_id, ws in list(active_connections[user_id].items()):
                last_time = last_ping.get(session_id, now)
                if now - last_time > 60: 
                    await ws.close()
                    del active_connections[user_id][session_id]
                    del last_ping[session_id]
                    logger.info(f"Disconnect user {user_id} session {session_id} due to inactivity")
        await asyncio.sleep(30)