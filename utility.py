import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta
from typing import Optional

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_polls = {}  # {message_id: poll_data}

    @commands.command(name='serverinfo')
    async def server_info(self, ctx):
        """Display server information"""
        guild = ctx.guild
        
        # Get server statistics
        total_members = guild.member_count
        online_members = len([m for m in guild.members if m.status != discord.Status.offline])
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        roles = len(guild.roles)
        emojis = len(guild.emojis)
        
        # Get server boost level
        boost_level = guild.premium_tier
        boost_count = guild.premium_subscription_count
        
        embed = discord.Embed(
            title=f"📊 {guild.name} Server Information",
            color=0x00ff00
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.add_field(name="👑 Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="🆔 Server ID", value=guild.id, inline=True)
        embed.add_field(name="📅 Created", value=guild.created_at.strftime("%B %d, %Y"), inline=True)
        
        embed.add_field(name="👥 Members", value=f"Total: {total_members}\nOnline: {online_members}", inline=True)
        embed.add_field(name="📝 Channels", value=f"Text: {text_channels}\nVoice: {voice_channels}", inline=True)
        embed.add_field(name="🎭 Roles", value=str(roles), inline=True)
        
        embed.add_field(name="😀 Emojis", value=str(emojis), inline=True)
        embed.add_field(name="🚀 Boost Level", value=f"Level {boost_level} ({boost_count} boosts)", inline=True)
        embed.add_field(name="🔒 Verification", value=str(guild.verification_level).title(), inline=True)
        
        if guild.description:
            embed.add_field(name="📄 Description", value=guild.description, inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(name='userinfo')
    async def user_info(self, ctx, member: Optional[discord.Member] = None):
        """Display user information"""
        if member is None:
            member = ctx.author
        
        # Get user roles
        roles = [role.mention for role in member.roles if role.name != "@everyone"]
        roles.reverse()  # Show highest role first
        
        # Get user status
        status_emoji = {
            discord.Status.online: "🟢",
            discord.Status.idle: "🟡", 
            discord.Status.dnd: "🔴",
            discord.Status.offline: "⚫"
        }
        
        status = status_emoji.get(member.status, "⚫")
        
        embed = discord.Embed(
            title=f"👤 {member.name} Information",
            color=member.color if member.color != discord.Color.default() else 0x00ff00
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        
        embed.add_field(name="🆔 User ID", value=member.id, inline=True)
        embed.add_field(name="📅 Account Created", value=member.created_at.strftime("%B %d, %Y"), inline=True)
        embed.add_field(name="📥 Joined Server", value=member.joined_at.strftime("%B %d, %Y") if member.joined_at else "Unknown", inline=True)
        
        embed.add_field(name="🎭 Nickname", value=member.nick if member.nick else "None", inline=True)
        embed.add_field(name="📊 Status", value=f"{status} {str(member.status).title()}", inline=True)
        embed.add_field(name="🎮 Activity", value=str(member.activity.name) if member.activity else "None", inline=True)
        
        if roles:
            roles_text = " ".join(roles[:10])  # Show first 10 roles
            if len(roles) > 10:
                roles_text += f" and {len(roles) - 10} more..."
            embed.add_field(name="🎭 Roles", value=roles_text, inline=False)
        
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)

    @commands.command(name='poll')
    async def create_poll(self, ctx, question: str, *options):
        """Create a poll (e.g., !poll "What's your favorite color?" Red Blue Green)"""
        if len(options) < 2:
            await ctx.send("❌ Please provide at least 2 options!")
            return
        
        if len(options) > 10:
            await ctx.send("❌ Maximum 10 options allowed!")
            return
        
        # Emoji numbers
        emoji_numbers = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        
        embed = discord.Embed(
            title="📊 Poll",
            description=f"**{question}**",
            color=0x00ff00
        )
        
        options_text = ""
        for i, option in enumerate(options):
            options_text += f"{emoji_numbers[i]} {option}\n"
        
        embed.add_field(name="Options", value=options_text, inline=False)
        embed.set_footer(text=f"Poll by {ctx.author.name}")
        
        message = await ctx.send(embed=embed)
        
        # Add reactions
        for i in range(len(options)):
            await message.add_reaction(emoji_numbers[i])
        
        # Store poll data
        self.active_polls[message.id] = {
            "question": question,
            "options": options,
            "author_id": ctx.author.id
        }

    @commands.command(name='pollresults')
    async def poll_results(self, ctx, message_id: int):
        """Show results of a poll"""
        try:
            message = await ctx.channel.fetch_message(message_id)
            if not message:
                await ctx.send("❌ Message not found!")
                return
            
            if message.id not in self.active_polls:
                await ctx.send("❌ This is not a poll!")
                return
            
            poll_data = self.active_polls[message.id]
            emoji_numbers = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
            
            embed = discord.Embed(
                title="📊 Poll Results",
                description=f"**{poll_data['question']}**",
                color=0x00ff00
            )
            
            total_votes = 0
            results = []
            
            # Count votes for each option
            for i, option in enumerate(poll_data["options"]):
                votes = 0
                for reaction in message.reactions:
                    if reaction.emoji == emoji_numbers[i]:
                        votes = reaction.count - 1  # Subtract bot's vote
                        break
                
                total_votes += votes
                results.append((option, votes))
            
            # Sort by votes
            results.sort(key=lambda x: x[1], reverse=True)
            
            # Display results
            for i, (option, votes) in enumerate(results):
                percentage = (votes / total_votes * 100) if total_votes > 0 else 0
                bar_length = int(percentage / 10)  # 10% per bar
                bar = "█" * bar_length + "░" * (10 - bar_length)
                
                embed.add_field(
                    name=f"{i+1}. {option}",
                    value=f"{bar} {votes} votes ({percentage:.1f}%)",
                    inline=False
                )
            
            embed.add_field(name="Total Votes", value=str(total_votes), inline=True)
            embed.set_footer(text=f"Poll by {ctx.author.name}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error: {e}")

    @commands.command(name='avatar')
    async def show_avatar(self, ctx, member: Optional[discord.Member] = None):
        """Show user's avatar"""
        if member is None:
            member = ctx.author
        
        embed = discord.Embed(
            title=f"🖼️ {member.name}'s Avatar",
            color=member.color if member.color != discord.Color.default() else 0x00ff00
        )
        
        embed.set_image(url=member.display_avatar.url)
        embed.add_field(name="Avatar URL", value=f"[Click here]({member.display_avatar.url})", inline=True)
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        
        await ctx.send(embed=embed)

    @commands.command(name='ping')
    async def ping(self, ctx):
        """Show bot latency"""
        embed = discord.Embed(
            title="🏓 Pong!",
            color=0x00ff00
        )
        
        embed.add_field(name="Bot Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="Status", value="🟢 Online", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command(name='uptime')
    async def uptime(self, ctx):
        """Show bot uptime"""
        uptime = datetime.utcnow() - self.bot.start_time if hasattr(self.bot, 'start_time') else timedelta(0)
        
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
        
        embed = discord.Embed(
            title="⏰ Bot Uptime",
            description=f"**{uptime_str}**",
            color=0x00ff00
        )
        
        await ctx.send(embed=embed)

    @commands.command(name='invite')
    async def invite_link(self, ctx):
        """Get bot invite link"""
        embed = discord.Embed(
            title="🔗 Invite Link",
            description="Click the link below to invite me to your server!",
            color=0x00ff00
        )
        
        # Generate invite link
        invite_link = discord.utils.oauth_url(
            self.bot.user.id,
            permissions=discord.Permissions(
                send_messages=True,
                embed_links=True,
                read_message_history=True,
                view_channel=True,
                connect=True,
                speak=True,
                use_slash_commands=True
            )
        )
        
        embed.add_field(name="Invite Link", value=f"[Click here to invite]({invite_link})", inline=False)
        embed.set_footer(text="Thanks for using me!")
        
        await ctx.send(embed=embed)

    @commands.command(name='support')
    async def support_info(self, ctx):
        """Show support information"""
        embed = discord.Embed(
            title="🆘 Support Information",
            description="Need help with the bot? Here's how to get support:",
            color=0x00ff00
        )
        
        embed.add_field(
            name="📚 Commands",
            value="Use `!help` to see all available commands",
            inline=False
        )
        
        embed.add_field(
            name="🔧 Issues",
            value="Check the bot logs for error messages",
            inline=False
        )
        
        embed.add_field(
            name="📖 Documentation",
            value="Check the README.md file for setup instructions",
            inline=False
        )
        
        embed.add_field(
            name="🎮 Features",
            value="• Leveling system\n• Voice tracking\n• Mini-games\n• Trivia\n• Giveaways\n• Utility commands",
            inline=False
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot)) 