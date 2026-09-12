import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

user_tasks = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("➕ Add Task", callback_data="add_task")],
        [InlineKeyboardButton("📋 View Today's Tasks", callback_data="view_tasks")],
        [InlineKeyboardButton("✅ Mark Task Done", callback_data="done_task")],
        [InlineKeyboardButton("🗑️ Clear All Tasks", callback_data="clear_tasks")],
        [InlineKeyboardButton("❓ Help", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"👋 Hello {user.first_name}!\n\n"
        f"I'm *DailyPlannerBot* — your personal task planner.\n\n"
        f"Use the buttons below or type /add to create a task.",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "📖 *How to use DailyPlannerBot*\n\n"
        "/start - Show main menu\n"
        "/add <task> - Add a new task\n"
        "/list - View all your tasks\n"
        "/done <number> - Mark a task as done\n"
        "/clear - Delete all tasks\n"
        "/help - Show this message"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    task_text = " ".join(context.args)

    if not task_text:
        await update.message.reply_text(
            "✏️ Please provide a task.\nExample: `/add Buy groceries`",
            parse_mode="Markdown",
        )
        return

    user_tasks.setdefault(user_id, []).append(
        {"task": task_text, "done": False, "created": datetime.now().isoformat()}
    )
    await update.message.reply_text(f"✅ Task added: *{task_text}*", parse_mode="Markdown")


async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    tasks = user_tasks.get(user_id, [])

    if not tasks:
        await update.message.reply_text("📭 You have no tasks yet. Use /add to create one.")
        return

    message = "📋 *Your Tasks:*\n\n"
    for i, t in enumerate(tasks, start=1):
        status = "✅" if t["done"] else "⬜"
        message += f"{i}. {status} {t['task']}\n"

    await update.message.reply_text(message, parse_mode="Markdown")


async def done_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    tasks = user_tasks.get(user_id, [])

    if not context.args:
        await update.message.reply_text("Usage: `/done <task_number>`", parse_mode="Markdown")
        return

    try:
        index = int(context.args[0]) - 1
        if 0 <= index < len(tasks):
            tasks[index]["done"] = True
            await update.message.reply_text(
                f"🎉 Task marked as done: *{tasks[index]['task']}*", parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❌ Invalid task number.")
    except ValueError:
        await update.message.reply_text("❌ Please provide a valid number.")


async def clear_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_tasks[user_id] = []
    await update.message.reply_text("🗑️ All your tasks have been cleared.")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "add_task":
        await query.message.reply_text(
            "✏️ Send me your task using:\n`/add Your task here`", parse_mode="Markdown"
        )
    elif query.data == "view_tasks":
        user_id = query.from_user.id
        tasks = user_tasks.get(user_id, [])
        if not tasks:
            await query.message.reply_text("📭 You have no tasks yet.")
            return
        message = "📋 *Your Tasks:*\n\n"
        for i, t in enumerate(tasks, start=1):
            status = "✅" if t["done"] else "⬜"
            message += f"{i}. {status} {t['task']}\n"
        await query.message.reply_text(message, parse_mode="Markdown")
    elif query.data == "done_task":
        await query.message.reply_text(
            "Use `/done <number>` to mark a task complete.", parse_mode="Markdown"
        )
    elif query.data == "clear_tasks":
        user_tasks[query.from_user.id] = []
        await query.message.reply_text("🗑️ All tasks cleared.")
    elif query.data == "help":
        await query.message.reply_text("Use /add, /list, /done, and /clear to manage your tasks.")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("🤔 I don't understand that command. Try /help.")


def main() -> None:
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set!")

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("add", add_task))
    application.add_handler(CommandHandler("list", list_tasks))
    application.add_handler(CommandHandler("done", done_task))
    application.add_handler(CommandHandler("clear", clear_tasks))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    logger.info("🤖 DailyPlannerBot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
