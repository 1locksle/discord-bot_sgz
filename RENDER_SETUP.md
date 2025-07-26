# 🚀 Render Deployment Guide

## 📋 Prerequisites
- Discord bot token
- Discord server and channel IDs
- GitHub account (free)

## 🎯 Step-by-Step Setup

### Step 1: Create GitHub Repository

1. **Go to GitHub.com** and sign in
2. **Create a new repository**:
   - Click "New repository"
   - Name it: `discord-bot`
   - Make it **Public** (free Render requires public repos)
   - Click "Create repository"

3. **Upload your bot files**:
   - Upload all your bot files to the repository
   - Make sure these files are included:
     - `bot.py`
     - `database.py`
     - `utils.py`
     - `requirements.txt`
     - `runtime.txt`
     - `Procfile`
     - `render.yaml`

### Step 2: Create Render Account

1. **Go to Render.com** and sign up
2. **Connect your GitHub account**
3. **Verify your email**

### Step 3: Deploy on Render

1. **Click "New +"** in Render dashboard
2. **Select "Web Service"**
3. **Connect your GitHub repository**:
   - Choose your `discord-bot` repository
   - Click "Connect"

4. **Configure the service**:
   - **Name**: `discord-bot` (or any name you want)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
   - **Plan**: `Free`

5. **Add Environment Variables**:
   - Click "Environment" tab
   - Add these variables:
     ```
     BOT_TOKEN = your_discord_bot_token_here
     GUILD_ID = your_server_id_here
     NOTIFICATION_CHANNEL_ID = your_notification_channel_id_here
     LOG_CHANNEL_ID = your_log_channel_id_here
     MODERATOR_ROLE_ID = your_moderator_role_id_here
     ```

6. **Deploy**:
   - Click "Create Web Service"
   - Wait for deployment (2-5 minutes)

### Step 4: Verify Deployment

1. **Check the logs** in Render dashboard
2. **Look for**: `🤖 [Bot Name] is now online!`
3. **Check your Discord server** - bot should be online

## 🔧 Troubleshooting

### Bot Not Starting
- Check the logs in Render dashboard
- Verify environment variables are correct
- Make sure bot token is valid

### Bot Not Responding
- Check if bot is online in Discord
- Verify bot has proper permissions
- Check channel IDs are correct

### Deployment Fails
- Check `requirements.txt` is correct
- Verify all files are uploaded to GitHub
- Check Python version in `runtime.txt`

## 📊 Monitoring

### View Logs
- Go to your service in Render dashboard
- Click "Logs" tab
- See real-time bot activity

### Check Status
- Green dot = Running
- Red dot = Error
- Yellow dot = Building

## 💰 Costs

- **Free tier**: 750 hours/month
- **Paid tier**: $7/month (unlimited)
- **Most Discord bots**: Free tier is sufficient

## 🎉 Success!

Your bot should now be running 24/7 on Render! 

### Test Commands
- `!help` - Show all commands
- `!level` - Check your level
- `!profile` - View your profile
- `!leaderboard` - See top players

## 🔄 Updates

To update your bot:
1. Push changes to GitHub
2. Render automatically redeploys
3. Bot updates in 2-5 minutes

## 📞 Support

If you need help:
- Check Render documentation
- Check the logs for errors
- Verify all environment variables 