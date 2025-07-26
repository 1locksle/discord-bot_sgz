import json
import asyncio
import aiofiles
from datetime import datetime, timedelta
from typing import Dict, Optional

class UserDatabase:
    def __init__(self):
        self.data = {}
        self.file_path = 'user_data.json'

    async def load_data(self):
        """Load user data from JSON file"""
        try:
            async with aiofiles.open(self.file_path, 'r') as f:
                content = await f.read()
                self.data = json.loads(content) if content else {}
        except FileNotFoundError:
            self.data = {}
        except json.JSONDecodeError:
            print("Error: Invalid JSON in user_data.json")
            self.data = {}

    async def save_data(self):
        """Save user data to JSON file"""
        try:
            async with aiofiles.open(self.file_path, 'w') as f:
                await f.write(json.dumps(self.data, indent=2))
        except Exception as e:
            print(f"Error saving data: {e}")

    async def get_user(self, user_id: str):
        """Get or create user data"""
        if user_id not in self.data:
            self.data[user_id] = {
                'xp': 0,
                'level': 1,
                'voice_time': 0,
                'total_voice_time': 0,
                'messages_sent': 0,
                'last_voice_join': None,
                'last_message_time': None
            }
        return self.data[user_id]

    async def update_user_xp(self, user_id: str, xp_gained: int):
        """Update user XP and check for level up"""
        user = await self.get_user(user_id)
        user['xp'] += xp_gained
        
        # Calculate new level (200 XP per level)
        new_level = (user['xp'] // 200) + 1
        leveled_up = new_level > user['level']
        user['level'] = new_level
        
        await self.save_data()
        return leveled_up, new_level

    async def update_voice_time(self, user_id: str, minutes: int):
        """Update user voice time"""
        user = await self.get_user(user_id)
        user['voice_time'] += minutes
        user['total_voice_time'] += minutes
        await self.save_data()

    async def set_voice_join_time(self, user_id: str):
        """Set voice join time for tracking"""
        user = await self.get_user(user_id)
        user["last_voice_join"] = datetime.utcnow().isoformat()
        await self.save_data()

    async def clear_voice_join_time(self, user_id: str) -> Optional[timedelta]:
        """Clear voice join time and return duration"""
        user = await self.get_user(user_id)
        if user["last_voice_join"]:
            join_time = datetime.fromisoformat(user["last_voice_join"])
            duration = datetime.utcnow() - join_time
            user["last_voice_join"] = None
            await self.save_data()
            return duration
        return None

    async def can_gain_message_xp(self, user_id: str, cooldown_seconds: int):
        """Check if user can gain XP from messages"""
        user = await self.get_user(user_id)
        last_time = user.get('last_message_time')
        
        if not last_time:
            return True
        
        try:
            last_time = datetime.fromisoformat(last_time)
            time_diff = datetime.utcnow() - last_time
            return time_diff.total_seconds() >= cooldown_seconds
        except:
            return True

    async def update_message_time(self, user_id: str):
        """Update last message time"""
        user = await self.get_user(user_id)
        user["last_message_time"] = datetime.utcnow().isoformat()
        await self.save_data()

    async def get_top_users(self, limit: int = 10):
        """Get top users by XP"""
        sorted_users = sorted(
            self.data.items(),
            key=lambda x: x[1]['xp'],
            reverse=True
        )
        return [{'user_id': user_id, **user_data} for user_id, user_data in sorted_users[:limit]] 