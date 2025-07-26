import discord
from discord.ext import commands
import random
import asyncio
import json
from typing import Dict, List, Optional

class Trivia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}  # {channel_id: game_data}
        self.scores = {}  # {user_id: score}
        self.questions = [
            {
                "question": "What is the capital of France?",
                "options": ["London", "Berlin", "Paris", "Madrid"],
                "correct": 2,
                "category": "Geography"
            },
            {
                "question": "Which planet is known as the Red Planet?",
                "options": ["Venus", "Mars", "Jupiter", "Saturn"],
                "correct": 1,
                "category": "Science"
            },
            {
                "question": "What is the largest mammal in the world?",
                "options": ["African Elephant", "Blue Whale", "Giraffe", "Hippopotamus"],
                "correct": 1,
                "category": "Science"
            },
            {
                "question": "Who painted the Mona Lisa?",
                "options": ["Vincent van Gogh", "Pablo Picasso", "Leonardo da Vinci", "Michelangelo"],
                "correct": 2,
                "category": "Art"
            },
            {
                "question": "What is the chemical symbol for gold?",
                "options": ["Ag", "Au", "Fe", "Cu"],
                "correct": 1,
                "category": "Science"
            },
            {
                "question": "Which year did World War II end?",
                "options": ["1943", "1944", "1945", "1946"],
                "correct": 2,
                "category": "History"
            },
            {
                "question": "What is the main ingredient in guacamole?",
                "options": ["Tomato", "Avocado", "Onion", "Lime"],
                "correct": 1,
                "category": "Food"
            },
            {
                "question": "Which programming language was created by Guido van Rossum?",
                "options": ["Java", "Python", "C++", "JavaScript"],
                "correct": 1,
                "category": "Technology"
            },
            {
                "question": "What is the largest ocean on Earth?",
                "options": ["Atlantic", "Indian", "Arctic", "Pacific"],
                "correct": 3,
                "category": "Geography"
            },
            {
                "question": "Who wrote 'Romeo and Juliet'?",
                "options": ["Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain"],
                "correct": 1,
                "category": "Literature"
            },
            {
                "question": "What is the smallest prime number?",
                "options": ["0", "1", "2", "3"],
                "correct": 2,
                "category": "Math"
            },
            {
                "question": "Which country is home to the kangaroo?",
                "options": ["New Zealand", "South Africa", "Australia", "India"],
                "correct": 2,
                "category": "Geography"
            },
            {
                "question": "What is the speed of light?",
                "options": ["299,792 km/s", "199,792 km/s", "399,792 km/s", "499,792 km/s"],
                "correct": 0,
                "category": "Science"
            },
            {
                "question": "Which element has the chemical symbol 'O'?",
                "options": ["Osmium", "Oxygen", "Oganesson", "Osmium"],
                "correct": 1,
                "category": "Science"
            },
            {
                "question": "What is the largest desert in the world?",
                "options": ["Sahara", "Antarctic", "Arabian", "Gobi"],
                "correct": 1,
                "category": "Geography"
            }
        ]

    @commands.command(name='trivia')
    async def start_trivia(self, ctx, rounds: int = 5):
        """Start a trivia game"""
        if ctx.channel.id in self.active_games:
            await ctx.send("❌ A trivia game is already in progress in this channel!")
            return

        if rounds < 1 or rounds > 20:
            await ctx.send("❌ Please choose between 1-20 rounds!")
            return

        # Initialize game
        game_data = {
            "rounds": rounds,
            "current_round": 1,
            "scores": {},
            "question": None,
            "correct_answer": None,
            "time_left": 30
        }
        
        self.active_games[ctx.channel.id] = game_data
        
        embed = discord.Embed(
            title="🎯 Trivia Game Starting!",
            description=f"A {rounds}-round trivia game is about to begin!\nReact with ✅ to join!",
            color=0x00ff00
        )
        embed.add_field(name="Rules", value="• You have 30 seconds to answer\n• First correct answer gets points\n• Points: 10 for correct, 0 for wrong", inline=False)
        
        message = await ctx.send(embed=embed)
        await message.add_reaction("✅")
        
        # Wait 10 seconds for players to join
        await asyncio.sleep(10)
        
        # Start the game
        await self.play_round(ctx)

    async def play_round(self, ctx):
        """Play a single round of trivia"""
        game_data = self.active_games[ctx.channel.id]
        
        if game_data["current_round"] > game_data["rounds"]:
            await self.end_game(ctx)
            return

        # Select random question
        question_data = random.choice(self.questions)
        game_data["question"] = question_data
        game_data["correct_answer"] = question_data["correct"]
        game_data["time_left"] = 30

        # Create question embed
        embed = discord.Embed(
            title=f"🎯 Round {game_data['current_round']}/{game_data['rounds']}",
            description=f"**{question_data['question']}**",
            color=0x0099ff
        )
        
        options_text = ""
        for i, option in enumerate(question_data["options"]):
            options_text += f"**{i+1}.** {option}\n"
        
        embed.add_field(name="Options", value=options_text, inline=False)
        embed.add_field(name="Category", value=question_data["category"], inline=True)
        embed.add_field(name="Time", value="30 seconds", inline=True)
        
        message = await ctx.send(embed=embed)
        
        # Add number reactions
        for i in range(len(question_data["options"])):
            await message.add_reaction(f"{i+1}️⃣")

        # Wait for answers
        correct_answer = None
        for _ in range(30):  # 30 seconds
            await asyncio.sleep(1)
            game_data["time_left"] -= 1
            
            # Check for correct answers
            if message.reactions:
                for reaction in message.reactions:
                    if reaction.emoji == f"{game_data['correct_answer']+1}️⃣":
                        async for user in reaction.users():
                            if not user.bot and user not in [correct_answer] if correct_answer else []:
                                correct_answer = user
                                break
                        if correct_answer:
                            break
                if correct_answer:
                    break

        # Show results
        await self.show_round_results(ctx, message, correct_answer, game_data)

    async def show_round_results(self, ctx, message, correct_answer, game_data):
        """Show the results of a round"""
        question_data = game_data["question"]
        
        embed = discord.Embed(
            title=f"🎯 Round {game_data['current_round']} Results",
            color=0x00ff00 if correct_answer else 0xff0000
        )
        
        if correct_answer:
            # Award points
            if correct_answer.id not in game_data["scores"]:
                game_data["scores"][correct_answer.id] = 0
            game_data["scores"][correct_answer.id] += 10
            
            embed.description = f"✅ **{correct_answer.name}** got it correct!"
            embed.add_field(name="Answer", value=f"**{question_data['options'][question_data['correct']]}**", inline=True)
            embed.add_field(name="Points", value=f"+10 points!", inline=True)
        else:
            embed.description = "⏰ Time's up! No one got it correct."
            embed.add_field(name="Correct Answer", value=f"**{question_data['options'][question_data['correct']]}**", inline=True)
        
        # Show current scores
        if game_data["scores"]:
            scores_text = ""
            sorted_scores = sorted(game_data["scores"].items(), key=lambda x: x[1], reverse=True)
            for i, (user_id, score) in enumerate(sorted_scores[:5]):
                user = self.bot.get_user(user_id)
                name = user.name if user else f"User {user_id}"
                scores_text += f"**{i+1}.** {name}: {score} points\n"
            
            embed.add_field(name="Current Scores", value=scores_text, inline=False)
        
        await ctx.send(embed=embed)
        
        # Move to next round
        game_data["current_round"] += 1
        
        if game_data["current_round"] <= game_data["rounds"]:
            await asyncio.sleep(3)
            await self.play_round(ctx)
        else:
            await self.end_game(ctx)

    async def end_game(self, ctx):
        """End the trivia game and show final results"""
        game_data = self.active_games[ctx.channel.id]
        
        embed = discord.Embed(
            title="🏆 Trivia Game Complete!",
            description="Final Results:",
            color=0xffd700
        )
        
        if game_data["scores"]:
            sorted_scores = sorted(game_data["scores"].items(), key=lambda x: x[1], reverse=True)
            
            # Update global scores
            for user_id, score in game_data["scores"].items():
                if user_id not in self.scores:
                    self.scores[user_id] = 0
                self.scores[user_id] += score
            
            # Show final rankings
            for i, (user_id, score) in enumerate(sorted_scores):
                user = self.bot.get_user(user_id)
                name = user.name if user else f"User {user_id}"
                medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "🏅"
                embed.add_field(name=f"{medal} {i+1}. {name}", value=f"{score} points", inline=False)
            
            winner_id = sorted_scores[0][0]
            winner = self.bot.get_user(winner_id)
            winner_name = winner.name if winner else f"User {winner_id}"
            embed.set_footer(text=f"🏆 Winner: {winner_name}!")
        else:
            embed.description = "No one participated in the game."
        
        await ctx.send(embed=embed)
        
        # Clean up
        del self.active_games[ctx.channel.id]

    @commands.command(name='triviascores')
    async def show_trivia_scores(self, ctx):
        """Show global trivia scores"""
        if not self.scores:
            await ctx.send("No trivia games have been played yet!")
            return
        
        embed = discord.Embed(
            title="🏆 Global Trivia Scores",
            color=0xffd700
        )
        
        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
        
        for i, (user_id, score) in enumerate(sorted_scores[:10]):
            user = self.bot.get_user(user_id)
            name = user.name if user else f"User {user_id}"
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "🏅"
            embed.add_field(name=f"{medal} {i+1}. {name}", value=f"{score} points", inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(name='triviareset')
    @commands.has_permissions(administrator=True)
    async def reset_trivia_scores(self, ctx):
        """Reset all trivia scores (Admin only)"""
        self.scores = {}
        await ctx.send("✅ All trivia scores have been reset!")

async def setup(bot):
    await bot.add_cog(Trivia(bot)) 