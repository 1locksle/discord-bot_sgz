import discord
from discord.ext import commands, tasks
import random
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.currency_name = "coins"
        self.currency_symbol = "🪙"
        self.user_data = {}  # {user_id: {"balance": int, "last_daily": str, "inventory": []}}
        self.shop_items = {
            "role_color": {"name": "Custom Role Color", "price": 1000, "description": "Change your role color"},
            "xp_boost": {"name": "XP Boost (1 hour)", "price": 500, "description": "2x XP for 1 hour"},
            "lucky_charm": {"name": "Lucky Charm", "price": 200, "description": "Better gambling odds"},
            "vip_badge": {"name": "VIP Badge", "price": 5000, "description": "Special VIP status"},
            "mystery_box": {"name": "Mystery Box", "price": 100, "description": "Random rewards"}
        }
        self.load_economy_data()

    def load_economy_data(self):
        """Load economy data from file"""
        try:
            with open('economy_data.json', 'r') as f:
                self.user_data = json.load(f)
        except FileNotFoundError:
            self.user_data = {}

    def save_economy_data(self):
        """Save economy data to file"""
        with open('economy_data.json', 'w') as f:
            json.dump(self.user_data, f, indent=2)

    def get_user_data(self, user_id: int) -> dict:
        """Get or create user data"""
        if str(user_id) not in self.user_data:
            self.user_data[str(user_id)] = {
                "balance": 0,
                "last_daily": None,
                "inventory": [],
                "xp_boost_until": None,
                "work_count": 0,
                "gamble_count": 0,
                "last_usage_date": None
            }
        # Reset work/gamble counts if it's a new day
        today = datetime.utcnow().date().isoformat()
        if self.user_data[str(user_id)].get('last_usage_date') != today:
            self.user_data[str(user_id)]['work_count'] = 0
            self.user_data[str(user_id)]['gamble_count'] = 0
            self.user_data[str(user_id)]['last_usage_date'] = today
        return self.user_data[str(user_id)]

    @commands.command(name='balance')
    async def check_balance(self, ctx, member: Optional[discord.Member] = None):
        """Check your or someone else's balance"""
        if member is None:
            member = ctx.author
        
        user_data = self.get_user_data(member.id)
        
        embed = discord.Embed(
            title=f"{self.currency_symbol} Balance",
            description=f"**{member.name}**'s balance",
            color=0xffd700
        )
        
        embed.add_field(name="Balance", value=f"{self.currency_symbol} {user_data['balance']:,}", inline=True)
        
        # Show inventory count
        inventory_count = len(user_data.get('inventory', []))
        embed.add_field(name="Inventory Items", value=str(inventory_count), inline=True)
        
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        
        await ctx.send(embed=embed)

    @commands.command(name='daily')
    async def daily_reward(self, ctx):
        """Claim daily reward"""
        user_data = self.get_user_data(ctx.author.id)
        
        now = datetime.utcnow()
        last_daily = user_data.get('last_daily')
        
        if last_daily:
            last_daily = datetime.fromisoformat(last_daily)
            time_diff = now - last_daily
            
            if time_diff.total_seconds() < 86400:  # 24 hours
                remaining = timedelta(days=1) - time_diff
                hours, remainder = divmod(remaining.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                
                await ctx.send(f"❌ You can claim daily reward again in {hours}h {minutes}m!")
                return
        
        # Award daily reward
        reward = random.randint(50, 200)
        user_data['balance'] += reward
        user_data['last_daily'] = now.isoformat()
        self.save_economy_data()
        
        embed = discord.Embed(
            title="🎁 Daily Reward Claimed!",
            description=f"You received {self.currency_symbol} **{reward:,}**!",
            color=0x00ff00
        )
        embed.add_field(name="New Balance", value=f"{self.currency_symbol} {user_data['balance']:,}", inline=True)
        embed.set_footer(text="Come back tomorrow for more rewards!")
        
        await ctx.send(embed=embed)

    @commands.command(name='work')
    async def work(self, ctx):
        """Work to earn coins (5 times per day)"""
        user_data = self.get_user_data(ctx.author.id)
        if user_data['work_count'] >= 5:
            await ctx.send("❌ You have reached your daily work limit (5 times per day). Come back tomorrow!")
            return
        amount = random.randint(20, 100)
        user_data['balance'] += amount
        user_data['work_count'] += 1
        self.save_economy_data()
        embed = discord.Embed(
            title="💼 Work Complete!",
            description=f"You earned {self.currency_symbol} **{amount:,}**! ({user_data['work_count']}/5 today)",
            color=0x00ff00
        )
        embed.add_field(name="New Balance", value=f"{self.currency_symbol} {user_data['balance']:,}", inline=True)
        await ctx.send(embed=embed)

    @commands.command(name='gamble')
    async def gamble(self, ctx, amount: int):
        """Gamble coins (5 times per day)"""
        user_data = self.get_user_data(ctx.author.id)
        if user_data['gamble_count'] >= 5:
            await ctx.send("❌ You have reached your daily gamble limit (5 times per day). Come back tomorrow!")
            return
        if amount <= 0:
            await ctx.send("❌ Please enter a valid amount to gamble.")
            return
        if user_data['balance'] < amount:
            await ctx.send("❌ You don't have enough coins to gamble that amount.")
            return
        win = random.choice([True, False])
        if win:
            winnings = amount
            user_data['balance'] += winnings
            result = f"You won {self.currency_symbol} **{winnings:,}**!"
        else:
            user_data['balance'] -= amount
            result = f"You lost {self.currency_symbol} **{amount:,}**. Better luck next time!"
        user_data['gamble_count'] += 1
        self.save_economy_data()
        embed = discord.Embed(
            title="🎲 Gamble Result",
            description=f"{result} ({user_data['gamble_count']}/5 today)",
            color=0x00ff00 if win else 0xff0000
        )
        embed.add_field(name="New Balance", value=f"{self.currency_symbol} {user_data['balance']:,}", inline=True)
        await ctx.send(embed=embed)

    @commands.command(name='shop')
    async def show_shop(self, ctx):
        """Show the shop"""
        embed = discord.Embed(
            title=f"🛒 {self.currency_symbol} Shop",
            description="Buy items with your coins!",
            color=0x00ff00
        )
        
        for item_id, item in self.shop_items.items():
            embed.add_field(
                name=f"{item['name']} - {self.currency_symbol} {item['price']:,}",
                value=item['description'],
                inline=False
            )
        
        embed.add_field(
            name="How to buy",
            value="Use `!buy <item_name>` to purchase items",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command(name='buy')
    async def buy_item(self, ctx, *, item_name: str):
        """Buy an item from the shop"""
        user_data = self.get_user_data(ctx.author.id)
        
        # Find item
        item = None
        item_id = None
        for iid, shop_item in self.shop_items.items():
            if shop_item['name'].lower() == item_name.lower():
                item = shop_item
                item_id = iid
                break
        
        if not item:
            await ctx.send("❌ Item not found! Use `!shop` to see available items.")
            return
        
        if user_data['balance'] < item['price']:
            await ctx.send(f"❌ You don't have enough coins! You need {self.currency_symbol} {item['price']:,}")
            return
        
        # Purchase item
        user_data['balance'] -= item['price']
        
        if 'inventory' not in user_data:
            user_data['inventory'] = []
        
        user_data['inventory'].append(item_id)
        self.save_economy_data()
        
        embed = discord.Embed(
            title="🛒 Purchase Successful!",
            description=f"You bought **{item['name']}** for {self.currency_symbol} {item['price']:,}!",
            color=0x00ff00
        )
        embed.add_field(name="New Balance", value=f"{self.currency_symbol} {user_data['balance']:,}", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command(name='inventory')
    async def show_inventory(self, ctx, member: Optional[discord.Member] = None):
        """Show your or someone else's inventory"""
        if member is None:
            member = ctx.author
        
        user_data = self.get_user_data(member.id)
        inventory = user_data.get('inventory', [])
        
        if not inventory:
            embed = discord.Embed(
                title="📦 Inventory",
                description=f"**{member.name}**'s inventory is empty!",
                color=0x808080
            )
        else:
            embed = discord.Embed(
                title="📦 Inventory",
                description=f"**{member.name}**'s items:",
                color=0x00ff00
            )
            # --- Active Effects Section ---
            effects = []
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
            if effects:
                embed.add_field(name="Active Effects", value="\n".join(effects), inline=False)
            # --- Item List ---
            # Count items
            item_counts = {}
            for item_id in inventory:
                item_counts[item_id] = item_counts.get(item_id, 0) + 1
            for item_id, count in item_counts.items():
                if item_id in self.shop_items:
                    item_name = self.shop_items[item_id]['name']
                    embed.add_field(name=f"{item_name} x{count}", value="", inline=True)
        
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        
        await ctx.send(embed=embed)

    @commands.command(name='richest')
    async def economy_leaderboard(self, ctx):
        """Show economy leaderboard"""
        if not self.user_data:
            await ctx.send("No economy data yet!")
            return
        
        # Sort users by balance
        sorted_users = sorted(
            self.user_data.items(),
            key=lambda x: x[1].get('balance', 0),
            reverse=True
        )
        
        embed = discord.Embed(
            title=f"🏆 {self.currency_symbol} Leaderboard",
            color=0xffd700
        )
        
        for i, (user_id, user_data) in enumerate(sorted_users[:10]):
            user = self.bot.get_user(int(user_id))
            name = user.name if user else f"User {user_id}"
            balance = user_data.get('balance', 0)
            
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "🏅"
            embed.add_field(
                name=f"{medal} {i+1}. {name}",
                value=f"{self.currency_symbol} {balance:,}",
                inline=False
            )
        
        await ctx.send(embed=embed)

    @commands.command(name='transfer')
    async def transfer_coins(self, ctx, member: discord.Member, amount: int):
        """Transfer coins to another user"""
        if amount <= 0:
            await ctx.send("❌ Please transfer a positive amount!")
            return
        
        if member.bot:
            await ctx.send("❌ You can't transfer coins to bots!")
            return
        
        if member == ctx.author:
            await ctx.send("❌ You can't transfer coins to yourself!")
            return
        
        user_data = self.get_user_data(ctx.author.id)
        target_data = self.get_user_data(member.id)
        
        if user_data['balance'] < amount:
            await ctx.send("❌ You don't have enough coins!")
            return
        
        # Transfer coins
        user_data['balance'] -= amount
        target_data['balance'] += amount
        self.save_economy_data()
        
        embed = discord.Embed(
            title="💸 Transfer Complete!",
            description=f"You transferred {self.currency_symbol} **{amount:,}** to **{member.name}**!",
            color=0x00ff00
        )
        embed.add_field(name="Your Balance", value=f"{self.currency_symbol} {user_data['balance']:,}", inline=True)
        embed.add_field(name=f"{member.name}'s Balance", value=f"{self.currency_symbol} {target_data['balance']:,}", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command(name='economyreset')
    @commands.has_permissions(administrator=True)
    async def reset_economy(self, ctx):
        """Reset all economy data (Admin only)"""
        self.user_data = {}
        self.save_economy_data()
        await ctx.send("✅ All economy data has been reset!")

    @commands.command(name='use')
    async def use_item(self, ctx, *, item_name: str):
        """Use an item from your inventory"""
        user_data = self.get_user_data(ctx.author.id)
        inventory = user_data.get('inventory', [])
        item_id = None
        item = None
        for iid, shop_item in self.shop_items.items():
            if shop_item['name'].lower() == item_name.lower():
                item_id = iid
                item = shop_item
                break
        if not item_id or item_id not in inventory:
            await ctx.send(f"❌ You do not have '{item_name}' in your inventory.")
            return

        # Handle item effects
        if item_id == 'mystery_box':
            reward_type = random.choice(['coins', 'xp'])
            if reward_type == 'coins':
                amount = random.randint(100, 500)
                user_data['balance'] += amount
                reward_msg = f"You opened a Mystery Box and received 🪙 **{amount} coins**!"
            else:
                amount = random.randint(50, 200)
                if 'xp' not in user_data:
                    user_data['xp'] = 0
                user_data['xp'] += amount
                reward_msg = f"You opened a Mystery Box and received ⭐ **{amount} XP**!"
            inventory.remove(item_id)
            embed = discord.Embed(title="🎁 Mystery Box Opened!", description=reward_msg, color=0x00ff00)
        elif item_id == 'xp_boost':
            now = datetime.utcnow()
            user_data['xp_boost_until'] = (now + timedelta(hours=1)).isoformat()
            inventory.remove(item_id)
            embed = discord.Embed(title="⚡ XP Boost Activated!", description="You will earn double XP for 1 hour!", color=0x00ff00)
        elif item_id == 'lucky_charm':
            now = datetime.utcnow()
            user_data['lucky_charm_until'] = (now + timedelta(hours=1)).isoformat()
            inventory.remove(item_id)
            embed = discord.Embed(title="🍀 Lucky Charm Activated!", description="You have better gambling odds for 1 hour!", color=0x00ff00)
        elif item_id == 'vip_badge':
            if user_data.get('vip_badge', False):
                embed = discord.Embed(title="👑 VIP Badge", description="You already have the VIP Badge!", color=0xffd700)
            else:
                user_data['vip_badge'] = True
                embed = discord.Embed(title="👑 VIP Badge Activated!", description="You are now a VIP! Enjoy your special status.", color=0xffd700)
        elif item_id == 'role_color':
            embed = discord.Embed(title="🎨 Custom Role Color", description="Feature coming soon! Contact an admin to claim your color.", color=0x0099ff)
        else:
            embed = discord.Embed(title="❓ Unknown Item", description="This item cannot be used.", color=0xff0000)
        self.save_economy_data()
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Economy(bot)) 