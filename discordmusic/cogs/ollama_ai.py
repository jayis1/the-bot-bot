import asyncio
import discord
from discord.ext import commands
import ollama
import logging
import config

class OllamaAI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ollama_host = config.OLLAMA_HOST
        self.ollama_model = config.OLLAMA_MODEL
        logging.info(f"OllamaAI cog initialized with host: {self.ollama_host}, model: {self.ollama_model}")

    async def _get_ollama_response(self, prompt: str):
        try:
            response = await asyncio.to_thread(
                ollama.chat,
                model=self.ollama_model,
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.7} # Adjust temperature for creativity/accuracy
            )
            return response['message']['content']
        except Exception as e:
            logging.error(f"Error communicating with Ollama: {e}", exc_info=True)
            return f"Sorry, I couldn't connect to Ollama or get a response. Error: {e}"

    @commands.command(name="recommend", help="Get song recommendations from AI. Usage: ?recommend <genre/mood/artist>")
    async def recommend(self, ctx, *, query: str):
        await ctx.send(f"Thinking of song recommendations based on '{query}'...")
        
        prompt = f"You are a music recommendation AI. Based on the following query, suggest 3 songs. For each song, provide the song title and artist. Do not include any additional conversational text, just the recommendations. Query: {query}"
        
        recommendations_text = await self._get_ollama_response(prompt)
        
        if "Sorry, I couldn't connect" in recommendations_text:
            await ctx.send(recommendations_text)
            return

        # Attempt to parse recommendations and search on YouTube
        response_lines = recommendations_text.split('\n')
        music_cog = self.bot.get_cog('Music')
        
        if music_cog:
            embed = discord.Embed(title="🎵 AI Song Recommendations 🎵", description=f"Based on: '{query}'", color=discord.Color.green())
            found_any_songs = False
            for line in response_lines:
                line = line.strip()
                if line and ('.' in line or '-' in line): # Basic parsing for "1. Song Title - Artist" or "Song Title - Artist"
                    parts = line.split('-', 1)
                    if len(parts) == 2:
                        title_artist_query = f"{parts[0].strip()} {parts[1].strip()}"
                        # Use the existing search command from Music cog
                        # Note: This will send a separate message for each search result.
                        # For a cleaner output, we might need to modify Music.search to return results
                        # instead of sending messages directly. For now, this is a quick integration.
                        await music_cog.search(ctx, query=title_artist_query)
                        found_any_songs = True
            if not found_any_songs:
                embed.add_field(name="Recommendations", value=recommendations_text, inline=False)
                embed.set_footer(text="Could not parse recommendations into searchable songs. Displaying raw AI response.")
                await ctx.send(embed=embed)
            else:
                await ctx.send("Here are some recommendations. I've tried to find them on YouTube for you:")
        else:
            embed = discord.Embed(title="🎵 AI Song Recommendations 🎵", description=f"Based on: '{query}'", color=discord.Color.green())
            embed.add_field(name="Recommendations", value=recommendations_text, inline=False)
            embed.set_footer(text="Music cog not found, cannot search for songs.")
            await ctx.send(embed=embed)


    @commands.command(name="askmusic", help="Ask the AI a question about music. Usage: ?askmusic <your question>")
    async def ask_music(self, ctx, *, question: str):
        await ctx.send(f"Thinking about your question: '{question}'...")
        
        prompt = f"You are a helpful AI assistant specializing in music knowledge. Answer the following question concisely and accurately. Question: {question}"
        
        answer_text = await self._get_ollama_response(prompt)
        
        if "Sorry, I couldn't connect" in answer_text:
            await ctx.send(answer_text)
            return

        embed = discord.Embed(title="🎶 Music Q&A 🎶", description=f"Your question: '{question}'", color=discord.Color.blue())
        embed.add_field(name="AI's Answer", value=answer_text, inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="joke", help="Ask the AI to tell a joke. Usage: ?joke")
    async def joke(self, ctx):
        await ctx.send("Thinking of a joke...")
        
        prompt = "Tell me a short, family-friendly joke."
        
        joke_text = await self._get_ollama_response(prompt)
        
        if "Sorry, I couldn't connect" in joke_text:
            await ctx.send(joke_text)
            return

        embed = discord.Embed(title="😂 AI Joke 😂", description=joke_text, color=discord.Color.orange())
        await ctx.send(embed=embed)

    @commands.command(name="fact", help="Ask the AI to tell a random fact. Usage: ?fact")
    async def fact(self, ctx):
        await ctx.send("Thinking of a random fact...")
        
        prompt = "Tell me a random, interesting fact."
        
        fact_text = await self._get_ollama_response(prompt)
        
        if "Sorry, I couldn't connect" in fact_text:
            await ctx.send(fact_text)
            return

        embed = discord.Embed(title="💡 AI Fact 💡", description=fact_text, color=discord.Color.purple())
        await ctx.send(embed=embed)

    @commands.command(name="aisong", help="Ask the AI to find songs and add them to the queue. Usage: ?aisong <description of songs/playlist>")
    async def aisong(self, ctx, *, query: str):
        await ctx.send(f"Thinking of songs based on '{query}'...")
        
        prompt = f"You are a music expert AI. Based on the following description, suggest 3 songs. For each song, provide the song title and artist, separated by a hyphen. Do not include any additional conversational text, just the recommendations. Description: {query}"
        
        recommendations_text = await self._get_ollama_response(prompt)
        
        if "Sorry, I couldn't connect" in recommendations_text:
            await ctx.send(recommendations_text)
            return

        # Attempt to parse recommendations and search on YouTube
        response_lines = recommendations_text.split('\n')
        music_cog = self.bot.get_cog('Music')
        
        if music_cog:
            embed = discord.Embed(title="🎵 AI Song Suggestions 🎵", description=f"Based on: '{query}'", color=discord.Color.green())
            found_any_songs = False
            for line in response_lines:
                line = line.strip()
                if line and ('.' in line or '-' in line): # Basic parsing for "1. Song Title - Artist" or "Song Title - Artist"
                    parts = line.split('-', 1)
                    if len(parts) == 2:
                        title_artist_query = f"{parts[0].strip()} {parts[1].strip()}"
                        await ctx.send(f"AI suggested: **{parts[0].strip()}** by **{parts[1].strip()}**. Attempting to add to queue...")
                        await music_cog.play(ctx, query=title_artist_query)
                        found_any_songs = True
            if not found_any_songs:
                embed.add_field(name="Suggestions", value=recommendations_text, inline=False)
                embed.set_footer(text="Could not parse suggestions into searchable songs. Displaying raw AI response.")
                await ctx.send(embed=embed)
            else:
                await ctx.send("Here are some suggestions. I've tried to add them to the queue for you:")
        else:
            embed = discord.Embed(title="🎵 AI Song Suggestions 🎵", description=f"Based on: '{query}'", color=discord.Color.green())
            embed.add_field(name="Suggestions", value=recommendations_text, inline=False)
            embed.set_footer(text="Music cog not found, cannot add songs to queue.")
            await ctx.send(embed=embed)

    @commands.command(name="aidj", help="Become an AI DJ! Get a playlist based on a mood or activity. Usage: ?aidj <mood/activity>")
    async def aidj(self, ctx, *, query: str):
        await ctx.send(f"Spinning up a playlist for: '{query}'...")
        
        prompt = f"""You are an AI DJ. Based on the following mood or activity, suggest 3 songs that fit the vibe. List each song on a new line in the exact format: 'Song Title - Artist'. IMPORTANT: Do NOT include any numbering, introductory text, conversational filler, special tokens (like <mask> or <unusedXX>), or concluding conversational text. Only provide the song list, one song per line.
            
            Mood/Activity: {query}"""
            
        recommendations_text = await self._get_ollama_response(prompt)
        
        if "Sorry, I couldn't connect" in recommendations_text:
            await ctx.send(recommendations_text)
            return

        response_lines = recommendations_text.split('\n')
        music_cog = self.bot.get_cog('Music')
        
        if music_cog:
            embed = discord.Embed(title="🎧 AI DJ's Mix 🎧", description=f"For: '{query}'", color=discord.Color.blue())
            found_any_songs = False
            for line in response_lines:
                line = line.strip()
                if line: # Process every non-empty line
                    parts = line.split('-', 1)
                    if len(parts) == 2:
                        title_artist_query = f"{parts[0].strip()} {parts[1].strip()}"
                        await ctx.send(f"AI DJ suggests: **{parts[0].strip()}** by **{parts[1].strip()}**. Adding to queue...")
                        await music_cog.play(ctx, query=title_artist_query)
                        found_any_songs = True
                    else:
                        logging.warning(f"Could not parse song suggestion from Ollama: {line}")
            if not found_any_songs:
                embed.add_field(name="Mix", value=recommendations_text, inline=False)
                embed.set_footer(text="Could not parse suggestions into playable songs. Displaying raw AI response.")
                await ctx.send(embed=embed)
            else:
                await ctx.send("Here's your custom mix! I've added them to the queue for you:")
        else:
            embed = discord.Embed(title="🎧 AI DJ's Mix 🎧", description=f"For: '{query}'", color=discord.Color.blue())
            embed.add_field(name="Mix", value=recommendations_text, inline=False)
            embed.set_footer(text="Music cog not found, cannot add songs to queue.")
            await ctx.send(embed=embed)

    @commands.command(name="aidj_longer", help="Become an AI DJ! Get a longer playlist (10 songs) based on a mood or activity. Usage: ?aidj_longer <mood/activity>")
    async def aidj_longer(self, ctx, *, query: str):
        await ctx.send(f"Spinning up a longer playlist for: '{query}'...")
        
        prompt = f"""You are an AI DJ. Based on the following mood or activity, suggest 10 songs that fit the vibe. List each song on a new line in the exact format: 'Song Title - Artist'. IMPORTANT: Do NOT include any numbering, introductory text, conversational filler, special tokens (like <mask> or <unusedXX>), or concluding conversational text. Only provide the song list, one song per line.
            
            Mood/Activity: {query}"""
            
        recommendations_text = await self._get_ollama_response(prompt)
        
        if "Sorry, I couldn't connect" in recommendations_text:
            await ctx.send(recommendations_text)
            return

        response_lines = recommendations_text.split('\n')
        music_cog = self.bot.get_cog('Music')
        
        if music_cog:
            embed = discord.Embed(title="🎧 AI DJ's Longer Mix 🎧", description=f"For: '{query}'", color=discord.Color.blue())
            found_any_songs = False
            for line in response_lines:
                line = line.strip()
                if line: # Process every non-empty line
                    parts = line.split('-', 1)
                    if len(parts) == 2:
                        title_artist_query = f"{parts[0].strip()} {parts[1].strip()}"
                        await ctx.send(f"AI DJ suggests: **{parts[0].strip()}** by **{parts[1].strip()}**. Adding to queue...")
                        await music_cog.play(ctx, query=title_artist_query)
                        found_any_songs = True
                    else:
                        logging.warning(f"Could not parse song suggestion from Ollama: {line}")
            if not found_any_songs:
                embed.add_field(name="Mix", value=recommendations_text, inline=False)
                embed.set_footer(text="Could not parse suggestions into playable songs. Displaying raw AI response.")
                await ctx.send(embed=embed)
            else:
                await ctx.send("Here's your custom longer mix! I've added them to the queue for you:")
        else:
            embed = discord.Embed(title="🎧 AI DJ's Longer Mix 🎧", description=f"For: '{query}'", color=discord.Color.blue())
            embed.add_field(name="Mix", value=recommendations_text, inline=False)
            embed.set_footer(text="Music cog not found, cannot add songs to queue.")
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(OllamaAI(bot))