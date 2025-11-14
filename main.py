import discord
from discord.ext import tasks, commands
import logging
from dotenv import load_dotenv
import os
import asyncio
import database
import aiohttp

"""
# ======= DATABASE SETUP AND CONNECTION ========
database.setup_database()

"""

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(name)s: %(message)s",
    handlers=[logging.FileHandler("discord.log", mode="w"), logging.StreamHandler()]
)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


@tasks.loop(minutes=10) 
async def check_github_loop():
    print("Loop: Checking for new GitHub commits...")
    conn = None
    try:
        conn = database.get_connection()
        cursor = conn.cursor()
        
       
        cursor.execute("SELECT channel_id, repo_name, last_commit_sha FROM GITHUB_REPO")
        repos_to_check = cursor.fetchall()

        if not repos_to_check:
            print("Loop: No repos to check.")
            return

       
        async with aiohttp.ClientSession() as session:
            for job in repos_to_check:
                channel_id, repo_name, last_commit_sha = job
                
                api_url = f"https://api.github.com/repos/{repo_name}/commits"
                
                try:
                    async with session.get(api_url) as response:
                        if response.status == 200:
                            commits = await response.json()
                            if not commits:
                                continue

                            new_sha = commits[0]['sha']

                            
                            if new_sha != last_commit_sha:
                                print(f"Loop: New commit found for {repo_name}!")
                                
              
                                channel = bot.get_channel(channel_id)
                                if not channel:
                                    print(f"Loop: ERROR - Cannot find channel {channel_id}")
                                    continue

                                if last_commit_sha is None:
                                    print(f"Loop: Initializing SHA for {repo_name}.")
                                else:
                                    commit_data = commits[0]['commit']
                                    author_name = commit_data['author']['name']
                                    commit_message = commit_data['message'].split('\n')[0] 
                                    commit_url = commits[0]['html_url']

                                    embed = discord.Embed(
                                        title=f"New Commit in {repo_name}",
                                        description=f"`{commit_message}`",
                                        url=commit_url,
                                        color=discord.Color.green()
                                    )
                                    embed.set_author(name=author_name)
                                    
                                    await channel.send(embed=embed)

                                cursor.execute(
                                    "UPDATE GITHUB_REPO SET last_commit_sha = ? WHERE channel_id = ? AND repo_name = ?",
                                    (new_sha, channel_id, repo_name)
                                )
                              

                        elif response.status == 404:
                            print(f"Loop: ERROR - Repo {repo_name} not found (404). Removing from watch.")
                            cursor.execute("DELETE FROM GITHUB_REPO WHERE channel_id = ? AND repo_name = ?", (channel_id, repo_name))
                        
                        
                        elif response.status == 403:
                             print("Loop: ERROR - GitHub API rate limit (403). Pausing for this loop.")

                except Exception as e:
                    print(f"Loop: ERROR processing {repo_name}: {e}")
    
    except Exception as e:
        print(f"Loop: CRITICAL database error: {e}")
    finally:
        if conn:
            conn.commit()
            conn.close()

@check_github_loop.before_loop
async def before_check_github_loop():
    await bot.wait_until_ready()


@bot.event
async def on_ready():
    database.setup_database()
    check_github_loop.start() 
    print(f'{bot.user} has connected to Discord!')

async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    await load_cogs()
    await bot.start(token)

asyncio.run(main())
