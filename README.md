# Discord LeetCode & GitHub Bot

A Discord bot that tracks LeetCode progress and monitors GitHub repositories for new commits. Built with discord.py and SQLite.

## Features

### LeetCode Integration
- **Register LeetCode accounts** - Link your Discord account to your LeetCode username
- **View stats** - Display detailed LeetCode statistics including problems solved, ranking, and reputation
- **Leaderboard** - Compete with server members on a top 10 leaderboard

### GitHub Integration
- **Watch repositories** - Monitor GitHub repos for new commits
- **Automatic notifications** - Get notified in Discord when new commits are pushed
- **Unwatch repos** - Stop tracking repositories you're no longer interested in

### Role Management
- **Self-assign roles** - Users can assign themselves predefined roles
- **Remove roles** - Users can remove their own roles

### Miscellaneous
- **Welcome messages** - Greet new members when they join
- **Polls** - Create quick polls with thumbs up/down reactions
- **Content moderation** - Basic word filtering

## Commands

### LeetCode Commands
- `!leetcode_register <username>` - Register your LeetCode username
- `!leetcode_unregister` - Unregister your LeetCode account
- `!leetcode_stats [username]` - View LeetCode statistics (defaults to your registered username)
- `!leetcode_leaderboard` - Display the top 10 LeetCode users on the server

### GitHub Commands
- `!github_watch <repo_url>` - Start watching a GitHub repository for new commits
- `!github_unwatch <repo_url>` - Stop watching a repository
- `!github_list` - List all watched repositories

### Role Commands
- `!assign <role_name>` - Assign yourself a role (Manual Coder, Vibe Coder)
- `!remove <role_name>` - Remove a role from yourself

### Miscellaneous Commands
- `!hello` - Get a friendly greeting
- `!ping` - Check if the bot is responsive
- `!poll <question>` - Create a poll with 👍/👎 reactions

## Setup

### Prerequisites
- Python 3.8+
- Discord Bot Token
- LeetCode API access
- GitHub API access (optional)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Sushrutha05/Discord-Bot.git
cd Discord-Bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with the following variables:
```env
DISCORD_TOKEN=<your_discord_bot_token>
LEETCODE_API=https://alfa-leetcode-api.onrender.com/
GITHUB_API_FINE=<your_github_fine_grained_token>
GITHUB_API_GEN=<your_github_general_token>
GITHUB_API_URL=https://api.github.com/repos/
```

Note: A `.env.example` file is provided as a template.

4. Run the bot:
```bash
python main.py
```

## Configuration

### Environment Variables
- `DISCORD_TOKEN` - Your Discord bot token from the Discord Developer Portal
- `LEETCODE_API` - LeetCode API endpoint (uses alfa-leetcode-api.onrender.com)
- `GITHUB_API_FINE` - GitHub fine-grained personal access token (optional, for higher rate limits)
- `GITHUB_API_GEN` - GitHub general personal access token (optional, for higher rate limits)
- `GITHUB_API_URL` - GitHub API base URL (default: https://api.github.com/repos/)

### Database
The bot uses SQLite to store:
- LeetCode user registrations and solved problem counts
- GitHub repository watch list with last commit SHA

Database file: `bot_database.db`

## How It Works

### GitHub Monitoring
The bot checks watched repositories every 10 minutes for new commits. When a new commit is detected:
1. Fetches the latest commit from GitHub API
2. Compares with the stored SHA
3. Sends an embed notification to the designated channel
4. Updates the database with the new SHA

### LeetCode Tracking
- User data is fetched from the alfa-leetcode-api
- Statistics are stored in the database for leaderboard functionality
- Leaderboard ranks users by total problems solved

## Project Structure
```
.
├── main.py              # Bot initialization and GitHub monitoring loop
├── database.py          # Database setup and connection management
├── cogs/
│   └── bot.py          # Command implementations (LeetCode, GitHub, Roles)
├── requirements.txt     # Python dependencies
├── .env                # Environment variables (not tracked)
└── bot_database.db     # SQLite database (auto-generated)
```

## Contributing
Contributions are welcome! Feel free to open issues or submit pull requests.


## Support
For issues or questions, please open an issue on GitHub or contact the me.
