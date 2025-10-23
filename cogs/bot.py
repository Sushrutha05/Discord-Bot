import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import aiohttp

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
leetcode_api = os.getenv('LEETCODE_API')
available_roles = ["Manual Coder", "Vibe Coder"]

leetcode_registered_users = {}

class LeetcodeCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def leetcode_register(self, ctx, *, username:str = None):
        if not username:
            await ctx.send(f"Please provide the Leetcode username inorder to register.\n")
            return

        leetcode_registered_users[ctx.author.id] = username
        await ctx.send(f"Leetcode username: {username}has been registered.\n")
        
    @commands.command()
    async def leetcode_unregister(self, ctx, *, username):
        if not username:
            await ctx.send(f"Please provide the Leetcode username inorder to register.\n")
            return
    
        if leetcode_registered_users[username] == ctx.author.id:
            del leetcode_registered_users[username]
            await ctx.send(f"Leetcode username: {username}has been deleted.\n")        
        else:
            await ctx.send(f"Only the person who has registered the LeetCode username can delete it.\n")
        

    @commands.command()
    async def leetcode_stats(self, ctx, *, username:str = None):
        if not username:
            username = leetcode_registered_users[ctx.author.id]
        
        leetcode_url = leetcode_api + username

        leetcode_url_solved = leetcode_url + '/solved'


        name = None
        ranking = 'N/A'
        reputation = 'N/A'
        total_sub_result_string = ""
        ac_result_string = ""
        solved_total = "N/A"
        easy_solved = "N/A"
        medium_solved = "N/A"
        hard_solved = "N/A"

        async with aiohttp.ClientSession() as session:

            async with session.get(leetcode_url) as response:
                if response.status == 200:   
                    json_response = await response.json()
                    name = json_response.get('name')
                    ranking = json_response.get('ranking')
                    reputation = json_response.get('reputation')
                elif response.status == 404:
                    await ctx.send(f"Error: LeetCode user '{username}' not found.")
                    return
                else:
                    await ctx.send(f"Error: The API is down or returned an error. (Status: {response.status})")
                    return


            async with session.get(leetcode_url_solved) as response:
                if response.status == 200:   
                    json_response = await response.json()
                    solved_total = json_response.get('solvedProblem', 'N/A')
                    easy_solved = json_response.get('easySolved', 'N/A')
                    medium_solved = json_response.get('mediumSolved', 'N/A')
                    hard_solved = json_response.get('hardSolved', 'N/A')

                    for item in json_response.get('totalSubmissionNum', []):
                        total_sub_result_string += f"**{item['difficulty']}**: {item['count']} , {item['submissions']} submissions.\n"

                    for item in json_response.get('acSubmissionNum', []):
                        ac_result_string += f"**{item['difficulty']}**: {item['count']} , {item['submissions']} submissions.\n"

                elif response.status == 404:
                    await ctx.send(f"Error: LeetCode user '{username}' not found.")
                    return
                else:
                    
                    await ctx.send(f"Error: The API is down or returned an error. (Status: {response.status})")
                    return

            embed = discord.Embed(
                title= f"{username}'s LeetCode Stats",
                url = leetcode_url 
            )
            embed.add_field(name="Name: ", value = name or "N/A", inline=True)
            embed.add_field(name="LeetCode Username: ", value = username, inline=True)
            embed.add_field(name="Rank: ", value = ranking, inline=True)
            embed.add_field(name="Reputation: ", value = reputation, inline=True)
            embed.add_field(name="Total Solved", value=f"**{solved_total}**", inline=False)
            embed.add_field(name="Easy", value=easy_solved, inline=True)
            embed.add_field(name="Medium", value=medium_solved, inline=True)
            embed.add_field(name="Hard", value=hard_solved, inline=True)
            embed.add_field(name="Total Submissions", value=total_sub_result_string, inline=False)
            embed.add_field(name="Accepted Submissions", value=ac_result_string, inline=False)

            await ctx.send(embed = embed)

    @commands.command()
    async def leetcode_leaderboard(self, ctx):
        await ctx.send(f"Leetcode Leaderboard feature coming soon {ctx.author.mention}!")


class GithubCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def github_watch(self, ctx):
        await ctx.send(f"Github Watch feature coming soon {ctx.author.mention}!")

    @commands.command()
    async def github_unwatch(self, ctx):
        await ctx.send(f"Github Un-Watch feature coming soon {ctx.author.mention}!")

    @commands.command()
    async def github_list(self, ctx):
        await ctx.send(f"Github List feature coming soon {ctx.author.mention}!")



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