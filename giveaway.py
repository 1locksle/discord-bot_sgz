import discord
from discord.ext import commands, tasks
import random
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_giveaways = {}  # {message_id: giveaway_data}
        self.giveaway_checker.start()

    def cog_unload(self):
        self.giveaway_checker.cancel()

    @commands.command(name='giveaway')
    @commands.has_permissions(manage_messages=True)
    async def start_giveaway(self, ctx, time: str, *, prize: str):
        """Start a giveaway (e.g., !giveaway 1h Discord Nitro)"""
        # Parse time
        time_seconds = self.parse_time(time)
        if time_seconds is None:
            await ctx.send("❌ Invalid time format! Use: 30s, 5m, 2h, 1d")
            return

        if time_seconds < 30:
            await ctx.send("❌ Giveaway must be at least 30 seconds!")
            return

        if time_seconds > 604800:  # 7 days
            await ctx.send("❌ Giveaway cannot be longer than 7 days!")
            return

        # Create giveaway embed
        end_time = datetime.utcnow() + timedelta(seconds=time_seconds)
        
        embed = discord.Embed(
            title="🎉 GIVEAWAY 🎉",
            description=f"**{prize}**",
            color=0x00ff00
        )
        embed.add_field(name="React with 🎉 to enter!", value="", inline=False)
        embed.add_field(name="Ends at", value=end_time.strftime("%Y-%m-%d %H:%M:%S UTC"), inline=True)
        embed.add_field(name="Hosted by", value=ctx.author.mention, inline=True)
        embed.set_footer(text="Click the 🎉 reaction to enter!")

        message = await ctx.send(embed=embed)
        await message.add_reaction("🎉")

        # Store giveaway data
        self.active_giveaways[message.id] = {
            "channel_id": ctx.channel.id,
            "prize": prize,
            "end_time": end_time,
            "host_id": ctx.author.id,
            "message_id": message.id
        }

        await ctx.send(f"✅ Giveaway started! Ends in {self.format_time(time_seconds)}")

    def parse_time(self, time_str: str) -> Optional[int]:
        """Parse time string to seconds"""
        time_str = time_str.lower()
        
        if time_str.endswith('s'):
            return int(time_str[:-1])
        elif time_str.endswith('m'):
            return int(time_str[:-1]) * 60
        elif time_str.endswith('h'):
            return int(time_str[:-1]) * 3600
        elif time_str.endswith('d'):
            return int(time_str[:-1]) * 86400
        else:
            return None

    def format_time(self, seconds: int) -> str:
        """Format seconds to human readable string"""
        if seconds < 60:
            return f"{seconds} seconds"
        elif seconds < 3600:
            return f"{seconds // 60} minutes"
        elif seconds < 86400:
            return f"{seconds // 3600} hours"
        else:
            return f"{seconds // 86400} days"

    @tasks.loop(seconds=10)
    async def giveaway_checker(self):
        """Check for ended giveaways"""
        current_time = datetime.utcnow()
        ended_giveaways = []

        for message_id, giveaway_data in self.active_giveaways.items():
            if current_time >= giveaway_data["end_time"]:
                ended_giveaways.append((message_id, giveaway_data))

        for message_id, giveaway_data in ended_giveaways:
            await self.end_giveaway(message_id, giveaway_data)

    async def end_giveaway(self, message_id: int, giveaway_data: dict):
        """End a giveaway and select winner"""
        try:
            channel = self.bot.get_channel(giveaway_data["channel_id"])
            if not channel:
                return

            message = await channel.fetch_message(message_id)
            if not message:
                return

            # Get participants
            reaction = None
            for r in message.reactions:
                if r.emoji == "🎉":
                    reaction = r
                    break

            if not reaction:
                await channel.send(f"❌ No one entered the giveaway for **{giveaway_data['prize']}**!")
                del self.active_giveaways[message_id]
                return

            # Get users who reacted
            participants = []
            async for user in reaction.users():
                if not user.bot:
                    participants.append(user)

            if not participants:
                await channel.send(f"❌ No valid participants for **{giveaway_data['prize']}**!")
                del self.active_giveaways[message_id]
                return

            # Select winner
            winner = random.choice(participants)

            # Create winner embed
            embed = discord.Embed(
                title="🎉 GIVEAWAY ENDED 🎉",
                description=f"**{giveaway_data['prize']}**",
                color=0xffd700
            )
            embed.add_field(name="Winner", value=f"🎊 {winner.mention} 🎊", inline=False)
            embed.add_field(name="Participants", value=f"{len(participants)} people entered", inline=True)
            embed.add_field(name="Hosted by", value=f"<@{giveaway_data['host_id']}>", inline=True)
            embed.set_footer(text="Congratulations!")

            await channel.send(f"🎊 Congratulations {winner.mention}! You won **{giveaway_data['prize']}**!", embed=embed)

            # Update original message
            original_embed = message.embeds[0]
            original_embed.color = 0xff0000
            original_embed.add_field(name="🎊 WINNER", value=winner.mention, inline=False)
            await message.edit(embed=original_embed)

        except Exception as e:
            print(f"Error ending giveaway: {e}")
        finally:
            # Clean up
            if message_id in self.active_giveaways:
                del self.active_giveaways[message_id]

    @commands.command(name='giveawaylist')
    async def list_giveaways(self, ctx):
        """List active giveaways"""
        if not self.active_giveaways:
            await ctx.send("No active giveaways!")
            return

        embed = discord.Embed(
            title="🎉 Active Giveaways",
            color=0x00ff00
        )

        for message_id, giveaway_data in self.active_giveaways.items():
            time_left = giveaway_data["end_time"] - datetime.utcnow()
            if time_left.total_seconds() > 0:
                time_str = self.format_time(int(time_left.total_seconds()))
                embed.add_field(
                    name=giveaway_data["prize"],
                    value=f"Ends in: {time_str}\nHost: <@{giveaway_data['host_id']}>\n[Go to Giveaway](https://discord.com/channels/{ctx.guild.id}/{giveaway_data['channel_id']}/{message_id})",
                    inline=False
                )

        await ctx.send(embed=embed)

    @commands.command(name='giveawayreroll')
    @commands.has_permissions(manage_messages=True)
    async def reroll_giveaway(self, ctx, message_id: int):
        """Reroll a giveaway winner"""
        try:
            message = await ctx.channel.fetch_message(message_id)
            if not message:
                await ctx.send("❌ Message not found!")
                return

            # Get participants
            reaction = None
            for r in message.reactions:
                if r.emoji == "🎉":
                    reaction = r
                    break

            if not reaction:
                await ctx.send("❌ No giveaway reaction found!")
                return

            # Get users who reacted
            participants = []
            async for user in reaction.users():
                if not user.bot:
                    participants.append(user)

            if not participants:
                await ctx.send("❌ No participants found!")
                return

            # Select new winner
            winner = random.choice(participants)

            embed = discord.Embed(
                title="🎉 GIVEAWAY REROLL 🎉",
                description=f"New winner selected!",
                color=0xffd700
            )
            embed.add_field(name="Winner", value=f"🎊 {winner.mention} 🎊", inline=False)
            embed.add_field(name="Participants", value=f"{len(participants)} people entered", inline=True)
            embed.set_footer(text="Congratulations!")

            await ctx.send(f"🎊 New winner: {winner.mention}!", embed=embed)

        except Exception as e:
            await ctx.send(f"❌ Error: {e}")

    @giveaway_checker.before_loop
    async def before_giveaway_checker(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Giveaway(bot)) 