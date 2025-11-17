import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import aiohttp
import sqlite3
import database
import re

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
leetcode_api = os.getenv('LEETCODE_API')
github_api_fine = os.getenv('GITHUB_API_FINE')
github_api_gen = os.getenv('GITHUB_API_GEN')
github_api_url = os.getenv('GITHUB_API_URL')
available_roles = ["Manual Coder", "Vibe Coder"]


class LeetcodeCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def leetcode_register(self, ctx, *, username: str = None):
        if not username:
            await ctx.send("Please provide a LeetCode username. Usage: `!leetcode_register <username>`")
            return
            
        conn = None
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            
            leetcode_url = leetcode_api + username
            leetcode_url_solved = leetcode_url + '/solved'
            async with aiohttp.ClientSession() as session:
                async with session.get(leetcode_url_solved) as response:
                    if response.status == 200:   
                        json_response = await response.json()
                        solved_total = json_response.get('solvedProblem', 0)

            sql = "INSERT OR REPLACE INTO LEETCODE_USER (discord_id, leetcode_username, solved_problem) VALUES (?, ?, ?)"
            cursor.execute(sql, (ctx.author.id, username, solved_total))

            conn.commit()

            await ctx.send(f"Success! Your LeetCode username has been registered as: `{username}`")

        except Exception as e:
            await ctx.send(f"An error occurred while trying to register: {e}")        
        finally:
            if conn:
                conn.close()
        
    @commands.command()
    async def leetcode_unregister(self, ctx):
        conn = None
        try:
            conn = database.get_connection()
            cursor = conn.cursor()

            sql = "DELETE FROM LEETCODE_USER WHERE discord_id = ?"
            
            cursor.execute(sql, (ctx.author.id,))
      
            if cursor.rowcount == 0:
                await ctx.send("You were not registered in the first place!")
            else:
                conn.commit() 
                await ctx.send("You have been successfully unregistered.")

        except Exception as e:
            await ctx.send(f"An error occurred while trying to unregister: {e}")

        finally:
            if conn:
                conn.close()
        

    @commands.command()
    async def leetcode_stats(self, ctx, *, username: str = None):

        async def fetch_from_db(discord_id: int):
            conn = None
            try:
                conn = database.get_connection()
                cursor = conn.cursor()

                sql = """
                SELECT leetcode_username
                FROM LEETCODE_USER
                WHERE discord_id = %s
                """
                cursor.execute(sql, (discord_id,))
                result = cursor.fetchone()
                return result[0] if result else None

            except Exception:
                return None

            finally:
                if conn:
                    conn.close()


        async def fetch_json(session, url: str):
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()
                if resp.status == 404:
                    return "not_found"
                return f"error:{resp.status}"


        
        if not username:
            username = await fetch_from_db(ctx.author.id)
            if not username:
                await ctx.send(
                    "I couldn't find a linked LeetCode username for you. "
                    "Please provide it explicitly."
                )
                return

        
        profile_url = leetcode_api + username
        solved_url = profile_url + "/solved"

        
        name = "N/A"
        ranking = "N/A"
        reputation = "N/A"
        solved_total = "N/A"
        easy_solved = "N/A"
        medium_solved = "N/A"
        hard_solved = "N/A"
        total_sub_string = ""
        ac_sub_string = ""

        async with aiohttp.ClientSession() as session:

            # --- Profile data ---
            prof = await fetch_json(session, profile_url)
            if prof == "not_found":
                await ctx.send(f"LeetCode user **{username}** not found.")
                return
            if isinstance(prof, str) and prof.startswith("error"):
                code = prof.split(":")[1]
                await ctx.send(f"LeetCode API error. (Status: {code})")
                return

            name = prof.get("name", "N/A")
            ranking = prof.get("ranking", "N/A")
            reputation = prof.get("reputation", "N/A")

            # --- Solved stats ---
            solved = await fetch_json(session, solved_url)
            if solved == "not_found":
                await ctx.send(f"LeetCode user **{username}** not found.")
                return
            if isinstance(solved, str) and solved.startswith("error"):
                code = solved.split(":")[1]
                await ctx.send(f"LeetCode API error. (Status: {code})")
                return

            solved_total = solved.get("solvedProblem", "N/A")
            easy_solved = solved.get("easySolved", "N/A")
            medium_solved = solved.get("mediumSolved", "N/A")
            hard_solved = solved.get("hardSolved", "N/A")

            for item in solved.get("totalSubmissionNum", []):
                diff = item.get("difficulty", "N/A")
                count = item.get("count", "N/A")
                subs = item.get("submissions", "N/A")
                total_sub_string += f"**{diff}**: {count}, {subs} submissions.\n"

            for item in solved.get("acSubmissionNum", []):
                diff = item.get("difficulty", "N/A")
                count = item.get("count", "N/A")
                subs = item.get("submissions", "N/A")
                ac_sub_string += f"**{diff}**: {count}, {subs} submissions.\n"

        
        if not total_sub_string:
            total_sub_string = "No submission data available."

        if not ac_sub_string:
            ac_sub_string = "No accepted submission data available."

        
        embed = discord.Embed(
            title=f"{username}'s LeetCode Stats",
            url=profile_url
        )

        embed.add_field(name="Name", value=name, inline=True)
        embed.add_field(name="LeetCode Username", value=username, inline=True)
        embed.add_field(name="Rank", value=ranking, inline=True)
        embed.add_field(name="Reputation", value=reputation, inline=True)
        embed.add_field(name="Total Solved", value=f"**{solved_total}**", inline=False)
        embed.add_field(name="Easy", value=easy_solved, inline=True)
        embed.add_field(name="Medium", value=medium_solved, inline=True)
        embed.add_field(name="Hard", value=hard_solved, inline=True)
        embed.add_field(name="Total Submissions", value=total_sub_string, inline=False)
        embed.add_field(name="Accepted Submissions", value=ac_sub_string, inline=False)

        await ctx.send(embed=embed)


    @commands.command()
    async def leetcode_leaderboard(self, ctx):
        conn = None

        try:
            conn = database.get_connection()
            cursor = conn.cursor()

            sql_query = """
                SELECT leetcode_username, solved_problem
                FROM LEETCODE_USER
                ORDER BY solved_problem DESC
                LIMIT 10
            """
            cursor.execute(sql_query)

            results = cursor.fetchall()

            if not results:
                await ctx.send("No users are registered for the leaderboard yet!")
                return
            
            

            for rank, user_data in enumerate(results, start=1):
                description_str = ""
                username = user_data[0]
                solved_count = user_data[1]

                if rank == 1:
                    description_str += f"🥇 **1. {username}** - {solved_count} solved\n"
                elif rank == 2:
                    description_str += f"🥈 **2. {username}** - {solved_count} solved\n"
                elif rank == 3:
                    description_str += f"🥉 **3. {username}** - {solved_count} solved\n"
                else:
                    description_str += f"**{rank}. {username}** - {solved_count} solved\n"

            embed = discord.Embed(
                title="🏆 LeetCode Leaderboard",
                description=description_str,
                color=discord.Color.gold() 
            )
            embed.set_footer(text="Data may be up to an hour old.")

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"An error occurred while fetching the leaderboard: {e}")
            print(f"Leaderboard Error: {e}")

        finally:
            
            if conn:
                conn.close()


class GithubCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def github_watch(self, ctx, repo_url:str):
        if 'github.com/' not in repo_url:
            return await ctx.send("Please provide valid repo url")
    
        repo_name = repo_url.split("github.com/", 1)[1].split("/", 2)[0:2]
        repo_name = "/".join(repo_name).strip()


        repo_watch_url = github_api_url + repo_name

        headers = {
            "User-Agent": "DiscordBot", 
            "Accept": "application/vnd.github+json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(repo_watch_url, headers=headers) as response:
                if(response.status == 200):
                    await ctx.send(f"Done. Watching {repo_name}")
                elif response.status == 404:
                    await ctx.send("404")
                else:
                    await ctx.send (f"Error: {response.status}")


        conn = None 
        try:
            conn = sqlite3.connect('bot_database.db')
            cursor = conn.cursor()

            channel_id_to_save = ctx.channel.id
            repo_name_to_save = repo_name 

            sql_query = "INSERT INTO GITHUB_REPO (channel_id, repo_name) VALUES (?, ?)"
            cursor.execute(sql_query, (channel_id_to_save, repo_name_to_save))

            conn.commit()

            await ctx.send(f"✅ Success! Now watching `{repo_name_to_save}` in this channel.")

        except sqlite3.IntegrityError:
            await ctx.send(f"This repo is already being watched in this channel.")

        except Exception as e:
            await ctx.send(f"An unexpected database error occurred: {e}")

        finally:
            if conn:
                conn.close()

    @commands.command()
    async def github_unwatch(self, ctx, *, repo_input: str = None):
        if not repo_input:
            await ctx.send("Please provide a repo URL or name. Usage: `!github_unwatch owner/repo`")
            return

        
        repo_name = None
        match = re.search(r"github\.com/([\w.-]+/[\w.-]+)", repo_input)
        if match:
            repo_name = match.group(1).replace(".git", "")
        elif "/" in repo_input: 
            repo_name = repo_input

        if not repo_name:
            await ctx.send("Invalid input. Please provide a full GitHub URL or a name in `owner/repo` format.")
            return

        
        conn = None
        try:
            conn = database.get_connection()
            cursor = conn.cursor()

            sql = "DELETE FROM GITHUB_REPO WHERE channel_id = ? AND repo_name = ?"
            
            cursor.execute(sql, (ctx.channel.id, repo_name))

            
            if cursor.rowcount == 0:
                
                await ctx.send(f"`{repo_name}` was not being watched in this channel.")
            else:
                
                conn.commit()
                await ctx.send(f"✅ Successfully unwatched `{repo_name}` for this channel.")

        except Exception as e:
            await ctx.send(f"An error occurred: {e}")
        finally:
            if conn:
                conn.close()

    @commands.command()
    async def github_list(self, ctx):

        conn = None 
        try:
            conn = sqlite3.connect('bot_database.db')
            cursor = conn.cursor()

            sql_query = "SELECT repo_name FROM GITHUB_REPO"
            cursor.execute(sql_query)
            rows = cursor.fetchall()

            if not rows:
                await ctx.send("No repositories found")
                return
            
            repo_list = "\n".join(f"- {row[0]}" for row in rows)[:-4]
            await ctx.send(f"📁 **Repositories being watched:**\n{repo_list}")

        except Exception as e:
            await ctx.send(f"An unexpected database error occurred: {e}")

        finally:
            if conn:
                conn.close()


class RoleCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def assign(self, ctx, *, role_name: str):
        if role_name not in available_roles:
            await ctx.send(f"You can only assign one of these roles: {', '.join(available_roles)}")
            return

        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role:
            await ctx.author.add_roles(role)
            await ctx.send(f"{ctx.author.mention} is now assigned the role **{role.name}**")
        else:
            await ctx.send(f"Role **'{role_name}'** not found on the server.")

    @commands.command()
    async def remove(self, ctx, *, role_name:str = None):
        if not role_name:
            await ctx.send("❗ Please specify a role to remove, e.g. `!remove Manual Coder`")
            return
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role in ctx.author.roles:
            await ctx.author.remove_roles(role)
            await ctx.send(f"{ctx.author.mention} has removed thier **{role.name} ** role")
        else:
            await ctx.send(f"Role **'{role_name}'** not found on the server.\n Or the Role **'{role_name}'** was not assigned to {ctx.author.mention}")


    @commands.command()
    async def poll(self, ctx, *, question):
        embed = discord.Embed(title = "Poll Time!", description= question)
        poll_message = await ctx.send(embed = embed)
        await poll_message.add_reaction("👍")
        await poll_message.add_reaction("👎")


class MiscellaneousCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"LeetBot is ready to go in {self.bot.user.name}")
        print("🔧 Loaded commands:")
        for command_name in self.bot.all_commands:
            print(f" - {command_name}")


    @commands.Cog.listener()
    async def on_member_join(self, member):
        await member.send(f"Welcome to the server {member.name}")


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
            
        if "shit" in message.content.lower():
            await message.delete()
            await message.channel.send(f"{message.author.mention} - don't use that word")

            await self.bot.process_commands(message)


    @commands.command()
    async def hello(self, ctx):
        await ctx.send(f"Hello {ctx.author.mention}!")


    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong!")

    @commands.command()
    async def check(self, ctx):
        await ctx.send(ctx.author.id)


async def setup(bot):
    await bot.add_cog(LeetcodeCommands(bot))
    await bot.add_cog(GithubCommands(bot))
    await bot.add_cog(RoleCommands(bot))
    await bot.add_cog(MiscellaneousCommands(bot))