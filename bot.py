import discord
from discord.ext import commands, tasks
import json
import asyncio
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from database import UserDatabase
from utils import create_embed, format_time, format_voice_time, get_level_progress, create_progress_bar

# Import cogs
from games import Games
from trivia import Trivia
from giveaway import Giveaway
from utility import Utility
from economy import Economy

# Load environment variables
load_dotenv()

# Load configuration from environment variables or config file
def load_config():
    # Try to load from environment variables first (for Render)
    bot_token = os.getenv('BOT_TOKEN')
    guild_id = os.getenv('GUILD_ID')
    notification_channel_id = os.getenv('NOTIFICATION_CHANNEL_ID')
    log_channel_id = os.getenv('LOG_CHANNEL_ID')
    moderator_role_id = os.getenv('MODERATOR_ROLE_ID')
    
    if bot_token:
        # Use environment variables
        config = {
            'bot_token': bot_token,
            'guild_id': guild_id or 'YOUR_GUILD_ID_HERE',
            'notification_channel_id': notification_channel_id or 'YOUR_NOTIFICATION_CHANNEL_ID_HERE',
            'log_channel_id': log_channel_id or 'YOUR_LOG_CHANNEL_ID_HERE',
            'moderator_role_id': moderator_role_id or 'YOUR_MODERATOR_ROLE_ID_HERE',
            'xp_settings': {
                'voice_xp_per_minute': 3,
                'message_xp': 2,
                'xp_cooldown_seconds': 60,
                'level_multiplier': 200
            },
            'embed_colors': {
                'join': '0x00ff00',
                'leave': '0xff0000',
                'level_up': '0xffff00',
                'info': '0x0099ff'
            }
        }
    else:
        # Fall back to config file
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading config.json: {e}")
            # Default config
            config = {
                'bot_token': 'YOUR_BOT_TOKEN_HERE',
                'guild_id': 'YOUR_GUILD_ID_HERE',
                'notification_channel_id': 'YOUR_NOTIFICATION_CHANNEL_ID_HERE',
                'log_channel_id': 'YOUR_LOG_CHANNEL_ID_HERE',
                'moderator_role_id': 'YOUR_MODERATOR_ROLE_ID_HERE',
                'xp_settings': {
                    'voice_xp_per_minute': 3,
                    'message_xp': 2,
                    'xp_cooldown_seconds': 60,
                    'level_multiplier': 200
                },
                'embed_colors': {
                    'join': '0x00ff00',
                    'leave': '0xff0000',
                    'level_up': '0xffff00',
                    'info': '0x0099ff'
                }
            }
    
    return config

config = load_config()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Set bot start time for uptime tracking
bot.start_time = datetime.now()

# Initialize database
db = UserDatabase()

# Voice tracking - simplified
voice_users = {}  # {user_id: join_time}

def get_channel_safely(channel_id):
    """Safely get a channel by ID with error handling"""
    try:
        if not channel_id or channel_id == 'YOUR_NOTIFICATION_CHANNEL_ID_HERE' or channel_id == 'YOUR_LOG_CHANNEL_ID_HERE':
            return None
        return bot.get_channel(int(channel_id))
    except (ValueError, TypeError):
        return None

@bot.event
async def on_ready():
    """Bot startup event"""
    print(f'🤖 {bot.user} is now online!')
    print(f'📊 Connected to {len(bot.guilds)} guild(s)')
    
    # Load user data
    await db.load_data()
    
    # Load all cogs
    await load_cogs()
    
    # Start online time tracking task
    online_time_task.start()
    
    # Set bot status
    await bot.change_presence(activity=discord.Game(name="!help | Leveling System"))

@bot.event
async def on_member_join(member):
    """Handle member join events"""
    guild = member.guild
    
    # Get notification channel
    notification_channel = get_channel_safely(config['notification_channel_id'])
    if not notification_channel:
        return
    
    # Create join embed
    embed = create_embed(
        title="🎉 Welcome!",
        description=f"{member.mention} has joined the server!",
        color=int(config['embed_colors']['join'], 16),
        fields=[
            ("Member", f"{member.name}#{member.discriminator}", True),
            ("Account Created", member.created_at.strftime("%B %d, %Y"), True),
            ("Member Count", f"{guild.member_count}", True)
        ],
        thumbnail=member.display_avatar.url,
        footer=f"User ID: {member.id}"
    )
    
    # Add moderator mention if configured
    content = ""
    if config.get('moderator_role_id') and config['moderator_role_id'] != 'YOUR_MODERATOR_ROLE_ID_HERE':
        try:
            moderator_role = guild.get_role(int(config['moderator_role_id']))
            if moderator_role:
                content = f"{moderator_role.mention} - New member joined!"
        except (ValueError, TypeError):
            pass
    
    try:
        await notification_channel.send(content=content, embed=embed)
    except discord.HTTPException as e:
        print(f"Error sending join notification: {e}")
    
    # Log to log channel
    log_channel = get_channel_safely(config['log_channel_id'])
    if log_channel:
        try:
            log_embed = create_embed(
                title="📝 Member Joined",
                description=f"**User:** {member.name}#{member.discriminator} ({member.id})",
                color=int(config['embed_colors']['info'], 16),
                fields=[
                    ("Joined At", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), True),
                    ("Account Age", format_time(datetime.utcnow() - member.created_at), True)
                ]
            )
            await log_channel.send(embed=log_embed)
        except discord.HTTPException as e:
            print(f"Error sending join log: {e}")

@bot.event
async def on_member_remove(member):
    """Handle member leave events"""
    guild = member.guild
    
    # Get notification channel
    notification_channel = get_channel_safely(config['notification_channel_id'])
    if not notification_channel:
        return
    
    # Calculate membership duration
    membership_duration = datetime.utcnow() - member.joined_at if member.joined_at else None
    duration_text = format_time(membership_duration) if membership_duration else "Unknown"
    
    # Create leave embed
    embed = create_embed(
        title="👋 Goodbye!",
        description=f"{member.mention} has left the server.",
        color=int(config['embed_colors']['leave'], 16),
        fields=[
            ("Member", f"{member.name}#{member.discriminator}", True),
            ("Membership Duration", duration_text, True),
            ("Member Count", f"{guild.member_count}", True)
        ],
        thumbnail=member.display_avatar.url,
        footer=f"User ID: {member.id}"
    )
    
    # Add moderator mention if configured
    content = ""
    if config.get('moderator_role_id') and config['moderator_role_id'] != 'YOUR_MODERATOR_ROLE_ID_HERE':
        try:
            moderator_role = guild.get_role(int(config['moderator_role_id']))
            if moderator_role:
                content = f"{moderator_role.mention} - Member left the server!"
        except (ValueError, TypeError):
            pass
    
    try:
        await notification_channel.send(content=content, embed=embed)
    except discord.HTTPException as e:
        print(f"Error sending leave notification: {e}")
    
    # Log to log channel
    log_channel = get_channel_safely(config['log_channel_id'])
    if log_channel:
        try:
            log_embed = create_embed(
                title="📝 Member Left",
                description=f"**User:** {member.name}#{member.discriminator} ({member.id})",
                color=int(config['embed_colors']['info'], 16),
                fields=[
                    ("Left At", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), True),
                    ("Membership Duration", duration_text, True)
                ]
            )
            await log_channel.send(embed=log_embed)
        except discord.HTTPException as e:
            print(f"Error sending leave log: {e}")

@bot.event
async def on_voice_state_update(member, before, after):
    """Handle voice channel join/leave events"""
    # Voice channel join
    if before.channel is None and after.channel is not None:
        await handle_voice_join(member, after.channel)
    
    # Voice channel leave
    elif before.channel is not None and after.channel is None:
        await handle_voice_leave(member, before.channel)
    
    # Voice channel move (user moved from one channel to another)
    elif before.channel is not None and after.channel is not None and before.channel != after.channel:
        await handle_voice_move(member, before.channel, after.channel)

async def handle_voice_join(member, channel):
    """Handle voice channel join"""
    # Set join time for tracking
    voice_users[member.id] = datetime.utcnow()
    await db.set_voice_join_time(str(member.id))
    
    # Get notification channel
    notification_channel = get_channel_safely(config['notification_channel_id'])
    if not notification_channel:
        return
    
    # Create join embed
    embed = create_embed(
        title="🎤 Voice Channel Join",
        description=f"{member.mention} joined **{channel.name}**",
        color=int(config['embed_colors']['join'], 16),
        fields=[
            ("Channel", channel.name, True),
            ("User", member.name, True),
            ("Time", datetime.utcnow().strftime("%H:%M:%S"), True)
        ],
        thumbnail=member.display_avatar.url
    )
    
    try:
        await notification_channel.send(embed=embed)
    except discord.HTTPException as e:
        print(f"Error sending voice join notification: {e}")

async def handle_voice_leave(member, channel):
    """Handle voice channel leave"""
    # Calculate voice time and award XP
    if member.id in voice_users:
        join_time = voice_users.pop(member.id)
        duration = datetime.utcnow() - join_time
        duration_minutes = int(duration.total_seconds() / 60)
        
        if duration_minutes > 0:
            # Award voice XP
            xp_gained = duration_minutes * config['xp_settings']['voice_xp_per_minute']
            leveled_up, new_level = await db.update_user_xp(str(member.id), xp_gained)
            await db.update_voice_time(str(member.id), duration_minutes)
            
            # Get notification channel
            notification_channel = get_channel_safely(config['notification_channel_id'])
            if notification_channel:
                # Create leave embed
                embed = create_embed(
                    title="🎤 Voice Channel Leave",
                    description=f"{member.mention} left **{channel.name}**",
                    color=int(config['embed_colors']['leave'], 16),
                    fields=[
                        ("Channel", channel.name, True),
                        ("Duration", format_time(duration), True),
                        ("XP Gained", f"+{xp_gained} XP", True)
                    ],
                    thumbnail=member.display_avatar.url
                )
                
                try:
                    await notification_channel.send(embed=embed)
                except discord.HTTPException as e:
                    print(f"Error sending voice leave notification: {e}")
                
                # Level up notification
                if leveled_up:
                    user_data = await db.get_user(str(member.id))
                    level_embed = create_embed(
                        title="🎉 Level Up!",
                        description=f"{member.mention} reached level **{new_level}**!",
                        color=int(config['embed_colors']['level_up'], 16),
                        fields=[
                            ("New Level", f"Level {new_level}", True),
                            ("Total XP", f"{user_data['xp']} XP", True)
                        ],
                        thumbnail=member.display_avatar.url
                    )
                    try:
                        await notification_channel.send(embed=level_embed)
                    except discord.HTTPException as e:
                        print(f"Error sending level up notification: {e}")

async def handle_voice_move(member, from_channel, to_channel):
    """Handle voice channel move"""
    # Get notification channel
    notification_channel = get_channel_safely(config['notification_channel_id'])
    if not notification_channel:
        return

    # Create move embed
    embed = create_embed(
        title="🎤 Voice Channel Move",
        description=f"{member.mention} moved from **{from_channel.name}** to **{to_channel.name}**",
        color=int(config['embed_colors']['info'], 16),
        fields=[
            ("From", from_channel.name, True),
            ("To", to_channel.name, True),
            ("User", member.name, True)
        ],
        thumbnail=member.display_avatar.url
    )

    try:
        await notification_channel.send(embed=embed)
    except discord.HTTPException as e:
        print(f"Error sending voice move notification: {e}")

@bot.event
async def on_message(message):
    """Handle message events for XP system"""
    if message.author.bot:
        return
    
    # Check if user can gain XP from messages
    if await db.can_gain_message_xp(str(message.author.id), config['xp_settings']['xp_cooldown_seconds']):
        # Award message XP
        xp_gained = config['xp_settings']['message_xp']
        leveled_up, new_level = await db.update_user_xp(str(message.author.id), xp_gained)
        await db.update_message_time(str(message.author.id))
        
        # Level up notification
        if leveled_up:
            channel = message.channel
            user_data = await db.get_user(str(message.author.id))
            level_embed = create_embed(
                title="🎉 Level Up!",
                description=f"{message.author.mention} reached level **{new_level}**!",
                color=int(config['embed_colors']['level_up'], 16),
                fields=[
                    ("New Level", f"Level {new_level}", True),
                    ("Total XP", f"{user_data['xp']} XP", True)
                ],
                thumbnail=message.author.display_avatar.url
            )
            try:
                await channel.send(embed=level_embed)
            except discord.HTTPException as e:
                print(f"Error sending level up notification: {e}")
    
    await bot.process_commands(message)

@tasks.loop(minutes=1)
async def online_time_task():
    """Award XP to users in voice channels every minute"""
    for guild in bot.guilds:
        for member in guild.members:
            if member.voice and not member.voice.afk and not member.bot:
                # Award voice XP for being online
                xp_gained = config['xp_settings']['voice_xp_per_minute']
                leveled_up, new_level = await db.update_user_xp(str(member.id), xp_gained)
                await db.update_voice_time(str(member.id), 1)
                
                # Level up notification
                if leveled_up:
                    notification_channel = get_channel_safely(config['notification_channel_id'])
                    if notification_channel:
                        user_data = await db.get_user(str(member.id))
                        level_embed = create_embed(
                            title="🎉 Level Up!",
                            description=f"{member.mention} reached level **{new_level}**!",
                            color=int(config['embed_colors']['level_up'], 16),
                            fields=[
                                ("New Level", f"Level {new_level}", True),
                                ("Total XP", f"{user_data['xp']} XP", True)
                            ],
                            thumbnail=member.display_avatar.url
                        )
                        try:
                            await notification_channel.send(embed=level_embed)
                        except discord.HTTPException as e:
                            print(f"Error sending level up notification: {e}")

# Commands
@bot.command(name='help')
async def help_command(ctx):
    """Show all available commands"""
    embed = discord.Embed(
        title="🤖 Discord Bot Commands",
        description="Here are all the available commands:",
        color=int(config['embed_colors']['info'], 16)
    )
    
    # Core Commands
    embed.add_field(
        name="🎯 Core Commands (3)",
        value="`!level` - Check your level and XP\n`!top` - Show top users by XP\n`!help` - Show this help message",
        inline=False
    )
    
    # Admin Commands
    embed.add_field(
        name="⚙️ Admin Commands (5)",
        value="`!setlevel <user> <level>` - Set user level\n`!addxp <user> <amount>` - Add XP to user\n`!resetuser <user>` - Reset specific user data\n`!resetall` - Reset all users data\n`!voicetime <user>` - Check user voice time",
        inline=False
    )
    
    # Economy Commands
    embed.add_field(
        name="💰 Economy Commands (9)",
        value="`!balance` - Check your coin balance\n`!daily` - Claim daily reward (once per day)\n`!work` - Work to earn coins (5 times per day)\n`!gamble <amount>` - Gamble your coins (5 times per day)\n`!shop` - View available items\n`!buy <item>` - Purchase items\n`!inventory` - View your items\n`!transfer <user> <amount>` - Transfer coins\n`!richest` - Show richest users",
        inline=False
    )
    
    # Games Commands
    embed.add_field(
        name="🎮 Mini-Games (8)",
        value="`!roll [dice]` - Roll dice (e.g., !roll 2d20)\n`!flip` - Flip a coin\n`!8ball <question>` - Ask the magic 8-ball\n`!random <min> <max>` - Get random number\n`!pick <option1> <option2> ...` - Pick randomly\n`!joke` - Get a random joke\n`!fortune` - Get your fortune\n`!rps <choice>` - Rock, Paper, Scissors",
        inline=False
    )
    
    # Trivia Commands
    embed.add_field(
        name="🧠 Trivia System (3)",
        value="`!trivia` - Start a trivia game\n`!triviascores` - Show trivia leaderboard\n`!triviareset` - Reset your trivia score",
        inline=False
    )
    
    # Giveaway Commands
    embed.add_field(
        name="🎁 Giveaway System (3)",
        value="`!giveaway <time> <prize>` - Start giveaway\n`!giveawaylist` - List active giveaways\n`!giveawayreroll <message_id>` - Reroll winner",
        inline=False
    )
    
    # Utility Commands
    embed.add_field(
        name="🔧 Utility Commands (9)",
        value="`!serverinfo` - Server information\n`!userinfo [user]` - User information\n`!poll <question> | <option1> | <option2> ...` - Create poll\n`!pollresults <message_id>` - Show poll results\n`!avatar [user]` - Show user avatar\n`!ping` - Check bot latency\n`!uptime` - Show bot uptime\n`!invite` - Get bot invite link\n`!support` - Get support information",
        inline=False
    )
    
    embed.set_footer(text="Use !help <command> for detailed information about a specific command")
    await ctx.send(embed=embed)

@bot.command(name='level')
async def level_command(ctx, member: discord.Member = None):
    """Check user level"""
    if member is None:
        member = ctx.author
    
    user_data = await db.get_user(str(member.id))
    current_xp, xp_needed = get_level_progress(user_data['xp'], user_data['level'])
    progress_bar = create_progress_bar(current_xp, 100)
    
    embed = create_embed(
        title=f"📊 {member.name}'s Level",
        description=f"Level **{user_data['level']}**",
        color=int(config['embed_colors']['info'], 16),
        fields=[
            ("Total XP", f"{user_data['xp']} XP", True),
            ("Current Level XP", f"{current_xp}/100", True),
            ("XP to Next Level", f"{xp_needed} XP", True),
            ("Progress", progress_bar, False),
            ("Voice Time", format_voice_time(user_data['voice_time']), True),
            ("Messages Sent", f"{user_data['messages_sent']}", True)
        ],
        thumbnail=member.display_avatar.url
    )
    await ctx.send(embed=embed)

@bot.command(name='profile')
async def profile_command(ctx, member: discord.Member = None):
    """View detailed user profile"""
    if member is None:
        member = ctx.author
    
    user_data = await db.get_user(str(member.id))
    current_xp, xp_needed = get_level_progress(user_data['xp'], user_data['level'])
    progress_bar = create_progress_bar(current_xp, 100)

    # --- Active Effects Section ---
    effects = []
    from datetime import datetime
    now = datetime.utcnow()
    # XP Boost
    xp_boost_until = user_data.get('xp_boost_until')
    if xp_boost_until:
        try:
            boost_end = datetime.fromisoformat(xp_boost_until)
            if boost_end > now:
                remaining = boost_end - now
                mins, secs = divmod(remaining.seconds, 60)
                hours, mins = divmod(mins, 60)
                effects.append(f"⚡ **XP Boost**: {hours}h {mins}m left")
        except Exception:
            pass
    # Lucky Charm
    lucky_charm_until = user_data.get('lucky_charm_until')
    if lucky_charm_until:
        try:
            charm_end = datetime.fromisoformat(lucky_charm_until)
            if charm_end > now:
                remaining = charm_end - now
                mins, secs = divmod(remaining.seconds, 60)
                hours, mins = divmod(mins, 60)
                effects.append(f"🍀 **Lucky Charm**: {hours}h {mins}m left")
        except Exception:
            pass
    # VIP Badge
    if user_data.get('vip_badge', False):
        effects.append("👑 **VIP Badge**: Permanent")

    fields = []
    if effects:
        fields.append(("Active Effects", "\n".join(effects), False))
    fields.extend([
        ("📈 Level Progress", progress_bar, False),
        ("🎤 Voice Activity", format_voice_time(user_data['voice_time']), True),
        ("💬 Messages Sent", f"{user_data['messages_sent']}", True),
        ("⏱️ Total Voice Time", format_voice_time(user_data['total_voice_time']), True)
    ])
    
    embed = create_embed(
        title=f"👤 {member.name}'s Profile",
        description=f"**Level {user_data['level']}** • {user_data['xp']} Total XP",
        color=int(config['embed_colors']['info'], 16),
        fields=fields,
        thumbnail=member.display_avatar.url,
        footer=f"Member since {member.joined_at.strftime('%B %d, %Y') if member.joined_at else 'Unknown'}"
    )
    await ctx.send(embed=embed)

@bot.command(name='top')
async def leaderboard_command(ctx):
    """Show top players"""
    top_users = await db.get_top_users(10)
    
    if not top_users:
        await ctx.send("No users found!")
        return
    
    description = ""
    for i, user_data in enumerate(top_users, 1):
        member = ctx.guild.get_member(int(user_data['user_id']))
        name = member.name if member else f"User {user_data['user_id']}"
        description += f"**{i}.** {name} • Level {user_data['level']} • {user_data['xp']} XP\n"
    
    embed = create_embed(
        title="🏆 Leaderboard",
        description=description,
        color=int(config['embed_colors']['info'], 16),
        footer="Top 10 players by XP"
    )
    await ctx.send(embed=embed)

@bot.command(name='voicetime')
async def voicetime_command(ctx, member: discord.Member = None):
    """Check user voice time"""
    if member is None:
        member = ctx.author
    
    user_data = await db.get_user(str(member.id))
    
    embed = create_embed(
        title=f"🎤 {member.name}'s Voice Time",
        description=f"Voice activity statistics",
        color=int(config['embed_colors']['info'], 16),
        fields=[
            ("Current Session", format_voice_time(user_data['voice_time']), True),
            ("Total Voice Time", format_voice_time(user_data['total_voice_time']), True),
            ("Voice XP Earned", f"{user_data['voice_time'] * config['xp_settings']['voice_xp_per_minute']} XP", True)
        ],
        thumbnail=member.display_avatar.url
    )
    await ctx.send(embed=embed)

# Admin commands
@bot.command(name='setlevel')
@commands.has_permissions(administrator=True)
async def setlevel_command(ctx, member: discord.Member, level: int):
    """Set user level (Admin only)"""
    if level < 1:
        await ctx.send("Level must be at least 1!")
        return
    
    user_data = await db.get_user(str(member.id))
    new_xp = (level - 1) * 100
    user_data['level'] = level
    user_data['xp'] = new_xp
    await db.save_data()
    
    embed = create_embed(
        title="⚙️ Level Set",
        description=f"{member.mention}'s level has been set to **{level}**",
        color=int(config['embed_colors']['info'], 16),
        fields=[
            ("New Level", f"Level {level}", True),
            ("New XP", f"{new_xp} XP", True)
        ]
    )
    await ctx.send(embed=embed)

@bot.command(name='addxp')
@commands.has_permissions(administrator=True)
async def addxp_command(ctx, member: discord.Member, amount: int):
    """Add XP to a user (Admin only)"""
    if amount <= 0:
        await ctx.send("❌ Please enter a positive amount of XP.")
        return
    
    user_data = await db.get_user(str(member.id))
    old_level = user_data['level']
    
    leveled_up, new_level = await db.update_user_xp(str(member.id), amount)
    
    embed = create_embed(
        title="🎯 XP Added",
        description=f"Added **{amount}** XP to {member.mention}",
        color=int(config['embed_colors']['level_up'], 16),
        fields=[
            ("Old Level", str(old_level), True),
            ("New Level", str(new_level), True),
            ("Total XP", f"{user_data['xp'] + amount} XP", True)
        ]
    )
    
    await ctx.send(embed=embed)

@bot.command(name='resetall')
@commands.has_permissions(administrator=True)
async def reset_all_users_command(ctx):
    """Reset all user levels and XP (Admin only)"""
    # Confirmation embed
    embed = discord.Embed(
        title="⚠️ WARNING: Reset All Users",
        description="This will **permanently delete** all user levels, XP, voice time, and message data for **everyone** in the server.",
        color=0xff0000
    )
    embed.add_field(name="What will be reset:", value="• All XP and levels\n• Voice time tracking\n• Message counts\n• All user progress", inline=False)
    embed.add_field(name="This action is:", value="• **IRREVERSIBLE**\n• **PERMANENT**\n• **AFFECTS ALL USERS**", inline=False)
    embed.set_footer(text="Type '!confirmreset' to proceed or wait 30 seconds to cancel")
    
    await ctx.send(embed=embed)
    
    # Wait for confirmation
    try:
        await bot.wait_for(
            'message',
            timeout=30.0,
            check=lambda m: m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == '!confirmreset'
        )
    except asyncio.TimeoutError:
        await ctx.send("❌ Reset cancelled - no confirmation received within 30 seconds.")
        return
    
    # Proceed with reset
    try:
        # Clear all user data
        db.data = {}
        await db.save_data()
        
        success_embed = discord.Embed(
            title="✅ Reset Complete",
            description="All user levels, XP, and data have been **permanently reset**.",
            color=0x00ff00
        )
        success_embed.add_field(name="Users affected", value="All users in the server", inline=True)
        success_embed.add_field(name="Data cleared", value="XP, levels, voice time, messages", inline=True)
        success_embed.set_footer(text="All users will start fresh from level 1")
        
        await ctx.send(embed=success_embed)
        
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Reset Failed",
            description=f"An error occurred while resetting user data: {str(e)}",
            color=0xff0000
        )
        await ctx.send(embed=error_embed)

@bot.command(name='resetuser')
@commands.has_permissions(administrator=True)
async def reset_user_command(ctx, member: discord.Member):
    """Reset a specific user's levels and XP (Admin only)"""
    # Confirmation embed
    embed = discord.Embed(
        title="⚠️ WARNING: Reset User",
        description=f"This will **permanently delete** all levels, XP, voice time, and message data for {member.mention}.",
        color=0xff0000
    )
    embed.add_field(name="What will be reset:", value="• All XP and levels\n• Voice time tracking\n• Message counts\n• All user progress", inline=False)
    embed.add_field(name="This action is:", value="• **IRREVERSIBLE**\n• **PERMANENT**\n• **AFFECTS THIS USER ONLY**", inline=False)
    embed.set_footer(text="Type '!confirmresetuser' to proceed or wait 30 seconds to cancel")
    
    await ctx.send(embed=embed)
    
    # Wait for confirmation
    try:
        await bot.wait_for(
            'message',
            timeout=30.0,
            check=lambda m: m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == '!confirmresetuser'
        )
    except asyncio.TimeoutError:
        await ctx.send("❌ Reset cancelled - no confirmation received within 30 seconds.")
        return
    
    # Proceed with reset
    try:
        user_id = str(member.id)
        
        # Check if user exists in database
        if user_id in db.data:
            # Reset user data to default values
            db.data[user_id] = {
                'xp': 0,
                'level': 1,
                'voice_time': 0,
                'total_voice_time': 0,
                'messages_sent': 0,
                'last_voice_join': None,
                'last_message_time': None
            }
            await db.save_data()
            
            success_embed = discord.Embed(
                title="✅ User Reset Complete",
                description=f"{member.mention} has been reset to level 1 with 0 XP.",
                color=0x00ff00
            )
            success_embed.add_field(name="User", value=member.mention, inline=True)
            success_embed.add_field(name="New Level", value="1", inline=True)
            success_embed.add_field(name="New XP", value="0", inline=True)
            
            await ctx.send(embed=success_embed)
        else:
            await ctx.send(f"❌ {member.mention} has no data to reset.")
            
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Reset Failed",
            description=f"An error occurred while resetting user data: {str(e)}",
            color=0xff0000
        )
        await ctx.send(embed=error_embed)

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing required argument! Use `!help <command>` for usage.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Invalid argument! Please check your input.")
    else:
        await ctx.send(f"❌ An error occurred: {error}")

# Load all cogs
async def load_cogs():
    """Load all bot cogs"""
    try:
        await bot.add_cog(Games(bot))
        print("✅ Games cog loaded")
    except Exception as e:
        print(f"❌ Failed to load Games cog: {e}")
    
    try:
        await bot.add_cog(Trivia(bot))
        print("✅ Trivia cog loaded")
    except Exception as e:
        print(f"❌ Failed to load Trivia cog: {e}")
    
    try:
        await bot.add_cog(Giveaway(bot))
        print("✅ Giveaway cog loaded")
    except Exception as e:
        print(f"❌ Failed to load Giveaway cog: {e}")
    
    try:
        await bot.add_cog(Utility(bot))
        print("✅ Utility cog loaded")
    except Exception as e:
        print(f"❌ Failed to load Utility cog: {e}")
    
    try:
        await bot.add_cog(Economy(bot))
        print("✅ Economy cog loaded")
    except Exception as e:
        print(f"❌ Failed to load Economy cog: {e}")

# Run the bot
if __name__ == "__main__":
    bot.run(config['bot_token'])