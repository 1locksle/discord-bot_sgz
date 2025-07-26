import random
import discord
from discord.ext import commands
from typing import Optional

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.eight_ball_responses = [
            "It is certain.", "It is decidedly so.", "Without a doubt.",
            "Yes - definitely.", "You may rely on it.", "As I see it, yes.",
            "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.",
            "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
            "Cannot predict now.", "Concentrate and ask again.",
            "Don't count on it.", "My reply is no.", "My sources say no.",
            "Outlook not so good.", "Very doubtful."
        ]
        
        self.jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "What do you call a fake noodle? An impasta!",
            "Why did the math book look so sad? Because it had too many problems!",
            "What do you call a bear with no teeth? A gummy bear!",
            "Why don't skeletons fight each other? They don't have the guts!",
            "What do you call a fish wearing a bowtie? So-fish-ticated!",
            "Why did the golfer bring two pairs of pants? In case he got a hole in one!",
            "What do you call a can opener that doesn't work? A can't opener!"
        ]
        
        self.fortunes = [
            "A beautiful, smart, and loving person will be coming into your life.",
            "A dubious friend may be an enemy in camouflage.",
            "A faithful friend is a strong defense.",
            "A fresh start will put you on your way.",
            "A golden egg of opportunity falls into your lap this month.",
            "A lifetime friend shall soon be made.",
            "A light heart carries you through all the hard times.",
            "A new perspective will come with the new year.",
            "A pleasant surprise is waiting for you.",
            "Adventure can be real happiness."
        ]

    @commands.command(name='roll')
    async def roll_dice(self, ctx, dice: str = "1d6"):
        """Roll dice in NdN format (e.g., !roll 2d20)"""
        try:
            if 'd' not in dice.lower():
                # Single number roll
                sides = int(dice)
                result = random.randint(1, sides)
                embed = discord.Embed(
                    title="🎲 Dice Roll",
                    description=f"You rolled a **{result}** on a d{sides}!",
                    color=0x00ff00
                )
                embed.set_footer(text=f"Requested by {ctx.author.name}")
                await ctx.send(embed=embed)
                return

            # Parse NdN format
            parts = dice.lower().split('d')
            if len(parts) != 2:
                await ctx.send("❌ Invalid format! Use NdN (e.g., 2d20) or just a number (e.g., 20)")
                return

            num_dice = int(parts[0])
            sides = int(parts[1])

            if num_dice > 100:
                await ctx.send("❌ Too many dice! Maximum is 100.")
                return

            if sides > 1000:
                await ctx.send("❌ Too many sides! Maximum is 1000.")
                return

            # Roll the dice
            results = [random.randint(1, sides) for _ in range(num_dice)]
            total = sum(results)

            embed = discord.Embed(
                title="🎲 Dice Roll",
                description=f"You rolled **{num_dice}d{sides}**!",
                color=0x00ff00
            )
            
            if num_dice == 1:
                embed.add_field(name="Result", value=f"**{total}**", inline=True)
            else:
                embed.add_field(name="Individual Rolls", value=f"`{', '.join(map(str, results))}`", inline=False)
                embed.add_field(name="Total", value=f"**{total}**", inline=True)

            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await ctx.send(embed=embed)

        except ValueError:
            await ctx.send("❌ Invalid format! Use NdN (e.g., 2d20) or just a number (e.g., 20)")

    @commands.command(name='flip')
    async def coin_flip(self, ctx, flips: int = 1):
        """Flip a coin (or multiple coins)"""
        if flips > 10:
            await ctx.send("❌ Too many flips! Maximum is 10.")
            return

        results = []
        heads = 0
        tails = 0

        for _ in range(flips):
            result = random.choice(['Heads', 'Tails'])
            results.append(result)
            if result == 'Heads':
                heads += 1
            else:
                tails += 1

        embed = discord.Embed(
            title="🪙 Coin Flip",
            description=f"Flipped the coin **{flips}** time(s)!",
            color=0xffd700
        )

        if flips == 1:
            embed.add_field(name="Result", value=f"**{results[0]}**", inline=True)
        else:
            embed.add_field(name="Results", value=f"`{', '.join(results)}`", inline=False)
            embed.add_field(name="Heads", value=f"**{heads}**", inline=True)
            embed.add_field(name="Tails", value=f"**{tails}**", inline=True)

        embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)

    @commands.command(name='8ball')
    async def eight_ball(self, ctx, *, question: str):
        """Ask the magic 8-ball a question"""
        if not question.endswith('?'):
            await ctx.send("❌ Please ask a question ending with '?'")
            return

        response = random.choice(self.eight_ball_responses)
        
        embed = discord.Embed(
            title="🎱 Magic 8-Ball",
            color=0x000000
        )
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="Answer", value=f"**{response}**", inline=False)
        embed.set_footer(text=f"Asked by {ctx.author.name}")
        await ctx.send(embed=embed)

    @commands.command(name='random')
    async def random_number(self, ctx, min_num: int, max_num: int):
        """Generate a random number between min and max"""
        if min_num > max_num:
            min_num, max_num = max_num, min_num

        if max_num - min_num > 1000000:
            await ctx.send("❌ Range too large! Maximum difference is 1,000,000.")
            return

        result = random.randint(min_num, max_num)
        
        embed = discord.Embed(
            title="🎲 Random Number",
            description=f"Random number between **{min_num}** and **{max_num}**:",
            color=0x00ff00
        )
        embed.add_field(name="Result", value=f"**{result}**", inline=True)
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)

    @commands.command(name='pick')
    async def pick_random(self, ctx, *, options: str):
        """Pick a random option from a list"""
        if ',' not in options:
            await ctx.send("❌ Please provide multiple options separated by commas!")
            return

        choices = [choice.strip() for choice in options.split(',')]
        if len(choices) < 2:
            await ctx.send("❌ Please provide at least 2 options!")
            return

        if len(choices) > 20:
            await ctx.send("❌ Too many options! Maximum is 20.")
            return

        winner = random.choice(choices)
        
        embed = discord.Embed(
            title="🎯 Random Pick",
            description="I randomly picked from your options:",
            color=0x00ff00
        )
        embed.add_field(name="Options", value=f"`{', '.join(choices)}`", inline=False)
        embed.add_field(name="Winner", value=f"**{winner}**", inline=True)
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)

    @commands.command(name='joke')
    async def tell_joke(self, ctx):
        """Tell a random joke"""
        joke = random.choice(self.jokes)
        
        embed = discord.Embed(
            title="😄 Random Joke",
            description=joke,
            color=0xffd700
        )
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)

    @commands.command(name='fortune')
    async def fortune_cookie(self, ctx):
        """Get a fortune cookie message"""
        fortune = random.choice(self.fortunes)
        
        embed = discord.Embed(
            title="🥠 Fortune Cookie",
            description=f"*{fortune}*",
            color=0xff6b6b
        )
        embed.set_footer(text=f"Fortune for {ctx.author.name}")
        await ctx.send(embed=embed)

    @commands.command(name='rps')
    async def rock_paper_scissors(self, ctx, choice: str):
        """Play Rock, Paper, Scissors"""
        choice = choice.lower()
        if choice not in ['rock', 'paper', 'scissors', 'r', 'p', 's']:
            await ctx.send("❌ Please choose: rock, paper, or scissors (or r, p, s)")
            return

        # Convert shorthand to full words
        choice_map = {'r': 'rock', 'p': 'paper', 's': 'scissors'}
        player_choice = choice_map.get(choice, choice)
        
        bot_choice = random.choice(['rock', 'paper', 'scissors'])
        
        # Determine winner
        if player_choice == bot_choice:
            result = "It's a tie! 🤝"
            color = 0x808080
        elif (
            (player_choice == 'rock' and bot_choice == 'scissors') or
            (player_choice == 'paper' and bot_choice == 'rock') or
            (player_choice == 'scissors' and bot_choice == 'paper')
        ):
            result = "You win! 🎉"
            color = 0x00ff00
        else:
            result = "I win! 😄"
            color = 0xff0000

        # Emoji mapping
        emoji_map = {'rock': '🪨', 'paper': '📄', 'scissors': '✂️'}
        
        embed = discord.Embed(
            title="🪨📄✂️ Rock, Paper, Scissors",
            description=result,
            color=color
        )
        embed.add_field(name="Your Choice", value=f"{emoji_map[player_choice]} {player_choice.title()}", inline=True)
        embed.add_field(name="My Choice", value=f"{emoji_map[bot_choice]} {bot_choice.title()}", inline=True)
        embed.set_footer(text=f"Played by {ctx.author.name}")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Games(bot)) 