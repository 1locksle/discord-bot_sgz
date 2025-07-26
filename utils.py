import discord
from datetime import timedelta
from typing import Optional

def create_embed(title: str, description: str, color: int, fields: list = None, thumbnail: str = None, footer: str = None) -> discord.Embed:
    """Create a formatted embed"""
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=discord.utils.utcnow()
    )
    
    if fields:
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
    
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    
    if footer:
        embed.set_footer(text=footer)
    
    return embed

def format_time(duration: timedelta) -> str:
    """Format timedelta to human readable string"""
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def format_voice_time(minutes: int) -> str:
    """Format voice time in minutes to human readable string"""
    hours = minutes // 60
    mins = minutes % 60
    
    if hours > 0:
        return f"{hours}h {mins}m"
    else:
        return f"{mins}m"

def get_level_progress(xp: int, level: int) -> tuple:
    """Get XP progress for current level"""
    xp_for_current_level = (level - 1) * 200
    xp_for_next_level = level * 200
    current_level_xp = xp - xp_for_current_level
    xp_needed = xp_for_next_level - xp
    
    return current_level_xp, xp_needed

def create_progress_bar(current: int, total: int, length: int = 10) -> str:
    """Create a visual progress bar"""
    filled = int((current / total) * length)
    bar = "█" * filled + "░" * (length - filled)
    return f"[{bar}] {current}/{total}" 