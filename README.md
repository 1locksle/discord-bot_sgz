# 🤖 Discord Bot - All-in-One Community Bot

A feature-rich Discord bot with leveling system, voice tracking, mini-games, trivia, giveaways, economy system, and utility commands!

> **⚠️ IMPORTANT**: This bot token has been reset for security. Please update your `config.json` with your own bot token and Discord server information.

## ✨ Features

### 🎯 Core Features

### **Member Tracking**
- **Join/Leave Notifications** - Rich embeds when users join or leave the server
- **Voice Channel Tracking** - Notifications for voice channel join, leave, and movement
- **Role Mentions** - Optional moderator role pings for events

### **XP & Leveling System**
- **Voice XP** - Earn 3 XP per minute in voice channels
- **Message XP** - Earn 2 XP per message (60-second cooldown)
- **Level Calculation** - 200 XP required per level (linear progression)
- **Progress Tracking** - Visual progress bars and detailed statistics

### 🎮 Mini-Games (8 Commands)
- **Dice Rolling** - Roll dice in NdN format (e.g., 2d20)
- **Coin Flip** - Flip coins
- **Magic 8-Ball** - Ask questions and get mystical answers
- **Rock, Paper, Scissors** - Play against the bot
- **Random Number Generator** - Generate random numbers
- **Random Picker** - Pick random options from a list
- **Jokes** - Tell random jokes
- **Fortune Cookies** - Get fortune cookie messages

### 🎯 Trivia System (3 Commands)
- **Interactive Trivia** - Multiple choice questions with reactions
- **Score Tracking** - Global and per-game scoring
- **Categories** - Science, Geography, History, Art, Literature, Math, Technology, Food
- **Leaderboards** - Track top trivia players

### 🎉 Giveaway System (3 Commands)
- **Automatic Giveaways** - Set time and prize, bot handles the rest
- **Reaction-based Entry** - Users react to enter
- **Automatic Winner Selection** - Random winner selection
- **Giveaway Management** - List active giveaways and reroll winners

### 💰 Economy System (11 Commands)

**Virtual currency system with daily limits and shop**

- `!balance` - Check your coin balance
- `!daily` - Claim daily reward (once per day)
- `!work` - Work to earn coins (5 times per day)
- `!gamble <amount>` - Gamble your coins (5 times per day)
- `!shop` - View available items
- `!buy <item>` - Purchase items from shop
- `!inventory` - View your purchased items
- `!transfer <user> <amount>` - Transfer coins to another user
- `!richest` - Show richest users leaderboard
- `!use <item>` - Use items from your inventory
- `!economyreset` - Reset economy data (Admin only)

### 🔧 Utility Commands (9 Commands)
- **Server Information** - Detailed server stats
- **User Information** - User profiles and stats
- **Polls** - Create interactive polls
- **Poll Results** - Show poll results
- **Avatar Display** - Show user avatars
- **Bot Status** - Ping and uptime
- **Invite Links** - Generate bot invite links
- **Support Information** - Help and documentation

## 🚀 Quick Setup

### Prerequisites
- **Python 3.12** (required for discord.py compatibility)
- **Discord Bot Token** (create at [Discord Developer Portal](https://discord.com/developers/applications))
- **Discord Server** with appropriate permissions

### Option 1: Local Setup
1. **Clone/Download** this repository
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure the bot:**
   - Edit `config.json` with your Discord IDs (see Configuration section below)
   - Or set environment variables (see below)
4. **Run the bot:**
   ```bash
   python bot.py
   ```

### Option 2: Render Hosting (Recommended for 24/7)
1. **Create GitHub repository** and upload all files
2. **Sign up for Render** (render.com)
3. **Create new Web Service**
4. **Connect your GitHub repository**
5. **Set environment variables** in Render dashboard:
   - `BOT_TOKEN` - Your Discord bot token
   - `GUILD_ID` - Your Discord server ID
   - `NOTIFICATION_CHANNEL_ID` - Channel for join/leave notifications
   - `LOG_CHANNEL_ID` - Channel for logging events
   - `MODERATOR_ROLE_ID` - Role to mention for events
6. **Deploy!** The bot will be online 24/7

### Option 3: Railway, Heroku, or Other Platforms
The bot is compatible with any platform that supports Python. Just set the environment variables and deploy!

## 📋 Configuration

### Environment Variables (for Render)
```env
BOT_TOKEN=your_discord_bot_token_here
GUILD_ID=your_guild_id_here
NOTIFICATION_CHANNEL_ID=your_notification_channel_id_here
LOG_CHANNEL_ID=your_log_channel_id_here
MODERATOR_ROLE_ID=your_moderator_role_id_here
```

### config.json (for local setup)
```json
{
    "bot_token": "YOUR_BOT_TOKEN_HERE",
    "guild_id": "YOUR_GUILD_ID_HERE",
    "notification_channel_id": "YOUR_NOTIFICATION_CHANNEL_ID_HERE",
    "log_channel_id": "YOUR_LOG_CHANNEL_ID_HERE",
    "moderator_role_id": "YOUR_MODERATOR_ROLE_ID_HERE",
    "xp_settings": {
        "voice_xp_per_minute": 3,
        "message_xp": 2,
        "xp_cooldown_seconds": 60,
        "level_multiplier": 200
    },
    "embed_colors": {
        "join": "0x00ff00",
        "leave": "0xff0000",
        "level_up": "0xffff00",
        "info": "0x0099ff"
    }
}
```

### How to Get Discord IDs
1. **Enable Developer Mode** in Discord (User Settings > Advanced > Developer Mode)
2. **Bot Token**: Create at [Discord Developer Portal](https://discord.com/developers/applications)
3. **Server ID**: Right-click server name → Copy Server ID
4. **Channel IDs**: Right-click channel → Copy Channel ID
5. **Role ID**: Right-click role → Copy Role ID

## 🎮 Commands

### 📊 Level Commands (5 Commands)
- `!level [user]` — Check user's level and XP
- `!profile [user]` — View detailed user profile
- `!top` — View top players by XP
- `!voicetime [user]` — Check user's voice time
- `!help` — Show all available commands

### 🎮 Game Commands (8 Commands)
- `!roll [dice]` — Roll dice (e.g., `!roll 2d20` or `!roll 20`)
- `!flip` — Flip a coin
- `!8ball <question>` — Ask the magic 8-ball a question
- `!rps <choice>` — Play Rock, Paper, Scissors
- `!random <min> <max>` — Generate random number
- `!pick <option1> <option2> ...` — Pick random option
- `!joke` — Tell a random joke
- `!fortune` — Get a fortune cookie message

### 🧠 Trivia Commands (3 Commands)
- `!trivia` — Start trivia game
- `!triviascores` — Show trivia leaderboard
- `!triviareset` — Reset your trivia score (Admin only)

### 🎁 Giveaway Commands (3 Commands)
- `!giveaway <time> <prize>` — Start a giveaway
  - Time format: `30s`, `5m`, `2h`, `1d`
  - Example: `!giveaway 1h Discord Nitro`
- `!giveawaylist` — List active giveaways
- `!giveawayreroll <message_id>` — Reroll giveaway winner (Admin only)

### 💰 Economy Commands (11 Commands)
- `!balance` — Check coin balance
- `!daily` — Claim daily reward (once per day)
- `!work` — Work to earn coins (5 times per day)
- `!gamble <amount>` — Gamble your coins (5 times per day)
- `!shop` — View available items
- `!buy <item>` — Buy item from shop
- `!inventory` — View inventory
- `!transfer <user> <amount>` — Transfer coins to user
- `!richest` — View richest players
- `!use <item>` — Use items from inventory
- `!economyreset` — Reset economy data (Admin only)

### 🔧 Utility Commands (9 Commands)
- `!serverinfo` — Display server information
- `!userinfo [user]` — Display user information
- `!poll <question> | <option1> | <option2> ...` — Create poll
- `!pollresults <message_id>` — Show poll results
- `!avatar [user]` — Show user's avatar
- `!ping` — Check bot latency
- `!uptime` — Show bot uptime
- `!invite` — Get bot invite link
- `!support` — Show support information

### ⚙️ Admin Commands (5 Commands)
- `!setlevel <user> <level>` — Set user's level
- `!addxp <user> <amount>` — Add XP to user
- `!resetuser <user>` — Reset specific user data
- `!resetall` — Reset all users data
- `!voicetime <user>` — Check user voice time

## 🛠️ Files Structure

```
discord-bot_sgz/
├── bot.py              # Main bot file with voice tracking and leveling
├── database.py         # User data management and persistence
├── utils.py            # Utility functions and helpers
├── games.py            # Mini-games cog (8 games)
├── trivia.py           # Trivia system cog with scoring
├── giveaway.py         # Giveaway system cog with automation
├── utility.py          # Utility commands cog (server info, polls, etc.)
├── economy.py          # Economy system cog with shop and currency
├── config.json         # Configuration file (update with your IDs!)
├── requirements.txt    # Python dependencies
├── runtime.txt         # Python version for deployment
├── Procfile           # Process file for deployment platforms
├── render.yaml        # Render deployment configuration
├── RENDER_SETUP.md    # Detailed Render setup guide
├── verify_setup.py    # Pre-deployment verification script
├── .gitignore         # Git ignore file for security
└── README.md          # This documentation file
```

## 🎯 XP System

### How XP Works
- **Voice XP**: 3 XP per minute in voice channels
- **Message XP**: 2 XP per message (60-second cooldown)
- **Level Calculation**: Level = (Total XP / 200) + 1
- **Progress**: Shows progress bar to next level

### Level Rewards
- **Level Up Notifications**: Automatic notifications when users level up
- **Progress Tracking**: Visual progress bars
- **Leaderboards**: Compare with other users

## 🎤 Voice Tracking

### Voice Events Tracked
- **Join**: User joins a voice channel (green embed)
- **Leave**: User leaves a voice channel (red embed)
- **Move**: User moves between voice channels (blue embed)

### Voice XP System
- **Real-time tracking** of voice channel time
- **Automatic XP awards** for time spent in voice
- **Session tracking** for current voice time
- **Total voice time** statistics

## 💰 Economy System

### Currency
- **Coins**: Virtual currency earned through various activities
- **Daily Rewards**: 50-200 coins per day
- **Work**: 20-100 coins per work session
- **Gambling**: Risk/reward system with multipliers

### Shop Items & Usage
- **Custom Role Color**: 1,000 coins — Change your role color (feature coming soon)
- **XP Boost (1 hour)**: 500 coins — 2x XP for 1 hour (use with `!use XP Boost (1 hour)`)
- **Lucky Charm**: 200 coins — Better gambling odds for 1 hour (use with `!use Lucky Charm`)
- **VIP Badge**: 5,000 coins — Special VIP status (permanent, use with `!use VIP Badge`)
- **Mystery Box**: 100 coins — Random rewards (use with `!use Mystery Box`)

### How to Use Items
- Purchase items with `!buy <item>`
- Use items from your inventory with `!use <item>`
- Temporary effects (XP Boost, Lucky Charm) show remaining time in `!inventory` and `!profile`
- Permanent effects (VIP Badge) are also displayed
- Mystery Box gives a random reward when used

### Viewing Active Effects
- Use `!inventory` or `!profile` to see your active boosts and badges at the top of the embed

## 🎮 Mini-Games

### Dice Rolling
- **Format**: `!roll 2d20` (2 dice, 20 sides each)
- **Single Roll**: `!roll 20` (1 die, 20 sides)
- **Limits**: Max 100 dice, max 1000 sides

### Trivia System
- **Categories**: Science, Geography, History, Art, Literature, Math, Technology, Food
- **Scoring**: 10 points per correct answer
- **Time Limit**: 30 seconds per question
- **Global Scores**: Persistent across games

### Giveaways
- **Time Formats**: seconds (s), minutes (m), hours (h), days (d)
- **Automatic**: Bot handles timing and winner selection
- **Reactions**: Users react with 🎉 to enter
- **Management**: List active giveaways and reroll winners

## 🔧 Technical Details

### Requirements
- Python 3.12 (required for discord.py compatibility)
- discord.py 2.3.2
- python-dotenv 1.0.0
- aiofiles 23.2.1

### Permissions Required
- Send Messages
- Embed Links
- Read Message History
- View Channels
- Connect (for voice tracking)
- Speak (for voice features)
- Use Slash Commands

### Data Storage
- **user_data.json**: User XP, levels, voice time
- **economy_data.json**: User balances, inventory, daily rewards
- **Trivia scores**: In-memory (resets on restart)

## 🚀 Deployment

### Render Setup
1. Follow the detailed guide in `RENDER_SETUP.md`
2. Set environment variables in Render dashboard
3. Deploy and enjoy 24/7 uptime!

### Local Development
1. Install Python 3.12
2. Install dependencies: `pip install -r requirements.txt`
3. Configure `config.json`
4. Run: `python bot.py`

## 🐛 Troubleshooting

### Common Issues
1. **Python 3.13 Error**: Downgrade to Python 3.12 (audioop module removed)
2. **Permission Errors**: Check bot permissions in Discord
3. **Channel ID Errors**: Verify channel IDs in config
4. **Import Errors**: Ensure all files are in the same directory
5. **Bot Token Issues**: Make sure your bot token is valid and not expired
6. **Missing Permissions**: Ensure the bot has all required permissions in your server

### Verification
Run `python verify_setup.py` to check your setup before deployment.

### Bot Permissions Required
- ✅ Send Messages
- ✅ Embed Links
- ✅ Read Message History
- ✅ View Channels
- ✅ Connect (for voice tracking)
- ✅ Speak (for voice features)
- ✅ Use Slash Commands
- ✅ Add Reactions (for trivia and giveaways)

## 📞 Support

- **Commands**: Use `!help` in Discord
- **Support Info**: Use `!support` in Discord
- **Documentation**: Check this README and `RENDER_SETUP.md`
- **Issues**: Check bot logs for error messages
- **GitHub**: Report issues or contribute to the project

## 🔒 Security Notes

- **Never commit your bot token** to version control
- **Use environment variables** for production deployments
- **Keep your config.json private** and add it to .gitignore
- **Regularly rotate your bot token** for security

## 🎉 Features Summary

This bot includes **43 commands** across **6 major systems**:

1. **Leveling System** - XP, levels, voice tracking
2. **Mini-Games** - 8 different games and activities
3. **Trivia System** - Interactive quiz games
4. **Giveaway System** - Automatic giveaways
5. **Economy System** - Virtual currency and shop
6. **Utility Commands** - Server info, polls, avatars

## 🔄 Recent Updates

### Security Improvements
- ✅ **Bot token security**: Removed exposed tokens from config
- ✅ **Added .gitignore**: Prevents sensitive data from being committed
- ✅ **Environment variable support**: Better for production deployments

### Documentation Updates
- ✅ **Enhanced README**: Better organization and clearer instructions
- ✅ **Setup guides**: More detailed configuration instructions
- ✅ **Troubleshooting**: Added common issues and solutions
- ✅ **Security notes**: Added important security guidelines

### Voice Tracking Features
- ✅ **Join notifications**
- ✅ **Leave notifications** 
- ✅ **Movement notifications**
- ✅ **XP tracking** for all voice time
- ✅ **Level up notifications**

Perfect for any Discord community looking for engagement, fun, and utility features!

---

# 📖 User Guide: All User Commands

Below is a categorized list of all commands available to regular users. Use these commands in your Discord server to interact with the bot's features!

## 📊 Level & Profile Commands
- `!level [user]` — Check your or another user's level and XP.
- `!profile [user]` — View a detailed profile for yourself or another user.
- `!top` — See the top players by XP.
- `!voicetime [user]` — Check your or another user's voice time.
- `!help` — Show all available commands and categories.

## 🎮 Mini-Games
- `!roll [dice]` — Roll dice (e.g., `!roll 2d20` or `!roll 20`).
- `!flip` — Flip a coin.
- `!8ball <question>` — Ask the magic 8-ball a question.
- `!rps <choice>` — Play Rock, Paper, Scissors against the bot.
- `!random <min> <max>` — Generate a random number in a range.
- `!pick <option1> <option2> ...` — Pick a random option from your list.
- `!joke` — Get a random joke.
- `!fortune` — Receive a fortune cookie message.

## 🧠 Trivia
- `!trivia` — Start a trivia game in your channel.
- `!triviascores` — View the global trivia leaderboard.

## 🎁 Giveaways
- `!giveaway <time> <prize>` — Start a giveaway (if you have permission).
- `!giveawaylist` — List all active giveaways.
- `!giveawayreroll <message_id>` — Reroll a giveaway winner (if you have permission).

## 💰 Economy
- `!balance` — Check your coin balance.
- `!daily` — Claim your daily reward (once per day).
- `!work` — Work to earn coins (up to 5 times per day).
- `!gamble <amount>` — Gamble your coins (up to 5 times per day).
- `!shop` — View items available for purchase.
- `!buy <item>` — Buy an item from the shop.
- `!inventory` — View your inventory of purchased items and see active effects.
- `!use <item>` — Use an item from your inventory (activates boosts, opens Mystery Box, etc.).
- `!transfer <user> <amount>` — Transfer coins to another user.
- `!richest` — See the richest users on the server.
- `!economyreset` — Reset economy data (Admin only).

## 🔧 Utility
- `!serverinfo` — Display information about the server.
- `!userinfo [user]` — Show information about yourself or another user.
- `!poll <question> | <option1> | <option2> ...` — Create a poll for users to vote on.
- `!pollresults <message_id>` — Show the results of a poll.
- `!avatar [user]` — Show your or another user's avatar.
- `!ping` — Check the bot's latency.
- `!uptime` — See how long the bot has been online.
- `!invite` — Get a link to invite the bot to another server.
- `!support` — Show support and help information.

**Note:** Some commands (like starting giveaways) may require special permissions in your server. If you get a permissions error, contact a server admin.

---

**Happy Botting! 🤖✨** 