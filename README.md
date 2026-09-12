# 📅 DailyPlannerBot

A simple Telegram bot to manage your daily tasks.

## Features
- ➕ Add tasks
- 📋 View all tasks
- ✅ Mark tasks as done
- 🗑️ Clear all tasks
- 🎛️ Inline keyboard menu

## Commands
| Command | Description |
|---------|-------------|
| `/start` | Show main menu |
| `/add <task>` | Add a new task |
| `/list` | View all tasks |
| `/done <number>` | Mark a task as done |
| `/clear` | Delete all tasks |
| `/help` | Show help message |

## Deployment on Railway
1. Push this repo to GitHub.
2. Create a new project on Railway.
3. Deploy from your GitHub repo.
4. Add environment variable: `TELEGRAM_BOT_TOKEN=<your_token>`
5. Railway will build and run the bot automatically.

## Local Development
```bash
pip install -r requirements.txt
cp .env.example .env
# Add your token to .env
python bot.py
